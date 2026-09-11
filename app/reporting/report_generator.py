from typing import List, Dict, Any
from datetime import datetime

class ReportGenerator:
    """Generates analytical reports for transactions, CI executions, and metrics."""
    
    def __init__(self):
        pass

    def generate_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            return {
                "total_records": 0,
                "summary": "No data available",
                "generated_at": datetime.utcnow().isoformat()
            }
        
        total_count = len(records)
        numeric_keys = [k for k, v in records[0].items() if isinstance(v, (int, float))]
        sums = {k: sum(r.get(k, 0) for r in records) for k in numeric_keys}
        averages = {k: (sums[k] / total_count) for k in numeric_keys}
        
        return {
            "total_records": total_count,
            "metrics_sum": sums,
            "metrics_avg": averages,
            "generated_at": datetime.utcnow().isoformat()
        }

    def generate_pipeline_efficiency_report(self, baseline_time: float, optimized_time: float, test_count_before: int, test_count_after: int) -> Dict[str, Any]:
        time_saved = max(0.0, baseline_time - optimized_time)
        time_reduction_pct = (time_saved / baseline_time * 100.0) if baseline_time > 0 else 0.0
        test_reduction = max(0, test_count_before - test_count_after)
        test_reduction_pct = (test_reduction / test_count_before * 100.0) if test_count_before > 0 else 0.0

        return {
            "baseline_runtime_sec": round(baseline_time, 2),
            "optimized_runtime_sec": round(optimized_time, 2),
            "time_saved_sec": round(time_saved, 2),
            "time_reduction_pct": round(time_reduction_pct, 2),
            "baseline_tests": test_count_before,
            "optimized_tests": test_count_after,
            "tests_skipped": test_reduction,
            "test_reduction_pct": round(test_reduction_pct, 2)
        }
