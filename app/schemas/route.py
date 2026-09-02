"""路线规划 REST 请求和响应模型。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RouteLocationRequest(BaseModel):
    """请求中可直接使用的已知坐标。"""

    longitude: float = Field(..., ge=-180, le=180, description="经度")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")


class RouteRequest(BaseModel):
    """兼容 TripStar 地址字段并允许复用已有 POI 坐标。"""

    origin_address: str = Field(..., min_length=1, max_length=300, description="起点地址或名称")
    destination_address: str = Field(..., min_length=1, max_length=300, description="终点地址或名称")
    origin_city: str | None = Field(default=None, max_length=100, description="起点城市")
    destination_city: str | None = Field(default=None, max_length=100, description="终点城市")
    route_type: Literal["walking", "driving", "transit"] = Field(
        default="walking",
        description="交通方式",
    )
    origin_location: RouteLocationRequest | None = Field(default=None, description="已知起点坐标")
    destination_location: RouteLocationRequest | None = Field(default=None, description="已知终点坐标")


class RouteLocationResponse(BaseModel):
    """路线响应中的坐标。"""

    longitude: float
    latitude: float


class RouteEndpointResponse(BaseModel):
    """路线响应中的起点或终点。"""

    name: str = ""
    address: str
    city: str = ""
    location: RouteLocationResponse


class RouteStepResponse(BaseModel):
    """路线响应中的导航步骤。"""

    instruction: str
    road: str = ""
    distance: int = Field(default=0, description="步骤距离，单位为米")
    duration: int = Field(default=0, description="步骤耗时，单位为秒")
    action: str = ""
    polyline: list[RouteLocationResponse] = Field(default_factory=list)


class RouteInfoResponse(BaseModel):
    """兼容 TripStar 基础字段的标准化路线事实。"""

    distance: int = Field(..., description="总距离，单位为米")
    duration: int = Field(..., description="总耗时，单位为秒")
    route_type: Literal["walking", "driving", "transit"]
    description: str
    provider_route_id: str = ""
    origin: RouteEndpointResponse
    destination: RouteEndpointResponse
    steps: list[RouteStepResponse] = Field(default_factory=list)


class RouteResponse(BaseModel):
    """路线规划接口响应。"""

    success: bool
    message: str
    provider: str
    cached: bool = False
    data: RouteInfoResponse
