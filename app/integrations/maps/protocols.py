"""地图供应商能力协议。"""

from __future__ import annotations

from typing import Protocol

from app.models.hotel import Hotel, HotelSearchCriteria
from app.models.route import RouteEndpoint, RouteMode, RoutePlan
from app.models.weather import WeatherForecast


class HotelProviderError(RuntimeError):
    """酒店供应商配置、网络或响应异常。"""


class HotelProvider(Protocol):
    """酒店业务依赖的最小供应商能力。"""

    provider_name: str

    def search_hotels(self, criteria: HotelSearchCriteria) -> list[Hotel]:
        """按城市、住宿偏好和区域查询酒店事实数据。"""


class WeatherProviderError(RuntimeError):
    """天气供应商配置、网络或响应异常。"""


class WeatherProvider(Protocol):
    """天气业务依赖的最小供应商能力。"""

    provider_name: str

    def forecast(self, city: str) -> list[WeatherForecast]:
        """查询供应商当前可提供的逐日天气预报。"""


class RouteProviderError(RuntimeError):
    """路线供应商配置、网络或响应异常。"""


class RouteProvider(Protocol):
    """路线业务依赖的最小供应商能力。"""

    provider_name: str

    def plan_route(
        self,
        origin: RouteEndpoint,
        destination: RouteEndpoint,
        mode: RouteMode,
    ) -> RoutePlan:
        """查询两个已确认坐标之间的路线事实。"""
