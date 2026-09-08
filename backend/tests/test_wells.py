import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token

client = TestClient(app)
client.headers["Authorization"] = f"Bearer {create_access_token({'sub': 'driller', 'role': 'Drilling Engineer', 'user_id': 1})}"

def test_list_wells():
    response = client.get("/api/wells")
    assert response.status_code == 200
    wells = response.json()
    assert len(wells) >= 30
    assert any(w["well_id"] == "WELL-001" for w in wells)

def test_get_active_well():
    response = client.get("/api/wells/active")
    assert response.status_code == 200
    well = response.json()
    assert well["is_active_well"] is True
    assert well["well_id"] == "WELL-001"

def test_get_nearby_wells():
    response = client.get("/api/wells/WELL-001/nearby?radius_km=25")
    assert response.status_code == 200
    nearby = response.json()
    assert len(nearby) > 0
    # Proximity order check
    distances = [item["distance_km"] for item in nearby]
    assert distances == sorted(distances)

def test_compare_wells():
    response = client.get("/api/wells/compare?well_ids=WELL-001&well_ids=WELL-002")
    assert response.status_code == 200
    comp = response.json()
    assert len(comp) == 2
    assert comp[0]["well"]["well_id"] == "WELL-001"
    assert len(comp[0]["formations"]) > 0
