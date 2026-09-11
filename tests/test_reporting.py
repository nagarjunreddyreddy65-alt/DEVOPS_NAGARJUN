import json
import pytest
from app.reporting.report_generator import ReportGenerator
from app.reporting.exporter import ReportExporter

@pytest.fixture
def generator():
    return ReportGenerator()

def test_generate_summary_empty(generator):
    summary = generator.generate_summary([])
    assert summary["total_records"] == 0
    assert summary["summary"] == "No data available"

def test_generate_summary_records(generator):
    records = [
        {"runtime": 10.0, "tests": 50},
        {"runtime": 20.0, "tests": 50}
    ]
    summary = generator.generate_summary(records)
    assert summary["total_records"] == 2
    assert summary["metrics_avg"]["runtime"] == 15.0
    assert summary["metrics_sum"]["tests"] == 100

def test_pipeline_efficiency_calculation(generator):
    eff = generator.generate_pipeline_efficiency_report(
        baseline_time=120.0,
        optimized_time=48.0,
        test_count_before=100,
        test_count_after=40
    )
    assert eff["time_reduction_pct"] == 60.0
    assert eff["test_reduction_pct"] == 60.0
    assert eff["time_saved_sec"] == 72.0
    assert eff["tests_skipped"] == 60

def test_export_to_json():
    data = {"test": "val", "num": 42}
    res = ReportExporter.to_json(data)
    loaded = json.loads(res)
    assert loaded["test"] == "val"

def test_export_to_csv():
    records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    res = ReportExporter.to_csv(records)
    assert "a,b" in res
    assert "1,2" in res
    assert "3,4" in res
