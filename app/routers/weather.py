"""城市天气预报接口。"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.schemas.weather import WeatherForecastResponse, WeatherResponse
from app.services.weather_service import (
    WeatherService,
    WeatherServiceError,
    WeatherStorageError,
    WeatherValidationError,
)


router = APIRouter(prefix="/api/weather", tags=["weather"])
map_router = APIRouter(prefix="/api/map", tags=["weather"])


def _forecast_response(item: object) -> WeatherForecastResponse:
    """将天气领域模型转换为独立的 REST 响应模型。"""
    payload = item.model_dump(mode="json") if hasattr(item, "model_dump") else item
    return WeatherForecastResponse.model_validate(payload)


def _query_weather(
    city: str,
    start_date: date | None,
    end_date: date | None,
) -> WeatherResponse:
    """执行天气业务查询并映射服务异常和 REST 响应。"""
    try:
        result = WeatherService().query(
            city,
            start_date=start_date,
            end_date=end_date,
        )
        return WeatherResponse(
            success=True,
            message="天气缓存查询成功" if result.cached else "天气查询成功",
            provider=result.provider,
            city=result.city,
            cached=result.cached,
            data=[_forecast_response(item) for item in result.forecasts],
        )
    except WeatherValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WeatherStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("", response_model=WeatherResponse)
def get_weather(
    city: str = Query(..., min_length=1, max_length=100, description="城市名称或 adcode"),
    start_date: date | None = Query(default=None, description="开始日期，格式 YYYY-MM-DD"),
    end_date: date | None = Query(default=None, description="结束日期，格式 YYYY-MM-DD"),
) -> WeatherResponse:
    """按城市和可选日期范围查询天气预报。"""
    return _query_weather(city, start_date, end_date)


@map_router.get("/weather", response_model=WeatherResponse)
def get_map_weather(
    city: str = Query(..., min_length=1, max_length=100, description="城市名称或 adcode"),
    start_date: date | None = Query(default=None, description="开始日期，格式 YYYY-MM-DD"),
    end_date: date | None = Query(default=None, description="结束日期，格式 YYYY-MM-DD"),
) -> WeatherResponse:
    """提供与 TripStar 地图路由兼容的天气查询地址。"""
    return _query_weather(city, start_date, end_date)
