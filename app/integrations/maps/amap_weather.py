"""高德 Web 服务天气预报接口适配。"""

from __future__ import annotations

from datetime import date
from typing import Any

import httpx
from pydantic import ValidationError

from app.models.weather import WeatherForecast

from .protocols import WeatherProviderError
from .settings import amap_api_key


class AmapWeatherProviderError(WeatherProviderError):
    """高德天气配置、网络或响应异常。"""


def _temperature(value: object) -> float | None:
    """将高德温度字段转换为摄氏度数值，缺失时保留空值。"""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _forecast_from_amap(
    item: dict[str, Any],
    *,
    city: str,
    province: str,
    adcode: str,
) -> WeatherForecast | None:
    """将高德逐日预报转换为天气领域模型。"""
    try:
        forecast_date = date.fromisoformat(str(item.get("date") or ""))
        return WeatherForecast(
            provider="amap",
            city=city,
            province=province,
            adcode=adcode,
            date=forecast_date,
            day_weather=str(item.get("dayweather") or ""),
            night_weather=str(item.get("nightweather") or ""),
            day_temperature=_temperature(item.get("daytemp")),
            night_temperature=_temperature(item.get("nighttemp")),
            day_wind_direction=str(item.get("daywind") or ""),
            night_wind_direction=str(item.get("nightwind") or ""),
            day_wind_power=str(item.get("daypower") or ""),
            night_wind_power=str(item.get("nightpower") or ""),
        )
    except (TypeError, ValueError, ValidationError):
        return None


class AmapWeatherProvider:
    """调用高德 Web 服务获取逐日天气预报。"""

    provider_name = "amap"
    WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 10,
        *,
        client: httpx.Client | None = None,
    ):
        """配置天气客户端，并支持测试注入替代 HTTP 客户端。"""
        self.api_key = (api_key or amap_api_key()).strip()
        if not self.api_key:
            raise AmapWeatherProviderError(
                "高德 API Key 未配置，请设置 AMAP_API_KEY 或 VITE_AMAP_WEB_KEY"
            )
        self._client = client or httpx.Client(timeout=timeout, trust_env=False)
        self._owns_client = client is None

    def forecast(self, city: str) -> list[WeatherForecast]:
        """查询城市未来天气，并返回高德当前有效预报范围内的数据。"""
        city = city.strip()
        if not city:
            raise AmapWeatherProviderError("天气查询城市不能为空")

        # NOTE: 高德只接受城市名或 adcode，请求前需移除“中国-”等业务前缀。
        provider_city = city.rsplit("-", 1)[-1].strip()
        try:
            response = self._client.get(
                self.WEATHER_URL,
                params={
                    "key": self.api_key,
                    "city": provider_city,
                    "extensions": "all",
                    "output": "JSON",
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AmapWeatherProviderError("高德天气请求失败") from exc

        if not isinstance(payload, dict):
            raise AmapWeatherProviderError("高德天气响应格式无效")
        if payload.get("status") != "1":
            raise AmapWeatherProviderError(
                f"高德天气查询失败: {payload.get('info', '未知错误')}"
            )
        forecasts = payload.get("forecasts") or []
        if not forecasts or not isinstance(forecasts[0], dict):
            raise AmapWeatherProviderError(f"高德天气没有找到城市“{city}”的预报")

        forecast_group = forecasts[0]
        casts = forecast_group.get("casts") or []
        province = str(forecast_group.get("province") or "")
        adcode = str(forecast_group.get("adcode") or "")
        result = [
            forecast
            for item in casts
            if isinstance(item, dict)
            for forecast in [
                _forecast_from_amap(
                    item,
                    city=city,
                    province=province,
                    adcode=adcode,
                )
            ]
            if forecast is not None
        ]
        if not result:
            raise AmapWeatherProviderError("高德天气响应中没有可用的逐日预报")
        return sorted(result, key=lambda item: item.date)

    def close(self) -> None:
        """关闭由当前 Provider 创建的 HTTP 客户端。"""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "AmapWeatherProvider":
        """返回可用于 with 语句的天气 Provider。"""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """离开 with 语句时释放 HTTP 资源。"""
        self.close()
