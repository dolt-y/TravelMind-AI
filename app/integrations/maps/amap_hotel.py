"""高德 Web 服务酒店搜索适配。"""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError

from app.models.hotel import Hotel, HotelSearchCriteria
from app.models.poi import POILocation

from .protocols import HotelProviderError
from .settings import amap_api_key


class AmapHotelProviderError(HotelProviderError):
    """高德酒店搜索配置、网络或响应异常。"""


def _text(value: object) -> str | None:
    """将高德字符串或字符串数组转换为可选文本。"""
    if isinstance(value, list):
        text = "、".join(str(item).strip() for item in value if str(item).strip())
    else:
        text = str(value or "").strip()
    return text or None


def _number(value: object) -> float | None:
    """将供应商数值字段转换为浮点数，缺失或非法时保留空值。"""
    if value in (None, "", []):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _location(value: object) -> POILocation | None:
    """将高德的“经度,纬度”文本转换为坐标。"""
    try:
        longitude, latitude = str(value).split(",", 1)
        return POILocation(longitude=float(longitude), latitude=float(latitude))
    except (TypeError, ValueError, ValidationError):
        return None


def _hotel_from_amap(item: dict[str, Any], city: str) -> Hotel | None:
    """将高德住宿 POI 转换为酒店领域对象。"""
    hotel_id = str(item.get("id") or "").strip()
    name = str(item.get("name") or "").strip()
    if not hotel_id or not name:
        return None

    biz_ext = item.get("biz_ext") if isinstance(item.get("biz_ext"), dict) else {}
    average_price = _number(biz_ext.get("cost"))
    photos = [
        str(photo.get("url"))
        for photo in (item.get("photos") or [])
        if isinstance(photo, dict) and photo.get("url")
    ]
    try:
        return Hotel(
            provider="amap",
            id=hotel_id,
            name=name,
            city=_text(item.get("cityname")) or city,
            address=_text(item.get("address")),
            location=_location(item.get("location")),
            type=_text(item.get("type")),
            rating=_number(biz_ext.get("rating")),
            average_price=average_price,
            price_range=None,
            tel=_text(item.get("tel")),
            photos=photos,
        )
    except ValidationError:
        return None


def _keywords(criteria: HotelSearchCriteria) -> str:
    """根据住宿偏好和景点区域生成高德酒店搜索关键词。"""
    parts = [criteria.area.strip(), criteria.accommodation.strip()]
    if not any(word in criteria.accommodation for word in ("酒店", "宾馆", "民宿", "旅馆")):
        parts.append("酒店")
    return " ".join(part for part in parts if part)


class AmapHotelProvider:
    """调用高德文本搜索获取住宿类 POI。"""

    provider_name = "amap"
    SEARCH_URL = "https://restapi.amap.com/v3/place/text"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 10,
        *,
        client: httpx.Client | None = None,
    ):
        """初始化酒店搜索客户端；测试时可注入带假响应的客户端。"""
        self.api_key = (api_key or amap_api_key()).strip()
        if not self.api_key:
            raise AmapHotelProviderError(
                "高德 API Key 未配置，请设置 AMAP_API_KEY 或 VITE_AMAP_WEB_KEY"
            )
        self._client = client or httpx.Client(timeout=timeout, trust_env=False)
        self._owns_client = client is None

    def search_hotels(self, criteria: HotelSearchCriteria) -> list[Hotel]:
        """搜索指定城市的住宿类 POI，并保留供应商实际返回的字段。"""
        try:
            response = self._client.get(
                self.SEARCH_URL,
                params={
                    "key": self.api_key,
                    "keywords": _keywords(criteria),
                    "types": "100000",
                    "city": criteria.city,
                    "citylimit": "true",
                    "offset": criteria.limit,
                    "page": 1,
                    "extensions": "all",
                    "output": "JSON",
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AmapHotelProviderError("高德酒店搜索请求失败") from exc

        if not isinstance(payload, dict):
            raise AmapHotelProviderError("高德酒店搜索响应格式无效")
        if payload.get("status") != "1":
            raise AmapHotelProviderError(
                f"高德酒店搜索失败: {payload.get('info', '未知错误')}"
            )

        result: list[Hotel] = []
        seen: set[str] = set()
        for item in payload.get("pois") or []:
            if not isinstance(item, dict):
                continue
            hotel = _hotel_from_amap(item, criteria.city)
            if hotel is None or hotel.id in seen:
                continue
            seen.add(hotel.id)
            result.append(hotel)
        return result[: criteria.limit]

    def close(self) -> None:
        """关闭由当前 Provider 创建的 HTTP 客户端。"""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "AmapHotelProvider":
        """返回可用于 with 语句的酒店 Provider。"""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """离开 with 语句时释放 HTTP 资源。"""
        self.close()
