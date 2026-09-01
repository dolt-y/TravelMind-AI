"""Spider_XHS PC 登录所需的设备标识生成工具。"""

from __future__ import annotations

import binascii
import hashlib
import random
import time


_A1_CHARSET = "abcdefghijklmnopqrstuvwxyz1234567890"


def generate_a1() -> str:
    """生成小红书 PC 登录使用的 a1 设备标识。"""
    timestamp = hex(int(time.time() * 1000))[2:]
    random_part = "".join(random.choices(_A1_CHARSET, k=30))
    payload = timestamp + random_part + "5" + "0" + "000"
    checksum = binascii.crc32(payload.encode()) & 0xFFFFFFFF
    return (payload + str(checksum))[:52]


def generate_web_id(a1: str) -> str:
    """根据 a1 生成 PC 会话使用的 webId。"""
    return hashlib.md5(a1.encode()).hexdigest()
