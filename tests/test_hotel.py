"""酒店 Provider、查询缓存和 REST 边界测试。"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from app.integrations.maps import AmapHotelProvider, HotelProviderError
from app.models.hotel import Hotel, HotelSearchCriteria, HotelSearchResult
from app.models.poi import POILocation
from app.schemas.hotel import HotelResponse
from app.services.hotel_service import HotelService, HotelServiceError
from app.storage.hotel_repository import HotelRepository


def _amap_payload() -> dict[str, object]:
    """生成不包含认证信息的高德酒店假响应。"""
    return {
        "status": "1",
        "pois": [
            {
                "id": "hotel-1",
                "name": "中轴酒店",
                "cityname": "北京市",
                "address": "东城区示例路 1 号",
                "location": "116.397,39.916",
                "type": "住宿服务;宾馆酒店;经济型连锁酒店",
                "tel": "010-12345678",
                "biz_ext": {"rating": "4.6", "cost": "420"},
                "photos": [{"url": "https://example.com/hotel.jpg"}],
            },
            {
                "id": "hotel-2",
                "name": "无价格酒店",
                "cityname": "北京市",
                "address": [],
                "location": [],
                "biz_ext": {},
                "photos": [],
            },
        ],
    }


class AmapHotelProviderTest(unittest.TestCase):
    """验证高德酒店查询条件和字段转换。"""

    def test_search_parses_hotel_facts_and_keeps_missing_values(self) -> None:
        """供应商缺失的地址、坐标、价格和评分应保持为空。"""
        requested_url = ""

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal requested_url
            requested_url = str(request.url)
            return httpx.Response(200, json=_amap_payload())

        client = httpx.Client(transport=httpx.MockTransport(handler))
        try:
            provider = AmapHotelProvider(api_key="test-key", client=client)
            hotels = provider.search_hotels(
                HotelSearchCriteria(
                    city="北京",
                    accommodation="经济型",
                    area="故宫附近",
                )
            )
        finally:
            client.close()

        self.assertEqual(len(hotels), 2)
        self.assertEqual(hotels[0].average_price, 420)
        self.assertEqual(hotels[0].rating, 4.6)
        self.assertIsNone(hotels[0].price_range)
        self.assertIsNone(hotels[1].address)
        self.assertIsNone(hotels[1].location)
        self.assertIsNone(hotels[1].average_price)
        self.assertIn("types=100000", requested_url)
        self.assertIn("%E6%95%85%E5%AE%AB%E9%99%84%E8%BF%91", requested_url)

    def test_search_rejects_provider_error(self) -> None:
        """高德业务错误不能作为空酒店列表返回。"""
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={"status": "0", "info": "INVALID_USER_KEY"},
                )
            )
        )
        try:
            provider = AmapHotelProvider(api_key="test-key", client=client)
            with self.assertRaisesRegex(HotelProviderError, "INVALID_USER_KEY"):
                provider.search_hotels(HotelSearchCriteria(city="北京"))
        finally:
            client.close()


class FakeHotelProvider:
    """按城市返回固定结果并记录调用次数的酒店假 Provider。"""

    provider_name = "amap"

    def __init__(self, *, fail: bool = False) -> None:
        self.calls = 0
        self.fail = fail

    def search_hotels(self, criteria: HotelSearchCriteria) -> list[Hotel]:
        """返回一个有价格和一个无价格的酒店。"""
        self.calls += 1
        if self.fail:
            raise HotelProviderError("酒店供应商不可用")
        return [
            Hotel(
                id=f"{criteria.city}-known",
                name=f"{criteria.city}高价酒店",
                city=criteria.city,
                location=POILocation(longitude=116.4, latitude=39.9),
                average_price=800,
            ),
            Hotel(
                id=f"{criteria.city}-unknown",
                name=f"{criteria.city}价格待确认酒店",
                city=criteria.city,
            ),
        ]


class HotelServiceTest(unittest.TestCase):
    """验证酒店条件过滤、缓存和多城市查询。"""

    def test_second_query_uses_sqlite_cache_and_preserves_empty_price(self) -> None:
        """重复条件应命中缓存，未知价格酒店不应被预算过滤。"""
        with TemporaryDirectory() as directory:
            provider = FakeHotelProvider()
            service = HotelService(
                provider=provider,
                repository=HotelRepository(Path(directory) / "hotel.db"),
                cache_ttl_seconds=3600,
            )
            criteria = HotelSearchCriteria(city="北京", budget_max=500)
            first = service.search(criteria)
            second = service.search(criteria)

        self.assertFalse(first.cached)
        self.assertTrue(second.cached)
        self.assertEqual(provider.calls, 1)
        self.assertEqual([hotel.id for hotel in second.hotels], ["北京-unknown"])

    def test_empty_result_is_cached(self) -> None:
        """供应商无结果也应缓存，避免重复请求相同条件。"""
        class EmptyProvider(FakeHotelProvider):
            def search_hotels(self, criteria: HotelSearchCriteria) -> list[Hotel]:
                self.calls += 1
                return []

        with TemporaryDirectory() as directory:
            provider = EmptyProvider()
            service = HotelService(
                provider=provider,
                repository=HotelRepository(Path(directory) / "hotel.db"),
            )
            first = service.search(HotelSearchCriteria(city="上海"))
            second = service.search(HotelSearchCriteria(city="上海"))

        self.assertFalse(first.cached)
        self.assertTrue(second.cached)
        self.assertEqual(provider.calls, 1)

    def test_provider_error_is_exposed_as_service_error(self) -> None:
        """供应商失败应保留为可识别的酒店业务错误。"""
        with TemporaryDirectory() as directory:
            service = HotelService(
                provider=FakeHotelProvider(fail=True),
                repository=HotelRepository(Path(directory) / "hotel.db"),
            )
            with self.assertRaisesRegex(HotelServiceError, "供应商不可用"):
                service.search(HotelSearchCriteria(city="北京"))

    def test_search_many_keeps_city_order(self) -> None:
        """多城市查询结果必须与行程城市顺序一致。"""
        with TemporaryDirectory() as directory:
            service = HotelService(
                provider=FakeHotelProvider(),
                repository=HotelRepository(Path(directory) / "hotel.db"),
            )
            results = service.search_many(
                [
                    HotelSearchCriteria(city="北京"),
                    HotelSearchCriteria(city="西安"),
                ]
            )

        self.assertEqual([result.criteria.city for result in results], ["北京", "西安"])


class HotelBoundaryTest(unittest.TestCase):
    """验证酒店领域模型、REST 模型和路由边界。"""

    def test_rest_model_is_independent_from_domain_model(self) -> None:
        """酒店 REST DTO 不应继承酒店领域模型。"""
        self.assertFalse(issubclass(HotelResponse, Hotel))

    def test_hotel_route_is_registered(self) -> None:
        """酒店搜索入口应出现在 OpenAPI。"""
        from main import app

        self.assertIn("/api/hotels/search", app.openapi()["paths"])

    def test_hotel_api_serializes_domain_result(self) -> None:
        """酒店接口应显式返回来源、缓存状态和查询条件。"""
        from main import app

        criteria = HotelSearchCriteria(city="北京", accommodation="经济型")
        result = HotelSearchResult(
            provider="amap",
            criteria=criteria,
            cached=True,
            hotels=[Hotel(id="hotel-1", name="示例酒店", city="北京")],
        )
        with patch("app.routers.hotel.HotelService") as service_class:
            service_class.return_value.search.return_value = result
            response = TestClient(app).get(
                "/api/hotels/search",
                params={"city": "北京", "accommodation": "经济型"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["cached"])
        self.assertEqual(payload["provider"], "amap")
        self.assertEqual(payload["criteria"]["accommodation"], "经济型")
        self.assertIsNone(payload["data"][0]["rating"])


if __name__ == "__main__":
    unittest.main()
