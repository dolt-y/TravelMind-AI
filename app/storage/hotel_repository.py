"""酒店搜索条件和结果的 SQLite 缓存。"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.models.hotel import Hotel, HotelSearchCriteria
from app.models.poi import POILocation

from .xhs_repository import database_path


class HotelRepositoryError(RuntimeError):
    """酒店搜索缓存读取或写入失败。"""


def _query_key(provider: str, criteria: HotelSearchCriteria) -> str:
    """生成包含全部业务条件的稳定缓存键。"""
    payload = {
        "provider": provider,
        **criteria.model_dump(mode="json"),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class HotelRepository:
    """在统一 SQLite 数据文件中保存酒店查询和标准化结果。"""

    def __init__(self, path: str | Path | None = None):
        """初始化酒店缓存表；未传路径时使用统一数据文件。"""
        self.path = Path(path) if path else database_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise HotelRepositoryError("无法创建酒店缓存目录") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """打开启用外键的 SQLite 连接。"""
        try:
            connection = sqlite3.connect(self.path, timeout=10)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except sqlite3.Error as exc:
            raise HotelRepositoryError("无法打开酒店缓存数据文件") from exc

    def _initialize(self) -> None:
        """创建酒店查询、结果和城市查询索引。"""
        try:
            with self._connect() as connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS hotel_searches (
                        query_key TEXT PRIMARY KEY,
                        provider TEXT NOT NULL,
                        city TEXT NOT NULL,
                        accommodation TEXT NOT NULL DEFAULT '',
                        area TEXT NOT NULL DEFAULT '',
                        budget_min REAL,
                        budget_max REAL,
                        result_limit INTEGER NOT NULL,
                        fetched_at TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_hotel_searches_city_fetched
                        ON hotel_searches(city, fetched_at DESC);
                    CREATE TABLE IF NOT EXISTS hotel_search_results (
                        query_key TEXT NOT NULL,
                        position INTEGER NOT NULL,
                        provider TEXT NOT NULL,
                        hotel_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        city TEXT NOT NULL DEFAULT '',
                        address TEXT,
                        longitude REAL,
                        latitude REAL,
                        type TEXT,
                        rating REAL,
                        average_price REAL,
                        price_range TEXT,
                        tel TEXT,
                        photos_json TEXT NOT NULL DEFAULT '[]',
                        PRIMARY KEY (query_key, provider, hotel_id),
                        FOREIGN KEY (query_key) REFERENCES hotel_searches(query_key)
                            ON DELETE CASCADE
                    );
                    """
                )
        except sqlite3.Error as exc:
            raise HotelRepositoryError("初始化酒店缓存表失败") from exc

    def get_search(
        self,
        *,
        provider: str,
        criteria: HotelSearchCriteria,
        max_age_seconds: int,
    ) -> list[Hotel] | None:
        """读取有效酒店缓存；没有缓存返回 None，空列表表示已缓存无结果。"""
        query_key = _query_key(provider, criteria)
        try:
            with self._connect() as connection:
                search = connection.execute(
                    "SELECT fetched_at FROM hotel_searches WHERE query_key = ?",
                    (query_key,),
                ).fetchone()
                if search is None:
                    return None
                fetched_at = datetime.fromisoformat(search["fetched_at"])
                age = (datetime.now(timezone.utc) - fetched_at).total_seconds()
                if age > max_age_seconds:
                    return None
                rows = connection.execute(
                    """
                    SELECT * FROM hotel_search_results
                    WHERE query_key = ? ORDER BY position ASC
                    """,
                    (query_key,),
                ).fetchall()
        except (sqlite3.Error, TypeError, ValueError) as exc:
            raise HotelRepositoryError("读取酒店搜索缓存失败") from exc

        result: list[Hotel] = []
        try:
            for row in rows:
                photos = json.loads(row["photos_json"])
                if not isinstance(photos, list):
                    raise ValueError("酒店图片缓存不是数组")
                location = None
                if row["longitude"] is not None and row["latitude"] is not None:
                    location = POILocation(
                        longitude=row["longitude"],
                        latitude=row["latitude"],
                    )
                result.append(
                    Hotel(
                        provider=row["provider"],
                        id=row["hotel_id"],
                        name=row["name"],
                        city=row["city"],
                        address=row["address"],
                        location=location,
                        type=row["type"],
                        rating=row["rating"],
                        average_price=row["average_price"],
                        price_range=row["price_range"],
                        tel=row["tel"],
                        photos=photos,
                    )
                )
        except (TypeError, ValueError) as exc:
            raise HotelRepositoryError("已保存的酒店数据格式无效") from exc
        return result

    def save_search(
        self,
        hotels: list[Hotel],
        *,
        provider: str,
        criteria: HotelSearchCriteria,
    ) -> None:
        """事务保存酒店查询条件和结果，包括无结果查询。"""
        query_key = _query_key(provider, criteria)
        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO hotel_searches (
                        query_key, provider, city, accommodation, area,
                        budget_min, budget_max, result_limit, fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(query_key) DO UPDATE SET fetched_at = excluded.fetched_at
                    """,
                    (
                        query_key,
                        provider,
                        criteria.city,
                        criteria.accommodation,
                        criteria.area,
                        criteria.budget_min,
                        criteria.budget_max,
                        criteria.limit,
                        fetched_at,
                    ),
                )
                connection.execute(
                    "DELETE FROM hotel_search_results WHERE query_key = ?",
                    (query_key,),
                )
                for position, hotel in enumerate(hotels):
                    connection.execute(
                        """
                        INSERT INTO hotel_search_results (
                            query_key, position, provider, hotel_id, name, city,
                            address, longitude, latitude, type, rating,
                            average_price, price_range, tel, photos_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            query_key,
                            position,
                            hotel.provider,
                            hotel.id,
                            hotel.name,
                            hotel.city,
                            hotel.address,
                            hotel.location.longitude if hotel.location else None,
                            hotel.location.latitude if hotel.location else None,
                            hotel.type,
                            hotel.rating,
                            hotel.average_price,
                            hotel.price_range,
                            hotel.tel,
                            json.dumps(hotel.photos, ensure_ascii=False),
                        ),
                    )
        except sqlite3.Error as exc:
            raise HotelRepositoryError("保存酒店搜索结果失败") from exc
