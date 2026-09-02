"""提供内部管理接口使用的轻量鉴权边界。"""

from __future__ import annotations

from hmac import compare_digest
import os
from typing import Annotated

from fastapi import Header, HTTPException, status


ADMIN_KEY_ENV = "TRAVELMIND_ADMIN_KEY"
ADMIN_KEY_HEADER = "X-TravelMind-Admin-Key"


def require_admin_key(
    supplied_key: Annotated[str | None, Header(alias=ADMIN_KEY_HEADER)] = None,
) -> None:
    """仅允许持有服务端管理员密钥的请求进入内部集成管理接口。"""
    configured_key = os.getenv(ADMIN_KEY_ENV, "").strip()
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="内部管理能力尚未配置",
        )
    # NOTE: 管理密钥只用于保护系统内容账号，不能复用为普通用户身份凭证。
    if not supplied_key or not compare_digest(supplied_key, configured_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员身份验证失败",
            headers={"WWW-Authenticate": "TravelMindAdminKey"},
        )
