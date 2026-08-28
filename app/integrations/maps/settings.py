"""地图供应商运行配置。"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


_PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_PROJECT_ROOT / ".env", override=False)


def amap_api_key() -> str:
    """按兼容顺序读取后端使用的高德 Web 服务 Key。"""
    return (
        os.getenv("AMAP_API_KEY", "").strip()
        or os.getenv("AMAP_MAPS_API_KEY", "").strip()
        or os.getenv("VITE_AMAP_WEB_KEY", "").strip()
    )
