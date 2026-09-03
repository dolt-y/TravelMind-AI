"""小红书系统账号登录态错误的 REST 边界测试。"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.integrations.xhs import XHSAuthenticationRequiredError, XHSProvider
from app.services.attraction_extractor import AttractionExtractionError
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
        with patch.dict("os.environ", {}, clear=True), patch(
            "app.integrations.xhs.provider.runtime_cookie", return_value=""
        ):
            for method, path, payload in requests:
                with self.subTest(path=path):
                    response = self.client.request(method, path, json=payload)

                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.json()["detail"]["code"], "XHS_AUTH_REQUIRED")
                    self.assertNotIn("Cookie", response.text)

    def test_regular_extraction_failure_remains_bad_gateway(self) -> None:
        """普通上游失败不能误导前端进入系统账号管理页。"""
        with patch(
            "app.routers.xhs.extract_attractions_with_metadata",
            side_effect=AttractionExtractionError("小红书网络请求失败"),
        ):
            response = self.client.post(
                "/api/xhs/attractions",
                json={"city": "深圳", "keywords": "美食", "language": "zh", "note_limit": 1},
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "小红书网络请求失败")

    def test_expired_upstream_session_is_authentication_required(self) -> None:
        """上游明确返回登录过期时必须保留登录态错误类型。"""
        provider = object.__new__(XHSProvider)
        provider.api = unittest.mock.Mock()
        provider.api.search_some_note.return_value = (False, "登录已过期", [])

        with self.assertRaises(XHSAuthenticationRequiredError):
            provider.search_notes("深圳旅行", limit=1)


if __name__ == "__main__":
    unittest.main()
