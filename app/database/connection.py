import sqlite3
import os
from typing import List, Optional
from .models import PipelineExecutionModel

class DatabaseManager:
    """Manages SQLite storage for application data and CI/CD pipeline execution telemetry."""

    def __init__(self, db_path: str = "data/pipeline.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_id TEXT NOT NULL,
                    files_changed INTEGER,
                    lines_added INTEGER,
                    lines_deleted INTEGER,
                    test_count INTEGER,
                    previous_runtime_sec REAL,
                    previous_failure INTEGER,
                    build_time_sec REAL,
                    test_time_sec REAL,
                    cpu_usage_pct REAL,
                    memory_usage_mb REAL,
                    pipeline_type TEXT DEFAULT 'baseline',
                    decision_action TEXT DEFAULT 'FULL_PIPELINE',
                    result INTEGER NOT NULL,
                    timestamp REAL NOT NULL
                );
            """)
            conn.commit()

    def record_run(self, data: dict):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO pipeline_runs (
                    commit_id, files_changed, lines_added, lines_deleted,
                    test_count, previous_runtime_sec, previous_failure,
                    build_time_sec, test_time_sec, cpu_usage_pct,
                    memory_usage_mb, pipeline_type, decision_action,
                    result, timestamp
                ) VALUES (
                    :commit_id, :files_changed, :lines_added, :lines_deleted,
                    :test_count, :previous_runtime_sec, :previous_failure,
                    :build_time_sec, :test_time_sec, :cpu_usage_pct,
                    :memory_usage_mb, :pipeline_type, :decision_action,
                    :result, :timestamp
                )
            """, data)
            conn.commit()

    def get_all_runs(self) -> List[sqlite3.Row]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM pipeline_runs ORDER BY id ASC")
            return cur.fetchall()

    def get_recent_runs(self, limit: int = 50) -> List[sqlite3.Row]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM pipeline_runs ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()
