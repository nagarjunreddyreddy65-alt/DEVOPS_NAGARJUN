import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import subprocess
import time
from typing import Dict, List, Optional, Tuple
import psutil
from app.database.connection import DatabaseManager

class FeatureCollector:
    """Collects commit metadata, code change metrics, test counts, and historical run data."""

    def __init__(self, repo_dir: str = ".", db_path: str = "data/pipeline.db"):
        self.repo_dir = repo_dir
        self.db = DatabaseManager(db_path=db_path)

    def get_git_commit_info(self, commit_sha: Optional[str] = None) -> Tuple[str, List[str], int, int]:
        """Extracts commit ID, changed files, lines added, and lines deleted using git."""
        try:
            if not commit_sha:
                res = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=self.repo_dir, capture_output=True, text=True, check=True
                )
                commit_sha = res.stdout.strip()

            # Diff stats against HEAD~1 or empty tree if first commit
            diff_res = subprocess.run(
                ["git", "diff", "--numstat", "HEAD~1", "HEAD"],
                cwd=self.repo_dir, capture_output=True, text=True
            )
            
            if diff_res.returncode != 0:
                # Fallback to current unstaged/staged diff or initial commit
                diff_res = subprocess.run(
                    ["git", "diff", "--numstat", "HEAD"],
                    cwd=self.repo_dir, capture_output=True, text=True
                )

            lines_added = 0
            lines_deleted = 0
            changed_files = []

            for line in diff_res.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        added = int(parts[0])
                        deleted = int(parts[1])
                    except ValueError:
                        added, deleted = 0, 0
                    filepath = parts[2]
                    lines_added += added
                    lines_deleted += deleted
                    changed_files.append(filepath)

            return commit_sha, changed_files, lines_added, lines_deleted
        except Exception:
            # Safe fallback if git is unavailable or repo not yet committed
            return "sim_" + str(int(time.time())), ["app/authentication/auth_service.py"], 15, 5

    def get_historical_pipeline_context(self) -> Tuple[float, int]:
        """Fetches the previous pipeline duration and outcome from the database."""
        try:
            recent = self.db.get_recent_runs(limit=1)
            if recent:
                prev = recent[0]
                prev_runtime = float(prev["build_time_sec"] + prev["test_time_sec"])
                prev_failure = int(prev["result"])
                return prev_runtime, prev_failure
        except Exception:
            pass
        return 25.0, 0

    def count_available_tests(self, test_files: Optional[List[str]] = None) -> int:
        """Counts the total number of test functions across the target test files."""
        if not test_files:
            test_dir = os.path.join(self.repo_dir, "tests")
            if not os.path.exists(test_dir):
                return 20
            test_files = [
                os.path.join(test_dir, f)
                for f in os.listdir(test_dir)
                if f.startswith("test_") and f.endswith(".py")
            ]

        total_tests = 0
        for fpath in test_files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("def test_"):
                            total_tests += 1
            except Exception:
                pass
        return max(total_tests, 1)

    def sample_resource_metrics(self) -> Tuple[float, float]:
        """Returns the current CPU usage (%) and process memory consumption (MB)."""
        cpu_pct = psutil.cpu_percent(interval=0.1)
        proc = psutil.Process(os.getpid())
        mem_mb = proc.memory_info().rss / (1024 * 1024)
        return float(cpu_pct), float(mem_mb)

    def collect_features_vector(
        self,
        changed_files: Optional[List[str]] = None,
        lines_added: int = 0,
        lines_deleted: int = 0,
        commit_id: Optional[str] = None
    ) -> Dict[str, any]:
        """Collects the full structured feature dictionary for inference or logging."""
        if changed_files is None or commit_id is None:
            git_id, git_files, git_add, git_del = self.get_git_commit_info()
            commit_id = commit_id or git_id
            changed_files = changed_files if changed_files is not None else git_files
            lines_added = lines_added if lines_added > 0 else git_add
            lines_deleted = lines_deleted if lines_deleted > 0 else git_del

        files_changed = len(changed_files)
        test_count = self.count_available_tests()
        prev_runtime, prev_failure = self.get_historical_pipeline_context()
        cpu_pct, mem_mb = self.sample_resource_metrics()

        return {
            "commit_id": commit_id,
            "files_changed": files_changed,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "test_count": test_count,
            "previous_runtime_sec": prev_runtime,
            "previous_failure": prev_failure,
            "cpu_usage_pct": cpu_pct,
            "memory_usage_mb": mem_mb,
            "changed_files": changed_files
        }

if __name__ == "__main__":
    collector = FeatureCollector()
    features = collector.collect_features_vector()
    print("Collected Features:", features)
