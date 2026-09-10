"""小红书登录挑战、状态轮询和浏览器会话交付服务。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import time
from threading import Lock, Timer
from typing import Any
from uuid import uuid4

from loguru import logger

from app.integrations.xhs.provider import (
    XHSLoginApi,
    XHSProvider,
    XHSProviderError,
    normalize_cookie,
)
from app.xhs_session import XHSClientSession, encode_xhs_session


LOGIN_TTL_SECONDS = 300
MAX_ACTIVE_LOGIN_TASKS = 12


class XHSLoginCapacityError(RuntimeError):
    """服务端同时处理的登录任务已达到上限。"""


@dataclass
class XHSLoginTask:
    """保存一次登录任务的非敏感状态和后台执行上下文。"""

    login_id: str
    method: str
    created_at: float
    expires_at: float
    state: str = "preparing"
    message: str = "正在初始化登录环境"
    qr_url: str | None = None
    user_nickname: str | None = None
    phone: str | None = None
    zone: str = "86"
    login: Any = None
    cookies: dict[str, str] | None = None
    result_session_token: str | None = None
    expiry_timer: Timer | None = None


class XHSLoginService:
    """为各浏览器提供相互隔离的三种小红书登录方式。"""

    def __init__(self) -> None:
        self._tasks: dict[str, XHSLoginTask] = {}
        self._lock = Lock()
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="xhs-login")

    def _new_task(self, method: str) -> XHSLoginTask:
        """创建短时登录任务，任务过期后不再接受状态变更。"""
        now = time.monotonic()
        task = XHSLoginTask(
            login_id=uuid4().hex,
            method=method,
            created_at=now,
            expires_at=now + LOGIN_TTL_SECONDS,
        )
        task.expiry_timer = Timer(LOGIN_TTL_SECONDS, self.cancel, args=(task.login_id,))
        task.expiry_timer.daemon = True
        with self._lock:
            self._cleanup_locked(now)
            # NOTE: 公开登录入口必须限制待处理任务总量，避免耗尽后台线程和上游连接。
            if len(self._tasks) >= MAX_ACTIVE_LOGIN_TASKS:
                raise XHSLoginCapacityError("当前登录请求较多，请稍后重试")
            self._tasks[task.login_id] = task
        # NOTE: 登录页面关闭后可能不再轮询，定时销毁保证挑战材料不会滞留在服务进程。
        task.expiry_timer.start()
        return task

    def _cleanup_locked(self, now: float) -> None:
        """清理过期任务，释放其中可能持有的上游 HTTP 客户端。"""
        for login_id, task in list(self._tasks.items()):
            if task.expires_at >= now:
                continue
            if task.login is not None:
                task.login.close()
            if task.expiry_timer is not None:
                task.expiry_timer.cancel()
            del self._tasks[login_id]

    def start_qrcode(self) -> XHSLoginTask:
        """创建二维码任务，二维码准备好后由状态接口返回地址。"""
        task = self._new_task("qrcode")
        self._executor.submit(self._run_qrcode, task.login_id)
        return task

    def start_phone(self, phone: str, zone: str) -> XHSLoginTask:
        """创建手机号任务，并在后台完成匿名设备初始化和验证码发送。"""
        task = self._new_task("phone")
        task.phone = phone
        task.zone = zone
        self._executor.submit(self._prepare_phone, task.login_id, phone, zone)
        return task

    def verify_phone(self, login_id: str, code: str) -> XHSLoginTask:
        """提交验证码并异步完成正式会话验证。"""
        task = self._get_task(login_id)
        with self._lock:
            if task.method != "phone" or task.state != "code_sent":
                raise ValueError("当前登录任务尚未准备好验证码确认")
            task.state = "authenticating"
            task.message = "正在验证手机号"
        self._executor.submit(self._run_phone_verify, login_id, code)
        return task

    def login_with_cookie(self, cookie: str) -> XHSLoginTask:
        """验证用户提交的完整 Cookie，等待路由写入当前浏览器。"""
        normalized = normalize_cookie(cookie)
        if not normalized:
            raise ValueError("Cookie 不能为空")
        try:
            with XHSProvider(cookie=normalized) as provider:
                provider.api.bootstrap()
        except XHSProviderError:
            raise
        except Exception as exc:
            raise XHSProviderError(f"Cookie 验证失败: {exc}") from exc
        session_token = encode_xhs_session(XHSClientSession(cookie=normalized))
        task = self._new_task("cookie")
        with self._lock:
            if self._tasks.get(task.login_id) is not task:
                raise XHSProviderError("Cookie 登录任务已取消")
            task.result_session_token = session_token
            task.state = "success"
            task.message = "Cookie 登录成功"
        return task

    def claim_session(self, login_id: str) -> str | None:
        """领取一次成功登录结果，避免任务继续持有可复用凭证。"""
        with self._lock:
            task = self._tasks.get(login_id)
            if task is None:
                return None
            if task.state != "success" or not task.result_session_token:
                return None
            result = task.result_session_token
            task.result_session_token = None
            self._tasks.pop(login_id, None)
            if task.expiry_timer is not None:
                task.expiry_timer.cancel()
            return result

    def cancel(self, login_id: str) -> None:
        """只取消指定浏览器正在处理的登录挑战。"""
        with self._lock:
            task = self._tasks.pop(login_id, None)
        if task is None:
            return
        if task.login is not None:
            try:
                task.login.close()
            except Exception:
                logger.warning("取消小红书登录挑战时关闭客户端失败")
        task.login = None
        task.cookies = None
        task.result_session_token = None
        if task.expiry_timer is not None:
            task.expiry_timer.cancel()

    def status(self, login_id: str) -> XHSLoginTask:
        """读取登录任务状态，过期任务按不存在处理。"""
        task = self._get_task(login_id)
        if task.expires_at < time.monotonic() and task.state not in {"success", "error"}:
            with self._lock:
                task.state = "expired"
                task.message = "登录任务已过期，请重新开始"
        return task

    def qrcode_url(self, login_id: str) -> str:
        """读取已准备好的二维码地址，未准备好时由路由返回冲突状态。"""
        task = self.status(login_id)
        if task.method != "qrcode":
            raise ValueError("当前任务不是二维码登录")
        if not task.qr_url:
            raise LookupError("二维码尚未准备好")
        return task.qr_url

    def _get_task(self, login_id: str) -> XHSLoginTask:
        """读取仍在有效期内的登录任务，不存在时抛出 LookupError。"""
        with self._lock:
            task = self._tasks.get(login_id)
        if task is None:
            raise LookupError("登录任务不存在或已过期")
        return task

    def _set_error(self, task: XHSLoginTask, message: str) -> None:
        """把上游失败转换成不包含 Cookie 的页面状态。"""
        with self._lock:
            task.state = "error"
            task.message = message
            login = task.login
            task.login = None
            task.cookies = None
            task.result_session_token = None
        if login is not None:
            login.close()

    def _finish(self, task: XHSLoginTask, login: Any, cookies: dict[str, str], user: dict[str, Any]) -> None:
        """保存待领取结果，路由写入浏览器后立即从任务中移除。"""
        nickname = str(user.get("nickname") or "")
        session_token = encode_xhs_session(
            XHSClientSession(
                cookie=login.cookies_to_str(cookies),
                user_nickname=nickname or None,
            )
        )
        with self._lock:
            # NOTE: 过期清理可能移除任务；已移除任务不得再交付登录结果。
            active = self._tasks.get(task.login_id) is task
            if active:
                task.result_session_token = session_token
                task.state = "success"
                task.message = "登录成功"
                task.user_nickname = nickname or None
                task.login = None
                task.cookies = None
        login.close()

    def _run_qrcode(self, login_id: str) -> None:
        """初始化二维码并持续轮询扫码、确认和正式会话状态。"""
        task = self._get_task(login_id)
        stage = "创建登录客户端"
        login: XHSLoginApi | None = None
        try:
            login = XHSLoginApi()
            with self._lock:
                task.login = login
            stage = "初始化匿名设备"
            cookies = login.generate_init_cookies()
            stage = "获取登录二维码"
            success, message, qr_data = login.generate_qrcode(cookies)
            if not success or not qr_data:
                raise RuntimeError(message or "二维码生成失败")
            stage = "检查二维码初始状态"
            success, message, cookies = login.check_qrcode_status(
                qr_data["qr_id"], qr_data["code"], cookies
            )
            if success or message != "请扫描二维码":
                raise RuntimeError(message or "二维码状态异常")
            stage = "验证本地指纹环境"
            login.ensure_webprofile(cookies)
            with self._lock:
                task.login = login
                task.cookies = cookies
                task.qr_url = str(qr_data["qr_url"])
                task.state = "waiting_scan"
                task.message = "请使用小红书 App 扫描二维码"

            stage = "等待扫码状态检查"
            deadline = time.monotonic() + LOGIN_TTL_SECONDS
            while time.monotonic() < deadline:
                success, message, cookies = login.check_qrcode_status(
                    qr_data["qr_id"], qr_data["code"], cookies
                )
                if success:
                    break
                with self._lock:
                    task.cookies = cookies
                    task.state = "waiting_confirm" if message == "请确认登录" else "waiting_scan"
                    task.message = message
                if message == "二维码已过期":
                    self._set_error(task, message)
                    return
                time.sleep(2)
            else:
                self._set_error(task, "等待扫码超时，请重新生成二维码")
                return

            stage = "验证正式登录状态"
            success, user, cookies = login.get_user_info(cookies)
            if not success or user.get("guest") is not False:
                raise RuntimeError("正式会话验证失败")
            self._finish(task, login, cookies, user)
        except Exception as exc:
            # NOTE: 登录失败日志不记录认证材料、手机号和上游响应正文。
            logger.error(
                "小红书二维码登录任务失败，步骤：{}，异常类型：{}",
                stage,
                type(exc).__name__,
            )
            self._set_error(task, "二维码登录失败，请重试")

    def _prepare_phone(self, login_id: str, phone: str, zone: str) -> None:
        """初始化手机号登录所需设备并发送一次验证码。"""
        task = self._get_task(login_id)
        stage = "创建登录客户端"
        login: XHSLoginApi | None = None
        try:
            login = XHSLoginApi()
            with self._lock:
                task.login = login
            stage = "初始化匿名设备"
            cookies = login.generate_init_cookies()
            stage = "验证本地指纹环境"
            login.ensure_webprofile(cookies)
            stage = "发送短信验证码"
            success, message, _ = login.send_phone_code(phone, cookies, zone=zone)
            if not success:
                raise RuntimeError(message or "验证码发送失败")
            with self._lock:
                task.login = login
                task.cookies = cookies
                task.state = "code_sent"
                task.message = "验证码已发送，请输入验证码"
        except Exception as exc:
            # NOTE: 登录失败日志不记录认证材料、手机号和上游响应正文。
            logger.error("小红书手机号登录初始化失败，异常类型：{}", type(exc).__name__)
            self._set_error(task, "验证码发送失败，请检查手机号后重试")

    def _run_phone_verify(self, login_id: str, code: str) -> None:
        """验证手机号验证码，并确认返回的是正式登录会话。"""
        task = self._get_task(login_id)
        login = task.login
        cookies = task.cookies
        if login is None or cookies is None:
            self._set_error(task, "登录任务状态已失效，请重新开始")
            return
        if not task.phone:
            self._set_error(task, "手机号登录任务缺少手机号，请重新开始")
            return
        try:
            success, message, result = login.login_by_phone(
                task.phone, code, cookies, zone=task.zone
            )
            if not success:
                raise RuntimeError(message or "验证码验证失败")
            cookies = result["cookies"]
            success, user, cookies = login.get_user_info(cookies)
            if not success or user.get("guest") is not False:
                raise RuntimeError("正式会话验证失败")
            self._finish(task, login, cookies, user)
        except Exception as exc:
            # NOTE: 登录失败日志不记录认证材料、手机号和上游响应正文。
            logger.error("小红书手机号验证码验证失败，异常类型：{}", type(exc).__name__)
            self._set_error(task, "验证码验证失败，请重试")


# NOTE: 登录挑战只保留短时状态，成功会话由对应浏览器领取后立即移除。
_LOGIN_SERVICE = XHSLoginService()


def get_xhs_login_service() -> XHSLoginService:
    """返回短时登录挑战服务，不提供跨请求共享的业务登录态。"""
    return _LOGIN_SERVICE
