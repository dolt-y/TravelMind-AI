"""酒店搜索接口。"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from app.models.hotel import HotelSearchCriteria
from app.schemas.hotel import (
    HotelResponse,
    HotelSearchCriteriaResponse,
    HotelSearchRequest,
    HotelSearchResponse,
)
from app.services.hotel_service import HotelService, HotelServiceError, HotelStorageError


router = APIRouter(prefix="/api/hotels", tags=["hotels"])


def _hotel_response(hotel: object) -> HotelResponse:
    """将酒店领域模型转换为独立的 REST 响应模型。"""
    payload = hotel.model_dump(mode="json") if hasattr(hotel, "model_dump") else hotel
    return HotelResponse.model_validate(payload)


@router.get("/search", response_model=HotelSearchResponse)
def search_hotels(
    city: str = Query(..., min_length=1, max_length=100, description="目的地城市"),
    accommodation: str = Query(default="", max_length=100, description="住宿偏好"),
    area: str = Query(default="", max_length=100, description="景点或住宿区域"),
    budget_min: float | None = Query(default=None, ge=0, description="每晚最低预算"),
    budget_max: float | None = Query(default=None, ge=0, description="每晚最高预算"),
    limit: int = Query(default=10, ge=1, le=50, description="最多返回数量"),
) -> HotelSearchResponse:
    """按城市、住宿偏好、预算和区域搜索酒店。"""
    try:
        request = HotelSearchRequest(
            city=city,
            accommodation=accommodation,
            area=area,
            budget_min=budget_min,
            budget_max=budget_max,
            limit=limit,
        )
        criteria = HotelSearchCriteria.model_validate(request.model_dump())
        result = HotelService().search(criteria)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HotelStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except HotelServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return HotelSearchResponse(
        success=bool(result.hotels),
        message="酒店搜索成功" if result.hotels else "未获取到酒店数据",
        provider=result.provider,
        cached=result.cached,
        criteria=HotelSearchCriteriaResponse.model_validate(
            result.criteria.model_dump(mode="json")
        ),
        data=[_hotel_response(hotel) for hotel in result.hotels],
    )
