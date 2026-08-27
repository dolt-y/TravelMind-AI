"""小红书搜索和笔记详情接口的数据模型。"""

from pydantic import BaseModel, Field


class XHSSearchRequest(BaseModel):
    """小红书笔记搜索请求参数。"""

    keyword: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    limit: int = Field(default=10, ge=1, le=50, description="返回笔记数量")
    sort_type: int = Field(default=0, ge=0, le=4, description="排序类型")


class XHSNoteResponse(BaseModel):
    """对外返回的标准化小红书笔记。"""

    note_id: str = Field(..., description="笔记 ID")
    title: str = Field(default="", description="笔记标题")
    content: str = Field(default="", description="笔记正文")
    source_url: str = Field(default="", description="笔记地址")
    xsec_source: str = Field(default="pc_search", description="详情请求来源")
    images: list[str] = Field(default_factory=list, description="笔记图片地址")
    author: str = Field(default="", description="作者昵称")
    liked_count: int = Field(default=0, description="点赞数量")


class XHSSearchResponse(BaseModel):
    """小红书搜索结果。"""

    keyword: str = Field(..., description="实际使用的搜索关键词")
    items: list[XHSNoteResponse] = Field(default_factory=list, description="笔记列表")
