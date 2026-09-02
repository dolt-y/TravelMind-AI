"""路线地址解析、供应商查询和缓存协调服务。"""

from __future__ import annotations

import os

from loguru import logger

from app.integrations.maps import (
    AmapRouteProvider,
    RouteProvider,
    RouteProviderError,
)
from app.models.poi import POILocation
from app.models.route import RouteEndpoint, RouteQuery, RouteQueryResult
from app.services.poi_service import POIService, POIServiceError
from app.storage.poi_repository import POIRepositoryError
from app.storage.route_repository import RouteRepository, RouteRepositoryError


class RouteServiceError(RuntimeError):
    """路线查询依赖或供应商处理异常。"""


class RouteStorageError(RouteServiceError):
    """路线查询无法从缓存读取或写入。"""


class RouteValidationError(RouteServiceError):
    """路线查询缺少可解析地点或必要城市信息。"""


def _cache_ttl_seconds() -> int:
    """读取路线缓存时长，非法配置使用二十四小时。"""
    try:
        return max(60, int(os.getenv("ROUTE_CACHE_TTL_SECONDS", "86400")))
    except ValueError:
        return 86400


class RouteService:
    """将地址或已有坐标转换为可复用的路线事实。"""

    def __init__(
        self,
        *,
        provider: RouteProvider | None = None,
        poi_service: POIService | None = None,
        repository: RouteRepository | None = None,
        cache_ttl_seconds: int | None = None,
    ):
        """初始化路线 Provider、地点解析服务和缓存仓储。"""
        self.provider = provider
        self.poi_service = poi_service
        try:
            self.repository = repository or RouteRepository()
        except RouteRepositoryError as exc:
            raise RouteStorageError(str(exc)) from exc
        configured_ttl = _cache_ttl_seconds() if cache_ttl_seconds is None else cache_ttl_seconds
        self.cache_ttl_seconds = max(60, configured_ttl)

    def _resolve_endpoint(
        self,
        *,
        address: str,
        city: str,
        location: POILocation | None,
    ) -> RouteEndpoint:
        """优先复用已确认坐标，否则通过 POI 搜索解析地点。"""
        if location is not None:
            return RouteEndpoint(name=address, address=address, city=city, location=location)
        if not city:
            raise RouteValidationError("未提供坐标时必须提供地点所在城市")
        try:
            poi_service = self.poi_service or POIService()
            pois = poi_service.search(address, city, citylimit=True, limit=1)
        except POIRepositoryError as exc:
            raise RouteStorageError(str(exc)) from exc
        except POIServiceError as exc:
            raise RouteServiceError(str(exc)) from exc
        if not pois:
            raise RouteValidationError(f"没有找到地点“{address}”")
        poi = pois[0]
        return RouteEndpoint(
            name=poi.name,
            address=poi.address or address,
            city=poi.city or city,
            location=poi.location,
        )

    def query(self, query: RouteQuery) -> RouteQueryResult:
        """查询两点路线，优先返回完整条件命中的有效缓存。"""
        provider_name = getattr(self.provider, "provider_name", "amap")
        logger.info(
            "开始查询路线：起点={}，终点={}，交通方式={}，供应商={}",
            query.origin_address,
            query.destination_address,
            query.route_type,
            provider_name,
        )
        try:
            cached = self.repository.get_route(
                provider=provider_name,
                query=query,
                max_age_seconds=self.cache_ttl_seconds,
            )
        except RouteRepositoryError as exc:
            raise RouteStorageError(str(exc)) from exc
        if cached is not None:
            logger.info(
                "路线缓存命中：距离={} 米，耗时={} 秒",
                cached.distance_meters,
                cached.duration_seconds,
            )
            return RouteQueryResult(
                provider=provider_name,
                cached=True,
                query=query,
                route=cached,
            )

        # NOTE: 公交路线需要城市参数；已知坐标也不能替代高德的城市字段。
        if query.route_type == "transit" and not (query.origin_city or query.destination_city):
            raise RouteValidationError("公共交通路线必须提供起点或终点城市")
        origin_city = query.origin_city or query.destination_city
        destination_city = query.destination_city or query.origin_city
        origin = self._resolve_endpoint(
            address=query.origin_address,
            city=origin_city,
            location=query.origin_location,
        )
        destination = self._resolve_endpoint(
            address=query.destination_address,
            city=destination_city,
            location=query.destination_location,
        )

        logger.info("路线缓存未命中，正在请求供应商：交通方式={}", query.route_type)
        try:
            if self.provider is None:
                with AmapRouteProvider() as provider:
                    route = provider.plan_route(origin, destination, query.route_type)
            else:
                route = self.provider.plan_route(origin, destination, query.route_type)
        except RouteProviderError as exc:
            logger.error("路线供应商查询失败：交通方式={}，原因={}", query.route_type, exc)
            raise RouteServiceError(str(exc)) from exc

        try:
            self.repository.save_route(provider=provider_name, query=query, route=route)
        except RouteRepositoryError as exc:
            raise RouteStorageError(str(exc)) from exc
        logger.info(
            "路线查询完成：距离={} 米，耗时={} 秒，步骤={} 个并已缓存",
            route.distance_meters,
            route.duration_seconds,
            len(route.steps),
        )
        return RouteQueryResult(
            provider=provider_name,
            cached=False,
            query=query,
            route=route,
        )
