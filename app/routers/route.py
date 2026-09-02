"""地图两点路线规划接口。"""

from fastapi import APIRouter, HTTPException

from app.models.route import RouteQuery
from app.schemas.route import (
    RouteEndpointResponse,
    RouteInfoResponse,
    RouteLocationResponse,
    RouteRequest,
    RouteResponse,
    RouteStepResponse,
)
from app.services.route_service import (
    RouteService,
    RouteServiceError,
    RouteStorageError,
    RouteValidationError,
)


router = APIRouter(prefix="/api/map", tags=["route"])


def _location_response(location: object) -> RouteLocationResponse:
    """将路线领域坐标转换为独立 REST 模型。"""
    payload = location.model_dump(mode="json") if hasattr(location, "model_dump") else location
    return RouteLocationResponse.model_validate(payload)


def _endpoint_response(endpoint: object) -> RouteEndpointResponse:
    """将路线端点转换为独立 REST 模型。"""
    return RouteEndpointResponse(
        name=endpoint.name,
        address=endpoint.address,
        city=endpoint.city,
        location=_location_response(endpoint.location),
    )


def _route_response(result: object) -> RouteResponse:
    """返回 TripStar 基础字段以及 TravelMind 的端点和步骤事实。"""
    route = result.route
    return RouteResponse(
        success=True,
        message="路线缓存查询成功" if result.cached else "路线规划成功",
        provider=result.provider,
        cached=result.cached,
        data=RouteInfoResponse(
            distance=route.distance_meters,
            duration=route.duration_seconds,
            route_type=route.mode,
            description=route.description,
            provider_route_id=route.provider_route_id,
            origin=_endpoint_response(route.origin),
            destination=_endpoint_response(route.destination),
            steps=[
                RouteStepResponse(
                    instruction=step.instruction,
                    road=step.road,
                    distance=step.distance_meters,
                    duration=step.duration_seconds,
                    action=step.action,
                    polyline=[_location_response(point) for point in step.polyline],
                )
                for step in route.steps
            ],
        ),
    )


@router.post("/route", response_model=RouteResponse)
def plan_route(request: RouteRequest) -> RouteResponse:
    """根据地址或已知坐标返回步行、驾车或公共交通路线。"""
    query = RouteQuery(
        origin_address=request.origin_address,
        destination_address=request.destination_address,
        origin_city=request.origin_city or "",
        destination_city=request.destination_city or "",
        route_type=request.route_type,
        origin_location=request.origin_location.model_dump() if request.origin_location else None,
        destination_location=(
            request.destination_location.model_dump() if request.destination_location else None
        ),
    )
    try:
        return _route_response(RouteService().query(query))
    except RouteValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RouteStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RouteServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
