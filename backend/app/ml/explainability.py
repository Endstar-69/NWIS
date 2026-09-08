"""
NWIS Engineering Physics Warnings Module.

CLASSIFICATION: [A] Real Implementation — Rule-Based Engineering Heuristics

IMPORTANT: This module does NOT implement SHAP (SHapley Additive exPlanations)
or any form of ML model attribution. It generates deterministic, physics-grounded
engineering warnings based on measured telemetry thresholds.

Real SHAP computation is handled by `backend/app/ml/shap_explainer.py` (Phase 7)
and is only active when a trained model is loaded.

Separation of concerns:
  - generate_engineering_warnings()  ← THIS FILE — physics/heuristic rules
  - shap_explainer.py               ← SHAP TreeExplainer on actual RF models (Phase 7)
"""
from typing import List, Dict, Any
from backend.app.schemas.risk import RiskFactorDetail


def generate_engineering_warnings(
    risk_type: str, features: Dict[str, float], probability: float
) -> List[RiskFactorDetail]:
    """
    Generates physics-grounded engineering warnings for a given risk type.

    These warnings are derived from:
    - Measured telemetry deltas (pressure, flow, torque)
    - Teale MSE (Mechanical Specific Energy)
    - ECD vs formation pore-pressure overbalance margin
    - Historical event density in current depth window

    WARNING: contribution_score values are engineering threshold weights, NOT
    SHAP values or ML feature importances. They represent relative severity of
    each physical indicator, not model-attribution scores.

    Returns:
        List[RiskFactorDetail]: Physics-grounded engineering warnings.
    """
    factors: List[RiskFactorDetail] = []
    depth = features.get("depth", 0.0)
    density = features.get("historical_event_density", 0.0)
    spp_delta = features.get("pressure_delta", 0.0)
    torque_delta = features.get("torque_delta", 0.0)
    overbalance = features.get("overbalance_sg", 0.0)
    fmt_score = features.get("formation_risk_score", 0.5)
    flow_delta = features.get("flow_delta", 0.0)
    mse = features.get("mse", 0.0)

    if risk_type == "MUD_LOSS":
        if density >= 2:
            factors.append(RiskFactorDetail(
                factor_name="Historical Offset Loss Zone Overlap",
                impact_level="HIGH",
                description=(
                    f"Current depth window ({int(depth-50)}–{int(depth+50)} m) has "
                    f"{int(density)} recorded loss events in offset well database. "
                    f"[Source: historical_event_density feature]"
                ),
                contribution_score=0.40
            ))
        if spp_delta < -40 or flow_delta < -30:
            factors.append(RiskFactorDetail(
                factor_name="Hydraulic Telemetry Drop",
                impact_level="HIGH",
                description=(
                    f"Standpipe pressure delta ({spp_delta:.1f} psi) and flow rate "
                    f"delta ({flow_delta:.1f} LPM) exhibit loss signature pattern. "
                    f"[Physics: pressure/flow decrease = potential formation loss]"
                ),
                contribution_score=0.35
            ))
        if fmt_score >= 0.8:
            factors.append(RiskFactorDetail(
                factor_name="High-Permeability Sand/Limestone Horizon",
                impact_level="MEDIUM",
                description=(
                    "Penetrating high-permeability Barail/Sylhet horizon with reduced "
                    "fracture gradient margin. [Source: formation_risk_score lookup table]"
                ),
                contribution_score=0.25
            ))

    elif risk_type == "STUCK_PIPE":
        if torque_delta > 1.5:
            factors.append(RiskFactorDetail(
                factor_name="Rotary Torque Trend Surge",
                impact_level="HIGH",
                description=(
                    f"Rotary torque delta spiked by +{torque_delta:.2f} kNm above rolling "
                    f"average, indicating hole drag or wall contact. "
                    f"[Physics: torque increase = drag/differential sticking indicator]"
                ),
                contribution_score=0.38
            ))
        if overbalance > 0.15:
            factors.append(RiskFactorDetail(
                factor_name="High Overbalance Margin",
                impact_level="HIGH",
                description=(
                    f"Effective mud overbalance is {overbalance:.2f} SG "
                    f"(~{int(overbalance*1420)} psi differential), elevating differential "
                    f"sticking risk against permeable formation. "
                    f"[Physics: ECD - pore_pressure_gradient > 0.15 SG]"
                ),
                contribution_score=0.32
            ))
        if mse > 400:
            factors.append(RiskFactorDetail(
                factor_name="Elevated Mechanical Specific Energy (MSE)",
                impact_level="MEDIUM",
                description=(
                    f"MSE is {mse:.1f} MPa (Teale formula), indicating poor drilling "
                    f"efficiency and potential bit balling or pack-off. "
                    f"[Physics: Teale MSE = axial + rotational energy per unit volume drilled]"
                ),
                contribution_score=0.20
            ))

    elif risk_type == "KICK":
        if overbalance < 0.03 and depth > 2800:
            factors.append(RiskFactorDetail(
                factor_name="Narrow Overbalance Margin",
                impact_level="HIGH",
                description=(
                    f"ECD operating near pore pressure threshold — overbalance is only "
                    f"{overbalance:.3f} SG margin. At depth {depth:.0f}m this creates "
                    f"underbalanced conditions favoring influx. "
                    f"[Physics: ECD - pore_pressure_gradient < 0.03 SG]"
                ),
                contribution_score=0.45
            ))
        if flow_delta > 40:
            factors.append(RiskFactorDetail(
                factor_name="Flow-Out Gain Anomaly",
                impact_level="HIGH",
                description=(
                    f"Return flow rate increased by +{flow_delta:.1f} LPM over baseline — "
                    f"potential formation fluid influx indicator. "
                    f"[Physics: flow_out > flow_in = potential kick signature]"
                ),
                contribution_score=0.35
            ))
        if fmt_score >= 0.75:
            factors.append(RiskFactorDetail(
                factor_name="Gas-Bearing Overpressured Transition Zone",
                impact_level="MEDIUM",
                description=(
                    "Formation risk score indicates high-pressure transition horizon. "
                    "[Source: formation_risk_score lookup table for Kopili/Barail]"
                ),
                contribution_score=0.20
            ))

    # Fallback: parameters within normal operating envelope
    if not factors:
        factors.append(RiskFactorDetail(
            factor_name="Baseline Operating Parameters",
            impact_level="LOW",
            description=(
                "No physics threshold violations detected. Parameters currently conform "
                "to standard operating envelope. Continued monitoring recommended."
            ),
            contribution_score=0.10
        ))

    return factors


# Backwards-compatibility alias for existing code that calls generate_risk_explanations
def generate_risk_explanations(
    risk_type: str, features: Dict[str, float], probability: float
) -> List[RiskFactorDetail]:
    """
    Deprecated alias for generate_engineering_warnings().
    Use generate_engineering_warnings() in new code.
    """
    return generate_engineering_warnings(risk_type, features, probability)
