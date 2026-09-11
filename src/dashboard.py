import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
from app.database.connection import DatabaseManager
from src.predict import run_prediction_pipeline

app = FastAPI(
    title="Autonomous DevOps AI Service",
    description="Adaptive CI/CD Optimization Decision API",
    version="1.0.0"
)

class PredictRequest(BaseModel):
    changed_files: List[str]
    lines_added: int = 0
    lines_deleted: int = 0
    commit_id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def index_dashboard():
    """Provides a dashboard view of the Autonomous DevOps pipeline."""
    db = DatabaseManager()
    runs = db.get_recent_runs(limit=10)
    
    table_rows = ""
    for r in runs:
        res_label = "<span style='color:green;font-weight:bold;'>SUCCESS</span>" if r["result"] == 0 else "<span style='color:red;font-weight:bold;'>FAILED</span>"
        table_rows += f"""
        <tr>
            <td><code>{r['commit_id']}</code></td>
            <td>{r['pipeline_type']}</td>
            <td><strong>{r['decision_action']}</strong></td>
            <td>{r['test_count']}</td>
            <td>{r['build_time_sec'] + r['test_time_sec']:.2f}s</td>
            <td>{r['cpu_usage_pct']:.1f}%</td>
            <td>{res_label}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Autonomous DevOps - AI CI/CD Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; background: #f8f9fa; color: #212529; }}
            h1 {{ color: #0366d6; }}
            .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 24px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e1e4e8; }}
            th {{ background: #f1f3f5; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; background: #e3f2fd; color: #0d47a1; }}
        </style>
    </head>
    <body>
        <h1>Autonomous DevOps: Intelligent CI/CD Pipeline</h1>
        <div class="card">
            <h2>System Status: <span style="color:green;">ONLINE</span></h2>
            <p>Adaptive machine learning engine active. Safety-fallback policy: <strong>failure_prob &ge; 0.80 &or; confidence &lt; 0.90 &rarr; FULL_PIPELINE</strong>.</p>
        </div>
        <div class="card">
            <h2>Recent CI/CD Telemetry Runs</h2>
            <table>
                <thead>
                    <tr>
                        <th>Commit</th>
                        <th>Pipeline Type</th>
                        <th>Action</th>
                        <th>Tests</th>
                        <th>Runtime</th>
                        <th>CPU %</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows if table_rows else "<tr><td colspan='7'>No recent runs found.</td></tr>"}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html

@app.post("/predict")
def predict_decision(req: PredictRequest):
    """Real-time prediction endpoint for pipeline webhooks or runner tasks."""
    try:
        decision = run_prediction_pipeline(
            changed_files=req.changed_files,
            lines_added=req.lines_added,
            lines_deleted=req.lines_deleted,
            commit_id=req.commit_id,
            export_github_output=False
        )
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telemetry")
def get_telemetry():
    """Returns raw pipeline execution logs from the database."""
    db = DatabaseManager()
    runs = db.get_all_runs()
    return {"total_runs": len(runs), "runs": [dict(r) for r in runs[-50:]]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.dashboard:app", host="0.0.0.0", port=8000, reload=False)
