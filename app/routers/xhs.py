"""小红书只读和旅行内容提取接口。"""

from fastapi import APIRouter, HTTPException, Query

from app.integrations.xhs import XHSNote, XHSProvider, XHSProviderError
from app.schemas.attraction import (
    XHSAttractionRequest,
    XHSAttractionHistoryResponse,
    XHSAttractionResponse,
)
from app.schemas.xhs import XHSNoteResponse, XHSSearchRequest, XHSSearchResponse
from app.services.attraction_extractor import (
    AttractionExtractionError,
    extract_attractions_with_metadata,
)
from app.storage.xhs_repository import XHSRepository, XHSRepositoryError

router = APIRouter(prefix="/api/xhs", tags=["xiaohongshu"])


def _response(note: XHSNote) -> XHSNoteResponse:
    """将内部笔记对象映射为不依赖 Spider 响应格式的接口模型。"""
    return XHSNoteResponse(**note.as_dict())


@router.get("/health")
def xhs_health() -> dict[str, object]:
    """报告配置状态，但不返回 Cookie 内容。"""
    from app.integrations.xhs.provider import _VENDOR_ROOT, cookie_from_environment

    return {
        "configured": bool(cookie_from_environment()),
        "vendor_present": _VENDOR_ROOT.is_dir(),
        "mode": "pc-read-only",
    }


@router.post("/search", response_model=XHSSearchResponse)
def search_xhs(request: XHSSearchRequest) -> XHSSearchResponse:
    """根据关键词搜索小红书笔记，并返回标准化的笔记卡片。"""
    try:
        with XHSProvider() as provider:
            notes = provider.search_notes(
                request.keyword,
                limit=request.limit,
                sort_type=request.sort_type,
            )
        return XHSSearchResponse(keyword=request.keyword, items=[_response(note) for note in notes])
    except XHSProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/notes/{note_id}", response_model=XHSNoteResponse)
def get_xhs_note(
    note_id: str,
    xsec_token: str = Query(default=""),
    xsec_source: str = Query(default="pc_search"),
) -> XHSNoteResponse:
    """根据笔记 ID 读取详情，令牌只用于本次上游请求。"""
    try:
        with XHSProvider() as provider:
            note = provider.get_note(
                note_id,
                xsec_token=xsec_token,
                xsec_source=xsec_source,
            )
        return _response(note)
    except XHSProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/attractions", response_model=XHSAttractionResponse)
def extract_xhs_attractions(request: XHSAttractionRequest) -> XHSAttractionResponse:
    """从指定城市的旅行笔记中提取景点候选。"""
    try:
        extraction = extract_attractions_with_metadata(
            city=request.city,
            keywords=request.keywords,
            language=request.language,
            note_limit=request.note_limit,
        )
        return XHSAttractionResponse(
            extraction_id=extraction.extraction_id,
            city=request.city,
            keywords=request.keywords,
            notes_count=extraction.notes_count,
            attractions=extraction.attractions,
        )
    except AttractionExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/attractions/{extraction_id}",
    response_model=XHSAttractionHistoryResponse,
)
def get_xhs_attraction_extraction(extraction_id: str) -> XHSAttractionHistoryResponse:
    """读取已保存的一次小红书景点提取结果。"""
    try:
        extraction = XHSRepository().get_extraction(extraction_id)
    except XHSRepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if extraction is None:
        raise HTTPException(status_code=404, detail="景点提取记录不存在")
    return XHSAttractionHistoryResponse(**extraction)
