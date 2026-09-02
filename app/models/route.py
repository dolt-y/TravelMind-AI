"""路线查询条件、区间事实和业务结果模型。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.poi import POILocation


RouteMode = Literal["walking", "driving", "transit"]


class RouteEndpoint(BaseModel):
    """路线起点或终点的地图事实。"""

    name: str = Field(default="", description="地点名称")
    address: str = Field(..., min_length=1, max_length=300, description="地点地址或查询文本")
    city: str = Field(default="", max_length=100, description="所在城市")
    location: POILocation = Field(..., description="地图供应商确认的坐标")


class RouteStep(BaseModel):
    """供应商返回的一段导航指引。"""

    instruction: str = Field(..., min_length=1, description="导航说明")
    road: str = Field(default="", description="道路或公共交通线路")
    distance_meters: int = Field(default=0, ge=0, description="步骤距离，单位为米")
    duration_seconds: int = Field(default=0, ge=0, description="步骤耗时，单位为秒")
    action: str = Field(default="", description="转向、换乘或到达动作")
    polyline: list[POILocation] = Field(default_factory=list, description="步骤轨迹坐标")


class RoutePlan(BaseModel):
    """地图供应商确认的两点路线事实。"""

    provider: str = Field(default="amap", description="路线供应商")
    provider_route_id: str = Field(default="", description="供应商路线标识")
    origin: RouteEndpoint
    destination: RouteEndpoint
    mode: RouteMode
    distance_meters: int = Field(..., ge=0, description="总距离，单位为米")
    duration_seconds: int = Field(..., ge=0, description="总耗时，单位为秒")
    description: str = Field(default="", description="路线摘要")
    steps: list[RouteStep] = Field(default_factory=list)


class RouteQuery(BaseModel):
    """路线业务接收的地址、城市、坐标和交通方式。"""

    origin_address: str = Field(..., min_length=1, max_length=300)
    destination_address: str = Field(..., min_length=1, max_length=300)
    origin_city: str = Field(default="", max_length=100)
    destination_city: str = Field(default="", max_length=100)
    route_type: RouteMode = "walking"
    origin_location: POILocation | None = None
    destination_location: POILocation | None = None

    @field_validator("origin_address", "destination_address", "origin_city", "destination_city")
    @classmethod
    def strip_text(cls, value: str) -> str:
        """移除地址和城市首尾空白，保证缓存键稳定。"""
        return value.strip()


class RouteQueryResult(BaseModel):
    """一次路线查询结果及其缓存状态。"""

    provider: str
    cached: bool = False
    query: RouteQuery
    route: RoutePlan
