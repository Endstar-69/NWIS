import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.ai.extractor import extractor, DocumentExtractor

client = TestClient(app)
driller_token = create_access_token({"sub": "driller", "role": "Drilling Engineer", "user_id": 1})
driller_headers = {"Authorization": f"Bearer {driller_token}"}
viewer_token = create_access_token({"sub": "viewer", "role": "Viewer", "user_id": 5})
viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

SAMPLE_PDF_PATH = Path("documents/sample_reports/demo_well_W001_DDR.pdf")
SAMPLE_TXT_PATH = Path("documents/sample_reports/demo_well_W001_DDR.txt")

def test_document_list_and_search():
    # Documents list
    response = client.get("/api/documents", headers=driller_headers)
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 3

    # Keyword Search
    kw_res = client.post("/api/search/keyword", json={
        "query": "mud loss LCM pill"
    }, headers=driller_headers)
    assert kw_res.status_code == 200
    items = kw_res.json()
    assert len(items) > 0

    # Assistant Grounded Query
    ast_res = client.post("/api/search/assistant", json={
        "question": "What happened in nearby wells around 3420 m?",
        "current_depth": 3420.0,
        "current_formation": "Barail Sandstone"
    }, headers=driller_headers)
    assert ast_res.status_code == 200
    ast_data = ast_res.json()
    assert "answer" in ast_data
    assert len(ast_data["grounded_evidence"]) > 0

def test_multi_strategy_pdf_extraction():
    assert SAMPLE_PDF_PATH.exists(), f"Sample PDF missing at {SAMPLE_PDF_PATH}"
    result = extractor.extract_content_from_file(SAMPLE_PDF_PATH)

    assert "pages" in result
    assert result["total_pages"] >= 1
    assert result["strategy_used"] in ["pdfplumber_text_and_tables", "pypdf_fallback"]
    
    first_page = result["pages"][0]
    assert "text" in first_page
    assert len(first_page["text"]) > 100
    assert "DAILY DRILLING REPORT" in first_page["text"]

def test_structured_event_extraction_from_pdf():
    content = extractor.extract_content_from_file(SAMPLE_PDF_PATH)
    events = extractor.extract_structured_events(content["pages"], SAMPLE_PDF_PATH.name)

    assert len(events) >= 1
    ev = events[0]
    
    # Verify entity extraction
    assert "DEMO-W001" in ev["well_name"]
    assert ev["start_depth"] == 3420.0
    assert ev["formation"] == "Barail Sandstone"
    assert ev["event_type"] == "MUD_LOSS"
    assert ev["severity"] == "HIGH"
    
    # Verify narratives
    assert "thief zone" in ev["cause"].lower() or "micro-fracture" in ev["cause"].lower()
    assert "pit volume" in ev["impact"].lower()
    assert "lcm pill" in ev["mitigation"].lower()
    assert "barail sandstone" in ev["lesson_learned"].lower()
    
    # Verify drilling parameters parsed
    dp = ev["drilling_parameters"]
    assert dp.get("wob") == 22.5
    assert dp.get("rpm") == 110.0
    assert dp.get("mud_weight") == 1.28
    assert dp.get("standpipe_pressure") == 2850.0

    # Verify provenance mask & quality
    mask = ev["extracted_fields_mask"]
    assert mask["well_name"] is True
    assert mask["start_depth"] is True
    assert mask["formation"] is True
    assert mask["event_type"] is True
    assert mask["cause"] is True
    assert mask["mitigation"] is True
    assert mask["drilling_parameters"] is True
    assert ev["extraction_quality"] == "HIGH"
    assert ev["confidence"] >= 0.75
    assert ev["provenance"]["classification"] == "[A] Real Implementation"

def test_depth_interval_extraction_from_text():
    sample_text = """
    Well Name: Dikom-104A
    Depth Interval: 3418.0 m - 3432.0 m
    Formation: Barail Sandstone
    Event: MUD_LOSS
    Severity: HIGH
    Cause: Hydrostatic pressure exceeded reservoir pore pressure.
    Impact: Active pit volume dropped 52 bbls.
    Mitigation: Squeezed 40 bbl LCM pill.
    Lesson Learned: Pre-treat active system.
    """
    pages = [{"page_number": 1, "text": sample_text, "tables": []}]
    events = extractor.extract_structured_events(pages, "test_ddr.txt")

    assert len(events) == 1
    ev = events[0]
    assert ev["start_depth"] == 3418.0
    assert ev["end_depth"] == 3432.0
    assert ev["extracted_fields_mask"]["start_depth"] is True
    assert ev["extracted_fields_mask"]["end_depth"] is True

def test_fallback_provenance_mask_when_fields_missing():
    sparse_text = "Rig report note: minor vibration noted on trip."
    pages = [{"page_number": 1, "text": sparse_text, "tables": []}]
    events = extractor.extract_structured_events(pages, "sparse.txt")

    assert len(events) == 1
    ev = events[0]
    
    # Missing fields must have explicit fallback labels
    assert "[FALLBACK]" in ev["cause"]
    assert "[FALLBACK]" in ev["mitigation"]
    assert "[FALLBACK]" in ev["impact"]
    assert ev["extracted_fields_mask"]["depth"] is False or ev["extracted_fields_mask"]["start_depth"] is False
    assert ev["extracted_fields_mask"]["cause"] is False
    assert ev["extraction_quality"] in ["LOW", "FALLBACK_DOMINATED"]
    assert ev["confidence"] <= 0.50

def test_document_upload_endpoint_integration():
    sample_content = b"""DAILY DRILLING REPORT - TEST UPLOAD
Well Name: WELL-UPLOAD-01
Current Depth: 2950.0 m
Formation: Tipam Sandstone
Event Type: KICK
Severity: CRITICAL
Cause: Penetrated high pressure gas streak.
Impact: Pit gain of 15 bbls.
Mitigation: Shut in BOP and circulated out kick.
Lesson Learned: Maintain flow check on drilling break.
WOB: 18.0 klbs | RPM: 95 | Mud Weight: 1.18 SG
"""
    files = {"file": ("test_ddr_upload.txt", io.BytesIO(sample_content), "text/plain")}
    response = client.post("/api/documents/upload", files=files, data={"well_id": "WELL-001"}, headers=driller_headers)
    assert response.status_code == 200
    data = response.json()

    assert "document_id" in data
    assert data["filename"] == "test_ddr_upload.txt"
    assert data["extracted_events_count"] == 1
    assert "extraction_quality_report" in data
    assert data["provenance"]["classification"] == "[A] Real Implementation"

    ev = data["extracted_events"][0]
    assert ev["event_type"] == "KICK"
    assert ev["severity"] == "CRITICAL"
    assert ev["start_depth"] == 2950.0
    assert ev["formation"] == "Tipam Sandstone"

def test_unauthenticated_document_upload_returns_401():
    files = {"file": ("test.txt", io.BytesIO(b"sample text"), "text/plain")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 401

def test_viewer_cannot_upload_document():
    files = {"file": ("test.txt", io.BytesIO(b"sample text"), "text/plain")}
    response = client.post("/api/documents/upload", files=files, headers=viewer_headers)
    assert response.status_code == 403
