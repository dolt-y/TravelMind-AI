"""酒店搜索领域模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.models.poi import POILocation


class Hotel(BaseModel):
    """地图供应商返回的酒店事实数据。"""

    provider: str = Field(default="amap", description="地图供应商")
    id: str = Field(..., min_length=1, description="地图供应商酒店 POI ID")
    name: str = Field(..., min_length=1, description="酒店名称")
    city: str = Field(default="", description="所在城市")
    address: str | None = Field(default=None, description="酒店地址")
    location: POILocation | None = Field(default=None, description="酒店坐标")
    type: str | None = Field(default=None, description="供应商返回的酒店类型")
    rating: float | None = Field(default=None, ge=0, description="供应商评分")
    average_price: float | None = Field(
        default=None,
        ge=0,
        description="供应商参考均价，具体计价口径以供应商为准",
    )
    price_range: str | None = Field(default=None, description="供应商价格文本")
    tel: str | None = Field(default=None, description="联系电话")
    photos: list[str] = Field(default_factory=list, description="酒店图片地址")


class HotelSearchCriteria(BaseModel):
    """一次酒店搜索使用的业务条件。"""

    city: str = Field(..., min_length=1, max_length=100, description="目的地城市")
    accommodation: str = Field(default="", max_length=100, description="住宿偏好")
    area: str = Field(default="", max_length=100, description="景点或住宿区域")
    budget_min: float | None = Field(default=None, ge=0, description="每晚最低预算")
    budget_max: float | None = Field(default=None, ge=0, description="每晚最高预算")
    limit: int = Field(default=10, ge=1, le=50, description="最多返回数量")

    @model_validator(mode="after")
    def validate_budget_range(self) -> "HotelSearchCriteria":
        """保证酒店每晚最低预算不高于最高预算。"""
        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_min > self.budget_max
        ):
            raise ValueError("酒店最低预算不能高于最高预算")
        return self


class HotelSearchResult(BaseModel):
    """酒店搜索结果及其来源和缓存状态。"""

    provider: str
    criteria: HotelSearchCriteria
    cached: bool = False
    hotels: list[Hotel] = Field(default_factory=list)
