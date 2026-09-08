"""
Comprehensive tests for Unified LLM Search, RAG Grounding, Dynamic Follow-ups, and Multi-turn History.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import settings

client = TestClient(app)


def test_health_check_endpoint():
    """Verifies GET /api/health returns operational status."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert "Nearby Wells" in data["system"]


def test_well_incidents_endpoint(geologist_headers):
    """Verifies GET /api/wells/{well_id}/incidents retrieves recorded incidents."""
    resp = client.get(f"{settings.API_PREFIX}/wells/WELL-002/incidents", headers=geologist_headers)
    assert resp.status_code == 200
    incidents = resp.json()
    assert isinstance(incidents, list)
    if incidents:
        assert all(inc.get("severity") in ["MEDIUM", "HIGH", "CRITICAL"] for inc in incidents)


def test_dynamic_suggestions_endpoint(geologist_headers):
    """Verifies GET /api/search/suggestions generates context-aware suggestions."""
    resp = client.get(
        f"{settings.API_PREFIX}/search/suggestions",
        params={"well_id": "WELL-001", "depth": 3667.7, "formation": "Barail Sandstone"},
        headers=geologist_headers
    )
    assert resp.status_code == 200
    suggestions = resp.json()
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    # Must be dynamic and reference current depth/formation
    assert any("3668" in s or "Barail" in s for s in suggestions)


def test_unified_search_historical_grounding(geologist_headers):
    """Verifies POST /api/search retrieves historical offset evidence and generates structured response."""
    payload = {
        "query": "What happened in nearby wells around 3668 m in Barail Sandstone?",
        "well_id": "WELL-001",
        "depth": 3667.7,
        "formation": "Barail Sandstone"
    }
    resp = client.post(f"{settings.API_PREFIX}/search", json=payload, headers=geologist_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert "answer" in data
    assert data["answer_type"] == "historical_evidence"
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    assert "conversation_id" in data
    assert isinstance(data["follow_up_questions"], list)
    assert len(data["follow_up_questions"]) > 0

    # Ensure source contains well, depth, and relevance
    src0 = data["sources"][0]
    assert "well" in src0
    assert "depth" in src0
    assert "document" in src0


def test_unified_search_general_knowledge(geologist_headers):
    """Verifies conceptual questions are classified as general_knowledge without fake historical claims."""
    payload = {
        "query": "What is differential sticking and how does it occur?",
        "well_id": "WELL-001",
        "depth": 3667.7,
        "formation": "Barail Sandstone"
    }
    resp = client.post(f"{settings.API_PREFIX}/search", json=payload, headers=geologist_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["answer_type"] == "general_knowledge"
    assert "Differential Sticking" in data["answer"]
    # Should not fabricate historical sources for conceptual definitions
    assert len(data["sources"]) == 0


def test_unified_search_insufficient_evidence(geologist_headers):
    """Verifies system handles unrecorded horizons with transparent insufficient evidence notice."""
    payload = {
        "query": "What incidents occurred at depth 9800 m in Martian Basalt formation?",
        "well_id": "WELL-001",
        "depth": 9800.0,
        "formation": "Martian Basalt"
    }
    resp = client.post(f"{settings.API_PREFIX}/search", json=payload, headers=geologist_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["answer_type"] == "insufficient_evidence"
    assert "Insufficient" in data["answer"] or "could not locate" in data["answer"]


def test_conversation_history_persistence(geologist_headers):
    """Verifies multi-turn conversation retains turns and GET /api/search/history lists them."""
    # Turn 1
    resp1 = client.post(
        f"{settings.API_PREFIX}/search",
        json={"query": "What offset wells had mud loss near 3650 m?"},
        headers=geologist_headers
    )
    assert resp1.status_code == 200
    conv_id = resp1.json()["conversation_id"]

    # Turn 2 using same conversation_id
    resp2 = client.post(
        f"{settings.API_PREFIX}/search",
        json={
            "query": "What mitigations were applied in those events?",
            "conversation_id": conv_id
        },
        headers=geologist_headers
    )
    assert resp2.status_code == 200
    assert resp2.json()["conversation_id"] == conv_id

    # Check search history endpoint
    hist_resp = client.get(f"{settings.API_PREFIX}/search/history", headers=geologist_headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert isinstance(history, list)
    assert any(h.get("conversation_id") == conv_id for h in history)
