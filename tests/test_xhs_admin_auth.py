"""小红书系统账号管理接口的权限边界测试。"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.integrations.xhs import provider as xhs_provider
from app.security import ADMIN_KEY_HEADER
from main import app


class XHSAdminAuthTest(unittest.TestCase):
    """验证普通用户无法访问系统内容账号的登录能力。"""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_admin_routes_are_disabled_without_server_key(self) -> None:
        """服务端未配置管理密钥时不能意外开放登录入口。"""
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.get("/api/admin/integrations/xhs/methods")

        self.assertEqual(response.status_code, 503)

    def test_admin_routes_reject_missing_or_wrong_key(self) -> None:
        """缺少或错误的密钥都不能读取内部登录能力。"""
        with patch.dict("os.environ", {"TRAVELMIND_ADMIN_KEY": "admin-secret"}, clear=True):
            missing = self.client.get("/api/admin/integrations/xhs/methods")
            wrong = self.client.get(
                "/api/admin/integrations/xhs/methods",
                headers={ADMIN_KEY_HEADER: "wrong-secret"},
            )

        self.assertEqual(missing.status_code, 401)
        self.assertEqual(wrong.status_code, 401)

    def test_admin_routes_accept_configured_key(self) -> None:
        """管理员通过验证后可以维护系统内容账号。"""
        with patch.dict("os.environ", {"TRAVELMIND_ADMIN_KEY": "admin-secret"}, clear=True):
            response = self.client.get(
                "/api/admin/integrations/xhs/methods",
                headers={ADMIN_KEY_HEADER: "admin-secret"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["methods"], ["cookie", "qrcode", "phone"])

    def test_legacy_public_login_route_is_removed(self) -> None:
        """旧公共地址必须消失，避免绕过管理员鉴权。"""
        response = self.client.get("/api/xhs/login/methods")

        self.assertEqual(response.status_code, 404)

    def test_admin_can_clear_runtime_session_and_disable_environment_fallback(self) -> None:
        """管理员退出后，本进程不能继续使用环境变量中的旧 Cookie。"""
        with patch.dict(
            "os.environ",
            {
                "TRAVELMIND_ADMIN_KEY": "admin-secret",
                "TRAVELMIND_XHS_COOKIE": "a1=environment-cookie",
            },
            clear=True,
        ), patch.object(xhs_provider, "_RUNTIME_COOKIE", None):
            self.assertEqual(xhs_provider.cookie_from_environment(), "a1=environment-cookie")
            response = self.client.delete(
                "/api/admin/integrations/xhs/session",
                headers={ADMIN_KEY_HEADER: "admin-secret"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["success"])
            self.assertEqual(xhs_provider.cookie_from_environment(), "")


if __name__ == "__main__":
    unittest.main()
