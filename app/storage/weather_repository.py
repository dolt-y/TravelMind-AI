"""天气预报的 SQLite 缓存。"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from app.models.weather import WeatherForecast

from .xhs_repository import database_path


class WeatherRepositoryError(RuntimeError):
    """天气缓存初始化、写入或读取异常。"""


class WeatherRepository:
    """按供应商、城市和预报日期缓存天气事实。"""

    def __init__(self, path: str | Path | None = None):
        """初始化天气缓存表；默认复用 TravelMind 的 SQLite 文件。"""
        self.path = Path(path) if path else database_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise WeatherRepositoryError(f"无法创建天气数据目录: {self.path.parent}") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """打开启用字典行读取的 SQLite 连接。"""
        try:
            connection = sqlite3.connect(self.path, timeout=10)
            connection.row_factory = sqlite3.Row
            return connection
        except sqlite3.Error as exc:
            raise WeatherRepositoryError("无法打开天气缓存数据文件") from exc

    def _initialize(self) -> None:
        """创建天气缓存表和城市日期查询索引。"""
        try:
            with self._connect() as connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS weather_forecasts (
                        provider TEXT NOT NULL,
                        city TEXT NOT NULL,
                        forecast_date TEXT NOT NULL,
                        province TEXT NOT NULL DEFAULT '',
                        adcode TEXT NOT NULL DEFAULT '',
                        day_weather TEXT NOT NULL DEFAULT '',
                        night_weather TEXT NOT NULL DEFAULT '',
                        day_temperature REAL,
                        night_temperature REAL,
                        day_wind_direction TEXT NOT NULL DEFAULT '',
                        night_wind_direction TEXT NOT NULL DEFAULT '',
                        day_wind_power TEXT NOT NULL DEFAULT '',
                        night_wind_power TEXT NOT NULL DEFAULT '',
                        fetched_at TEXT NOT NULL,
                        PRIMARY KEY (provider, city, forecast_date)
                    );
                    CREATE INDEX IF NOT EXISTS idx_weather_city_date
                        ON weather_forecasts(city, forecast_date);
                    """
                )
        except sqlite3.Error as exc:
            raise WeatherRepositoryError("初始化天气缓存表失败") from exc

    def save_forecasts(self, forecasts: Iterable[WeatherForecast]) -> None:
        """保存逐日预报，同一供应商、城市和日期使用最新结果覆盖。"""
        rows = list(forecasts)
        if not rows:
            return
        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as connection:
                for item in rows:
                    connection.execute(
                        """
                        INSERT INTO weather_forecasts (
                            provider, city, forecast_date, province, adcode,
                            day_weather, night_weather, day_temperature, night_temperature,
                            day_wind_direction, night_wind_direction,
                            day_wind_power, night_wind_power, fetched_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(provider, city, forecast_date) DO UPDATE SET
                            province = excluded.province,
                            adcode = excluded.adcode,
                            day_weather = excluded.day_weather,
                            night_weather = excluded.night_weather,
                            day_temperature = excluded.day_temperature,
                            night_temperature = excluded.night_temperature,
                            day_wind_direction = excluded.day_wind_direction,
                            night_wind_direction = excluded.night_wind_direction,
                            day_wind_power = excluded.day_wind_power,
                            night_wind_power = excluded.night_wind_power,
                            fetched_at = excluded.fetched_at
                        """,
                        (
                            item.provider,
                            item.city,
                            item.date.isoformat(),
                            item.province,
                            item.adcode,
                            item.day_weather,
                            item.night_weather,
                            item.day_temperature,
                            item.night_temperature,
                            item.day_wind_direction,
                            item.night_wind_direction,
                            item.day_wind_power,
                            item.night_wind_power,
                            fetched_at,
                        ),
                    )
        except sqlite3.Error as exc:
            raise WeatherRepositoryError("保存天气预报失败") from exc

    def get_forecasts(
        self,
        *,
        provider: str,
        city: str,
        max_age_seconds: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[WeatherForecast]:
        """读取仍在有效期内的城市天气，可按预报日期范围过滤。"""
        conditions = ["provider = ?", "city = ?", "fetched_at >= ?"]
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        parameters: list[object] = [provider, city, cutoff.isoformat()]
        if start_date is not None:
            conditions.append("forecast_date >= ?")
            parameters.append(start_date.isoformat())
        if end_date is not None:
            conditions.append("forecast_date <= ?")
            parameters.append(end_date.isoformat())
        sql = f"""
            SELECT * FROM weather_forecasts
            WHERE {' AND '.join(conditions)}
            ORDER BY forecast_date
        """
        try:
            with self._connect() as connection:
                rows = connection.execute(sql, parameters).fetchall()
        except sqlite3.Error as exc:
            raise WeatherRepositoryError("读取天气缓存失败") from exc
        try:
            return [
                WeatherForecast(
                    provider=row["provider"],
                    city=row["city"],
                    province=row["province"],
                    adcode=row["adcode"],
                    date=date.fromisoformat(row["forecast_date"]),
                    day_weather=row["day_weather"],
                    night_weather=row["night_weather"],
                    day_temperature=row["day_temperature"],
                    night_temperature=row["night_temperature"],
                    day_wind_direction=row["day_wind_direction"],
                    night_wind_direction=row["night_wind_direction"],
                    day_wind_power=row["day_wind_power"],
                    night_wind_power=row["night_wind_power"],
                )
                for row in rows
            ]
        except (TypeError, ValueError) as exc:
            raise WeatherRepositoryError("天气缓存数据格式无效") from exc
