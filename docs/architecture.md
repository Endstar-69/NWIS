# NWIS Architecture & System Design

## 1. System Overview

The **Nearby Wells Intelligence System (NWIS)** is an AI/ML-driven decision-support platform engineered to provide institutional memory from offset and historical wells directly into active drilling operations alongside OIL India's **eRTMAC** (enhanced Real-Time Monitoring and Analytics Centre) concept.

```text
+-----------------------------------------------------------------------------------+
|                                 NWIS REACT FRONTEND                               |
|   (Vite + React 18 + TypeScript + Tailwind CSS + Lucide Icons + Recharts + Leaflet)|
+-----------------------------------------------------------------------------------+
             |                                              ^
             | REST APIs (HTTP / JSON)                      | Live WebSocket Stream
             v                                              |
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND APP                                |
|   * Core Auth & JWT Security        * Geospatial Spatial Engine (Haversine/PostGIS)|
|   * Offset Well Correlation Engine  * Rule + ML Risk Prediction Engine            |
|   * Proactive Alert Engine          * Decision-Support Recommendation Engine      |
+-----------------------------------------------------------------------------------+
      |                      |                       |                     |
      v                      v                       v                     v
+------------+       +---------------+       +---------------+     +---------------+
| SQLITE /   |       |  DOCUMENT NLP |       | ML RISK ENGINE|     | TELEMETRY     |
| POSTGRESQL |       |  EXTRACTION   |       |  (Scikit-Learn|     | SIMULATOR     |
| (Relational|       |  & EMBEDDINGS |       |   Models)     |     | (eRTMAC Live  |
|  Database) |       |  (Cosine RAG) |       |               |     |  Stream Stub) |
+------------+       +---------------+       +---------------+     +---------------+
```

---

## 2. Component Architecture

### A. Frontend Layer (`frontend/`)
- **Framework**: Vite + React 18 + TypeScript.
- **Styling**: Tailwind CSS with industrial dark/light high-contrast engineering aesthetics.
- **Mapping**: Leaflet with OpenStreetMap tiles, customizable offset radius rings (1km, 5km, 10km, 25km, 50km), and dynamic well marker clustering.
- **Charts & Telemetry**: Recharts dynamic time/depth plots for ROP, WOB, RPM, Torque, SPP, Flow Rate, Mud Weight, and ECD.
- **Real-Time Subscription**: Native WebSocket client auto-reconnecting to `/ws/well/{well_id}`.

### B. Backend Layer (`backend/app/`)
- **FastAPI**: Async ASGI application exposing REST endpoints and WebSockets.
- **Services Architecture**:
  - `WellService`: Spatial distance calculations, offset well similarity scoring, and trajectory interpolation.
  - `RiskService`: Dynamic ML feature extraction and inference invocation across Mud Loss, Stuck Pipe, and Kick models.
  - `AlertEngine`: Multi-parameter threshold monitoring and offset risk correlation generating `INFO`, `WATCH`, `HIGH`, and `CRITICAL` alerts.
  - `RecommendationEngine`: Evidence-grounded operational guidance linking offset incidents to actionable mitigations.
  - `SearchService` & `RAGAssistant`: Semantic cosine similarity vector search + keyword search with strict zero-hallucination guardrails.
  - `DocumentExtractor`: Deterministic and NLP regex extraction pipeline for Daily Drilling Reports (DDR) and Well Completion Reports (WCR).

### C. Data & ML Pipeline (`ml/`, `scripts/`, `artifacts/`)
- **Synthetic Data Engine**: Reproducible data generator modeling 30 synthetic wells in the Assam-Arakan basin with 10 geological formations (Alluvium to Disang), 173 historical events, and 8,760 parameter points.
- **Machine Learning Models**:
  - `mud_loss_model.joblib`: Random Forest Classifier predicting lost circulation risks based on pressure deltas, flow rate drops, and permeable horizon crossings.
  - `stuck_pipe_model.joblib`: Random Forest Classifier identifying differential and mechanical sticking risk from torque spikes, overbalance, and Mechanical Specific Energy (MSE).
  - `kick_model.joblib`: Random Forest Classifier detecting gas influx and abnormal formation pore pressure regimes.

---

## 3. Data Flow Diagram

```text
[Historical Reports: PDF / DDR / WCR]
                  │
                  ▼
         [Document Extractor]
                  │
                  ├──> [Structured Events Table] (SQLite / PostgreSQL)
                  │
                  └──> [Text Embeddings Vector Space] (Normalized Cosine)
                             │
                             ▼
[Active Well Telemetry] ────> [ML Feature Builder] (Rolling deltas, MSE, Offset density)
         │                           │
         │                           ▼
         │                 [ML Inference Models] (Mud Loss, Stuck Pipe, Kick)
         │                           │
         ▼                           ▼
[Geospatial Engine] ───────> [Proactive Alert Engine]
 (Radius & Similarity)               │
                                     ▼
                      [Evidence-Linked Recommendations]
                                     │
                                     ▼
                       [Interactive NWIS Dashboard]
```

---

## 4. Security & Governance

1. **Authentication**: JWT token-based authentication with role-based access control (`Admin`, `Drilling Engineer`, `Geologist`, `Supervisor`, `Viewer`).
2. **Data Integrity & Labeling**:
   - All synthetic records are tagged with `is_demo_data = True`.
   - The UI displays an unmissable banner: `DEMO ENVIRONMENT - SYNTHETIC DATA`.
   - AI outputs include clear disclaimers: `DECISION SUPPORT ONLY - NOT AN AUTONOMOUS DRILLING COMMAND`.
3. **Audit Trail**: Action logging for search queries, alert acknowledgments, and report ingestions stored in `audit_logs`.
