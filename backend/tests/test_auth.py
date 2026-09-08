import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "DEMO" in data["environment"]

def test_system_status_endpoint():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["counts"]["wells"] >= 30

def test_login_success():
    response = client.post("/api/auth/login-json", json={
        "username": "driller",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "Drilling Engineer"

def test_login_failure():
    response = client.post("/api/auth/login-json", json={
        "username": "driller",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
