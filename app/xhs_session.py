"""浏览器独立小红书会话的加密、读取和清理。"""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import json
import os

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, Request, Response


SESSION_COOKIE_NAME = "travelmind_xhs_session"
SESSION_SECRET_ENV = "TRAVELMIND_SESSION_SECRET"
SESSION_MAX_AGE_SECONDS = 7 * 24 * 60 * 60
SESSION_COOKIE_PATH = "/api"


class XHSSessionError(RuntimeError):
    """客户端会话无法创建或读取。"""


class XHSSessionConfigurationError(XHSSessionError):
    """服务端缺少用于保护客户端会话的加密密钥。"""


class XHSSessionInvalidError(XHSSessionError):
    """客户端没有提供有效的小红书会话。"""


@dataclass(frozen=True)
class XHSClientSession:
    """服务端单次请求可使用的小红书认证信息。"""

    cookie: str
    user_nickname: str | None = None


def _cipher() -> Fernet:
    """从独立密钥派生 Fernet 密钥，原始配置不会进入令牌。"""
    secret = os.getenv(SESSION_SECRET_ENV, "").strip()
    if len(secret) < 32:
        raise XHSSessionConfigurationError(
            "客户端会话加密密钥未配置或长度不足 32 个字符"
        )
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
    return Fernet(key)


def validate_session_configuration() -> None:
    """在启动登录挑战前确认服务能够签发客户端会话。"""
    _cipher()


def encode_xhs_session(session: XHSClientSession) -> str:
    """把上游 Cookie 加密为只能由当前服务解开的客户端令牌。"""
    payload = json.dumps(
        {"cookie": session.cookie, "user_nickname": session.user_nickname},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return _cipher().encrypt(payload).decode("ascii")


def decode_xhs_session(token: str) -> XHSClientSession:
    """验证令牌完整性和有效期，并恢复本次请求所需认证信息。"""
    if not token:
        raise XHSSessionInvalidError("客户端尚未登录小红书")
    try:
        payload = json.loads(
            _cipher().decrypt(
                token.encode("ascii"),
                ttl=SESSION_MAX_AGE_SECONDS,
            )
        )
        cookie = str(payload.get("cookie") or "").strip()
        nickname = str(payload.get("user_nickname") or "").strip() or None
    except (InvalidToken, UnicodeError, ValueError, TypeError, AttributeError) as exc:
        raise XHSSessionInvalidError("客户端小红书登录态无效或已过期") from exc
    if not cookie:
        raise XHSSessionInvalidError("客户端小红书登录态不完整")
    return XHSClientSession(cookie=cookie, user_nickname=nickname)


def session_from_request(request: Request) -> XHSClientSession:
    """从当前浏览器请求读取会话，不回退到进程变量或环境 Cookie。"""
    return decode_xhs_session(request.cookies.get(SESSION_COOKIE_NAME, ""))


def xhs_authentication_required(message: str) -> HTTPException:
    """构造缺少有效登录态时的 XHS_AUTH_REQUIRED 接口错误。"""
    # NOTE: 503 表示内容来源暂不可用，不能与普通用户自身的 401 身份认证混淆。
    return HTTPException(
        status_code=503,
        detail={"code": "XHS_AUTH_REQUIRED", "message": message},
    )


def require_xhs_session(request: Request) -> XHSClientSession:
    """读取当前请求会话，并将失效状态转换为稳定接口错误。"""
    try:
        return session_from_request(request)
    except XHSSessionConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "XHS_SESSION_NOT_CONFIGURED",
                "message": "客户端会话能力尚未配置，请联系服务提供方",
            },
        ) from exc
    except XHSSessionInvalidError as exc:
        raise xhs_authentication_required(
            "当前浏览器尚未登录小红书，请先完成登录"
        ) from exc


def _secure_cookie(request: Request) -> bool:
    """HTTPS 部署启用 Secure，本地 HTTP 开发仍可完成登录。"""
    return request.url.scheme == "https"


def set_xhs_session_token_cookie(
    response: Response,
    request: Request,
    token: str,
) -> None:
    """把已加密的登录结果交付当前浏览器，不在接口正文中暴露令牌。"""
    if len(token) > 3800:
        raise XHSSessionError("小红书登录态过大，无法安全保存到浏览器")
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=_secure_cookie(request),
        samesite="lax",
        path=SESSION_COOKIE_PATH,
    )


def clear_xhs_session_cookie(response: Response, request: Request) -> None:
    """通知当前浏览器删除自己的会话，不影响其他客户端。"""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=_secure_cookie(request),
        samesite="lax",
        path=SESSION_COOKIE_PATH,
    )
