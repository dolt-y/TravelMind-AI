"""高德 Web 服务步行、驾车和公交路线适配。"""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError

from app.models.poi import POILocation
from app.models.route import RouteEndpoint, RouteMode, RoutePlan, RouteStep

from .protocols import RouteProviderError
from .settings import amap_api_key


class AmapRouteProviderError(RouteProviderError):
    """高德路线配置、网络或响应异常。"""


def _integer(value: object) -> int:
    """将供应商整数或小数字符串转换为非负整数。"""
    try:
        return max(0, int(float(str(value or "0"))))
    except (TypeError, ValueError):
        return 0


def _polyline(value: object) -> list[POILocation]:
    """将高德分号分隔轨迹转换为坐标列表，忽略非法点。"""
    result: list[POILocation] = []
    for point in str(value or "").split(";"):
        try:
            longitude, latitude = point.split(",", 1)
            result.append(POILocation(longitude=float(longitude), latitude=float(latitude)))
        except (TypeError, ValueError, ValidationError):
            continue
    return result


def _step(item: dict[str, Any], *, instruction: str | None = None, road: str | None = None) -> RouteStep | None:
    """将一个供应商导航片段转换为路线步骤。"""
    text = str(instruction if instruction is not None else item.get("instruction") or "").strip()
    if not text:
        return None
    return RouteStep(
        instruction=text,
        road=str(road if road is not None else item.get("road") or ""),
        distance_meters=_integer(item.get("distance")),
        duration_seconds=_integer(item.get("duration")),
        action=str(item.get("action") or item.get("assistant_action") or ""),
        polyline=_polyline(item.get("polyline")),
    )


def _path_steps(path: dict[str, Any]) -> list[RouteStep]:
    """解析步行或驾车路线的顺序导航步骤。"""
    return [
        step
        for item in path.get("steps") or []
        if isinstance(item, dict)
        for step in [_step(item)]
        if step is not None
    ]


def _transit_steps(transit: dict[str, Any]) -> list[RouteStep]:
    """按换乘顺序展开公交方案中的步行、公交、铁路和出租车片段。"""
    result: list[RouteStep] = []
    for segment in transit.get("segments") or []:
        if not isinstance(segment, dict):
            continue
        walking = segment.get("walking") if isinstance(segment.get("walking"), dict) else {}
        result.extend(_path_steps(walking))

        bus = segment.get("bus") if isinstance(segment.get("bus"), dict) else {}
        for line in bus.get("buslines") or []:
            if not isinstance(line, dict):
                continue
            departure = line.get("departure_stop") if isinstance(line.get("departure_stop"), dict) else {}
            arrival = line.get("arrival_stop") if isinstance(line.get("arrival_stop"), dict) else {}
            line_name = str(line.get("name") or "公交")
            instruction = f"乘坐{line_name}，从{departure.get('name', '起点站')}到{arrival.get('name', '终点站')}"
            step = _step(line, instruction=instruction, road=line_name)
            if step is not None:
                result.append(step)

        railway = segment.get("railway") if isinstance(segment.get("railway"), dict) else {}
        if railway:
            departure = railway.get("departure_stop") if isinstance(railway.get("departure_stop"), dict) else {}
            arrival = railway.get("arrival_stop") if isinstance(railway.get("arrival_stop"), dict) else {}
            railway_name = str(railway.get("name") or "铁路")
            instruction = f"乘坐{railway_name}，从{departure.get('name', '起点站')}到{arrival.get('name', '终点站')}"
            step = _step(railway, instruction=instruction, road=railway_name)
            if step is not None:
                result.append(step)

        taxi = segment.get("taxi") if isinstance(segment.get("taxi"), dict) else {}
        if taxi:
            step = _step(taxi, instruction="乘坐出租车前往下一站", road="出租车")
            if step is not None:
                result.append(step)
    return result


class AmapRouteProvider:
    """调用高德路线服务并返回可持久化的标准路线事实。"""

    provider_name = "amap"
    ROUTE_URLS = {
        "walking": "https://restapi.amap.com/v3/direction/walking",
        "driving": "https://restapi.amap.com/v3/direction/driving",
        "transit": "https://restapi.amap.com/v3/direction/transit/integrated",
    }

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 15,
        *,
        client: httpx.Client | None = None,
    ):
        """初始化路线客户端；测试时可注入带假响应的 HTTP 客户端。"""
        self.api_key = (api_key or amap_api_key()).strip()
        if not self.api_key:
            raise AmapRouteProviderError(
                "高德 API Key 未配置，请设置 AMAP_API_KEY 或 VITE_AMAP_WEB_KEY"
            )
        self._client = client or httpx.Client(timeout=timeout, trust_env=False)
        self._owns_client = client is None

    def plan_route(
        self,
        origin: RouteEndpoint,
        destination: RouteEndpoint,
        mode: RouteMode,
    ) -> RoutePlan:
        """查询两个坐标之间的首选路线，并解析总量和逐步导航。"""
        params: dict[str, object] = {
            "key": self.api_key,
            "origin": f"{origin.location.longitude},{origin.location.latitude}",
            "destination": f"{destination.location.longitude},{destination.location.latitude}",
            "output": "JSON",
        }
        if mode == "driving":
            params.update({"strategy": 0, "extensions": "base"})
        elif mode == "transit":
            city = origin.city or destination.city
            if not city:
                raise AmapRouteProviderError("公共交通路线需要提供起点或终点城市")
            params.update({"city": city, "cityd": destination.city or city, "extensions": "base"})

        try:
            response = self._client.get(self.ROUTE_URLS[mode], params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AmapRouteProviderError("高德路线请求失败") from exc
        if not isinstance(payload, dict):
            raise AmapRouteProviderError("高德路线响应格式无效")
        if payload.get("status") != "1":
            raise AmapRouteProviderError(
                f"高德路线查询失败: {payload.get('info', '未知错误')}"
            )

        route_group = payload.get("route") if isinstance(payload.get("route"), dict) else {}
        candidates = route_group.get("transits" if mode == "transit" else "paths") or []
        if not candidates or not isinstance(candidates[0], dict):
            raise AmapRouteProviderError("高德没有返回可用路线")
        selected = candidates[0]
        steps = _transit_steps(selected) if mode == "transit" else _path_steps(selected)
        distance = _integer(selected.get("distance")) or sum(item.distance_meters for item in steps)
        duration = _integer(selected.get("duration")) or sum(item.duration_seconds for item in steps)
        if distance <= 0 or duration <= 0:
            raise AmapRouteProviderError("高德路线缺少有效距离或耗时")
        description = "；".join(item.instruction for item in steps[:4])
        if not description:
            description = f"全程约 {distance} 米，预计 {max(1, round(duration / 60))} 分钟"

        return RoutePlan(
            provider="amap",
            provider_route_id=str(selected.get("id") or ""),
            origin=origin,
            destination=destination,
            mode=mode,
            distance_meters=distance,
            duration_seconds=duration,
            description=description,
            steps=steps,
        )

    def close(self) -> None:
        """关闭由当前 Provider 创建的 HTTP 客户端。"""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "AmapRouteProvider":
        """返回可用于 with 语句的路线 Provider。"""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """离开 with 语句时释放 HTTP 资源。"""
        self.close()
