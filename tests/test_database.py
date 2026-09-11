import pytest
import os
import time
from app.database.connection import DatabaseManager

@pytest.fixture
def db_manager(tmp_path):
    db_file = os.path.join(tmp_path, "test_pipeline.db")
    return DatabaseManager(db_path=db_file)

def test_record_and_get_runs(db_manager):
    sample_run = {
        "commit_id": "c0ffee1",
        "files_changed": 3,
        "lines_added": 45,
        "lines_deleted": 12,
        "test_count": 25,
        "previous_runtime_sec": 14.5,
        "previous_failure": 0,
        "build_time_sec": 2.1,
        "test_time_sec": 12.4,
        "cpu_usage_pct": 35.2,
        "memory_usage_mb": 142.5,
        "pipeline_type": "baseline",
        "decision_action": "FULL_PIPELINE",
        "result": 0,
        "timestamp": time.time()
    }
    db_manager.record_run(sample_run)
    runs = db_manager.get_all_runs()
    assert len(runs) == 1
    row = runs[0]
    assert row["commit_id"] == "c0ffee1"
    assert row["files_changed"] == 3
    assert row["result"] == 0

def test_get_recent_runs_limit(db_manager):
    for i in range(10):
        db_manager.record_run({
            "commit_id": f"commit_{i}",
            "files_changed": i,
            "lines_added": i * 10,
            "lines_deleted": i * 2,
            "test_count": 20,
            "previous_runtime_sec": 10.0,
            "previous_failure": 0,
            "build_time_sec": 1.0,
            "test_time_sec": 9.0,
            "cpu_usage_pct": 20.0,
            "memory_usage_mb": 100.0,
            "pipeline_type": "ai_optimized",
            "decision_action": "OPTIMIZE_TESTS",
            "result": 0,
            "timestamp": time.time() + i
        })
    recent = db_manager.get_recent_runs(limit=3)
    assert len(recent) == 3
    assert recent[0]["commit_id"] == "commit_9"
