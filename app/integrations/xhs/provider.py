"""封装内置 Spider_XHS PC 客户端，向业务层提供统一的小红书只读数据。"""
from __future__ import annotations

import json
import os
import sys
from threading import Lock
from pathlib import Path
from typing import Any
from urllib.parse import quote

from dotenv import load_dotenv

from app.models.xhs import XHSNote


_VENDOR_ROOT = Path(__file__).resolve().parents[3] / "vendor" / "spider_xhs"
_PROJECT_ROOT = _VENDOR_ROOT.parents[1]
load_dotenv(_PROJECT_ROOT / ".env", override=False)
if str(_VENDOR_ROOT) not in sys.path:
    # 说明：上游客户端使用顶层 ``xhs_utils`` 导入，路径注入限制在适配层内。
    sys.path.insert(0, str(_VENDOR_ROOT))

from apis.xhs_pc_apis import XHS_Apis  # noqa: E402 - 注入路径后再导入上游客户端
from apis.xhs_pc_login_apis import XHSLoginApi  # noqa: E402 - 统一由适配层加载登录客户端
from xhs_utils.xhs_pc import XHSPcAuth  # noqa: E402 - 注入路径后再导入上游鉴权类


_RUNTIME_COOKIE = ""
_RUNTIME_COOKIE_LOCK = Lock()


def set_runtime_cookie(cookie: str) -> None:
    """保存当前进程使用的登录会话，供 Web 登录成功后的后续请求复用。"""
    global _RUNTIME_COOKIE
    with _RUNTIME_COOKIE_LOCK:
        _RUNTIME_COOKIE = normalize_cookie(cookie)


def clear_runtime_cookie() -> None:
    """清除 Web 登录产生的进程内会话，不影响 .env 配置。"""
    global _RUNTIME_COOKIE
    with _RUNTIME_COOKIE_LOCK:
        _RUNTIME_COOKIE = ""


def runtime_cookie() -> str:
    """读取当前进程会话，供健康检查和 Provider 初始化使用。"""
    with _RUNTIME_COOKIE_LOCK:
        return _RUNTIME_COOKIE


class XHSProviderError(RuntimeError):
    """可安全转换为接口错误响应的预期服务异常。"""


def normalize_cookie(value: str | list[dict[str, Any]] | dict[str, Any] | None) -> str:
    """将请求头字符串或浏览器导出的 Cookie 数据统一为请求头字符串。"""
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        items = value if isinstance(value, list) else [value]
        pairs = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if name:
                pairs.append(f"{name}={str(item.get('value', ''))}")
        return "; ".join(pairs)

    normalized = str(value).strip()
    if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {"'", '"'}:
        normalized = normalized[1:-1].strip()
    if normalized.startswith(("[", "{")):
        try:
            return normalize_cookie(json.loads(normalized))
        except json.JSONDecodeError:
            pass
    return normalized


def cookie_from_environment() -> str:
    """优先读取 Web 登录会话，否则读取环境变量中的 Cookie。"""
    return runtime_cookie() or normalize_cookie(
        os.getenv("TRAVELMIND_XHS_COOKIE") or os.getenv("XHS_COOKIE") or os.getenv("COOKIES")
    )


def _first_image_urls(note_card: dict[str, Any]) -> list[str]:
    """从笔记卡片的多种图片字段中提取不重复的图片地址。"""
    urls: list[str] = []
    for image in note_card.get("image_list") or []:
        if not isinstance(image, dict):
            continue
        info_list = image.get("info_list") or []
        candidates = [item.get("url") for item in info_list if isinstance(item, dict)]
        candidates.extend(
            image.get(key) for key in ("url_default", "url_pre", "url") if image.get(key)
        )
        for url in candidates:
            if url and url not in urls:
                urls.append(str(url))
    return urls


def _note_from_item(item: dict[str, Any], *, source: str = "pc_search") -> XHSNote:
    """将搜索或详情响应中的笔记卡片转换为 XHSNote。"""
    note_card = item.get("note_card") or item.get("noteCard") or {}
    note_id = str(item.get("id") or item.get("note_id") or note_card.get("note_id") or "")
    token = str(item.get("xsec_token") or note_card.get("xsec_token") or "")
    source_url = str(item.get("url") or "")
    if not source_url and note_id:
        source_url = f"https://www.xiaohongshu.com/explore/{quote(note_id)}"
    interaction = note_card.get("interact_info") or {}
    user = note_card.get("user") or {}
    return XHSNote(
        note_id=note_id,
        title=str(note_card.get("display_title") or note_card.get("title") or ""),
        content=str(note_card.get("desc") or ""),
        source_url=source_url,
        xsec_token=token,
        xsec_source=source,
        images=_first_image_urls(note_card),
        author=str(user.get("nickname") or ""),
        liked_count=int(interaction.get("liked_count") or 0),
    )


class XHSProvider:
    """对 Spider_XHS PC API 客户端提供鉴权、搜索和详情读取封装。"""

    def __init__(self, cookie: str | None = None, proxies: dict[str, str] | None = None):
        """使用传入或环境变量中的 Cookie 初始化小红书客户端。"""
        self.cookie = normalize_cookie(cookie) if cookie is not None else cookie_from_environment()
        if not self.cookie:
            raise XHSProviderError(
                "XHS Cookie 未配置，请设置 TRAVELMIND_XHS_COOKIE 或 XHS_COOKIE"
            )
        try:
            self.auth = XHSPcAuth.from_cookie(self.cookie, proxies=proxies)
            self.api = XHS_Apis(self.auth)
        except Exception as exc:
            raise XHSProviderError(f"初始化小红书客户端失败: {exc}") from exc

    def search_notes(
        self,
        keyword: str,
        *,
        limit: int = 10,
        sort_type: int = 0,
        proxies: dict[str, str] | None = None,
    ) -> list[XHSNote]:
        """按关键词搜索笔记，并将上游结果转换为稳定的 XHSNote 列表。

        ``limit`` 控制上游返回数量，``sort_type`` 控制搜索排序方式。
        """
        if not str(keyword).strip():
            raise XHSProviderError("搜索关键词不能为空")
        if limit < 1 or limit > 50:
            raise XHSProviderError("搜索数量必须在 1 到 50 之间")
        try:
            success, message, items = self.api.search_some_note(
                str(keyword).strip(), limit, sort_type_choice=sort_type, proxies=proxies
            )
        except Exception as exc:
            raise XHSProviderError(f"小红书搜索请求失败: {exc}") from exc
        if not success:
            raise XHSProviderError(f"小红书搜索失败: {message}")
        return [_note_from_item(item) for item in (items or []) if isinstance(item, dict)]

    def get_note(
        self,
        note_id: str,
        *,
        xsec_token: str = "",
        xsec_source: str = "pc_search",
        proxies: dict[str, str] | None = None,
    ) -> XHSNote:
        """根据笔记 ID 和详情令牌读取完整笔记内容，并转换为 XHSNote。"""
        if not str(note_id).strip():
            raise XHSProviderError("note_id 不能为空")
        query = f"?xsec_source={quote(xsec_source)}&xsec_token={quote(xsec_token)}"
        url = f"https://www.xiaohongshu.com/explore/{quote(str(note_id))}{query}"
        try:
            success, message, response = self.api.get_note_info(url, proxies=proxies)
        except Exception as exc:
            raise XHSProviderError(f"小红书详情请求失败: {exc}") from exc
        if not success:
            raise XHSProviderError(f"小红书详情获取失败: {message}")
        items = ((response or {}).get("data") or {}).get("items") or []
        if not items or not isinstance(items[0], dict):
            raise XHSProviderError("小红书详情响应中没有笔记数据")
        return _note_from_item(items[0], source=xsec_source)

    def close(self) -> None:
        """释放 Spider_XHS 鉴权客户端占用的运行时资源。"""
        self.auth.close()

    def __enter__(self) -> "XHSProvider":
        """返回可用于 with 语句的客户端实例。"""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """离开 with 语句时关闭客户端资源。"""
        self.close()
