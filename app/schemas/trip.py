"""旅行规划主流程的 REST 请求和响应模型。"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .attraction import AttractionCandidate
from .hotel import HotelResponse
from .weather import WeatherForecastResponse


class TripCityStayRequest(BaseModel):
    """多城市请求中的单个城市停留配置。"""

    city: str = Field(..., min_length=1, max_length=100)
    days: int = Field(..., ge=1, le=15)


class TripPlanRequest(BaseModel):
    """提交旅行规划任务时使用的用户输入。"""

    city: str = Field(default="", max_length=100, description="单城市快捷输入")
    cities: list[TripCityStayRequest] = Field(default_factory=list, max_length=6)
    start_date: date
    end_date: date
    transportation: Literal["walking", "driving", "transit"] = "transit"
    accommodation: str = Field(default="舒适型酒店", max_length=100)
    preferences: list[str] = Field(default_factory=list, max_length=12)
    free_text_input: str = Field(default="", max_length=1000)
    language: Literal["zh", "en", "ja"] = "zh"
    note_limit: int = Field(default=4, ge=1, le=10)
    travelers: int = Field(default=1, ge=1, le=20)
    total_budget: float | None = Field(default=None, ge=0)
    hotel_budget_max: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_destination(self) -> "TripPlanRequest":
        """单城市和多城市输入至少提供一种，且不能表达冲突目的地。"""
        self.city = self.city.strip()
        if not self.city and not self.cities:
            raise ValueError("请至少提供一个目的地城市")
        if self.city and self.cities:
            raise ValueError("city 与 cities 只能使用一种")
        return self


class TripMealResponse(BaseModel):
    """每日餐饮建议。"""

    type: Literal["breakfast", "lunch", "dinner", "snack"]
    name: str
    description: str = ""
    estimated_cost: float = 0


class TripLocationResponse(BaseModel):
    """行程路线中的经纬度。"""

    longitude: float
    latitude: float


class TripRouteEndpointResponse(BaseModel):
    """行程路线中的起点或终点。"""

    name: str = ""
    address: str
    city: str = ""
    location: TripLocationResponse


class TripRouteStepResponse(BaseModel):
    """行程路线的一段导航说明。"""

    instruction: str
    road: str = ""
    distance_meters: int = 0
    duration_seconds: int = 0
    action: str = ""
    polyline: list[TripLocationResponse] = Field(default_factory=list)


class TripRoutePlanResponse(BaseModel):
    """地图服务确认的两点路线事实。"""

    provider: str
    provider_route_id: str = ""
    origin: TripRouteEndpointResponse
    destination: TripRouteEndpointResponse
    mode: Literal["walking", "driving", "transit"]
    distance_meters: int
    duration_seconds: int
    description: str = ""
    steps: list[TripRouteStepResponse] = Field(default_factory=list)


class TripRouteSegmentResponse(BaseModel):
    """每日相邻景点之间的路线。"""

    origin_name: str
    destination_name: str
    route: TripRoutePlanResponse


class TripDayResponse(BaseModel):
    """单日行程响应。"""

    day_index: int
    date: date
    city: str
    is_transfer_day: bool = False
    transfer_info: str = ""
    description: str
    transportation: Literal["walking", "driving", "transit"]
    attractions: list[AttractionCandidate] = Field(default_factory=list)
    meals: list[TripMealResponse] = Field(default_factory=list)
    hotel: HotelResponse | None = None
    weather: WeatherForecastResponse | None = None
    routes: list[TripRouteSegmentResponse] = Field(default_factory=list)


class TripBudgetResponse(BaseModel):
    """完整行程的预算汇总。"""

    currency: str
    attractions: float
    hotels: float
    meals: float
    transportation: float
    total: float
    target: float | None = None


class TripPlanResponse(BaseModel):
    """完整行程响应。"""

    plan_id: str
    cities: list[str]
    start_date: date
    end_date: date
    travelers: int
    days: list[TripDayResponse]
    recommended_hotels: list[HotelResponse] = Field(default_factory=list)
    budget: TripBudgetResponse
    overall_suggestions: str
    warnings: list[str] = Field(default_factory=list)
    source_extraction_ids: list[str] = Field(default_factory=list)
    created_at: datetime


class TripCreateResponse(BaseModel):
    """任务提交成功后的查询凭据。"""

    task_id: str
    status: Literal["submitted"]
    status_url: str
    ws_url: str
    message: str


class TripTaskResponse(BaseModel):
    """规划任务当前状态和完成后的行程结果。"""

    task_id: str
    status: Literal["submitted", "processing", "completed", "failed"]
    stage: str
    progress: int
    message: str
    error_code: str | None = None
    error: str | None = None
    plan_id: str | None = None
    result: TripPlanResponse | None = None
    created_at: datetime
    updated_at: datetime


class TripHistoryItemResponse(BaseModel):
    """历史行程列表中的摘要。"""

    plan_id: str
    cities: list[str]
    start_date: date
    end_date: date
    travelers: int
    days_count: int
    created_at: datetime


class TripHistoryResponse(BaseModel):
    """历史行程列表。"""

    items: list[TripHistoryItemResponse] = Field(default_factory=list)
