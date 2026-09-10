"""POI 搜索、详情和景点图片接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.integrations.xhs import XHSAuthenticationRequiredError
from app.schemas.poi import POIDetailResponse, POIPhotoResponse, POIResponse, POISearchResponse
from app.services.poi_service import POIService, POIServiceError
from app.xhs_session import (
    XHSClientSession,
    require_xhs_session,
    xhs_authentication_required,
)

router = APIRouter(prefix="/api/poi", tags=["poi"])
map_router = APIRouter(prefix="/api/map", tags=["poi"])


def _poi_response(poi: object) -> POIResponse:
    """将地图领域模型转换为独立的 REST 响应模型。"""
    payload = poi.model_dump(mode="json") if hasattr(poi, "model_dump") else poi
    return POIResponse.model_validate(payload)


def _search_response(
    keywords: str,
    city: str,
    citylimit: bool,
    limit: int,
) -> POISearchResponse:
    """执行 POI 业务搜索并映射为 REST 响应。"""
    try:
        pois = POIService().search(keywords, city, citylimit, limit)
        return POISearchResponse(
            success=bool(pois),
            message="POI 搜索成功" if pois else "未获取到 POI 数据",
            data=[_poi_response(poi) for poi in pois],
        )
    except POIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/search", response_model=POISearchResponse)
def search_poi(
    keywords: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    city: str = Query(default="北京", min_length=1, max_length=50, description="城市名称"),
    citylimit: bool = Query(default=True, description="是否限制在指定城市内"),
    limit: int = Query(default=20, ge=1, le=50, description="最多返回数量"),
) -> POISearchResponse:
    """搜索地图 POI，保存结果后返回标准化列表。"""
    return _search_response(keywords, city, citylimit, limit)


@map_router.get("/poi", response_model=POISearchResponse)
def search_map_poi(
    keywords: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    city: str = Query(..., min_length=1, max_length=50, description="城市名称"),
    citylimit: bool = Query(default=True, description="是否限制在指定城市内"),
    limit: int = Query(default=20, ge=1, le=50, description="最多返回数量"),
) -> POISearchResponse:
    """兼容地图路由下的 POI 搜索地址。"""
    return _search_response(keywords, city, citylimit, limit)


@router.get("/detail/{poi_id}", response_model=POIDetailResponse)
def get_poi_detail(poi_id: str) -> POIDetailResponse:
    """读取已保存的 POI 详情，未命中时请求高德并保存。"""
    try:
        poi = POIService().detail(poi_id)
        return POIDetailResponse(success=True, message="获取 POI 详情成功", data=_poi_response(poi))
    except POIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/photo", response_model=POIPhotoResponse)
async def get_poi_photo(
    name: str = Query(..., min_length=1, max_length=100, description="景点名称"),
    city: str = Query(default="", max_length=50, description="所在城市"),
    session: XHSClientSession = Depends(require_xhs_session),
) -> POIPhotoResponse:
    """获取景点的小红书首图，并缓存图片地址。"""
    try:
        photo_url = await POIService(xhs_cookie=session.cookie).photo(name, city)
        return POIPhotoResponse(
            success=True,
            message="获取景点图片成功" if photo_url else "未找到景点图片",
            data={"name": name, "photo_url": photo_url},
        )
    except XHSAuthenticationRequiredError as exc:
        raise xhs_authentication_required(
            "当前浏览器的小红书登录态已失效，请重新登录"
        ) from exc
    except POIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
