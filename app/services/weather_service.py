"""天气查询、日期覆盖校验和缓存协调服务。"""

from __future__ import annotations

import os
from datetime import date, timedelta

from loguru import logger

from app.integrations.maps import (
    AmapWeatherProvider,
    WeatherProvider,
    WeatherProviderError,
)
from app.models.weather import WeatherForecast, WeatherQueryResult
from app.storage.weather_repository import WeatherRepository, WeatherRepositoryError


class WeatherServiceError(RuntimeError):
    """天气查询依赖或数据处理异常。"""


class WeatherValidationError(WeatherServiceError):
    """天气查询城市或日期范围无效。"""


class WeatherStorageError(WeatherServiceError):
    """天气查询结果无法从缓存读取或写入。"""


def _cache_ttl_seconds() -> int:
    """读取天气缓存时长，非法配置使用三小时。"""
    try:
        return max(60, int(os.getenv("WEATHER_CACHE_TTL_SECONDS", "10800")))
    except ValueError:
        return 10800


def _requested_dates(start_date: date | None, end_date: date | None) -> set[date] | None:
    """校验日期参数并生成查询必须覆盖的日期集合。"""
    if start_date is None and end_date is None:
        return None
    if start_date is None:
        raise WeatherValidationError("指定结束日期时必须同时提供开始日期")
    end_date = end_date or start_date
    if end_date < start_date:
        raise WeatherValidationError("天气查询结束日期不能早于开始日期")
    if (end_date - start_date).days > 30:
        raise WeatherValidationError("天气查询日期范围不能超过 31 天")
    return {
        start_date + timedelta(days=offset)
        for offset in range((end_date - start_date).days + 1)
    }


def _covers(forecasts: list[WeatherForecast], expected: set[date] | None) -> bool:
    """判断缓存或供应商结果是否完整覆盖用户请求日期。"""
    if not forecasts:
        return False
    if expected is None:
        return True
    return expected.issubset({item.date for item in forecasts})


def _filter_dates(
    forecasts: list[WeatherForecast],
    expected: set[date] | None,
) -> list[WeatherForecast]:
    """仅保留用户日期范围内的预报。"""
    if expected is None:
        return forecasts
    return [item for item in forecasts if item.date in expected]


class WeatherService:
    """协调天气 Provider、日期范围和 SQLite 缓存。"""

    def __init__(
        self,
        *,
        provider: WeatherProvider | None = None,
        repository: WeatherRepository | None = None,
        cache_ttl_seconds: int | None = None,
    ):
        """初始化天气依赖，允许测试注入假 Provider 和临时数据库。"""
        self.provider = provider
        try:
            self.repository = repository or WeatherRepository()
        except WeatherRepositoryError as exc:
            raise WeatherStorageError(str(exc)) from exc
        configured_ttl = _cache_ttl_seconds() if cache_ttl_seconds is None else cache_ttl_seconds
        self.cache_ttl_seconds = max(60, configured_ttl)

    def query(
        self,
        city: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> WeatherQueryResult:
        """查询指定城市和日期范围的天气，优先返回有效缓存。"""
        city = city.strip()
        if not city:
            raise WeatherValidationError("天气查询城市不能为空")
        expected = _requested_dates(start_date, end_date)
        provider_name = getattr(self.provider, "provider_name", "amap")
        logger.info("开始查询天气：城市={}，供应商={}", city, provider_name)
        try:
            cached = self.repository.get_forecasts(
                provider=provider_name,
                city=city,
                max_age_seconds=self.cache_ttl_seconds,
                start_date=start_date,
                end_date=end_date or start_date,
            )
        except WeatherRepositoryError as exc:
            raise WeatherStorageError(str(exc)) from exc
        if _covers(cached, expected):
            logger.info("天气缓存命中：城市={}，返回 {} 天", city, len(cached))
            return WeatherQueryResult(
                provider=provider_name,
                city=city,
                cached=True,
                forecasts=_filter_dates(cached, expected),
            )

        logger.info("天气缓存未命中，正在请求供应商：城市={}", city)
        try:
            if self.provider is None:
                with AmapWeatherProvider() as provider:
                    forecasts = provider.forecast(city)
            else:
                forecasts = self.provider.forecast(city)
        except WeatherProviderError as exc:
            logger.error("天气供应商查询失败：城市={}，原因={}", city, exc)
            raise WeatherServiceError(str(exc)) from exc

        # 供应商可能返回规范城市名，缓存仍使用用户查询城市，确保相同请求可以稳定命中。
        forecasts = [
            item.model_copy(update={"provider": provider_name, "city": city})
            for item in forecasts
        ]

        try:
            self.repository.save_forecasts(forecasts)
        except WeatherRepositoryError as exc:
            raise WeatherStorageError(str(exc)) from exc

        selected = _filter_dates(forecasts, expected)
        if not _covers(selected, expected):
            available = "、".join(item.date.isoformat() for item in forecasts) or "无"
            raise WeatherValidationError(
                f"天气供应商当前未覆盖完整日期范围，可用预报日期：{available}"
            )
        logger.info("天气查询完成：城市={}，返回 {} 天并已缓存", city, len(selected))
        return WeatherQueryResult(
            provider=provider_name,
            city=city,
            cached=False,
            forecasts=selected,
        )
