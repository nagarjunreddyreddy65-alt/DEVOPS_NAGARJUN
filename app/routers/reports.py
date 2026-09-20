from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.reporting.report_generator import ReportGenerator
from app.reporting.exporter import ReportExporter

router = APIRouter(prefix="/api/v1/reports", tags=["Reports & Analytics"])

generator = ReportGenerator()

class EfficiencyReportRequest(BaseModel):
    baseline_runtime_sec: float
    optimized_runtime_sec: float
    baseline_tests: int
    optimized_tests: int

class SummaryReportRequest(BaseModel):
    records: List[Dict[str, Any]]

@router.post("/efficiency")
def get_pipeline_efficiency(req: EfficiencyReportRequest):
    return generator.generate_pipeline_efficiency_report(
        baseline_time=req.baseline_runtime_sec,
        optimized_time=req.optimized_runtime_sec,
        test_count_before=req.baseline_tests,
        test_count_after=req.optimized_tests
    )

@router.post("/summary")
def get_metrics_summary(req: SummaryReportRequest):
    return generator.generate_summary(req.records)

@router.post("/export/csv")
def export_csv(records: List[Dict[str, Any]]):
    csv_data = ReportExporter.to_csv(records)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})

@router.post("/export/json")
def export_json(data: Dict[str, Any]):
    json_data = ReportExporter.to_json(data)
    return Response(content=json_data, media_type="application/json")
