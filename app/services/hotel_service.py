"""酒店查询条件、供应商调用和缓存协调服务。"""

from __future__ import annotations

import os
from collections.abc import Iterable

from loguru import logger

from app.integrations.maps import (
    AmapHotelProvider,
    HotelProvider,
    HotelProviderError,
)
from app.models.hotel import Hotel, HotelSearchCriteria, HotelSearchResult
from app.storage.hotel_repository import HotelRepository, HotelRepositoryError


class HotelServiceError(RuntimeError):
    """酒店查询依赖或数据处理异常。"""


class HotelStorageError(HotelServiceError):
    """酒店查询结果无法从缓存读取或写入。"""


def _cache_ttl_seconds() -> int:
    """读取酒店缓存时长，非法配置使用二十四小时。"""
    try:
        return max(60, int(os.getenv("HOTEL_CACHE_TTL_SECONDS", "86400")))
    except ValueError:
        return 86400


def _matches_known_budget(hotel: Hotel, criteria: HotelSearchCriteria) -> bool:
    """按供应商参考价过滤明确超预算的酒店；价格缺失时保留候选。"""
    price = hotel.average_price
    if price is None:
        return True
    if criteria.budget_min is not None and price < criteria.budget_min:
        return False
    if criteria.budget_max is not None and price > criteria.budget_max:
        return False
    return True


class HotelService:
    """按业务条件查询酒店并复用 SQLite 缓存。"""

    def __init__(
        self,
        *,
        provider: HotelProvider | None = None,
        repository: HotelRepository | None = None,
        cache_ttl_seconds: int | None = None,
    ):
        """配置酒店 Provider 和缓存仓储，并支持测试注入替代实现。"""
        self.provider = provider
        try:
            self.repository = repository or HotelRepository()
        except HotelRepositoryError as exc:
            raise HotelStorageError(str(exc)) from exc
        configured_ttl = _cache_ttl_seconds() if cache_ttl_seconds is None else cache_ttl_seconds
        self.cache_ttl_seconds = max(60, configured_ttl)

    def search(self, criteria: HotelSearchCriteria) -> HotelSearchResult:
        """按城市和住宿条件查询酒店，优先返回有效缓存。"""
        provider_name = getattr(self.provider, "provider_name", "amap")
        logger.info(
            "开始查询酒店：城市={}，住宿偏好={}，区域={}，供应商={}",
            criteria.city,
            criteria.accommodation or "无",
            criteria.area or "无",
            provider_name,
        )
        try:
            cached = self.repository.get_search(
                provider=provider_name,
                criteria=criteria,
                max_age_seconds=self.cache_ttl_seconds,
            )
        except HotelRepositoryError as exc:
            raise HotelStorageError(str(exc)) from exc
        if cached is not None:
            logger.info("酒店缓存命中：城市={}，返回 {} 家", criteria.city, len(cached))
            return HotelSearchResult(
                provider=provider_name,
                criteria=criteria,
                cached=True,
                hotels=cached,
            )

        logger.info("酒店缓存未命中，正在请求供应商：城市={}", criteria.city)
        try:
            if self.provider is None:
                with AmapHotelProvider() as provider:
                    hotels = provider.search_hotels(criteria)
            else:
                hotels = self.provider.search_hotels(criteria)
        except HotelProviderError as exc:
            logger.error("酒店供应商查询失败：城市={}，原因={}", criteria.city, exc)
            raise HotelServiceError(str(exc)) from exc

        hotels = [hotel for hotel in hotels if _matches_known_budget(hotel, criteria)]
        try:
            self.repository.save_search(
                hotels,
                provider=provider_name,
                criteria=criteria,
            )
        except HotelRepositoryError as exc:
            raise HotelStorageError(str(exc)) from exc
        logger.info("酒店查询完成：城市={}，返回 {} 家并已缓存", criteria.city, len(hotels))
        return HotelSearchResult(
            provider=provider_name,
            criteria=criteria,
            cached=False,
            hotels=hotels,
        )

    def search_many(
        self,
        criteria_items: Iterable[HotelSearchCriteria],
    ) -> list[HotelSearchResult]:
        """按输入顺序查询多个城市，供行程编排汇总城市资料。"""
        return [self.search(criteria) for criteria in criteria_items]
