"""小红书笔记、提取记录和景点候选的 SQLite 持久化。"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from dotenv import load_dotenv


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=False)


class XHSRepositoryError(RuntimeError):
    """小红书持久化操作失败。"""


def database_path() -> Path:
    """返回小红书数据文件路径，并确保数据目录存在。"""
    configured_dir = os.getenv("TRAVELMIND_DATA_DIR", "").strip()
    data_dir = Path(configured_dir).expanduser() if configured_dir else _PROJECT_ROOT / "data"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise XHSRepositoryError(f"无法创建数据目录: {data_dir}") from exc
    return data_dir / "travelmind.db"


def _now() -> str:
    """生成统一保存的 UTC 时间字符串。"""
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    """将列表等复合字段编码为 SQLite 可保存的 JSON 文本。"""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class XHSRepository:
    """使用 SQLite 保存小红书原文和景点提取结果。"""

    def __init__(self, path: str | Path | None = None):
        """初始化数据库文件，并在首次使用时创建所需数据表。"""
        self.path = Path(path) if path else database_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise XHSRepositoryError(f"无法创建数据目录: {self.path.parent}") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """打开启用外键和 WAL 的 SQLite 连接。"""
        try:
            connection = sqlite3.connect(self.path, timeout=10)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA journal_mode = WAL")
            return connection
        except sqlite3.Error as exc:
            raise XHSRepositoryError(f"无法打开数据文件: {self.path}") from exc

    def _initialize(self) -> None:
        """创建笔记、提取记录、景点候选及其查询索引。"""
        schema = """
        CREATE TABLE IF NOT EXISTS xhs_notes (
            note_id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            source_url TEXT NOT NULL DEFAULT '',
            xsec_source TEXT NOT NULL DEFAULT 'pc_search',
            images_json TEXT NOT NULL DEFAULT '[]',
            author TEXT NOT NULL DEFAULT '',
            liked_count INTEGER NOT NULL DEFAULT 0,
            fetched_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS xhs_extractions (
            extraction_id TEXT PRIMARY KEY,
            city TEXT NOT NULL,
            keywords TEXT NOT NULL DEFAULT '',
            language TEXT NOT NULL DEFAULT 'zh',
            note_ids_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attraction_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            extraction_id TEXT NOT NULL,
            name TEXT NOT NULL,
            name_zh TEXT NOT NULL,
            name_en TEXT NOT NULL,
            reason TEXT NOT NULL,
            duration INTEGER NOT NULL,
            reservation_required INTEGER NOT NULL DEFAULT 0,
            reservation_tips TEXT NOT NULL DEFAULT '',
            poi_id TEXT NOT NULL DEFAULT '',
            address TEXT NOT NULL DEFAULT '',
            longitude REAL,
            latitude REAL,
            rating REAL,
            photos_json TEXT NOT NULL DEFAULT '[]',
            source_note_ids_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            FOREIGN KEY (extraction_id) REFERENCES xhs_extractions(extraction_id)
                ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_xhs_extractions_city_created
            ON xhs_extractions(city, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_attraction_candidates_extraction
            ON attraction_candidates(extraction_id);
        """
        try:
            with self._connect() as connection:
                connection.executescript(schema)
                # NOTE: 为已有数据库补充 POI 字段，保证历史提取记录仍可读取。
                columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(attraction_candidates)")
                }
                additions = {
                    "poi_id": "TEXT NOT NULL DEFAULT ''",
                    "address": "TEXT NOT NULL DEFAULT ''",
                    "longitude": "REAL",
                    "latitude": "REAL",
                    "rating": "REAL",
                    "photos_json": "TEXT NOT NULL DEFAULT '[]'",
                }
                for name, definition in additions.items():
                    if name not in columns:
                        connection.execute(
                            f"ALTER TABLE attraction_candidates ADD COLUMN {name} {definition}"
                        )
        except sqlite3.Error as exc:
            raise XHSRepositoryError("初始化小红书数据表失败") from exc

    def save_extraction(
        self,
        city: str,
        keywords: str,
        language: str,
        notes: Iterable[dict[str, Any]],
        candidates: Iterable[dict[str, Any]],
    ) -> str:
        """保存原始笔记和一次完整的景点提取结果，并返回提取记录 ID。

        同一 ``note_id`` 的原文会更新为本次抓取内容；提取记录和候选在同一事务中写入。
        """
        extraction_id = uuid4().hex
        created_at = _now()
        note_rows = list(notes)
        note_ids = [str(note.get("note_id") or "") for note in note_rows]
        note_ids = [note_id for note_id in note_ids if note_id]
        candidate_rows = list(candidates)
        try:
            with self._connect() as connection:
                for note in note_rows:
                    note_id = str(note.get("note_id") or "").strip()
                    if not note_id:
                        continue
                    connection.execute(
                        """
                        INSERT INTO xhs_notes (
                            note_id, title, content, source_url, xsec_source,
                            images_json, author, liked_count, fetched_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(note_id) DO UPDATE SET
                            title = excluded.title,
                            content = excluded.content,
                            source_url = excluded.source_url,
                            xsec_source = excluded.xsec_source,
                            images_json = excluded.images_json,
                            author = excluded.author,
                            liked_count = excluded.liked_count,
                            fetched_at = excluded.fetched_at
                        """,
                        (
                            note_id,
                            str(note.get("title") or ""),
                            str(note.get("content") or "")[:100000],
                            str(note.get("source_url") or ""),
                            str(note.get("xsec_source") or "pc_search"),
                            _json(note.get("images") or []),
                            str(note.get("author") or ""),
                            int(note.get("liked_count") or 0),
                            created_at,
                        ),
                    )
                connection.execute(
                    """
                    INSERT INTO xhs_extractions (
                        extraction_id, city, keywords, language, note_ids_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (extraction_id, city, keywords, language, _json(note_ids), created_at),
                )
                for candidate in candidate_rows:
                    connection.execute(
                        """
                        INSERT INTO attraction_candidates (
                            extraction_id, name, name_zh, name_en, reason, duration,
                            reservation_required, reservation_tips,
                            poi_id, address, longitude, latitude, rating, photos_json,
                            source_note_ids_json, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            extraction_id,
                            str(candidate.get("name") or ""),
                            str(candidate.get("name_zh") or ""),
                            str(candidate.get("name_en") or ""),
                            str(candidate.get("reason") or ""),
                            int(candidate.get("duration") or 120),
                            int(bool(candidate.get("reservation_required"))),
                            str(candidate.get("reservation_tips") or ""),
                            str(candidate.get("poi_id") or ""),
                            str(candidate.get("address") or ""),
                            self._candidate_coordinate(candidate, "longitude"),
                            self._candidate_coordinate(candidate, "latitude"),
                            candidate.get("rating"),
                            _json(candidate.get("photos") or []),
                            _json(note_ids),
                            created_at,
                        ),
                    )
        except (sqlite3.Error, TypeError, ValueError) as exc:
            raise XHSRepositoryError("保存小红书提取结果失败") from exc
        return extraction_id

    @staticmethod
    def _candidate_coordinate(candidate: dict[str, Any], key: str) -> float | None:
        """读取候选景点坐标，未完成 POI 补全时返回空值。"""
        location = candidate.get("location") or {}
        if not isinstance(location, dict):
            return None
        value = location.get(key)
        return float(value) if value is not None else None

    def get_extraction(self, extraction_id: str) -> dict[str, Any] | None:
        """按提取记录 ID 读取城市信息、笔记数量和景点候选。"""
        try:
            with self._connect() as connection:
                extraction = connection.execute(
                    "SELECT * FROM xhs_extractions WHERE extraction_id = ?",
                    (extraction_id,),
                ).fetchone()
                if extraction is None:
                    return None
                candidates = connection.execute(
                    """
                    SELECT name, name_zh, name_en, reason, duration,
                           reservation_required, reservation_tips, poi_id, address,
                           longitude, latitude, rating, photos_json
                    FROM attraction_candidates
                    WHERE extraction_id = ?
                    ORDER BY id
                    """,
                    (extraction_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise XHSRepositoryError("读取小红书提取结果失败") from exc
        try:
            attractions = []
            for candidate in candidates:
                item = {
                    **dict(candidate),
                    "reservation_required": bool(candidate["reservation_required"]),
                    "photos": json.loads(candidate["photos_json"] or "[]"),
                }
                item.pop("photos_json", None)
                item.pop("longitude", None)
                item.pop("latitude", None)
                if candidate["longitude"] is not None and candidate["latitude"] is not None:
                    item["location"] = {
                        "longitude": candidate["longitude"],
                        "latitude": candidate["latitude"],
                    }
                else:
                    item["location"] = None
                attractions.append(item)
        except (TypeError, ValueError) as exc:
            raise XHSRepositoryError("读取的小红书候选 POI 数据格式无效") from exc
        return {
            "extraction_id": extraction["extraction_id"],
            "city": extraction["city"],
            "keywords": extraction["keywords"],
            "language": extraction["language"],
            "notes_count": len(json.loads(extraction["note_ids_json"])),
            "attractions": attractions,
            "created_at": extraction["created_at"],
        }
