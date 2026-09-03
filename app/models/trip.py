"""旅行请求、每日安排、预算和任务状态的领域模型。"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .hotel import Hotel
from .route import RoutePlan, RouteMode
from .weather import WeatherForecast
from .xhs import AttractionCandidate


TripLanguage = Literal["zh", "en", "ja"]
TripTaskStatus = Literal["submitted", "processing", "completed", "failed"]
MealType = Literal["breakfast", "lunch", "dinner", "snack"]


class TripCityStay(BaseModel):
    """一个城市及其在完整行程中占用的自然日数量。"""

    city: str = Field(..., min_length=1, max_length=100)
    days: int = Field(..., ge=1, le=15)


class TripPlanningRequest(BaseModel):
    """经过 REST 层转换后供编排服务使用的旅行需求。"""

    cities: list[TripCityStay] = Field(..., min_length=1, max_length=6)
    start_date: date
    end_date: date
    transportation: RouteMode = "transit"
    accommodation: str = Field(default="舒适型酒店", max_length=100)
    preferences: list[str] = Field(default_factory=list, max_length=12)
    extra_requirements: str = Field(default="", max_length=1000)
    language: TripLanguage = "zh"
    note_limit: int = Field(default=4, ge=1, le=10)
    travelers: int = Field(default=1, ge=1, le=20)
    total_budget: float | None = Field(default=None, ge=0)
    hotel_budget_max: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_dates_and_stays(self) -> "TripPlanningRequest":
        """保证城市停留天数与用户选择的日期完整一致。"""
        if self.end_date < self.start_date:
            raise ValueError("行程结束日期不能早于开始日期")
        travel_days = (self.end_date - self.start_date).days + 1
        if travel_days > 30:
            raise ValueError("一次行程不能超过 30 天")
        if sum(item.days for item in self.cities) != travel_days:
            raise ValueError("各城市停留天数之和必须等于行程天数")
        return self


class TripMeal(BaseModel):
    """规划模型给出的餐饮建议，费用仅作为行程预算估算。"""

    type: MealType
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    estimated_cost: float = Field(default=0, ge=0, le=5000)


class TripRouteSegment(BaseModel):
    """同一天两个相邻景点之间经过地图服务确认的路线。"""

    origin_name: str
    destination_name: str
    route: RoutePlan


class TripDay(BaseModel):
    """一个自然日的城市、景点顺序、餐饮、住宿、天气和路线。"""

    day_index: int = Field(..., ge=1, le=30)
    date: date
    city: str
    is_transfer_day: bool = False
    transfer_info: str = ""
    description: str
    transportation: RouteMode
    attractions: list[AttractionCandidate] = Field(default_factory=list)
    meals: list[TripMeal] = Field(default_factory=list)
    hotel: Hotel | None = None
    weather: WeatherForecast | None = None
    routes: list[TripRouteSegment] = Field(default_factory=list)


class TripBudget(BaseModel):
    """由已知酒店参考价和规划餐饮估算确定性汇总的预算。"""

    currency: str = "CNY"
    attractions: float = Field(default=0, ge=0)
    hotels: float = Field(default=0, ge=0)
    meals: float = Field(default=0, ge=0)
    transportation: float = Field(default=0, ge=0)
    total: float = Field(default=0, ge=0)
    target: float | None = Field(default=None, ge=0)


class TripPlan(BaseModel):
    """已经过日期、地点来源、路线端点和预算校验的完整行程。"""

    plan_id: str
    cities: list[str]
    start_date: date
    end_date: date
    travelers: int
    days: list[TripDay]
    recommended_hotels: list[Hotel] = Field(default_factory=list)
    budget: TripBudget
    overall_suggestions: str
    warnings: list[str] = Field(default_factory=list)
    source_extraction_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TripTask(BaseModel):
    """可在服务重启后继续查询的旅行规划任务快照。"""

    task_id: str
    status: TripTaskStatus
    stage: str
    progress: int = Field(ge=0, le=100)
    message: str
    error_code: str | None = None
    error: str | None = None
    plan_id: str | None = None
    created_at: datetime
    updated_at: datetime
