"""天气查询 REST 响应模型。"""

from datetime import date as Date

from pydantic import BaseModel, Field


class WeatherForecastResponse(BaseModel):
    """对外返回的单日天气预报。"""

    provider: str = Field(..., description="天气供应商")
    city: str = Field(..., description="查询城市")
    province: str = Field(default="", description="省级行政区")
    adcode: str = Field(default="", description="城市行政区划编码")
    date: Date = Field(..., description="预报日期")
    day_weather: str = Field(default="", description="白天天气")
    night_weather: str = Field(default="", description="夜间天气")
    day_temperature: float | None = Field(default=None, description="白天温度，单位为摄氏度")
    night_temperature: float | None = Field(default=None, description="夜间温度，单位为摄氏度")
    day_wind_direction: str = Field(default="", description="白天风向")
    night_wind_direction: str = Field(default="", description="夜间风向")
    day_wind_power: str = Field(default="", description="白天风力")
    night_wind_power: str = Field(default="", description="夜间风力")


class WeatherResponse(BaseModel):
    """天气查询结果。"""

    success: bool
    message: str
    provider: str
    city: str
    cached: bool = False
    data: list[WeatherForecastResponse] = Field(default_factory=list)
