"""酒店搜索 REST 请求和响应模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class HotelSearchRequest(BaseModel):
    """酒店搜索接口接收的查询条件。"""

    city: str = Field(..., min_length=1, max_length=100, description="目的地城市")
    accommodation: str = Field(default="", max_length=100, description="住宿偏好")
    area: str = Field(default="", max_length=100, description="景点或住宿区域")
    budget_min: float | None = Field(default=None, ge=0, description="每晚最低预算")
    budget_max: float | None = Field(default=None, ge=0, description="每晚最高预算")
    limit: int = Field(default=10, ge=1, le=50, description="最多返回数量")

    @model_validator(mode="after")
    def validate_budget_range(self) -> "HotelSearchRequest":
        """拒绝最低预算高于最高预算的查询。"""
        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_min > self.budget_max
        ):
            raise ValueError("酒店最低预算不能高于最高预算")
        return self


class HotelLocationResponse(BaseModel):
    """酒店 REST 响应中的坐标。"""

    longitude: float
    latitude: float


class HotelResponse(BaseModel):
    """酒店事实数据的 REST 响应模型。"""

    provider: str
    id: str
    name: str
    city: str = ""
    address: str | None = None
    location: HotelLocationResponse | None = None
    type: str | None = None
    rating: float | None = None
    average_price: float | None = None
    price_range: str | None = None
    tel: str | None = None
    photos: list[str] = Field(default_factory=list)


class HotelSearchCriteriaResponse(BaseModel):
    """酒店响应中回显的实际查询条件。"""

    city: str
    accommodation: str = ""
    area: str = ""
    budget_min: float | None = None
    budget_max: float | None = None
    limit: int = 10


class HotelSearchResponse(BaseModel):
    """酒店搜索接口响应。"""

    success: bool
    message: str
    provider: str
    cached: bool
    criteria: HotelSearchCriteriaResponse
    data: list[HotelResponse] = Field(default_factory=list)
