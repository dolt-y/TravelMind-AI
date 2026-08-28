"""POI兴趣地点 搜索、详情和景点图片业务服务。"""

from __future__ import annotations

import asyncio

from loguru import logger

from app.integrations.maps import AmapPOIProvider, AmapPOIProviderError
from app.integrations.xhs import XHSProvider, XHSProviderError
from app.models.poi import POI
from app.storage.poi_repository import POIRepository, POIRepositoryError


class POIServiceError(RuntimeError):
    """POI 业务操作失败。"""


def _search_photo_from_xhs(name: str) -> str:
    """从小红书搜索景点笔记并提取首张图片地址。"""
    with XHSProvider() as provider:
        notes = provider.search_notes(f"{name} 风景", limit=5, sort_type=1)
        photo_url = next((url for note in notes for url in note.images), "")
        if photo_url:
            return photo_url
        for note in notes:
            if not note.note_id:
                continue
            try:
                detail = provider.get_note(
                    note.note_id,
                    xsec_token=note.xsec_token,
                    xsec_source=note.xsec_source,
                )
            except XHSProviderError:
                continue
            photo_url = next(iter(detail.images), "")
            if photo_url:
                return photo_url
    return ""


class POIService:
    """协调地图 POI、景点图片和 SQLite 持久化。"""

    def __init__(
        self,
        *,
        provider: AmapPOIProvider | None = None,
        repository: POIRepository | None = None,
    ):
        """初始化地图 Provider 和 POI 仓储。"""
        self.provider = provider
        self.repository = repository or POIRepository()

    def search(self, keywords: str, city: str, citylimit: bool, limit: int) -> list[POI]:
        """搜索 POI，保存结果后返回标准化领域对象。"""
        logger.info("开始查询高德 POI：城市={}，关键词={}", city, keywords)
        try:
            if self.provider is None:
                with AmapPOIProvider() as provider:
                    pois = provider.search(keywords, city, citylimit=citylimit, limit=limit)
            else:
                pois = self.provider.search(keywords, city, citylimit=citylimit, limit=limit)
            self.repository.save_search(pois, keywords=keywords, city=city)
            logger.info("高德 POI 查询完成：返回 {} 条并已保存", len(pois))
            return pois
        except (AmapPOIProviderError, POIRepositoryError) as exc:
            raise POIServiceError(str(exc)) from exc

    def detail(self, poi_id: str) -> POI:
        """优先读取已保存的 POI 详情，未命中时请求高德并保存。"""
        try:
            cached = self.repository.get_poi(poi_id)
            if cached is not None:
                logger.info("POI 详情命中本地缓存：{}", poi_id)
                return cached
            logger.info("POI 详情未命中缓存，正在请求高德：{}", poi_id)
            if self.provider is None:
                with AmapPOIProvider() as provider:
                    poi = provider.detail(poi_id)
            else:
                poi = self.provider.detail(poi_id)
            self.repository.save_search([poi], keywords="", city=poi.city)
            logger.info("POI 详情获取完成并已保存：{}", poi.name)
            return poi
        except (AmapPOIProviderError, POIRepositoryError) as exc:
            raise POIServiceError(str(exc)) from exc

    async def photo(self, name: str, city: str | None = None) -> str:
        """读取景点图片缓存，未命中时从小红书搜索首张图片并保存。"""
        name = name.strip()
        city = (city or "").strip()
        if not name:
            raise POIServiceError("景点名称不能为空")
        try:
            cached = self.repository.get_photo(name, city)
            if cached is not None:
                logger.info("景点图片命中本地缓存：{}", name)
                return cached
            logger.info("景点图片未命中缓存，正在搜索小红书：{}", name)
            # 说明：小红书客户端是同步实现，放到线程中避免阻塞 FastAPI 事件循环。
            photo_url = await asyncio.to_thread(_search_photo_from_xhs, name)
        except (XHSProviderError, POIRepositoryError) as exc:
            raise POIServiceError(str(exc)) from exc
        try:
            self.repository.save_photo(name, city, photo_url)
        except POIRepositoryError as exc:
            raise POIServiceError(str(exc)) from exc
        logger.info("景点图片查询完成：{}{}", name, "，已找到图片" if photo_url else "，未找到图片")
        return photo_url
