import pytest
from fastapi.testclient import TestClient
from src.dashboard import app

@pytest.fixture
def client():
    return TestClient(app)

def test_dashboard_html_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Autonomous DevOps" in response.text
    assert "System Status" in response.text

def test_dashboard_telemetry_endpoint(client):
    response = client.get("/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "total_runs" in data
    assert data["total_runs"] >= 500
    assert len(data["runs"]) > 0

def test_dashboard_predict_endpoint(client):
    payload = {
        "changed_files": ["app/payment/payment_gateway.py"],
        "lines_added": 25,
        "lines_deleted": 3
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "action" in res
    assert "selected_tests" in res
    assert "failure_probability" in res
    assert "predicted_runtime_sec" in res
