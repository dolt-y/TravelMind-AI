"""天气预报领域模型。"""

from __future__ import annotations

from datetime import date as Date

from pydantic import BaseModel, Field


class WeatherForecast(BaseModel):
    """天气供应商返回的单日预报事实。"""

    provider: str = Field(default="amap", description="天气供应商")
    city: str = Field(..., min_length=1, max_length=100, description="查询城市")
    province: str = Field(default="", max_length=100, description="省级行政区")
    adcode: str = Field(default="", max_length=20, description="城市行政区划编码")
    date: Date = Field(..., description="预报日期")
    day_weather: str = Field(default="", max_length=100, description="白天天气")
    night_weather: str = Field(default="", max_length=100, description="夜间天气")
    day_temperature: float | None = Field(default=None, description="白天温度，单位为摄氏度")
    night_temperature: float | None = Field(default=None, description="夜间温度，单位为摄氏度")
    day_wind_direction: str = Field(default="", max_length=50, description="白天风向")
    night_wind_direction: str = Field(default="", max_length=50, description="夜间风向")
    day_wind_power: str = Field(default="", max_length=50, description="白天风力")
    night_wind_power: str = Field(default="", max_length=50, description="夜间风力")


class WeatherQueryResult(BaseModel):
    """一次天气查询的业务结果及缓存状态。"""

    provider: str
    city: str
    cached: bool = False
    forecasts: list[WeatherForecast] = Field(default_factory=list)
