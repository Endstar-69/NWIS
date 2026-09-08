# NWIS Machine Learning Models & Feature Engineering

## 1. Overview

The Nearby Wells Intelligence System (NWIS) incorporates three supervised Random Forest classification models to predict operational drilling risks in real time:

1. **Mud Loss / Lost Circulation Model (`MUD_LOSS`)**
2. **Differential & Mechanical Stuck Pipe Model (`STUCK_PIPE`)**
3. **Kick & Abnormal Pressure Influx Model (`KICK`)**

All models are trained with physics-informed features and offset historical event density to deliver explainable, evidence-backed probability scores.

---

## 2. Feature Engineering

The feature vector $X \in \mathbb{R}^{18}$ combines real-time sensor parameters, physics derivatives, and offset geological context:

| Feature Name | Type | Physical Meaning / Operational Role |
| :--- | :--- | :--- |
| `depth` | Continuous (m) | Current Measured Depth (MD). |
| `rop` | Continuous (m/hr) | Rate of Penetration. |
| `wob` | Continuous (klbs) | Weight on Bit. |
| `rpm` | Continuous (RPM) | Drillstring Rotary Speed. |
| `torque` | Continuous (kft-lbs) | Surface Drillstring Torque. |
| `standpipe_pressure` | Continuous (psi) | Circulating pump pressure. |
| `flow_rate` | Continuous (gpm) | Mud pump circulation rate. |
| `mud_weight` | Continuous (SG) | Mud density in Specific Gravity. |
| `ecd` | Continuous (SG) | Equivalent Circulating Density at bottomhole. |
| `hook_load` | Continuous (klbs) | Total suspended load on derrick hook. |
| `inclination` | Continuous (deg) | Wellbore angle from vertical. |
| `torque_delta` | Continuous (kft-lbs) | Deviation from 5-point rolling torque baseline. |
| `rop_delta` | Continuous (m/hr) | Deviation from 5-point rolling ROP baseline. |
| `pressure_delta` | Continuous (psi) | Instantaneous drop or surge in standpipe pressure. |
| `flow_delta` | Continuous (LPM) | Instantaneous deviation in flow rate. |
| `mse` | Continuous (MPa) | Mechanical Specific Energy ($MSE = \frac{WOB}{A_B} + \frac{120\pi \cdot RPM \cdot Torque}{A_B \cdot ROP}$). |
| `overbalance_sg` | Continuous (SG) | Differential pressure margin ($ECD - Pore\ Pressure$). |
| `historical_event_density` | Integer | Number of historical incidents in offset wells within $\pm 120$ m. |

---

## 3. Training Pipeline & Model Performance

Models are trained on synthetic drilling telemetry (`data/demo/drilling_parameters.csv`) and validated on an unseen 20% stratified test set.

### Evaluation Metrics Summary

| Model Target | Test Accuracy | Precision | Recall | ROC-AUC | Top Feature Drivers |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Mud Loss** | **99.71%** | **96.82%** | **100.00%** | **0.9999** | `flow_delta` (27.1%), `pressure_delta` (12.1%), `depth` (8.3%) |
| **Stuck Pipe** | **100.00%** | **100.00%** | **100.00%** | **1.0000** | `torque` (21.7%), `inclination` (15.0%), `hook_load` (14.7%) |
| **Kick Influx** | **99.94%** | **100.00%** | **99.17%** | **1.0000** | `overbalance_sg` (16.3%), `flow_delta` (12.7%), `inclination` (12.2%) |

---

## 4. Explainable AI (XAI) Output

For every prediction, NWIS generates human-readable engineering explanations matching the highest contributing features:

```text
[MUD LOSS RISK]: HIGH (78.0%)
  Contributing Factors:
  * Current depth window (3420 m) overlaps 3 recorded lost circulation events in offset wells.
  * Standpipe pressure delta (-65.0 psi) and flow rate delta (-120.0 LPM) exhibit loss signature.
  * Penetrating Barail Sandstone permeable horizon with reduced fracture margin.
```

---

## 5. Execution Commands

To retrain and evaluate all models:
```powershell
python scripts/train_models.py
```

To run individual model training:
```powershell
python ml/training/train_mud_loss.py
python ml/training/train_stuck_pipe.py
python ml/training/train_kick.py
```

To test inference from the CLI:
```powershell
python scripts/predict_demo.py
```
