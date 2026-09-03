"""旅行规划任务、完整行程、每日安排和路线段的 SQLite 持久化。"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.trip import TripPlan, TripPlanningRequest, TripTask

from .xhs_repository import database_path


class TripRepositoryError(RuntimeError):
    """旅行任务或行程读取、写入失败。"""


def _now() -> str:
    """生成用于任务排序和状态更新时间的 UTC 时间。"""
    return datetime.now(timezone.utc).isoformat()


class TripRepository:
    """在统一 SQLite 文件中保存可恢复的主流程状态和结果。"""

    def __init__(self, path: str | Path | None = None):
        """初始化行程相关数据表；不修改已有内容和地图缓存表。"""
        self.path = Path(path) if path else database_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise TripRepositoryError("无法创建旅行规划数据目录") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """打开启用外键、WAL 和字典行读取的 SQLite 连接。"""
        try:
            connection = sqlite3.connect(self.path, timeout=15)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA journal_mode = WAL")
            return connection
        except sqlite3.Error as exc:
            raise TripRepositoryError("无法打开旅行规划数据文件") from exc

    def _initialize(self) -> None:
        """创建任务、行程、每日安排和路线段表及查询索引。"""
        schema = """
        CREATE TABLE IF NOT EXISTS trip_tasks (
            task_id TEXT PRIMARY KEY,
            request_json TEXT NOT NULL,
            status TEXT NOT NULL,
            stage TEXT NOT NULL,
            progress INTEGER NOT NULL,
            message TEXT NOT NULL,
            error_code TEXT,
            error TEXT,
            plan_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_trip_tasks_updated
            ON trip_tasks(updated_at DESC);
        CREATE TABLE IF NOT EXISTS trip_plans (
            plan_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL UNIQUE,
            cities_json TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            travelers INTEGER NOT NULL,
            plan_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES trip_tasks(task_id)
        );
        CREATE INDEX IF NOT EXISTS idx_trip_plans_created
            ON trip_plans(created_at DESC);
        CREATE TABLE IF NOT EXISTS trip_days (
            plan_id TEXT NOT NULL,
            day_index INTEGER NOT NULL,
            city TEXT NOT NULL,
            trip_date TEXT NOT NULL,
            day_json TEXT NOT NULL,
            PRIMARY KEY (plan_id, day_index),
            FOREIGN KEY (plan_id) REFERENCES trip_plans(plan_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_trip_days_city_date
            ON trip_days(city, trip_date);
        CREATE TABLE IF NOT EXISTS trip_route_segments (
            plan_id TEXT NOT NULL,
            day_index INTEGER NOT NULL,
            position INTEGER NOT NULL,
            origin_name TEXT NOT NULL,
            destination_name TEXT NOT NULL,
            route_json TEXT NOT NULL,
            PRIMARY KEY (plan_id, day_index, position),
            FOREIGN KEY (plan_id, day_index) REFERENCES trip_days(plan_id, day_index)
                ON DELETE CASCADE
        );
        """
        try:
            with self._connect() as connection:
                connection.executescript(schema)
        except sqlite3.Error as exc:
            raise TripRepositoryError("初始化旅行规划数据表失败") from exc

    def create_task(self, task_id: str, request: TripPlanningRequest) -> TripTask:
        """持久化已提交任务，并返回可立即查询的状态快照。"""
        created_at = _now()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO trip_tasks (
                        task_id, request_json, status, stage, progress, message,
                        created_at, updated_at
                    ) VALUES (?, ?, 'submitted', 'submitted', 5, ?, ?, ?)
                    """,
                    (
                        task_id,
                        request.model_dump_json(),
                        "旅行需求已提交，正在准备规划",
                        created_at,
                        created_at,
                    ),
                )
        except sqlite3.Error as exc:
            raise TripRepositoryError("保存旅行规划任务失败") from exc
        task = self.get_task(task_id)
        if task is None:
            raise TripRepositoryError("旅行规划任务保存后无法读取")
        return task

    def update_task(
        self,
        task_id: str,
        *,
        status: str,
        stage: str,
        progress: int,
        message: str,
        error_code: str | None = None,
        error: str | None = None,
    ) -> None:
        """原子更新任务进度或失败信息。"""
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    UPDATE trip_tasks
                    SET status = ?, stage = ?, progress = ?, message = ?,
                        error_code = ?, error = ?, updated_at = ?
                    WHERE task_id = ?
                    """,
                    (
                        status,
                        stage,
                        max(0, min(100, progress)),
                        message,
                        error_code,
                        error,
                        _now(),
                        task_id,
                    ),
                )
                if cursor.rowcount != 1:
                    raise TripRepositoryError("旅行规划任务不存在")
        except sqlite3.Error as exc:
            raise TripRepositoryError("更新旅行规划任务失败") from exc

    def complete_task(self, task_id: str, plan: TripPlan) -> None:
        """在同一事务中保存完整行程、每日安排、路线段并完成任务。"""
        plan_payload = plan.model_dump(mode="json")
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO trip_plans (
                        plan_id, task_id, cities_json, start_date, end_date,
                        travelers, plan_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        plan.plan_id,
                        task_id,
                        json.dumps(plan.cities, ensure_ascii=False),
                        plan.start_date.isoformat(),
                        plan.end_date.isoformat(),
                        plan.travelers,
                        json.dumps(plan_payload, ensure_ascii=False),
                        plan.created_at.isoformat(),
                    ),
                )
                for day in plan.days:
                    connection.execute(
                        """
                        INSERT INTO trip_days (plan_id, day_index, city, trip_date, day_json)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            plan.plan_id,
                            day.day_index,
                            day.city,
                            day.date.isoformat(),
                            day.model_dump_json(),
                        ),
                    )
                    for position, segment in enumerate(day.routes):
                        connection.execute(
                            """
                            INSERT INTO trip_route_segments (
                                plan_id, day_index, position, origin_name,
                                destination_name, route_json
                            ) VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                plan.plan_id,
                                day.day_index,
                                position,
                                segment.origin_name,
                                segment.destination_name,
                                segment.route.model_dump_json(),
                            ),
                        )
                cursor = connection.execute(
                    """
                    UPDATE trip_tasks
                    SET status = 'completed', stage = 'completed', progress = 100,
                        message = ?, plan_id = ?, error_code = NULL, error = NULL,
                        updated_at = ?
                    WHERE task_id = ?
                    """,
                    ("旅行计划生成完成", plan.plan_id, _now(), task_id),
                )
                if cursor.rowcount != 1:
                    raise TripRepositoryError("旅行规划任务不存在")
        except sqlite3.Error as exc:
            raise TripRepositoryError("保存完整旅行计划失败") from exc

    def get_task(self, task_id: str) -> TripTask | None:
        """按任务 ID 读取最新持久化状态。"""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM trip_tasks WHERE task_id = ?",
                    (task_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise TripRepositoryError("读取旅行规划任务失败") from exc
        return TripTask.model_validate(dict(row)) if row is not None else None

    def get_request(self, task_id: str) -> TripPlanningRequest | None:
        """读取任务最初提交的领域请求，供恢复和审计使用。"""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT request_json FROM trip_tasks WHERE task_id = ?",
                    (task_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise TripRepositoryError("读取旅行规划请求失败") from exc
        if row is None:
            return None
        try:
            return TripPlanningRequest.model_validate_json(row["request_json"])
        except ValueError as exc:
            raise TripRepositoryError("已保存的旅行规划请求格式无效") from exc

    def get_plan(self, plan_id: str) -> TripPlan | None:
        """按计划 ID 读取完整行程。"""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT plan_json FROM trip_plans WHERE plan_id = ?",
                    (plan_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise TripRepositoryError("读取旅行计划失败") from exc
        if row is None:
            return None
        try:
            return TripPlan.model_validate_json(row["plan_json"])
        except ValueError as exc:
            raise TripRepositoryError("已保存的旅行计划格式无效") from exc

    def list_plans(self, limit: int = 20) -> list[dict[str, Any]]:
        """按创建时间倒序返回历史行程摘要。"""
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT plan_id, cities_json, start_date, end_date,
                           travelers, plan_json, created_at
                    FROM trip_plans ORDER BY created_at DESC LIMIT ?
                    """,
                    (max(1, min(100, limit)),),
                ).fetchall()
            items = []
            for row in rows:
                payload = json.loads(row["plan_json"])
                items.append(
                    {
                        "plan_id": row["plan_id"],
                        "cities": json.loads(row["cities_json"]),
                        "start_date": row["start_date"],
                        "end_date": row["end_date"],
                        "travelers": row["travelers"],
                        "days_count": len(payload.get("days") or []),
                        "created_at": row["created_at"],
                    }
                )
            return items
        except (sqlite3.Error, TypeError, ValueError) as exc:
            raise TripRepositoryError("读取历史旅行计划失败") from exc
