"""封装 OpenAI-compatible Chat Completions，提供景点提取所需的文本和 JSON 解析。"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


class LLMServiceError(RuntimeError):
    """LLM 配置、网络请求或响应格式异常。"""


def _first_environment(*names: str) -> str:
    """按给定顺序读取第一个非空环境变量。"""
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


class LLMService:
    """调用 OpenAI-compatible Chat Completions 接口，并隐藏鉴权细节。"""

    def __init__(self) -> None:
        """从环境变量加载密钥、服务地址、模型和超时配置。"""
        self.api_key = _first_environment("LLM_API_KEY", "OPENAI_API_KEY")
        if not self.api_key:
            raise LLMServiceError(
                "LLM 未配置，请设置 LLM_API_KEY 或 OPENAI_API_KEY"
            )
        self.base_url = (
            _first_environment("LLM_BASE_URL", "OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.model = _first_environment("LLM_MODEL_ID", "OPENAI_MODEL") or "gpt-4o-mini"
        timeout = _first_environment("LLM_TIMEOUT") or "60"
        try:
            timeout_seconds = max(1, int(timeout))
        except ValueError as exc:
            raise LLMServiceError("LLM_TIMEOUT 必须是正整数") from exc
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout_seconds,
            http_client=httpx.Client(timeout=timeout_seconds, trust_env=False),
        )

    def complete(self, prompt: str) -> str:
        """提交景点提取提示词并返回模型文本，不记录密钥或原始请求头。"""
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是旅行内容整理助手，只输出用户要求的 JSON。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content or ""
        except Exception as exc:
            raise LLMServiceError("LLM 请求失败，请检查服务地址、模型和网络配置") from exc
        if not content.strip():
            raise LLMServiceError("LLM 返回内容为空")
        return content


def parse_json_payload(content: str) -> list[dict[str, Any]]:
    """从纯 JSON、代码块或带少量说明的模型文本中提取对象数组。"""
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    decoder = json.JSONDecoder()

    candidates = [text]
    array_start = text.find("[")
    if array_start >= 0:
        candidates.append(text[array_start:])
    for candidate in candidates:
        try:
            value, _ = decoder.raw_decode(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict) and isinstance(value.get("attractions"), list):
            return [item for item in value["attractions"] if isinstance(item, dict)]
    raise LLMServiceError("LLM 返回内容不是有效的景点 JSON 数组")
