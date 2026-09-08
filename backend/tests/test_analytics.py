import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token

client = TestClient(app)
client.headers["Authorization"] = f"Bearer {create_access_token({'sub': 'driller', 'role': 'Drilling Engineer', 'user_id': 1})}"

def test_knowledge_graph_endpoint():
    response = client.get("/api/analytics/knowledge-graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert len(data["nodes"]) > 0

def test_risk_heatmap_endpoint():
    response = client.get("/api/analytics/risk-heatmap")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "depth_interval" in data[0]

def test_what_if_simulation_endpoint():
    payload = {
        "depth": 3420.0,
        "formation": "Barail Sandstone",
        "mud_weight": 1.28,
        "sim_mud_weight": 1.34,
        "flow_rate": 550.0,
        "sim_flow_rate": 450.0,
        "wob": 22.0,
        "sim_wob": 26.0,
        "rpm": 110.0,
        "sim_rpm": 90.0,
        "standpipe_pressure": 2800.0,
        "sim_standpipe_pressure": 2650.0
    }
    response = client.post("/api/analytics/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "simulated" in data
    assert "risk_deltas" in data

def test_npt_cost_endpoint():
    response = client.get("/api/analytics/npt-cost")
    assert response.status_code == 200
    data = response.json()
    assert "total_npt_hours" in data
    assert "projected_nwis_savings_crores" in data
    assert len(data["breakdown"]) > 0

def test_depth_explorer_endpoint():
    response = client.get("/api/analytics/depth-explorer?depth=3420.0")
    assert response.status_code == 200
    data = response.json()
    assert data["target_depth"] == 3420.0
    assert "formation" in data
    assert "predicted_risks" in data

def test_daily_report_endpoint():
    response = client.get("/api/analytics/daily-report?well_id=1")
    assert response.status_code == 200
    data = response.json()
    assert "markdown_content" in data

def test_predictive_timeline_endpoint():
    response = client.get("/api/analytics/predictive-timeline?depth=3420.0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
