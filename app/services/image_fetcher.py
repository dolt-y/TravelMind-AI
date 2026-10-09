"""导出文档使用的景点图片下载与缩略图处理。"""

from __future__ import annotations

import io
from functools import lru_cache

import httpx
from loguru import logger
from PIL import Image, ImageOps, UnidentifiedImageError

THUMBNAIL_SIZE = (480, 360)
MAX_IMAGE_BYTES = 4 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 5.0
_ALLOWED_CONTENT_TYPES = (
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
)
_USER_AGENT = "TravelMind-AI/0.1 (itinerary export)"


def _download(url: str) -> bytes | None:
    """流式下载图片，超出大小上限或类型不符时放弃。"""
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, trust_env=False, follow_redirects=True) as client:
            with client.stream("GET", url, headers={"User-Agent": _USER_AGENT}) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
                if content_type and content_type not in _ALLOWED_CONTENT_TYPES:
                    logger.info("景点图片类型不受支持，已跳过：{}（{}）", url, content_type)
                    return None
                buffer = bytearray()
                for chunk in response.iter_bytes():
                    buffer.extend(chunk)
                    if len(buffer) > MAX_IMAGE_BYTES:
                        logger.info("景点图片体积超出上限，已跳过：{}", url)
                        return None
                return bytes(buffer)
    except httpx.HTTPError as exc:
        logger.info("景点图片下载失败，已跳过：{}（{}）", url, exc)
        return None


def _to_thumbnail(payload: bytes) -> bytes | None:
    """把任意尺寸图片裁剪并缩放为统一比例的 JPEG 缩略图。"""
    try:
        with Image.open(io.BytesIO(payload)) as image:
            normalized = ImageOps.exif_transpose(image) or image
            cropped = ImageOps.fit(
                normalized.convert("RGB"),
                THUMBNAIL_SIZE,
                method=Image.Resampling.LANCZOS,
            )
            output = io.BytesIO()
            cropped.save(output, format="JPEG", quality=82, optimize=True)
            return output.getvalue()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        logger.info("景点图片无法解析，已跳过（{}）", exc)
        return None


@lru_cache(maxsize=128)
def fetch_attraction_image(url: str) -> bytes | None:
    """返回景点缩略图字节；地址无效、下载失败或解析失败时返回 None。"""
    if not url or not url.startswith(("http://", "https://")):
        return None
    payload = _download(url)
    if payload is None:
        return None
    return _to_thumbnail(payload)
