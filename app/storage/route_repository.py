"""两点路线事实的 SQLite 缓存。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

from app.models.route import RoutePlan, RouteQuery

from .xhs_repository import database_path


class RouteRepositoryError(RuntimeError):
    """路线缓存初始化、读取或写入异常。"""


def _query_key(provider: str, query: RouteQuery) -> str:
    """根据供应商和完整路线条件生成稳定缓存键。"""
    payload = {"provider": provider, **query.model_dump(mode="json")}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class RouteRepository:
    """在统一 SQLite 文件中保存标准化路线及其查询时间。"""

    def __init__(self, path: str | Path | None = None):
        """初始化路线缓存表；未传路径时使用统一数据文件。"""
        self.path = Path(path) if path else database_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RouteRepositoryError("无法创建路线缓存目录") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """打开启用字典行读取的 SQLite 连接。"""
        try:
            connection = sqlite3.connect(self.path, timeout=10)
            connection.row_factory = sqlite3.Row
            return connection
        except sqlite3.Error as exc:
            raise RouteRepositoryError("无法打开路线缓存数据文件") from exc

    def _initialize(self) -> None:
        """创建路线查询表和按时间清理使用的索引。"""
        try:
            with self._connect() as connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS route_queries (
                        query_key TEXT PRIMARY KEY,
                        provider TEXT NOT NULL,
                        route_type TEXT NOT NULL,
                        origin_address TEXT NOT NULL,
                        destination_address TEXT NOT NULL,
                        origin_city TEXT NOT NULL DEFAULT '',
                        destination_city TEXT NOT NULL DEFAULT '',
                        query_json TEXT NOT NULL,
                        route_json TEXT NOT NULL,
                        fetched_at TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_route_queries_fetched
                        ON route_queries(fetched_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_route_queries_endpoints
                        ON route_queries(origin_city, destination_city, route_type);
                    """
                )
        except sqlite3.Error as exc:
            raise RouteRepositoryError("初始化路线缓存表失败") from exc

    def get_route(
        self,
        *,
        provider: str,
        query: RouteQuery,
        max_age_seconds: int,
    ) -> RoutePlan | None:
        """读取仍在有效期内且完整匹配查询条件的路线。"""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT route_json FROM route_queries
                    WHERE query_key = ? AND fetched_at >= ?
                    """,
                    (_query_key(provider, query), cutoff.isoformat()),
                ).fetchone()
        except sqlite3.Error as exc:
            raise RouteRepositoryError("读取路线缓存失败") from exc
        if row is None:
            return None
        try:
            return RoutePlan.model_validate(json.loads(row["route_json"]))
        except (TypeError, ValueError) as exc:
            raise RouteRepositoryError("路线缓存数据格式无效") from exc

    def save_route(self, *, provider: str, query: RouteQuery, route: RoutePlan) -> None:
        """保存路线事实，相同查询条件使用最新供应商结果覆盖。"""
        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO route_queries (
                        query_key, provider, route_type, origin_address,
                        destination_address, origin_city, destination_city,
                        query_json, route_json, fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(query_key) DO UPDATE SET
                        query_json = excluded.query_json,
                        route_json = excluded.route_json,
                        fetched_at = excluded.fetched_at
                    """,
                    (
                        _query_key(provider, query),
                        provider,
                        query.route_type,
                        query.origin_address,
                        query.destination_address,
                        query.origin_city,
                        query.destination_city,
                        json.dumps(query.model_dump(mode="json"), ensure_ascii=False),
                        json.dumps(route.model_dump(mode="json"), ensure_ascii=False),
                        fetched_at,
                    ),
                )
        except sqlite3.Error as exc:
            raise RouteRepositoryError("保存路线缓存失败") from exc
