"""内部管理员维护小红书内容账号使用的登录接口。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.schemas.xhs_login import (
    XHSCookieLoginRequest,
    XHSLoginMethodsResponse,
    XHSLoginStartResponse,
    XHSLoginStatusResponse,
    XHSLogoutResponse,
    XHSPhoneLoginStartRequest,
    XHSPhoneLoginVerifyRequest,
)
from app.services.xhs_login import XHSLoginTask, get_xhs_login_service
from app.security import require_admin_key


# NOTE: 小红书账号属于系统内容来源，普通用户的旅行搜索不应接触这些认证材料。
router = APIRouter(
    prefix="/api/admin/integrations/xhs",
    tags=["internal-xiaohongshu-integration"],
    dependencies=[Depends(require_admin_key)],
)


def _status_response(task: XHSLoginTask) -> XHSLoginStatusResponse:
    """将任务对象转换为不包含 Cookie 和手机号的 REST 响应。"""
    return XHSLoginStatusResponse(
        login_id=task.login_id,
        method=task.method,
        state=task.state,
        message=task.message,
        qr_url=task.qr_url,
        user_nickname=task.user_nickname,
    )


def _start_response(task: XHSLoginTask) -> XHSLoginStartResponse:
    """返回登录任务的公开标识和有效期。"""
    return XHSLoginStartResponse(
        login_id=task.login_id,
        method=task.method,
        state=task.state,
        message=task.message,
        expires_in=300,
    )


@router.get("/methods", response_model=XHSLoginMethodsResponse)
def login_methods() -> XHSLoginMethodsResponse:
    """返回当前支持的三种 PC 登录方式。"""
    return XHSLoginMethodsResponse(methods=["cookie", "qrcode", "phone"])


@router.delete("/session", response_model=XHSLogoutResponse)
def clear_login_session() -> XHSLogoutResponse:
    """清除当前进程使用的小红书系统账号登录态。"""
    get_xhs_login_service().logout()
    return XHSLogoutResponse(success=True, message="小红书登录态已清除")


@router.post("/qrcode/start", response_model=XHSLoginStartResponse)
def start_qrcode_login() -> XHSLoginStartResponse:
    """创建二维码登录任务，实际网络初始化在后台线程执行。"""
    return _start_response(get_xhs_login_service().start_qrcode())


@router.get("/{login_id}/status", response_model=XHSLoginStatusResponse)
def login_status(login_id: str) -> XHSLoginStatusResponse:
    """返回二维码或手机号登录任务的当前状态。"""
    try:
        task = get_xhs_login_service().status(login_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="登录任务不存在或已过期") from exc
    return _status_response(task)


@router.get("/{login_id}/qrcode")
def login_qrcode(login_id: str) -> Response:
    """将上游二维码地址转换为 SVG，供 Web 页面直接展示。"""
    try:
        qr_url = get_xhs_login_service().qrcode_url(login_id)
    except LookupError as exc:
        raise HTTPException(status_code=409, detail="二维码尚未准备好") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        import qrcode

        from qrcode.image.svg import SvgPathImage

        image = qrcode.make(qr_url, image_factory=SvgPathImage)
        output = image.to_string()
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="二维码组件未安装，请先同步 Python 依赖") from exc
    return Response(
        content=output,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store"},
    )


@router.post("/phone/start", response_model=XHSLoginStartResponse)
def start_phone_login(request: XHSPhoneLoginStartRequest) -> XHSLoginStartResponse:
    """创建手机号登录任务，并异步发送一次验证码。"""
    if not request.phone.isdigit():
        raise HTTPException(status_code=422, detail="手机号只能包含数字")
    return _start_response(get_xhs_login_service().start_phone(request.phone, request.zone))


@router.post("/phone/verify", response_model=XHSLoginStartResponse)
def verify_phone_login(request: XHSPhoneLoginVerifyRequest) -> XHSLoginStartResponse:
    """提交验证码，后台完成正式会话验证。"""
    if not request.code.isdigit():
        raise HTTPException(status_code=422, detail="验证码只能包含数字")
    try:
        task = get_xhs_login_service().verify_phone(request.login_id, request.code)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="登录任务不存在或已过期") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _start_response(task)


@router.post("/cookie", response_model=XHSLoginStartResponse)
def login_with_cookie(request: XHSCookieLoginRequest) -> XHSLoginStartResponse:
    """验证完整 Cookie 并切换当前服务进程使用的登录会话。"""
    try:
        task = get_xhs_login_service().login_with_cookie(request.cookie)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=502, detail="Cookie 验证失败，请确认 Cookie 仍然有效")
    return _start_response(task)
