"""为当前浏览器建立和清理小红书客户端会话。"""

from __future__ import annotations

from collections import defaultdict, deque
import time
from threading import Lock

from fastapi import APIRouter, HTTPException, Query, Request
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
from app.services.xhs_login import (
    XHSLoginCapacityError,
    XHSLoginTask,
    get_xhs_login_service,
)
from app.xhs_session import (
    XHSSessionConfigurationError,
    XHSSessionError,
    clear_xhs_session_cookie,
    set_xhs_session_token_cookie,
    validate_session_configuration,
)


router = APIRouter(
    prefix="/api/xhs/login",
    tags=["xiaohongshu-login"],
)

LOGIN_RATE_LIMIT = 8
LOGIN_RATE_WINDOW_SECONDS = 60
_login_attempts: dict[str, deque[float]] = defaultdict(deque)
_login_attempts_lock = Lock()


def _require_login_capacity(request: Request) -> None:
    """限制单个客户端创建登录任务的频率。"""
    client_host = request.client.host if request.client else "unknown"
    now = time.monotonic()
    cutoff = now - LOGIN_RATE_WINDOW_SECONDS
    with _login_attempts_lock:
        attempts = _login_attempts[client_host]
        while attempts and attempts[0] <= cutoff:
            attempts.popleft()
        if len(attempts) >= LOGIN_RATE_LIMIT:
            retry_after = max(1, int(attempts[0] + LOGIN_RATE_WINDOW_SECONDS - now))
            raise HTTPException(
                status_code=429,
                detail="登录请求过于频繁，请稍后重试",
                headers={"Retry-After": str(retry_after)},
            )
        attempts.append(now)


def _capacity_response(exc: XHSLoginCapacityError) -> HTTPException:
    """将全局登录任务容量限制转换为客户端可识别的响应。"""
    return HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "30"})


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


def _require_session_configuration() -> None:
    """把缺少加密密钥转换为不泄露配置内容的服务错误。"""
    try:
        validate_session_configuration()
    except XHSSessionConfigurationError as exc:
        raise HTTPException(status_code=503, detail="客户端会话能力尚未配置") from exc


def _deliver_session(task: XHSLoginTask, request: Request, response: Response) -> None:
    """登录成功后把加密会话写入发起请求的浏览器。"""
    result = get_xhs_login_service().claim_session(task.login_id)
    if result is None:
        raise HTTPException(status_code=410, detail="登录任务已过期，请重新登录")
    try:
        set_xhs_session_token_cookie(response, request, result)
    except XHSSessionError as exc:
        raise HTTPException(status_code=500, detail="客户端登录态保存失败，请重新登录") from exc


@router.get("/methods", response_model=XHSLoginMethodsResponse)
def login_methods() -> XHSLoginMethodsResponse:
    """返回当前支持的三种 PC 登录方式。"""
    return XHSLoginMethodsResponse(methods=["cookie", "qrcode", "phone"])


@router.delete("/session", response_model=XHSLogoutResponse)
def clear_login_session(
    request: Request,
    response: Response,
    login_id: str | None = Query(default=None, min_length=8, max_length=80),
) -> XHSLogoutResponse:
    """清除当前浏览器会话，并按需取消该页面发起的登录挑战。"""
    if login_id:
        get_xhs_login_service().cancel(login_id)
    clear_xhs_session_cookie(response, request)
    return XHSLogoutResponse(success=True, message="当前浏览器的小红书登录态已清除")


@router.post("/qrcode/start", response_model=XHSLoginStartResponse)
def start_qrcode_login(request: Request) -> XHSLoginStartResponse:
    """创建二维码登录任务，实际网络初始化在后台线程执行。"""
    _require_session_configuration()
    _require_login_capacity(request)
    try:
        return _start_response(get_xhs_login_service().start_qrcode())
    except XHSLoginCapacityError as exc:
        raise _capacity_response(exc) from exc


@router.get("/{login_id}/status", response_model=XHSLoginStatusResponse)
def login_status(login_id: str, request: Request, response: Response) -> XHSLoginStatusResponse:
    """返回二维码或手机号登录任务的当前状态。"""
    try:
        task = get_xhs_login_service().status(login_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="登录任务不存在或已过期") from exc
    if task.state == "success":
        _deliver_session(task, request, response)
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
def start_phone_login(
    payload: XHSPhoneLoginStartRequest,
    request: Request,
) -> XHSLoginStartResponse:
    """创建手机号登录任务，并异步发送一次验证码。"""
    _require_session_configuration()
    _require_login_capacity(request)
    if not payload.phone.isdigit():
        raise HTTPException(status_code=422, detail="手机号只能包含数字")
    try:
        return _start_response(
            get_xhs_login_service().start_phone(payload.phone, payload.zone)
        )
    except XHSLoginCapacityError as exc:
        raise _capacity_response(exc) from exc


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
def login_with_cookie(
    payload: XHSCookieLoginRequest,
    request: Request,
    response: Response,
) -> XHSLoginStartResponse:
    """验证完整 Cookie，并加密写入当前浏览器。"""
    _require_session_configuration()
    _require_login_capacity(request)
    try:
        task = get_xhs_login_service().login_with_cookie(payload.cookie)
    except XHSLoginCapacityError as exc:
        raise _capacity_response(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=502, detail="Cookie 验证失败，请确认 Cookie 仍然有效")
    _deliver_session(task, request, response)
    return _start_response(task)
