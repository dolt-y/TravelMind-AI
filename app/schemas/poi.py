"""POI 搜索、详情和图片接口模型。"""

from pydantic import BaseModel, Field

from app.models.poi import POI


class POISearchRequest(BaseModel):
    """POI 搜索请求参数。"""

    keywords: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    city: str = Field(default="北京", min_length=1, max_length=50, description="城市名称")
    citylimit: bool = Field(default=True, description="是否限制在指定城市内")
    limit: int = Field(default=20, ge=1, le=50, description="最多返回数量")


class POISearchResponse(BaseModel):
    """POI 搜索响应。"""

    success: bool
    message: str
    data: list[POI] = Field(default_factory=list)


class POIDetailResponse(BaseModel):
    """POI 详情响应。"""

    success: bool
    message: str
    data: POI | None = None


class POIPhotoResponse(BaseModel):
    """景点图片响应。"""

    success: bool
    message: str
    data: dict[str, str] = Field(default_factory=dict)
