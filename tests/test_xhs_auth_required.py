"""小红书系统账号登录态错误的 REST 边界测试。"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.integrations.xhs import XHSAuthenticationRequiredError, XHSProvider
from app.services.attraction_extractor import AttractionExtractionError
from app.xhs_session import SESSION_COOKIE_NAME, XHSClientSession, encode_xhs_session
from main import app


class XHSAuthenticationRequiredBoundaryTest(unittest.TestCase):
    """验证缺少系统账号登录态时前端可依赖稳定错误码。"""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_xhs_content_routes_return_auth_required_without_cookie(self) -> None:
        """所有实时小红书内容入口都应返回相同的登录提示。"""
        requests = (
            ("post", "/api/xhs/search", {"keyword": "深圳旅行", "limit": 1}),
            ("get", "/api/xhs/notes/example-note", None),
            (
                "post",
                "/api/xhs/attractions",
                {"city": "深圳", "keywords": "美食", "language": "zh", "note_limit": 1},
            ),
        )
        self.client.cookies.clear()
        with patch.dict("os.environ", {}, clear=True):
            for method, path, payload in requests:
                with self.subTest(path=path):
                    response = self.client.request(method, path, json=payload)

                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.json()["detail"]["code"], "XHS_AUTH_REQUIRED")
                    self.assertNotIn("Cookie", response.text)

    def test_regular_extraction_failure_remains_bad_gateway(self) -> None:
        """普通上游失败不能误导前端进入系统账号管理页。"""
        with patch.dict(
            "os.environ",
            {"TRAVELMIND_SESSION_SECRET": "test-session-secret-with-at-least-32-characters"},
            clear=True,
        ), patch(
            "app.routers.xhs.extract_attractions_with_metadata",
            side_effect=AttractionExtractionError("小红书网络请求失败"),
        ):
            self.client.cookies.set(
                SESSION_COOKIE_NAME,
                encode_xhs_session(
                    XHSClientSession(
                        cookie="a1=valid-client-cookie; web_session=valid-client-session"
                    )
                ),
                path="/api",
            )
            response = self.client.post(
                "/api/xhs/attractions",
                json={"city": "深圳", "keywords": "美食", "language": "zh", "note_limit": 1},
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "小红书网络请求失败")

    def test_trip_submission_requires_current_browser_session(self) -> None:
        """完整规划不能借用其他客户端或服务环境中的小红书登录态。"""
        self.client.cookies.clear()
        response = self.client.post(
            "/api/trip/plan",
            json={
                "city": "深圳",
                "start_date": "2026-10-01",
                "end_date": "2026-10-02",
            },
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "XHS_AUTH_REQUIRED")

    def test_provider_never_falls_back_to_environment_cookie(self) -> None:
        """业务 Provider 必须由当前请求显式提供 Cookie。"""
        with patch.dict(
            "os.environ",
            {"TRAVELMIND_XHS_COOKIE": "a1=legacy-environment-cookie"},
            clear=True,
        ):
            with self.assertRaises(XHSAuthenticationRequiredError):
                XHSProvider()

    def test_expired_upstream_session_is_authentication_required(self) -> None:
        """上游明确返回登录过期时必须保留登录态错误类型。"""
        provider = object.__new__(XHSProvider)
        provider.api = unittest.mock.Mock()
        provider.api.search_some_note.return_value = (False, "登录已过期", [])

        with self.assertRaises(XHSAuthenticationRequiredError):
            provider.search_notes("深圳旅行", limit=1)

    def test_poi_photo_preserves_expired_session_error(self) -> None:
        """景点图片查询遇到上游登录过期时应引导当前浏览器重新登录。"""
        with patch.dict(
            "os.environ",
            {"TRAVELMIND_SESSION_SECRET": "test-session-secret-with-at-least-32-characters"},
            clear=True,
        ), patch(
            "app.services.poi_service.POIService.photo",
            side_effect=XHSAuthenticationRequiredError("小红书系统账号登录已失效"),
        ):
            self.client.cookies.set(
                SESSION_COOKIE_NAME,
                encode_xhs_session(XHSClientSession(cookie="a1=expired-client-cookie")),
                path="/api",
            )
            response = self.client.get(
                "/api/poi/photo",
                params={"name": "世界之窗", "city": "深圳"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "XHS_AUTH_REQUIRED")


if __name__ == "__main__":
    unittest.main()
