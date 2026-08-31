"""地图供应商适配模块。"""

from .amap import AmapPOIProvider, AmapPOIProviderError
from .amap_hotel import AmapHotelProvider, AmapHotelProviderError
from .amap_weather import AmapWeatherProvider, AmapWeatherProviderError
from .protocols import HotelProvider, HotelProviderError, WeatherProvider, WeatherProviderError

__all__ = [
    "AmapPOIProvider",
    "AmapPOIProviderError",
    "AmapHotelProvider",
    "AmapHotelProviderError",
    "AmapWeatherProvider",
    "AmapWeatherProviderError",
    "HotelProvider",
    "HotelProviderError",
    "WeatherProvider",
    "WeatherProviderError",
]
