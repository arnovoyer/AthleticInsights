import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from backend.models import ActivityCreate


class ActivityRepository:
    def __init__(self, database_url: str) -> None:
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Nur sqlite:/// wird im MVP unterstuetzt.")
        self.db_path = database_url.replace("sqlite:///", "", 1)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    avg_hr INTEGER NOT NULL,
                    tss REAL NOT NULL,
                    source TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create_activity(self, activity: ActivityCreate, tss_value: float) -> dict[str, Any]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO activities (date, sport, duration, avg_hr, tss, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    activity.date.isoformat(),
                    activity.sport,
                    activity.duration,
                    activity.avg_hr,
                    tss_value,
                    activity.source,
                ),
            )
            conn.commit()
            activity_id = cur.lastrowid

        return {
            "id": int(activity_id),
            "date": activity.date,
            "sport": activity.sport,
            "duration": activity.duration,
            "avg_hr": activity.avg_hr,
            "tss": tss_value,
            "source": activity.source,
        }

    def list_activities(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, date, sport, duration, avg_hr, tss, source
                FROM activities
                ORDER BY date ASC, id ASC
                """
            ).fetchall()

        activities: list[dict[str, Any]] = []
        for row in rows:
            activities.append(
                {
                    "id": int(row[0]),
                    "date": date.fromisoformat(row[1]),
                    "sport": row[2],
                    "duration": int(row[3]),
                    "avg_hr": int(row[4]),
                    "tss": float(row[5]),
                    "source": row[6],
                }
            )
        return activities
