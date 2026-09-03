"""业务领域模型包；接口传输模型统一放在 schemas 包中。"""

from .hotel import Hotel, HotelSearchCriteria, HotelSearchResult
from .poi import POI, POILocation
from .trip import TripDay, TripPlan, TripPlanningRequest
from .weather import WeatherForecast, WeatherQueryResult
from .xhs import AttractionCandidate, XHSExtraction, XHSNote

__all__ = [
    "AttractionCandidate",
    "Hotel",
    "HotelSearchCriteria",
    "HotelSearchResult",
    "POI",
    "POILocation",
    "TripDay",
    "TripPlan",
    "TripPlanningRequest",
    "WeatherForecast",
    "WeatherQueryResult",
    "XHSExtraction",
    "XHSNote",
]
