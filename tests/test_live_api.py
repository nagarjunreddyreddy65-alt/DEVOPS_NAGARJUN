import pytest
from fastapi.testclient import TestClient
from app.api_server import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["database"] == "CONNECTED"

def test_auth_registration_and_login_flow(client):
    reg_payload = {
        "username": "alice_test",
        "password": "Password123!",
        "email": "alice@test.com",
        "role": "user"
    }
    # Register
    res_reg = client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code in [201, 400]  # 400 if user already registered in prev run
    
    # Login
    login_payload = {"username": "admin", "password": "AdminPass123!"}
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    assert token_data["role"] == "admin"

    # Profile lookup
    res_me = client.get(f"/api/v1/auth/me?token={token_data['access_token']}")
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "admin"

def test_payment_charge_and_refund_flow(client):
    charge_payload = {
        "customer_id": "cust_live_1",
        "amount": 150.0,
        "currency": "USD"
    }
    res_charge = client.post("/api/v1/payments/charge", json=charge_payload)
    assert res_charge.status_code == 200
    tx = res_charge.json()
    assert tx["status"] == "COMPLETED"
    assert tx["amount"] == 150.0

    # Refund
    refund_payload = {"transaction_id": tx["transaction_id"], "amount": 50.0}
    res_refund = client.post("/api/v1/payments/refund", json=refund_payload)
    assert res_refund.status_code == 200
    assert "Successfully refunded" in res_refund.json()["message"]

def test_reports_efficiency_endpoint(client):
    payload = {
        "baseline_runtime_sec": 120.0,
        "optimized_runtime_sec": 60.0,
        "baseline_tests": 100,
        "optimized_tests": 50
    }
    res = client.post("/api/v1/reports/efficiency", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["time_reduction_pct"] == 50.0
    assert data["test_reduction_pct"] == 50.0
