"""路线 Provider、缓存、业务服务和 REST 边界测试。"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from app.integrations.maps import AmapRouteProvider, AmapRouteProviderError, RouteProviderError
from app.models.poi import POI, POILocation
from app.models.route import (
    RouteEndpoint,
    RoutePlan,
    RouteQuery,
    RouteQueryResult,
    RouteStep,
)
from app.schemas.route import RouteInfoResponse
from app.services.route_service import RouteService, RouteServiceError, RouteValidationError
from app.storage.route_repository import RouteRepository


def _endpoint(name: str, longitude: float, latitude: float, city: str = "北京") -> RouteEndpoint:
    """生成带确定坐标的路线端点。"""
    return RouteEndpoint(
        name=name,
        address=f"{name}地址",
        city=city,
        location=POILocation(longitude=longitude, latitude=latitude),
    )


def _walking_payload() -> dict[str, object]:
    """生成包含轨迹和两段导航的高德步行假响应。"""
    return {
        "status": "1",
        "route": {
            "paths": [
                {
                    "id": "walk-1",
                    "distance": "1250",
                    "duration": "900",
                    "steps": [
                        {
                            "instruction": "沿东长安街向西步行",
                            "road": "东长安街",
                            "distance": "700",
                            "duration": "500",
                            "action": "直行",
                            "polyline": "116.407,39.904;116.401,39.905",
                        },
                        {
                            "instruction": "右转到达目的地",
                            "road": "南池子大街",
                            "distance": "550",
                            "duration": "400",
                            "action": "右转",
                        },
                    ],
                }
            ]
        },
    }


class AmapRouteProviderTest(unittest.TestCase):
    """验证高德三种路线的参数和字段解析。"""

    def test_walking_route_parses_distance_duration_steps_and_polyline(self) -> None:
        """步行响应应保留总量、导航说明和轨迹坐标。"""
        requested_url = ""

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal requested_url
            requested_url = str(request.url)
            return httpx.Response(200, json=_walking_payload())

        client = httpx.Client(transport=httpx.MockTransport(handler))
        try:
            route = AmapRouteProvider(api_key="test-key", client=client).plan_route(
                _endpoint("天安门", 116.397, 39.908),
                _endpoint("故宫", 116.403, 39.924),
                "walking",
            )
        finally:
            client.close()

        self.assertEqual(route.distance_meters, 1250)
        self.assertEqual(route.duration_seconds, 900)
        self.assertEqual(route.provider_route_id, "walk-1")
        self.assertEqual(len(route.steps), 2)
        self.assertEqual(len(route.steps[0].polyline), 2)
        self.assertIn("direction/walking", requested_url)
        self.assertIn("origin=116.397%2C39.908", requested_url)

    def test_transit_route_uses_origin_and_destination_cities(self) -> None:
        """跨城市公交请求必须分别传入起点和终点城市。"""
        requested_url = ""
        payload = {
            "status": "1",
            "route": {
                "transits": [
                    {
                        "id": "transit-1",
                        "distance": "120000",
                        "duration": "7200",
                        "segments": [
                            {
                                "bus": {
                                    "buslines": [
                                        {
                                            "name": "城际专线",
                                            "distance": "120000",
                                            "duration": "7200",
                                            "departure_stop": {"name": "北京站"},
                                            "arrival_stop": {"name": "天津站"},
                                        }
                                    ]
                                }
                            }
                        ],
                    }
                ]
            },
        }

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal requested_url
            requested_url = str(request.url)
            return httpx.Response(200, json=payload)

        client = httpx.Client(transport=httpx.MockTransport(handler))
        try:
            route = AmapRouteProvider(api_key="test-key", client=client).plan_route(
                _endpoint("北京站", 116.427, 39.903, "北京"),
                _endpoint("天津站", 117.210, 39.136, "天津"),
                "transit",
            )
        finally:
            client.close()

        self.assertEqual(route.mode, "transit")
        self.assertEqual(route.steps[0].road, "城际专线")
        self.assertIn("city=%E5%8C%97%E4%BA%AC", requested_url)
        self.assertIn("cityd=%E5%A4%A9%E6%B4%A5", requested_url)

    def test_driving_route_uses_driving_endpoint_and_strategy(self) -> None:
        """驾车路线应使用高德驾车端点并携带稳定策略。"""
        requested_url = ""

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal requested_url
            requested_url = str(request.url)
            return httpx.Response(200, json=_walking_payload())

        client = httpx.Client(transport=httpx.MockTransport(handler))
        try:
            route = AmapRouteProvider(api_key="test-key", client=client).plan_route(
                _endpoint("天安门", 116.397, 39.908),
                _endpoint("颐和园", 116.275, 39.999),
                "driving",
            )
        finally:
            client.close()

        self.assertEqual(route.mode, "driving")
        self.assertIn("direction/driving", requested_url)
        self.assertIn("strategy=0", requested_url)

    def test_provider_rejects_timeout_and_empty_route(self) -> None:
        """网络超时和空路线都不能返回零距离的伪结果。"""
        timeout_client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("timeout"))
            )
        )
        try:
            with self.assertRaisesRegex(AmapRouteProviderError, "请求失败"):
                AmapRouteProvider(api_key="test-key", client=timeout_client).plan_route(
                    _endpoint("起点", 116.3, 39.9),
                    _endpoint("终点", 116.4, 39.9),
                    "driving",
                )
        finally:
            timeout_client.close()

        empty_client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"status": "1", "route": {"paths": []}})
            )
        )
        try:
            with self.assertRaisesRegex(AmapRouteProviderError, "可用路线"):
                AmapRouteProvider(api_key="test-key", client=empty_client).plan_route(
                    _endpoint("起点", 116.3, 39.9),
                    _endpoint("终点", 116.4, 39.9),
                    "walking",
                )
        finally:
            empty_client.close()


class FakePOIService:
    """将地址转换为固定 POI 并记录解析次数。"""

    def __init__(self) -> None:
        self.calls = 0

    def search(self, keywords: str, city: str, citylimit: bool, limit: int) -> list[POI]:
        """按查询顺序返回不同坐标。"""
        self.calls += 1
        return [
            POI(
                id=f"poi-{self.calls}",
                name=keywords,
                address=f"{city}{keywords}",
                city=city,
                location=POILocation(longitude=116.3 + self.calls * 0.01, latitude=39.9),
            )
        ]


class FakeRouteProvider:
    """返回固定路线并记录供应商调用次数。"""

    provider_name = "amap"

    def __init__(self, *, fail: bool = False) -> None:
        self.calls = 0
        self.fail = fail

    def plan_route(self, origin: RouteEndpoint, destination: RouteEndpoint, mode: str) -> RoutePlan:
        """根据收到的端点生成可断言的路线事实。"""
        self.calls += 1
        if self.fail:
            raise RouteProviderError("路线供应商不可用")
        return RoutePlan(
            provider="amap",
            origin=origin,
            destination=destination,
            mode=mode,
            distance_meters=1800,
            duration_seconds=1200,
            description="沿测试道路前往目的地",
            steps=[RouteStep(instruction="沿测试道路直行", distance_meters=1800, duration_seconds=1200)],
        )


class RouteServiceTest(unittest.TestCase):
    """验证地址解析、坐标复用、错误转换和 SQLite 缓存。"""

    def test_second_query_uses_route_cache_before_geocoding(self) -> None:
        """相同条件重复查询不应再次解析地址或请求路线供应商。"""
        with TemporaryDirectory() as directory:
            poi_service = FakePOIService()
            provider = FakeRouteProvider()
            service = RouteService(
                provider=provider,
                poi_service=poi_service,
                repository=RouteRepository(Path(directory) / "route.db"),
                cache_ttl_seconds=3600,
            )
            query = RouteQuery(
                origin_address="天安门",
                destination_address="故宫",
                origin_city="北京",
                destination_city="北京",
            )
            first = service.query(query)
            second = service.query(query)

        self.assertFalse(first.cached)
        self.assertTrue(second.cached)
        self.assertEqual(provider.calls, 1)
        self.assertEqual(poi_service.calls, 2)
        self.assertEqual(second.route.steps[0].instruction, "沿测试道路直行")

    def test_known_coordinates_skip_poi_lookup(self) -> None:
        """景点已有坐标时应直接计算路线，避免重复 POI 搜索。"""
        with TemporaryDirectory() as directory:
            poi_service = FakePOIService()
            service = RouteService(
                provider=FakeRouteProvider(),
                poi_service=poi_service,
                repository=RouteRepository(Path(directory) / "route.db"),
            )
            service.query(
                RouteQuery(
                    origin_address="天安门",
                    destination_address="故宫",
                    route_type="walking",
                    origin_location=POILocation(longitude=116.397, latitude=39.908),
                    destination_location=POILocation(longitude=116.403, latitude=39.924),
                )
            )

        self.assertEqual(poi_service.calls, 0)

    def test_transit_requires_city_and_provider_error_is_exposed(self) -> None:
        """公交缺少城市应提前拒绝，供应商异常应保留为业务错误。"""
        with TemporaryDirectory() as directory:
            repository = RouteRepository(Path(directory) / "route.db")
            service = RouteService(provider=FakeRouteProvider(), repository=repository)
            with self.assertRaisesRegex(RouteValidationError, "必须提供"):
                service.query(
                    RouteQuery(
                        origin_address="起点",
                        destination_address="终点",
                        route_type="transit",
                        origin_location=POILocation(longitude=116.3, latitude=39.9),
                        destination_location=POILocation(longitude=116.4, latitude=39.9),
                    )
                )

            failing = RouteService(
                provider=FakeRouteProvider(fail=True),
                repository=repository,
            )
            with self.assertRaisesRegex(RouteServiceError, "供应商不可用"):
                failing.query(
                    RouteQuery(
                        origin_address="起点",
                        destination_address="终点",
                        route_type="driving",
                        origin_location=POILocation(longitude=116.3, latitude=39.9),
                        destination_location=POILocation(longitude=116.4, latitude=39.9),
                    )
                )


class RouteBoundaryTest(unittest.TestCase):
    """验证路线领域模型、REST DTO 和兼容入口。"""

    def test_rest_model_is_independent_from_domain_model(self) -> None:
        """路线 REST DTO 不应继承路线领域模型。"""
        self.assertFalse(issubclass(RouteInfoResponse, RoutePlan))

    def test_route_api_serializes_compatible_and_detailed_fields(self) -> None:
        """接口应保留 TripStar 总量字段并返回缓存、端点和步骤。"""
        from main import app

        query = RouteQuery(
            origin_address="天安门",
            destination_address="故宫",
            origin_city="北京",
            destination_city="北京",
        )
        route = RoutePlan(
            origin=_endpoint("天安门", 116.397, 39.908),
            destination=_endpoint("故宫", 116.403, 39.924),
            mode="walking",
            distance_meters=1250,
            duration_seconds=900,
            description="沿东长安街步行",
            steps=[RouteStep(instruction="向西步行", distance_meters=1250, duration_seconds=900)],
        )
        result = RouteQueryResult(provider="amap", cached=True, query=query, route=route)
        with patch("app.routers.route.RouteService") as service_class:
            service_class.return_value.query.return_value = result
            response = TestClient(app).post(
                "/api/map/route",
                json={
                    "origin_address": "天安门",
                    "destination_address": "故宫",
                    "origin_city": "北京",
                    "destination_city": "北京",
                    "route_type": "walking",
                    "origin_location": {"longitude": 116.397, "latitude": 39.908},
                    "destination_location": {"longitude": 116.403, "latitude": 39.924},
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["cached"])
        self.assertEqual(payload["data"]["distance"], 1250)
        self.assertEqual(payload["data"]["duration"], 900)
        self.assertEqual(payload["data"]["steps"][0]["instruction"], "向西步行")
        submitted_query = service_class.return_value.query.call_args.args[0]
        self.assertEqual(submitted_query.origin_location.longitude, 116.397)
        self.assertEqual(submitted_query.destination_location.latitude, 39.924)
        self.assertIn("/api/map/route", app.openapi()["paths"])


if __name__ == "__main__":
    unittest.main()
