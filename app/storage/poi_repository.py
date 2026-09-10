"""POI 搜索结果和景点图片的 SQLite 持久化。"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from typing import Iterable

from app.models.poi import POI, POILocation

from .xhs_repository import database_path


class POIRepositoryError(RuntimeError):
    """POI 持久化操作失败。"""


class POIRepository:
    """在与小红书相同的 SQLite 文件中保存 POI 数据。"""

    def __init__(self, path: str | Path | None = None):
        """配置 POI 持久化使用的 SQLite 文件并创建所需数据表。"""
        self.path = Path(path) if path else database_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise POIRepositoryError(f"无法创建 POI 数据目录: {self.path.parent}") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """打开启用外键的 SQLite 连接。"""
        try:
            connection = sqlite3.connect(self.path, timeout=10)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except sqlite3.Error as exc:
            raise POIRepositoryError("无法打开 POI 数据文件") from exc

    def _initialize(self) -> None:
        """创建 POI 结果和图片缓存表。"""
        try:
            with self._connect() as connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS poi_records (
                        provider TEXT NOT NULL,
                        poi_id TEXT NOT NULL,
                        keywords TEXT NOT NULL DEFAULT '',
                        city TEXT NOT NULL DEFAULT '',
                        name TEXT NOT NULL,
                        type TEXT NOT NULL DEFAULT '',
                        address TEXT NOT NULL DEFAULT '',
                        longitude REAL NOT NULL,
                        latitude REAL NOT NULL,
                        tel TEXT,
                        rating REAL,
                        photos_json TEXT NOT NULL DEFAULT '[]',
                        fetched_at TEXT NOT NULL,
                        PRIMARY KEY (provider, poi_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_poi_records_city_name
                        ON poi_records(city, name);
                    CREATE TABLE IF NOT EXISTS poi_photos (
                        name TEXT NOT NULL,
                        city TEXT NOT NULL DEFAULT '',
                        photo_url TEXT NOT NULL DEFAULT '',
                        fetched_at TEXT NOT NULL,
                        PRIMARY KEY (name, city)
                    );
                    """
                )
        except sqlite3.Error as exc:
            raise POIRepositoryError("初始化 POI 数据表失败") from exc

    def save_search(self, pois: Iterable[POI], *, keywords: str, city: str) -> None:
        """批量保存 POI 搜索结果，同一供应商和 ID 使用最新数据更新。"""
        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as connection:
                for poi in pois:
                    connection.execute(
                        """
                        INSERT INTO poi_records (
                            provider, poi_id, keywords, city, name, type, address,
                            longitude, latitude, tel, rating, photos_json, fetched_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(provider, poi_id) DO UPDATE SET
                            keywords = excluded.keywords,
                            city = excluded.city,
                            name = excluded.name,
                            type = excluded.type,
                            address = excluded.address,
                            longitude = excluded.longitude,
                            latitude = excluded.latitude,
                            tel = excluded.tel,
                            rating = excluded.rating,
                            photos_json = excluded.photos_json,
                            fetched_at = excluded.fetched_at
                        """,
                        (
                            "amap",
                            poi.id,
                            keywords,
                            city,
                            poi.name,
                            poi.type,
                            poi.address,
                            poi.location.longitude,
                            poi.location.latitude,
                            poi.tel,
                            poi.rating,
                            json.dumps(poi.photos, ensure_ascii=False),
                            fetched_at,
                        ),
                    )
        except sqlite3.Error as exc:
            raise POIRepositoryError("保存 POI 搜索结果失败") from exc

    def get_poi(self, poi_id: str) -> POI | None:
        """按 POI ID 读取已保存的高德结果。"""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM poi_records WHERE provider = 'amap' AND poi_id = ?",
                    (poi_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise POIRepositoryError("读取 POI 详情失败") from exc
        if row is None:
            return None
        try:
            photos = json.loads(row["photos_json"])
            if not isinstance(photos, list):
                raise ValueError("photos_json 不是数组")
            return POI(
                id=row["poi_id"],
                name=row["name"],
                type=row["type"],
                address=row["address"],
                location=POILocation(longitude=row["longitude"], latitude=row["latitude"]),
                tel=row["tel"],
                city=row["city"],
                rating=row["rating"],
                photos=photos,
            )
        except (TypeError, ValueError) as exc:
            raise POIRepositoryError("已保存的 POI 数据格式无效") from exc

    def get_photo(self, name: str, city: str) -> str | None:
        """读取景点图片缓存；空字符串也视为已缓存的查询结果。"""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT photo_url FROM poi_photos WHERE name = ? AND city = ?",
                    (name, city),
                ).fetchone()
        except sqlite3.Error as exc:
            raise POIRepositoryError("读取景点图片缓存失败") from exc
        return None if row is None else row["photo_url"]

    def save_photo(self, name: str, city: str, photo_url: str) -> None:
        """保存景点图片地址，包括未找到图片时的空结果。"""
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO poi_photos (name, city, photo_url, fetched_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(name, city) DO UPDATE SET
                        photo_url = excluded.photo_url,
                        fetched_at = excluded.fetched_at
                    """,
                    (name, city, photo_url, datetime.now(timezone.utc).isoformat()),
                )
        except sqlite3.Error as exc:
            raise POIRepositoryError("保存景点图片缓存失败") from exc
