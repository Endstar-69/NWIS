"""
Unit and Integration Tests for Phase 7 — Genuine Explainability with SHAP.
"""

import pytest
import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ml.shap_explainer import shap_explainer, ShapExplainerEngine
from backend.app.ml.explainability import generate_engineering_warnings
from backend.app.ml.inference import inference_engine
from backend.app.schemas.risk import FeatureShapAttribution, ModelShapExplanation
from backend.app.core.database import SessionLocal

client = TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_shap_explainer_availability():
    assert shap_explainer.is_available is True


def test_shap_explainer_on_benchmark_models():
    # Test for each benchmark model in artifacts
    risk_models = {
        "MUD_LOSS": "artifacts/models/mud_loss_model.joblib",
        "STUCK_PIPE": "artifacts/models/stuck_pipe_model.joblib",
        "KICK": "artifacts/models/kick_model.joblib"
    }

    for risk_type, model_path in risk_models.items():
        model = joblib.load(model_path)
        feature_names = list(model.feature_names_in_)

        # Create a representative feature sample
        sample_dict = {feat: 0.0 for feat in feature_names}
        sample_dict.update({
            "depth": 3450.0,
            "torque_delta": 2.5,
            "pressure_delta": -45.0,
            "flow_delta": 35.0,
            "overbalance_sg": 0.18,
            "mse": 420.0,
            "formation_risk_score": 0.85,
            "historical_event_density": 3.0
        })
        df_sample = pd.DataFrame([sample_dict])[feature_names]

        explanation = shap_explainer.explain_prediction(risk_type, model, df_sample, top_n=6)
        assert explanation is not None
        assert isinstance(explanation, ModelShapExplanation)
        assert 0.0 <= explanation.base_value <= 1.0
        assert 0.0 <= explanation.prediction_value <= 1.0
        assert len(explanation.top_features) == 6

        # Check top feature attributes
        top_feat = explanation.top_features[0]
        assert isinstance(top_feat, FeatureShapAttribution)
        assert top_feat.feature_name in feature_names
        assert top_feat.impact_direction in ["INCREASES_RISK", "DECREASES_RISK", "NEUTRAL"]
        assert top_feat.absolute_importance == pytest.approx(abs(top_feat.shap_value), rel=1e-3)


def test_shap_mathematical_additive_property():
    """Verifies Shapley efficiency/additivity: E[f(x)] + sum(phi_i) = f(x)."""
    model = joblib.load("artifacts/models/mud_loss_model.joblib")
    explainer = shap_explainer.get_explainer("MUD_LOSS", model)
    assert explainer is not None

    sample_dict = {feat: 1.0 for feat in model.feature_names_in_}
    sample_dict["pressure_delta"] = -60.0
    sample_dict["flow_delta"] = -40.0
    df_sample = pd.DataFrame([sample_dict])[list(model.feature_names_in_)]

    shap_raw = explainer.shap_values(df_sample)
    class1_shap = shap_raw[0, :, 1]
    base_val = float(explainer.expected_value[1])
    reconstructed_pred = base_val + float(np.sum(class1_shap))

    actual_pred = float(model.predict_proba(df_sample)[0][1])
    assert reconstructed_pred == pytest.approx(actual_pred, abs=1e-5)


def test_clean_separation_physics_warnings_vs_shap():
    """Verifies that engineering warnings and SHAP attributions are cleanly separated."""
    telemetry = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 12.5,
        "wob": 14.0,
        "rpm": 120.0,
        "torque": 22.0,
        "standpipe_pressure": 2450.0,
        "flow_rate": 2100.0,
        "mud_weight": 1.25,
        "ecd": 1.32,
        "hook_load": 110.0,
        "inclination": 12.0,
        "azimuth": 45.0
    }

    # Run inference engine
    predictions = inference_engine.predict_risk(telemetry, historical_events=[])

    for r_type in ["MUD_LOSS", "STUCK_PIPE", "KICK"]:
        p = predictions[r_type]

        # 1. Engineering warnings must be present and physics-grounded
        assert hasattr(p, "engineering_warnings")
        assert isinstance(p.engineering_warnings, list)
        assert len(p.engineering_warnings) > 0
        for w in p.engineering_warnings:
            assert hasattr(w, "contribution_score")
            assert w.impact_level in ["HIGH", "MEDIUM", "LOW"]

        # 2. SHAP attributions must be computed from TreeExplainer
        assert hasattr(p, "shap_attribution")
        assert p.shap_attribution is not None
        assert p.shap_attribution.methodology == "TreeExplainer (Tree SHAP exact feature attribution)"
        assert len(p.shap_attribution.top_features) > 0

        # 3. shap_summary must map feature names to numerical float SHAP values
        assert hasattr(p, "shap_summary")
        assert isinstance(p.shap_summary, dict)
        assert len(p.shap_summary) > 0


def test_explain_endpoint_integration(driller_headers):
    payload = {
        "well_id": "WELL-001",
        "depth": 3420.0,
        "formation_name": "Barail Sandstone",
        "rop": 12.0,
        "wob": 15.0,
        "rpm": 110.0,
        "torque": 24.0,
        "standpipe_pressure": 2300.0,
        "flow_rate": 2050.0,
        "mud_weight": 1.25,
        "ecd": 1.30,
        "hook_load": 115.0
    }

    resp = client.post("/api/risk/explain", json=payload, headers=driller_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["well_id"] == "WELL-001"
    assert "shap_explanations" in data
    assert "engineering_warnings" in data
    assert "MUD_LOSS" in data["shap_explanations"]
    assert "STUCK_PIPE" in data["shap_explanations"]
    assert "KICK" in data["shap_explanations"]

    # Verify mud loss explanation contains top features
    ml_exp = data["shap_explanations"]["MUD_LOSS"]
    assert ml_exp is not None
    assert "base_value" in ml_exp
    assert "prediction_value" in ml_exp
    assert len(ml_exp["top_features"]) > 0


def test_explain_endpoint_rbac(viewer_headers):
    payload = {
        "well_id": "WELL-001",
        "depth": 3400.0,
        "formation_name": "Barail Sandstone",
        "rop": 10.0, "wob": 10.0, "rpm": 100.0, "torque": 15.0,
        "standpipe_pressure": 2500.0, "flow_rate": 2100.0, "mud_weight": 1.2, "ecd": 1.25,
        "hook_load": 100.0
    }

    # Viewer should be forbidden (403) from /api/risk/explain (requires engineer)
    resp_viewer = client.post("/api/risk/explain", json=payload, headers=viewer_headers)
    assert resp_viewer.status_code == 403

    # Unauthenticated should receive 401
    resp_anon = client.post("/api/risk/explain", json=payload)
    assert resp_anon.status_code == 401
