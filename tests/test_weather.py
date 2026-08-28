"""天气 Provider、日期校验和 SQLite 缓存测试。"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from app.integrations.maps import AmapWeatherProvider, AmapWeatherProviderError
from app.models.weather import WeatherForecast, WeatherQueryResult
from app.schemas.weather import WeatherForecastResponse
from app.services.weather_service import WeatherService, WeatherValidationError
from app.storage.weather_repository import WeatherRepository


def _amap_payload() -> dict[str, object]:
    """生成不包含认证信息的高德天气假响应。"""
    return {
        "status": "1",
        "forecasts": [
            {
                "city": "北京市",
                "adcode": "110000",
                "province": "北京",
                "casts": [
                    {
                        "date": "2026-08-28",
                        "dayweather": "晴",
                        "nightweather": "多云",
                        "daytemp": "31",
                        "nighttemp": "22",
                        "daywind": "南",
                        "nightwind": "南",
                        "daypower": "1-3",
                        "nightpower": "1-3",
                    },
                    {
                        "date": "2026-08-29",
                        "dayweather": "雷阵雨",
                        "nightweather": "小雨",
                        "daytemp": "29",
                        "nighttemp": "21",
                        "daywind": "东南",
                        "nightwind": "东",
                        "daypower": "1-3",
                        "nightpower": "1-3",
                    },
                ],
            }
        ],
    }


class AmapWeatherProviderTest(unittest.TestCase):
    """验证高德字段转换和错误识别。"""

    def test_forecast_parses_daily_weather(self) -> None:
        """正常响应应转换为数值温度和逐日领域模型。"""
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=_amap_payload())
            )
        )
        try:
            provider = AmapWeatherProvider(api_key="test-key", client=client)
            result = provider.forecast("北京")
        finally:
            client.close()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].city, "北京")
        self.assertEqual(result[0].day_temperature, 31)
        self.assertEqual(result[1].day_weather, "雷阵雨")

    def test_forecast_rejects_provider_error(self) -> None:
        """高德业务错误不能作为空天气列表静默返回。"""
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={"status": "0", "info": "INVALID_USER_KEY", "forecasts": []},
                )
            )
        )
        try:
            provider = AmapWeatherProvider(api_key="test-key", client=client)
            with self.assertRaisesRegex(AmapWeatherProviderError, "INVALID_USER_KEY"):
                provider.forecast("北京")
        finally:
            client.close()

    def test_forecast_rejects_empty_data(self) -> None:
        """城市不存在或空预报应返回可识别的供应商错误。"""
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"status": "1", "forecasts": []})
            )
        )
        try:
            provider = AmapWeatherProvider(api_key="test-key", client=client)
            with self.assertRaisesRegex(AmapWeatherProviderError, "没有找到城市"):
                provider.forecast("不存在的城市")
        finally:
            client.close()


class FakeWeatherProvider:
    """记录调用次数的天气假 Provider。"""

    provider_name = "amap"

    def __init__(self) -> None:
        self.calls = 0

    def forecast(self, city: str) -> list[WeatherForecast]:
        """返回两天固定天气，便于验证缓存和日期筛选。"""
        self.calls += 1
        return [
            WeatherForecast(city=city, date=date(2026, 8, 28), day_weather="晴"),
            WeatherForecast(city=city, date=date(2026, 8, 29), day_weather="多云"),
        ]


class WeatherServiceTest(unittest.TestCase):
    """验证天气缓存和日期覆盖规则。"""

    def test_second_query_uses_sqlite_cache(self) -> None:
        """相同城市和日期的重复查询不应再次请求供应商。"""
        with TemporaryDirectory() as directory:
            repository = WeatherRepository(Path(directory) / "weather.db")
            provider = FakeWeatherProvider()
            service = WeatherService(
                provider=provider,
                repository=repository,
                cache_ttl_seconds=3600,
            )
            first = service.query("北京", start_date=date(2026, 8, 28))
            second = service.query("北京", start_date=date(2026, 8, 28))

        self.assertFalse(first.cached)
        self.assertTrue(second.cached)
        self.assertEqual(provider.calls, 1)
        self.assertEqual(len(second.forecasts), 1)

    def test_query_rejects_uncovered_date_range(self) -> None:
        """供应商未覆盖请求日期时不能返回不完整天气。"""
        with TemporaryDirectory() as directory:
            service = WeatherService(
                provider=FakeWeatherProvider(),
                repository=WeatherRepository(Path(directory) / "weather.db"),
            )
            with self.assertRaisesRegex(WeatherValidationError, "未覆盖完整日期范围"):
                service.query(
                    "北京",
                    start_date=date(2026, 8, 28),
                    end_date=date(2026, 8, 30),
                )


class WeatherBoundaryTest(unittest.TestCase):
    """验证领域模型、REST 模型和路由边界。"""

    def test_rest_model_is_independent_from_domain_model(self) -> None:
        """天气 REST DTO 不应继承天气领域模型。"""
        self.assertFalse(issubclass(WeatherForecastResponse, WeatherForecast))

    def test_weather_routes_are_registered(self) -> None:
        """独立天气入口和 TripStar 兼容入口都应出现在 OpenAPI。"""
        from main import app

        paths = app.openapi()["paths"]
        self.assertIn("/api/weather", paths)
        self.assertIn("/api/map/weather", paths)

    def test_weather_api_serializes_domain_result(self) -> None:
        """天气接口应显式转换日期、缓存状态和天气事实。"""
        from main import app

        result = WeatherQueryResult(
            provider="amap",
            city="北京",
            cached=True,
            forecasts=[
                WeatherForecast(
                    city="北京",
                    date=date(2026, 8, 28),
                    day_weather="晴",
                    day_temperature=31,
                )
            ],
        )
        with patch("app.routers.weather.WeatherService") as service_class:
            service_class.return_value.query.return_value = result
            response = TestClient(app).get(
                "/api/weather",
                params={"city": "北京", "start_date": "2026-08-28"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["cached"])
        self.assertEqual(payload["data"][0]["date"], "2026-08-28")
        self.assertEqual(payload["data"][0]["day_temperature"], 31.0)


if __name__ == "__main__":
    unittest.main()
