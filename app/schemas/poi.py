"""POI 搜索、详情和图片接口模型。"""

from pydantic import BaseModel, Field

class POILocationResponse(BaseModel):
    """REST 响应中的 POI 坐标。"""

    longitude: float = Field(..., description="经度")
    latitude: float = Field(..., description="纬度")


class POIResponse(BaseModel):
    """地图 POI 的 REST 响应模型。"""

    id: str = Field(..., description="地图供应商 POI ID")
    name: str = Field(..., description="POI 名称")
    type: str = Field(default="", description="POI 类型")
    address: str = Field(default="", description="POI 地址")
    location: POILocationResponse = Field(..., description="POI 坐标")
    tel: str | None = Field(default=None, description="联系电话")
    city: str = Field(default="", description="所在城市")
    rating: float | None = Field(default=None, description="评分")
    photos: list[str] = Field(default_factory=list, description="图片地址")


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
    data: list[POIResponse] = Field(default_factory=list)


class POIDetailResponse(BaseModel):
    """POI 详情响应。"""

    success: bool
    message: str
    data: POIResponse | None = None


class POIPhotoResponse(BaseModel):
    """景点图片响应。"""

    success: bool
    message: str
    data: dict[str, str] = Field(default_factory=dict)
