"""小红书笔记、景点候选和提取记录的领域模型。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .poi import POILocation


class XHSNote(BaseModel):
    """小红书笔记的标准化业务对象。"""

    note_id: str = Field(..., min_length=1, description="笔记 ID")
    title: str = Field(default="", description="笔记标题")
    content: str = Field(default="", description="笔记正文")
    source_url: str = Field(default="", description="笔记地址")
    # NOTE: 详情令牌只供当前上游请求使用，不进入 REST 响应和持久化记录。
    xsec_token: str = Field(default="", exclude=True, repr=False, description="详情请求令牌")
    xsec_source: str = Field(default="pc_search", description="详情请求来源")
    images: list[str] = Field(default_factory=list, description="笔记图片地址")
    author: str = Field(default="", description="作者昵称")
    liked_count: int = Field(default=0, ge=0, description="点赞数量")

    def as_dict(self) -> dict[str, Any]:
        """转换为不包含详情令牌的接口或仓储数据。"""
        return self.model_dump(exclude={"xsec_token"})


class AttractionCandidate(BaseModel):
    """从小红书旅行笔记中提取并可用于行程规划的景点候选。"""

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


class XHSExtraction(BaseModel):
    """一次小红书景点提取及其持久化标识。"""

    extraction_id: str = Field(..., description="持久化提取记录 ID")
    city: str = Field(..., description="目的地城市")
    keywords: str = Field(default="", description="提取使用的偏好关键词")
    language: str = Field(default="zh", description="结果语言")
    notes_count: int = Field(default=0, ge=0, description="实际参与提取的笔记数量")
    attractions: list[AttractionCandidate] = Field(default_factory=list, description="景点候选列表")
    created_at: str = Field(default="", description="记录创建时间")
