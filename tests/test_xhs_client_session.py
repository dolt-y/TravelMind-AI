"""小红书浏览器隔离会话的加密和交付测试。"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.services.xhs_login import XHSLoginService
from app.xhs_session import (
    SESSION_COOKIE_NAME,
    XHSClientSession,
    XHSSessionInvalidError,
    decode_xhs_session,
    encode_xhs_session,
)
from main import app


SESSION_ENV = {
    "TRAVELMIND_SESSION_SECRET": "test-session-secret-with-at-least-32-characters",
}


class XHSClientSessionTest(unittest.TestCase):
    """验证上游认证信息仅以不可读密文保存在对应浏览器。"""

    def test_encrypted_session_round_trip_and_tamper_detection(self) -> None:
        """令牌不能暴露原始 Cookie，且任何篡改都必须失效。"""
        raw_cookie = "a1=sensitive-value; web_session=private-session"
        with patch.dict("os.environ", SESSION_ENV, clear=True):
            token = encode_xhs_session(
                XHSClientSession(cookie=raw_cookie, user_nickname="测试账号")
            )
            decoded = decode_xhs_session(token)

            self.assertNotIn("sensitive-value", token)
            self.assertEqual(decoded.cookie, raw_cookie)
            self.assertEqual(decoded.user_nickname, "测试账号")
            replacement = "A" if token[-1] != "A" else "B"
            with self.assertRaises(XHSSessionInvalidError):
                decode_xhs_session(f"{token[:-1]}{replacement}")

    def test_cookie_login_sets_httponly_session_without_returning_credentials(self) -> None:
        """Cookie 登录成功后只通过 HttpOnly 响应 Cookie 交付密文。"""
        raw_cookie = "a1=sensitive-value; web_session=private-session"
        client = TestClient(app)
        with patch.dict("os.environ", SESSION_ENV, clear=True), patch(
            "app.services.xhs_login.XHSProvider"
        ) as provider_class:
            provider_class.return_value.__enter__.return_value.api.bootstrap.return_value = None
            response = client.post(
                "/api/xhs/login/cookie",
                json={"cookie": raw_cookie},
            )

            set_cookie = response.headers.get("set-cookie", "")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["state"], "success")
            self.assertIn(f"{SESSION_COOKIE_NAME}=", set_cookie)
            self.assertIn("HttpOnly", set_cookie)
            self.assertIn("SameSite=lax", set_cookie)
            self.assertNotIn(raw_cookie, set_cookie)
            self.assertNotIn(raw_cookie, response.text)
            self.assertTrue(client.get("/api/xhs/health").json()["configured"])
        client.close()

    def test_async_login_status_delivers_session_once(self) -> None:
        """二维码和手机号成功后都应签发当前浏览器会话并销毁临时任务。"""
        raw_cookie = "a1=sensitive-value; web_session=private-session"
        for method in ("qrcode", "phone"):
            with self.subTest(method=method):
                service = XHSLoginService()
                task = service._new_task(method)
                task.state = "success"
                task.message = "登录成功"
                client = TestClient(app)
                try:
                    with patch.dict("os.environ", SESSION_ENV, clear=True):
                        task.result_session_token = encode_xhs_session(
                            XHSClientSession(cookie=raw_cookie)
                        )
                    with patch.dict("os.environ", SESSION_ENV, clear=True), patch(
                        "app.routers.xhs_login.get_xhs_login_service",
                        return_value=service,
                    ):
                        response = client.get(
                            f"/api/xhs/login/{task.login_id}/status",
                        )
                        repeated = client.get(
                            f"/api/xhs/login/{task.login_id}/status",
                        )

                    set_cookie = response.headers.get("set-cookie", "")
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(f"{SESSION_COOKIE_NAME}=", set_cookie)
                    self.assertIn("HttpOnly", set_cookie)
                    self.assertNotIn(raw_cookie, response.text)
                    self.assertEqual(repeated.status_code, 404)
                finally:
                    client.close()
                    service._executor.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    unittest.main()
