"""地图供应商适配模块。"""

from .amap import AmapPOIProvider, AmapPOIProviderError
from .amap_weather import AmapWeatherProvider, AmapWeatherProviderError
from .protocols import WeatherProvider, WeatherProviderError

__all__ = [
    "AmapPOIProvider",
    "AmapPOIProviderError",
    "AmapWeatherProvider",
    "AmapWeatherProviderError",
    "WeatherProvider",
    "WeatherProviderError",
]
