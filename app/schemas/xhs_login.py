"""小红书登录页面使用的请求和响应模型。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


LoginMethod = Literal["cookie", "qrcode", "phone"]
LoginState = Literal[
    "preparing",
    "waiting_scan",
    "waiting_confirm",
    "code_sent",
    "authenticating",
    "success",
    "expired",
    "error",
]


class XHSLoginMethodsResponse(BaseModel):
    """返回登录页面可展示的登录方式。"""

    methods: list[LoginMethod]


class XHSLoginStartResponse(BaseModel):
    """返回异步登录任务标识，不返回登录凭证。"""

    login_id: str
    method: LoginMethod
    state: LoginState
    message: str
    expires_in: int


class XHSLoginStatusResponse(BaseModel):
    """返回二维码或验证码任务的当前状态。"""

    login_id: str
    method: LoginMethod
    state: LoginState
    message: str
    qr_url: str | None = None
    user_nickname: str | None = None


class XHSPhoneLoginStartRequest(BaseModel):
    """提交手机号以初始化验证码登录任务。"""

    phone: str = Field(min_length=6, max_length=20)
    zone: str = Field(default="86", min_length=1, max_length=6)


class XHSPhoneLoginVerifyRequest(BaseModel):
    """提交手机号验证码以完成登录。"""

    login_id: str = Field(min_length=8, max_length=80)
    code: str = Field(min_length=4, max_length=12)


class XHSCookieLoginRequest(BaseModel):
    """提交完整 Cookie，仅用于服务端验证和建立运行会话。"""

    cookie: str = Field(min_length=8, max_length=20000)
