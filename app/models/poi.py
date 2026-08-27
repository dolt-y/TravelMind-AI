"""POI 领域模型，统一地图服务和业务层之间的数据结构。"""

from pydantic import BaseModel, Field


class POILocation(BaseModel):
    """POI 的经纬度坐标。"""

    longitude: float = Field(..., description="经度")
    latitude: float = Field(..., description="纬度")


class POI(BaseModel):
    """地图服务返回的兴趣点业务对象。"""

    id: str = Field(..., min_length=1, description="地图供应商 POI ID")
    name: str = Field(..., min_length=1, description="POI 名称")
    type: str = Field(default="", description="POI 类型")
    address: str = Field(default="", description="POI 地址")
    location: POILocation = Field(..., description="POI 坐标")
    tel: str | None = Field(default=None, description="联系电话")
    city: str = Field(default="", description="所在城市")
    rating: float | None = Field(default=None, description="评分")
    photos: list[str] = Field(default_factory=list, description="图片地址")

