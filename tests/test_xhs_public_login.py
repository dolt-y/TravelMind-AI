"""小红书公开客户端登录接口的边界测试。"""

from __future__ import annotations

import time
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.routers import xhs_login as login_router
from app.services.xhs_login import XHSLoginCapacityError, XHSLoginTask
from app.xhs_session import SESSION_COOKIE_NAME, XHSClientSession, encode_xhs_session
from main import app


SESSION_ENV = {
    "TRAVELMIND_SESSION_SECRET": "test-session-secret-with-at-least-32-characters",
}


class XHSPublicLoginTest(unittest.TestCase):
    """验证每个访问者都可登录，同时限制公开入口的资源消耗。"""

    def setUp(self) -> None:
        with login_router._login_attempts_lock:
            login_router._login_attempts.clear()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        with login_router._login_attempts_lock:
            login_router._login_attempts.clear()

    def test_login_methods_are_public(self) -> None:
        """登录方式无需管理员密钥即可读取。"""
        response = self.client.get("/api/xhs/login/methods")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["methods"], ["cookie", "qrcode", "phone"])

    def test_legacy_admin_route_is_removed(self) -> None:
        """旧管理员地址不再提供登录能力。"""
        response = self.client.get("/api/admin/integrations/xhs/methods")

        self.assertEqual(response.status_code, 404)

    def test_login_challenge_requires_session_encryption(self) -> None:
        """服务端不能在缺少会话加密密钥时创建登录挑战。"""
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.post("/api/xhs/login/qrcode/start")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "客户端会话能力尚未配置")

    def test_login_creation_is_rate_limited_per_client(self) -> None:
        """单个客户端一分钟内不能无限创建登录任务。"""
        now = time.monotonic()
        task = XHSLoginTask(
            login_id="public-login-task",
            method="qrcode",
            created_at=now,
            expires_at=now + 300,
        )
        service = Mock()
        service.start_qrcode.return_value = task

        with patch.dict("os.environ", SESSION_ENV, clear=True), patch(
            "app.routers.xhs_login.get_xhs_login_service",
            return_value=service,
        ):
            responses = [
                self.client.post("/api/xhs/login/qrcode/start")
                for _ in range(login_router.LOGIN_RATE_LIMIT)
            ]
            rejected = self.client.post("/api/xhs/login/qrcode/start")

        self.assertTrue(all(response.status_code == 200 for response in responses))
        self.assertEqual(rejected.status_code, 429)
        self.assertIn("Retry-After", rejected.headers)

    def test_capacity_error_returns_retryable_response(self) -> None:
        """全局任务达到上限时返回明确的限流状态。"""
        service = Mock()
        service.start_qrcode.side_effect = XHSLoginCapacityError(
            "当前登录请求较多，请稍后重试"
        )

        with patch.dict("os.environ", SESSION_ENV, clear=True), patch(
            "app.routers.xhs_login.get_xhs_login_service",
            return_value=service,
        ):
            response = self.client.post("/api/xhs/login/qrcode/start")

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "30")

    def test_logout_only_clears_current_browser_session(self) -> None:
        """退出只删除当前浏览器的加密会话，不影响其他客户端。"""
        other_client = TestClient(app)
        try:
            with patch.dict("os.environ", SESSION_ENV, clear=True):
                self.client.cookies.set(
                    SESSION_COOKIE_NAME,
                    encode_xhs_session(XHSClientSession(cookie="a1=first-browser")),
                    domain="testserver.local",
                    path="/api",
                )
                other_client.cookies.set(
                    SESSION_COOKIE_NAME,
                    encode_xhs_session(XHSClientSession(cookie="a1=second-browser")),
                    domain="testserver.local",
                    path="/api",
                )
                response = self.client.delete("/api/xhs/login/session")

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["success"])
                self.assertFalse(
                    self.client.get("/api/xhs/health").json()["configured"]
                )
                self.assertTrue(
                    other_client.get("/api/xhs/health").json()["configured"]
                )
        finally:
            other_client.close()


if __name__ == "__main__":
    unittest.main()
