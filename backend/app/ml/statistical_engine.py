"""
NWIS Rolling Statistical & Multivariate Anomaly Engine — Phase 3 Implementation.

CLASSIFICATION: [A] Real Implementation (Tier 2 Statistical Engine).
Implements rolling univariate Z-score analysis and unsupervised Isolation Forest anomaly detection.

Features:
  1. Rolling history buffer per well_id (retains last 60 observations).
  2. Univariate rolling Z-score detection across drilling channels:
     - Standpipe Pressure (SPP)
     - Rotary Torque
     - Flow Rate / Delta Flow
     - Rate of Penetration (ROP)
     - Teale MSE
  3. Multivariate Isolation Forest anomaly detection for non-linear correlation shifts.
  4. Statistical risk scores mapped to MUD_LOSS, STUCK_PIPE, and KICK signatures.
"""

import math
from collections import deque
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from sklearn.ensemble import IsolationForest

FEATURE_NAMES = ["spp", "torque", "flow", "rop", "wob", "rpm", "mse"]


def _safe_float(val: Any, default: float) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


class RollingStatisticalEngine:
    """
    Maintains time-series telemetry windows per active well and computes
    rolling Z-scores and Isolation Forest anomaly scores.
    """

    def __init__(self, buffer_maxlen: int = 60, min_history_for_isoforest: int = 12):
        self.buffer_maxlen = buffer_maxlen
        self.min_history_for_isoforest = min_history_for_isoforest
        # Map: well_id -> deque of feature dictionaries
        self._buffers: Dict[str, deque] = {}
        # Cached fitted Isolation Forest models per well
        self._models: Dict[str, IsolationForest] = {}

    def get_or_create_buffer(self, well_id: str) -> deque:
        if well_id not in self._buffers:
            self._buffers[well_id] = deque(maxlen=self.buffer_maxlen)
        return self._buffers[well_id]

    def clear_buffer(self, well_id: str):
        if well_id in self._buffers:
            self._buffers[well_id].clear()
        if well_id in self._models:
            del self._models[well_id]

    def add_telemetry_point(self, well_id: str, point: Dict[str, float]):
        """Appends a normalized vector to the active buffer."""
        buf = self.get_or_create_buffer(well_id)
        flow_val = point.get("flow_out")
        if flow_val is None:
            flow_val = point.get("flow_rate")

        vec = {
            "spp": _safe_float(point.get("standpipe_pressure", point.get("spp")), 2350.0),
            "torque": _safe_float(point.get("torque"), 13.0),
            "flow": _safe_float(flow_val, 1950.0),
            "delta_flow": _safe_float(point.get("delta_flow"), 0.0),
            "rop": _safe_float(point.get("rop"), 9.5),
            "wob": _safe_float(point.get("wob"), 15.0),
            "rpm": _safe_float(point.get("rpm"), 110.0),
            "mse": _safe_float(point.get("teale_mse_mpa", point.get("mse")), 40.0),
        }
        buf.append(vec)

    def evaluate_tier2_statistical_risk(
        self, well_id: str, current_point: Dict[str, Any]
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Calculates rolling Z-scores and Isolation Forest outlier status for the current point.
        
        Returns:
            statistical_scores: { "MUD_LOSS": float, "STUCK_PIPE": float, "KICK": float }
            stats_metrics: details containing z_scores, isolation_forest_outlier, etc.
        """
        # Ensure current point is registered in buffer
        self.add_telemetry_point(well_id, current_point)
        buf = self.get_or_create_buffer(well_id)
        n_samples = len(buf)

        # Baseline default return when buffer is warming up
        if n_samples < 4:
            return (
                {"MUD_LOSS": 0.10, "STUCK_PIPE": 0.10, "KICK": 0.10},
                {
                    "buffer_samples": n_samples,
                    "z_scores": {},
                    "is_multivariate_outlier": False,
                    "multivariate_anomaly_score": 0.0,
                    "engine_status": "WARMING_UP",
                },
            )

        # Extract numpy matrix of historical features
        history = list(buf)
        spp_vals = np.array([p["spp"] for p in history])
        torque_vals = np.array([p["torque"] for p in history])
        flow_vals = np.array([p["flow"] for p in history])
        delta_flow_vals = np.array([p["delta_flow"] for p in history])
        rop_vals = np.array([p["rop"] for p in history])
        mse_vals = np.array([p["mse"] for p in history])

        curr_flow_val = current_point.get("flow_out")
        if curr_flow_val is None:
            curr_flow_val = current_point.get("flow_rate")

        curr_spp = _safe_float(current_point.get("standpipe_pressure", current_point.get("spp")), float(spp_vals[-1]))
        curr_torque = _safe_float(current_point.get("torque"), float(torque_vals[-1]))
        curr_flow = _safe_float(curr_flow_val, float(flow_vals[-1]))
        curr_delta_flow = _safe_float(current_point.get("delta_flow"), float(delta_flow_vals[-1]))
        curr_rop = _safe_float(current_point.get("rop"), float(rop_vals[-1]))
        curr_mse = _safe_float(current_point.get("teale_mse_mpa", current_point.get("mse")), float(mse_vals[-1]))

        # Calculate Univariate Z-scores: Z = (x - mean) / (std + eps)
        # Using the past window (excluding current if enough samples, else full)
        def compute_z(val: float, arr: np.ndarray, min_std: float = 1.0) -> float:
            mu = float(np.mean(arr))
            sigma = max(min_std, float(np.std(arr)))
            return round(float((val - mu) / sigma), 2)

        z_spp = compute_z(curr_spp, spp_vals, min_std=15.0)
        z_torque = compute_z(curr_torque, torque_vals, min_std=0.8)
        z_flow = compute_z(curr_flow, flow_vals, min_std=12.0)
        z_delta_flow = compute_z(curr_delta_flow, delta_flow_vals, min_std=8.0)
        z_rop = compute_z(curr_rop, rop_vals, min_std=0.6)
        z_mse = compute_z(curr_mse, mse_vals, min_std=5.0)

        z_scores = {
            "z_standpipe_pressure": z_spp,
            "z_rotary_torque": z_torque,
            "z_flow_out": z_flow,
            "z_delta_flow": z_delta_flow,
            "z_rop": z_rop,
            "z_teale_mse": z_mse,
        }

        # ── Multivariate Isolation Forest Outlier Analysis ────────────────────
        is_outlier = False
        anomaly_score = 0.0

        if n_samples >= self.min_history_for_isoforest:
            try:
                # Build feature matrix (N x 7)
                X = np.column_stack([
                    spp_vals,
                    torque_vals,
                    flow_vals,
                    rop_vals,
                    np.array([p["wob"] for p in history]),
                    np.array([p["rpm"] for p in history]),
                    mse_vals,
                ])

                # Fit or retrieve model
                clf = IsolationForest(
                    n_estimators=35,
                    contamination=0.10,
                    random_state=42,
                    n_jobs=1
                )
                clf.fit(X)
                self._models[well_id] = clf

                current_vec = np.array([[
                    curr_spp,
                    curr_torque,
                    curr_flow,
                    curr_rop,
                    float(current_point.get("wob", 15.0)),
                    float(current_point.get("rpm", 110.0)),
                    curr_mse,
                ]])

                pred = clf.predict(current_vec)[0]  # -1 for anomaly, 1 for inlier
                raw_decision = float(clf.decision_function(current_vec)[0])
                # Normalize decision function to [0, 1] anomaly score:
                # raw_decision > 0 -> inlier; raw_decision < 0 -> outlier
                anomaly_score = round(float(np.clip(0.5 - raw_decision * 2.5, 0.0, 1.0)), 2)
                is_outlier = bool(pred == -1 or anomaly_score >= 0.65)
            except Exception:
                is_outlier = False
                anomaly_score = 0.0

        # ── Map Statistical Anomalies to Drilling Hazards ──────────────────────
        # Mud Loss: driven by negative SPP delta/Z-score and negative Flow Z-score
        mud_loss_stat = 0.08
        if z_delta_flow < -2.0 or z_flow < -2.2:
            mud_loss_stat += 0.40
        if z_spp < -2.0:
            mud_loss_stat += 0.30
        if is_outlier and (z_flow < -1.5 or z_spp < -1.5):
            mud_loss_stat += 0.20
        mud_loss_stat = round(float(np.clip(mud_loss_stat, 0.05, 0.95)), 2)

        # Stuck Pipe: driven by positive Torque Z-score, positive MSE Z-score, and positive SPP Z-score
        stuck_pipe_stat = 0.08
        if z_torque > 2.2:
            stuck_pipe_stat += 0.45
        elif z_torque > 1.6:
            stuck_pipe_stat += 0.25
        if z_mse > 2.0:
            stuck_pipe_stat += 0.25
        if z_spp > 2.0:
            stuck_pipe_stat += 0.20
        if is_outlier and (z_torque > 1.5 or z_mse > 1.5):
            stuck_pipe_stat += 0.15
        stuck_pipe_stat = round(float(np.clip(stuck_pipe_stat, 0.05, 0.95)), 2)

        # Kick / Influx: driven by positive Flow Z-score, positive ROP Z-score, and negative SPP Z-score
        kick_stat = 0.06
        if z_delta_flow > 2.0 or z_flow > 2.2:
            kick_stat += 0.45
        if z_rop > 2.0:
            kick_stat += 0.25
        if is_outlier and (z_delta_flow > 1.5 or z_flow > 1.5):
            kick_stat += 0.20
        kick_stat = round(float(np.clip(kick_stat, 0.05, 0.95)), 2)

        statistical_scores = {
            "MUD_LOSS": mud_loss_stat,
            "STUCK_PIPE": stuck_pipe_stat,
            "KICK": kick_stat,
        }

        stats_metrics = {
            "buffer_samples": n_samples,
            "z_scores": z_scores,
            "is_multivariate_outlier": is_outlier,
            "multivariate_anomaly_score": anomaly_score,
            "engine_status": "ACTIVE",
        }

        return statistical_scores, stats_metrics


# Global singleton statistical engine instance
statistical_engine = RollingStatisticalEngine()
