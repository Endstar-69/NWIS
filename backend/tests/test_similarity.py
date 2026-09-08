import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.services.similarity_service import (
    haversine_distance,
    compute_distance_score,
    compute_depth_overlap_score,
    extract_lithology_tokens,
    compute_formation_similarity,
    compute_reservoir_similarity,
    compute_trajectory_similarity,
    compute_event_hazard_similarity,
    calculate_multi_factor_similarity,
    DEFAULT_SIMILARITY_WEIGHTS
)

client = TestClient(app)
auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'driller', 'role': 'Drilling Engineer', 'user_id': 1})}"}

def test_haversine_calculation():
    # Dikom to Moran ~35-40 km
    lat1, lon1 = 27.4200, 95.3200
    lat2, lon2 = 27.2000, 95.0500
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    assert 30.0 < dist < 45.0

def test_haversine_same_point():
    dist = haversine_distance(27.4200, 95.3200, 27.4200, 95.3200)
    assert dist == 0.0

def test_haversine_symmetry():
    d1 = haversine_distance(27.42, 95.32, 27.35, 95.25)
    d2 = haversine_distance(27.35, 95.25, 27.42, 95.32)
    assert d1 == d2

def test_distance_score_linear():
    score_0 = compute_distance_score(0.0, max_radius_km=50.0, decay_mode="linear")
    assert score_0 == 1.0

    score_25 = compute_distance_score(25.0, max_radius_km=50.0, decay_mode="linear")
    assert score_25 == 0.5

    score_50 = compute_distance_score(50.0, max_radius_km=50.0, decay_mode="linear")
    assert score_50 == 0.0

    score_beyond = compute_distance_score(60.0, max_radius_km=50.0, decay_mode="linear")
    assert score_beyond == 0.0

def test_distance_score_exponential():
    score_0 = compute_distance_score(0.0, max_radius_km=50.0, decay_mode="exponential")
    assert score_0 == 1.0

    score_15 = compute_distance_score(15.0, max_radius_km=50.0, decay_mode="exponential")
    score_30 = compute_distance_score(30.0, max_radius_km=50.0, decay_mode="exponential")
    assert 0.0 < score_30 < score_15 < 1.0

def test_depth_overlap_identical():
    score, details = compute_depth_overlap_score(4000.0, 4000.0)
    assert score == 1.0
    assert details["iou"] == 1.0

def test_depth_overlap_disjoint_scale():
    score, details = compute_depth_overlap_score(2000.0, 4000.0)
    assert score == 0.5
    assert details["iou"] == 0.5

def test_depth_overlap_with_active_window():
    # Active well drilling at 3000m. Offset well reaches 4200m (fully penetrates window 2750-3250)
    score_deep, details_deep = compute_depth_overlap_score(3000.0, 4200.0, active_depth=3000.0, window_delta=250.0)
    assert details_deep["active_coverage"] == 1.0
    assert score_deep > 0.70

    # Offset well stopped at 2000m (never reached active window 2750-3250)
    score_shallow, details_shallow = compute_depth_overlap_score(3000.0, 2000.0, active_depth=3000.0, window_delta=250.0)
    assert details_shallow["active_coverage"] < 1.0
    assert score_shallow < score_deep

def test_extract_lithology_tokens():
    tokens = extract_lithology_tokens("Mottled Plastic Clay, Reactive Shale with Sandstone streaks")
    assert "clay" in tokens
    assert "shale" in tokens
    assert "sandstone" in tokens
    assert "limestone" not in tokens

def test_formation_similarity_same_field_and_depth():
    score, common_fmts, details = compute_formation_similarity(
        depth1=3800.0,
        depth2=3800.0,
        active_field="Dikom",
        offset_field="Dikom",
        active_basin="Assam-Arakan",
        offset_basin="Assam-Arakan"
    )
    assert score >= 0.95
    assert details["continuity_factor"] == 1.0
    assert len(common_fmts) >= 6
    assert "Tipam Sandstone" in common_fmts
    assert "Barail Sandstone" in common_fmts

def test_formation_similarity_different_basin():
    score_same, _, _ = compute_formation_similarity(
        depth1=3800.0, depth2=3800.0,
        active_field="Dikom", offset_field="Dikom",
        active_basin="Assam-Arakan", offset_basin="Assam-Arakan"
    )
    score_diff, _, _ = compute_formation_similarity(
        depth1=3800.0, depth2=3800.0,
        active_field="Dikom", offset_field="Cambay-Field",
        active_basin="Assam-Arakan", offset_basin="Cambay"
    )
    assert score_diff < score_same

def test_trajectory_similarity_profiles():
    # Stations with vertical inclination (< 5 deg)
    w_vert = SimpleNamespace(
        well_type="Development",
        trajectories=[SimpleNamespace(inclination=1.2), SimpleNamespace(inclination=2.1)]
    )
    # Stations with high deviation (> 45 deg)
    w_horiz = SimpleNamespace(
        well_type="Development",
        trajectories=[SimpleNamespace(inclination=30.0), SimpleNamespace(inclination=68.0)]
    )
    # Vertical vs Vertical
    score_vv, _ = compute_trajectory_similarity(w_vert, w_vert)
    assert score_vv >= 0.95

    # Vertical vs Horizontal
    score_vh, details_vh = compute_trajectory_similarity(w_vert, w_horiz)
    assert score_vh < 0.50
    assert "Vertical vs Horizontal" in details_vh["profile_category"]

def test_event_hazard_similarity_cosine():
    # Identical incident profile
    ev1 = [
        SimpleNamespace(event_type="KICK", severity="CRITICAL"),
        SimpleNamespace(event_type="MUD_LOSS", severity="HIGH")
    ]
    ev2 = [
        SimpleNamespace(event_type="KICK", severity="CRITICAL"),
        SimpleNamespace(event_type="MUD_LOSS", severity="HIGH")
    ]
    score_ident, det_ident = compute_event_hazard_similarity(ev1, ev2)
    assert score_ident == 1.0
    assert det_ident["method"] == "hazard_vector_cosine"

    # Orthogonal incident profile (no shared hazards)
    ev_kick_only = [SimpleNamespace(event_type="KICK", severity="CRITICAL")]
    ev_cement_only = [SimpleNamespace(event_type="CEMENTING_ISSUE", severity="LOW")]
    score_ortho, _ = compute_event_hazard_similarity(ev_kick_only, ev_cement_only)
    assert score_ortho == 0.0

def test_event_hazard_similarity_clean_wells():
    score_both_clean, det = compute_event_hazard_similarity([], [])
    assert score_both_clean == 1.0
    assert det["method"] == "incident_free_parity"

    # Active clean, offset has hazards
    score_act_clean, det_clean = compute_event_hazard_similarity(
        [],
        [SimpleNamespace(event_type="KICK", severity="HIGH")]
    )
    assert 0.50 <= score_act_clean <= 1.0
    assert det_clean["method"] == "offset_hazard_baseline"

def test_calculate_multi_factor_similarity_comprehensive():
    w_active = SimpleNamespace(
        well_id="WELL-001",
        field="Dikom",
        basin="Assam-Arakan",
        well_type="Development",
        target_depth=4300.0,
        current_depth=3420.0,
        is_active_well=True,
        trajectories=[]
    )
    w_offset = SimpleNamespace(
        well_id="WELL-002",
        field="Nahorkatiya",
        basin="Assam-Arakan",
        well_type="Development",
        target_depth=4100.0,
        current_depth=4100.0,
        is_active_well=False,
        trajectories=[]
    )
    events_active = [SimpleNamespace(event_type="MUD_LOSS", severity="HIGH", formation="Bokabil Formation")]
    events_offset = [SimpleNamespace(event_type="MUD_LOSS", severity="HIGH", formation="Bokabil Formation")]

    comp_score, breakdown = calculate_multi_factor_similarity(
        active_well=w_active,
        offset_well=w_offset,
        distance_km=12.4,
        active_events=events_active,
        offset_events=events_offset,
        max_radius_km=30.0
    )

    assert 0.0 <= comp_score <= 100.0
    assert "distance_score" in breakdown
    assert "formation_score" in breakdown
    assert "depth_score" in breakdown
    assert "reservoir_score" in breakdown
    assert "trajectory_score" in breakdown
    assert "events_score" in breakdown
    assert "formula" in breakdown
    assert "method_details" in breakdown
    assert breakdown["provenance"]["classification"] == "[A] Real Implementation"

    # Verify weights sum to 1.0
    weights_sum = sum(breakdown["weights_used"].values())
    assert pytest.approx(weights_sum, abs=0.01) == 1.0

def test_nearby_wells_api_endpoint():
    response = client.get("/api/wells/WELL-001/nearby?radius_km=30.0&min_similarity=10.0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    assert "well" in first
    assert "distance_km" in first
    assert "similarity_score" in first
    assert "similarity_breakdown" in first
    assert "common_formations" in first
    assert isinstance(first["common_formations"], list)

    sb = first["similarity_breakdown"]
    assert 0.0 <= sb["distance_score"] <= 1.0
    assert 0.0 <= sb["formation_score"] <= 1.0
    assert 0.0 <= sb["depth_score"] <= 1.0
    assert "weights_used" in sb
    assert sb["provenance"]["classification"] == "[A] Real Implementation"

    # Verify sorted primarily by proximity (distance_km)
    distances = [item["distance_km"] for item in data]
    assert distances == sorted(distances)
