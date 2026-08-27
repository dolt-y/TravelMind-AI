"""景点候选提取接口的数据模型。"""

from pydantic import BaseModel, Field

from app.models.poi import POILocation


class AttractionCandidate(BaseModel):
    """从旅行笔记中提取的景点候选。"""

    name: str = Field(..., min_length=1, max_length=100, description="景点名称")
    name_zh: str = Field(..., min_length=1, max_length=100, description="中文名称")
    name_en: str = Field(..., min_length=1, max_length=160, description="英文名称")
    reason: str = Field(..., min_length=1, max_length=1000, description="推荐理由")
    duration: int = Field(..., ge=1, le=1440, description="建议游玩时长，单位为分钟")
    reservation_required: bool = Field(default=False, description="是否需要提前预约")
    reservation_tips: str = Field(default="", max_length=1000, description="预约提示")
    poi_id: str = Field(default="", max_length=100, description="地图供应商 POI ID")
    address: str = Field(default="", max_length=300, description="景点地址")
    location: POILocation | None = Field(default=None, description="景点经纬度")
    rating: float | None = Field(default=None, ge=0, description="地图供应商评分")
    photos: list[str] = Field(default_factory=list, description="景点图片地址")


class XHSAttractionRequest(BaseModel):
    """小红书景点候选提取请求。"""

    city: str = Field(..., min_length=1, max_length=50, description="目的地城市")
    keywords: str = Field(default="", max_length=100, description="旅行偏好或主题关键词")
    language: str = Field(default="zh", pattern="^(zh|en|ja)$", description="结果语言")
    note_limit: int = Field(default=4, ge=1, le=10, description="参与提取的笔记数量")


class XHSAttractionResponse(BaseModel):
    """小红书景点候选提取响应。"""

    extraction_id: str = Field(..., description="持久化提取记录 ID")
    city: str = Field(..., description="目的地城市")
    keywords: str = Field(default="", description="提取使用的偏好关键词")
    notes_count: int = Field(ge=0, description="实际参与提取的笔记数量")
    attractions: list[AttractionCandidate] = Field(default_factory=list, description="景点候选列表")


class XHSAttractionHistoryResponse(XHSAttractionResponse):
    """已保存的小红书景点候选记录。"""

    created_at: str = Field(..., description="记录创建时间")
