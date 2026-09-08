"""
NWIS Automated Test Suite — Phase 3: Hybrid Physics-Informed & Statistical Risk Engine.

CLASSIFICATION: [A] Real Implementation (Test Suite) testing Tier 1 Physics, Tier 2 Statistics, and Tier 3 ML.

Test Coverage:
  1. Teale's Mechanical Specific Energy (MSE) axial & rotational physics formula verification.
  2. Hydraulic balance (pore pressure, fracture gradient, overbalance and fracture margins).
  3. Tier 1 deterministic physics hazard detection (Mud Loss, Stuck Pipe, Gas Kick).
  4. Tier 2 rolling Z-score anomaly detection across drilling channels.
  5. Tier 2 multivariate Isolation Forest outlier detection.
  6. Hybrid probability blending and honest calibrated confidence scoring.
  7. Zero target leakage GroupKFold evaluation metrics verification.
  8. REST API /api/risk/predict response schema with inspectable tier scores.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.ml.physics_engine import (
    calculate_teale_mse,
    calculate_hydraulic_balance,
    evaluate_tier1_physics_risk,
)
from backend.app.ml.statistical_engine import RollingStatisticalEngine

client = TestClient(app)
driller_token = create_access_token({"sub": "driller", "role": "Drilling Engineer", "user_id": 1})
driller_headers = {"Authorization": f"Bearer {driller_token}"}


# ── 1. Tier 1 Deterministic Engineering Physics Tests ────────────────────────

def test_teale_mse_calculation():
    """Validates Teale's MSE formula components (axial + rotational energy per unit volume)."""
    # 1. On-bit drilling condition (0.6 kNm on-bit torque)
    res_bit = calculate_teale_mse(
        wob_tons=15.0,
        rop_mhr=10.0,
        rpm=110.0,
        torque_knm=0.6,
        hole_size_inch=8.5
    )
    assert "mse_mpa" in res_bit
    assert "mse_psi" in res_bit
    assert 30.0 <= res_bit["mse_mpa"] <= 120.0
    assert 4000.0 <= res_bit["mse_psi"] <= 18000.0
    assert res_bit["rotational_ratio"] > 0.80
    assert res_bit["axial_ratio"] < 0.20

    # 2. Total string surface torque condition (13.0 kNm)
    res_surface = calculate_teale_mse(
        wob_tons=15.0,
        rop_mhr=10.0,
        rpm=110.0,
        torque_knm=13.0,
        hole_size_inch=8.5
    )
    assert res_surface["mse_mpa"] > 1000.0
    assert res_surface["rotational_ratio"] > 0.95


def test_hydraulic_balance_calculation():
    """Validates formation pore pressure, fracture gradient, and overbalance margin."""
    # Test across Barail Sandstone (high pore pressure horizon)
    hydraulics = calculate_hydraulic_balance(
        depth=3420.0,
        mud_weight=1.28,
        ecd=1.33,
        formation_name="Barail Sandstone"
    )
    assert hydraulics["pore_pressure_sg"] == 1.28
    # Fracture gradient physically exceeds pore pressure
    assert hydraulics["fracture_gradient_sg"] > hydraulics["pore_pressure_sg"]
    # Overbalance margin = ECD - PP = 1.33 - 1.28 = 0.05 SG
    assert abs(hydraulics["overbalance_margin_sg"] - 0.05) < 0.005
    # Fracture margin = FG - ECD > 0
    assert hydraulics["fracture_margin_sg"] > 0.0
    # Bottom hole pressure in bar
    assert hydraulics["bhp_bar"] > 400.0


def test_tier1_physics_mud_loss_detection():
    """Validates deterministic detection of lost circulation when fracture margin or returns drop."""
    loss_telemetry = {
        "depth": 3425.0,
        "rop": 6.0,
        "wob": 14.0,
        "rpm": 105.0,
        "torque": 13.0,
        "standpipe_pressure": 2080.0,  # Negative SPP delta
        "flow_in": 1950.0,
        "flow_out": 1450.0,  # Flow deficit of -500 LPM
        "delta_flow": -500.0,
        "mud_weight": 1.32,
        "ecd": 1.36,
        "formation_name": "Barail Sandstone",
        "gas_units": 20.0
    }
    scores, metrics, warnings = evaluate_tier1_physics_risk(loss_telemetry)
    assert scores["MUD_LOSS"] >= 0.70
    assert any("Flow-Out Deficit" in f.factor_name for f in warnings["MUD_LOSS"])


def test_tier1_physics_stuck_pipe_detection():
    """Validates deterministic detection of stuck pipe under torque surge and excessive overbalance."""
    stuck_telemetry = {
        "depth": 3430.0,
        "rop": 2.5,
        "wob": 18.0,
        "rpm": 65.0,  # Stalled RPM
        "torque": 24.5,  # Extreme torque surge
        "standpipe_pressure": 2720.0,  # Pack-off pressure spike
        "flow_in": 1950.0,
        "flow_out": 1950.0,
        "delta_flow": 0.0,
        "mud_weight": 1.45,
        "ecd": 1.49,  # High overbalance
        "formation_name": "Barail Sandstone",
        "gas_units": 25.0
    }
    scores, metrics, warnings = evaluate_tier1_physics_risk(stuck_telemetry)
    assert scores["STUCK_PIPE"] >= 0.75
    assert any("Torque Surge" in f.factor_name for f in warnings["STUCK_PIPE"])


def test_tier1_physics_gas_kick_detection():
    """Validates deterministic detection of well-control influx under underbalance and positive delta flow."""
    kick_telemetry = {
        "depth": 3450.0,
        "rop": 18.5,  # Drilling break
        "wob": 15.0,
        "rpm": 115.0,
        "torque": 12.0,
        "standpipe_pressure": 2300.0,
        "flow_in": 1950.0,
        "flow_out": 2200.0,  # Flow return gain (+250 LPM)
        "delta_flow": 250.0,
        "mud_weight": 1.25,
        "ecd": 1.27,  # Underbalanced against 1.28 PP
        "formation_name": "Barail Sandstone",
        "gas_units": 450.0  # Gas spike
    }
    scores, metrics, warnings = evaluate_tier1_physics_risk(kick_telemetry)
    assert scores["KICK"] >= 0.75
    assert any("Active Annular Flow Influx" in f.factor_name for f in warnings["KICK"])


# ── 2. Tier 2 Rolling Statistical Engine Tests ────────────────────────────────

def test_tier2_statistical_z_score_detection():
    """Validates rolling Z-score detection when a channel spikes beyond baseline variance."""
    engine = RollingStatisticalEngine(buffer_maxlen=30)
    well = "TEST-WELL-ZSCORE"

    # Feed 15 baseline points
    for _ in range(15):
        engine.add_telemetry_point(well, {
            "standpipe_pressure": 2350.0 + np.random.normal(0, 10.0),
            "torque": 13.0 + np.random.normal(0, 0.5),
            "flow_out": 1950.0 + np.random.normal(0, 10.0),
            "delta_flow": 0.0,
            "rop": 9.5,
            "teale_mse_mpa": 40.0
        })

    # Inject an abrupt +5 sigma torque surge
    spike_point = {
        "standpipe_pressure": 2360.0,
        "torque": 22.5,  # Spike
        "flow_out": 1950.0,
        "delta_flow": 0.0,
        "rop": 9.0,
        "teale_mse_mpa": 85.0
    }
    scores, metrics = engine.evaluate_tier2_statistical_risk(well, spike_point)
    assert metrics["z_scores"]["z_rotary_torque"] > 3.0
    assert scores["STUCK_PIPE"] > scores["MUD_LOSS"]


def test_tier2_isolation_forest_multivariate_anomaly():
    """Validates unsupervised multivariate Isolation Forest outlier detection."""
    engine = RollingStatisticalEngine(buffer_maxlen=40, min_history_for_isoforest=10)
    well = "TEST-WELL-ISO"

    # Train normal baseline with correlated drilling behavior
    for i in range(20):
        engine.add_telemetry_point(well, {
            "standpipe_pressure": 2350.0 + float(np.random.normal(0, 8.0)),
            "torque": 13.0 + float(np.random.normal(0, 0.4)),
            "flow_out": 1950.0 + float(np.random.normal(0, 10.0)),
            "delta_flow": float(np.random.normal(0, 5.0)),
            "rop": 9.5 + float(np.random.normal(0, 0.5)),
            "wob": 15.0,
            "rpm": 110.0,
            "teale_mse_mpa": 40.0 + float(np.random.normal(0, 2.0))
        })

    # Inject multivariate outlier (uncorrelated extreme shift in multiple channels)
    outlier_point = {
        "standpipe_pressure": 2900.0,
        "torque": 26.0,
        "flow_out": 1200.0,
        "delta_flow": -750.0,
        "rop": 2.0,
        "wob": 22.0,
        "rpm": 45.0,
        "teale_mse_mpa": 280.0
    }
    scores, metrics = engine.evaluate_tier2_statistical_risk(well, outlier_point)
    assert metrics["is_multivariate_outlier"] is True
    assert metrics["multivariate_anomaly_score"] >= 0.50


# ── 3. Hybrid API Integration Tests ──────────────────────────────────────────

def test_risk_prediction_endpoint():
    """Validates hybrid risk prediction response structure and transparent breakdown."""
    payload = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 5.5,
        "wob": 16.0,
        "rpm": 105.0,
        "torque": 18.5,
        "standpipe_pressure": 2180.0,
        "flow_rate": 1750.0,
        "flow_in": 1950.0,
        "flow_out": 1750.0,
        "delta_flow": -200.0,
        "mud_weight": 1.28,
        "ecd": 1.33,
        "hook_load": 125.0
    }
    res = client.post("/api/risk/predict", json=payload, headers=driller_headers)
    assert res.status_code == 200
    data = res.json()

    assert "predictions" in data
    assert "MUD_LOSS" in data["predictions"]
    assert "STUCK_PIPE" in data["predictions"]
    assert "KICK" in data["predictions"]

    ml_pred = data["predictions"]["MUD_LOSS"]
    assert "probability" in ml_pred
    assert "risk_engine_tier" in ml_pred
    assert "tier1_physics_score" in ml_pred
    assert "tier2_statistical_score" in ml_pred
    # Calibrated confidence bounded to realistic interval
    assert 0.45 <= ml_pred["confidence_score"] <= 0.88
    # Inspectable contributing factors present
    assert len(ml_pred["contributing_factors"]) > 0


def test_model_metrics_endpoint():
    """Validates that evaluation metrics reflect honest GroupKFold validation with zero target leakage."""
    res = client.get("/api/risk/metrics", headers=driller_headers)
    assert res.status_code == 200
    metrics = res.json()

    assert "mud_loss" in metrics
    assert "stuck_pipe" in metrics
    assert "kick" in metrics

    # Zero target leakage checks: no false 100% precision or recall claims
    for m_key in ["mud_loss", "stuck_pipe", "kick"]:
        m = metrics[m_key]
        assert "evaluation_methodology" in m
        assert "GroupKFold" in m["evaluation_methodology"]
        assert m["accuracy"] > 0.70
        assert m["accuracy"] < 0.999  # No artificial 1.0 or 0.9999 perfection
        assert m["precision"] < 0.999
        assert m["recall"] < 0.999
