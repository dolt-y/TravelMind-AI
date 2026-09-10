"""高德 Web 服务 POI 接口适配。"""

from __future__ import annotations

from typing import Any

import httpx

from app.models.poi import POI, POILocation

from .settings import amap_api_key


class AmapPOIProviderError(RuntimeError):
    """高德 POI 配置、网络或响应异常。"""


def _location(value: str) -> POILocation | None:
    """将高德的“经度,纬度”文本转换为坐标模型。"""
    try:
        longitude, latitude = value.split(",", 1)
        return POILocation(longitude=float(longitude), latitude=float(latitude))
    except (AttributeError, TypeError, ValueError):
        return None


def _poi_from_amap(item: dict[str, Any]) -> POI | None:
    """将高德 POI 字段映射为 TravelMind 领域对象。"""
    poi_id = str(item.get("id") or "").strip()
    name = str(item.get("name") or "").strip()
    location = _location(str(item.get("location") or ""))
    if not poi_id or not name or location is None:
        return None
    photos = [
        str(photo.get("url"))
        for photo in (item.get("photos") or [])
        if isinstance(photo, dict) and photo.get("url")
    ]
    rating_value = item.get("biz_ext", {}).get("rating") if isinstance(item.get("biz_ext"), dict) else None
    try:
        rating = float(rating_value) if rating_value not in (None, "") else None
    except (TypeError, ValueError):
        rating = None
    return POI(
        id=poi_id,
        name=name,
        type=str(item.get("type") or ""),
        address=str(item.get("address") or ""),
        location=location,
        tel=str(item.get("tel") or "") or None,
        city=str(item.get("cityname") or ""),
        rating=rating,
        photos=photos,
    )


class AmapPOIProvider:
    """调用高德 Web 服务完成 POI 搜索和详情查询。"""

    SEARCH_URL = "https://restapi.amap.com/v3/place/text"
    DETAIL_URL = "https://restapi.amap.com/v3/place/detail"

    def __init__(self, api_key: str | None = None, timeout: float = 10):
        """配置仅使用显式 Key 且不继承系统代理的 HTTP 客户端。"""
        self.api_key = (api_key or amap_api_key()).strip()
        if not self.api_key:
            raise AmapPOIProviderError(
                "高德 API Key 未配置，请设置 AMAP_API_KEY 或 VITE_AMAP_WEB_KEY"
            )
        self._client = httpx.Client(timeout=timeout, trust_env=False)

    def search(
        self,
        keywords: str,
        city: str,
        *,
        citylimit: bool = True,
        limit: int = 20,
    ) -> list[POI]:
        """按关键词和城市搜索 POI，并返回标准化结果。"""
        keywords = keywords.strip()
        city = city.strip()
        if not keywords:
            raise AmapPOIProviderError("POI 搜索关键词不能为空")
        if not city:
            raise AmapPOIProviderError("POI 搜索城市不能为空")
        params = {
            "key": self.api_key,
            "keywords": keywords,
            "city": city,
            "citylimit": "true" if citylimit else "false",
            "offset": max(1, min(50, limit)),
            "page": 1,
            "extensions": "all",
        }
        try:
            response = self._client.get(self.SEARCH_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AmapPOIProviderError("高德 POI 搜索请求失败") from exc
        if payload.get("status") != "1":
            raise AmapPOIProviderError(f"高德 POI 搜索失败: {payload.get('info', '未知错误')}")
        return [
            poi
            for item in payload.get("pois", [])
            if isinstance(item, dict)
            for poi in [_poi_from_amap(item)]
            if poi is not None
        ]

    def detail(self, poi_id: str) -> POI:
        """根据高德 POI ID 获取详情。"""
        poi_id = poi_id.strip()
        if not poi_id:
            raise AmapPOIProviderError("POI ID 不能为空")
        try:
            response = self._client.get(
                self.DETAIL_URL,
                params={"key": self.api_key, "id": poi_id, "extensions": "all"},
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AmapPOIProviderError("高德 POI 详情请求失败") from exc
        if payload.get("status") != "1":
            raise AmapPOIProviderError(f"高德 POI 详情失败: {payload.get('info', '未知错误')}")
        pois = payload.get("pois") or []
        poi = _poi_from_amap(pois[0]) if pois and isinstance(pois[0], dict) else None
        if poi is None:
            raise AmapPOIProviderError("高德 POI 详情没有可用数据")
        return poi

    def close(self) -> None:
        """关闭 HTTP 客户端连接池。"""
        self._client.close()

    def __enter__(self) -> "AmapPOIProvider":
        """返回可用于 with 语句的 POI Provider。"""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """离开 with 语句时释放 HTTP 资源。"""
        self.close()
