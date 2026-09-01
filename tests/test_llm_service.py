"""大模型调用配置和百炼深度思考开关测试。"""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services.llm_service import LLMService, LLMServiceError


class LLMServiceTest(unittest.TestCase):
    """验证景点结构化提取不会被深度思考无意拖慢。"""

    def _service(self, base_url: str, thinking: str = "false") -> tuple[LLMService, Mock]:
        """使用假 OpenAI 客户端构造指定服务地址的 LLM 服务。"""
        completions = Mock()
        completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="[]"))]
        )
        client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
        environment = {
            "LLM_API_KEY": "test-key",
            "LLM_BASE_URL": base_url,
            "LLM_MODEL_ID": "test-model",
            "LLM_TIMEOUT": "180",
            "LLM_ENABLE_THINKING": thinking,
        }
        with patch.dict("os.environ", environment, clear=True), patch(
            "app.services.llm_service.OpenAI", return_value=client
        ):
            service = LLMService()
        return service, completions

    def test_dashscope_disables_thinking_by_default(self) -> None:
        """百炼景点提取请求应显式关闭深度思考。"""
        service, completions = self._service(
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        self.assertEqual(service.complete("test"), "[]")
        self.assertEqual(
            completions.create.call_args.kwargs["extra_body"],
            {"enable_thinking": False},
        )

    def test_other_provider_does_not_receive_dashscope_option(self) -> None:
        """其他兼容服务不应收到百炼专用请求字段。"""
        service, completions = self._service("https://api.openai.com/v1")

        service.complete("test")

        self.assertNotIn("extra_body", completions.create.call_args.kwargs)

    def test_invalid_thinking_option_is_rejected(self) -> None:
        """错误的开关值应在发送请求前提示配置问题。"""
        with patch.dict(
            "os.environ",
            {
                "LLM_API_KEY": "test-key",
                "LLM_ENABLE_THINKING": "yes",
            },
            clear=True,
        ):
            with self.assertRaisesRegex(LLMServiceError, "只能设置为 true 或 false"):
                LLMService()


if __name__ == "__main__":
    unittest.main()
