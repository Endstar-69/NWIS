# NWIS — System Classification & Capability Provenance Registry

**Version:** Phase 0 (Truth & Baseline Cleanup)
**Date:** September 2026
**Purpose:** Mandatory provenance disclosure for all subsystems per SIH evaluation criteria.

---

## Classification Framework

| Code | Meaning |
|------|---------|
| **[A]** | Real Implementation — genuinely implemented and working |
| **[B]** | Physics-Based Simulation — real formulae, synthetic input parameters |
| **[C]** | Synthetic Demo/Reference Data — representative dataset for demonstration |
| **[D]** | Optional Enterprise Integration — planned; requires external system |

---

## Backend Subsystem Classification

### Core Infrastructure

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| SQLAlchemy ORM + SQLite | `core/database.py` | **[A]** | Production-ready |
| FastAPI routing | `main.py`, `api/*.py` | **[A]** | All routes functional |
| Pydantic schemas + validation | `schemas/*.py` | **[A]** | Type-validated |
| Docker Compose environment | `docker-compose.yml` | **[A]** | Requires PostgreSQL for prod |
| JWT token creation/verification | `core/security.py` | **[A] partial** | JWT decode works; bcrypt added Phase 1 |
| RBAC (Role-Based Access Control) | `api/auth.py` | **[D] planned** | Routes unprotected until Phase 1 |
| Audit Logging | — | **[D] planned** | Not yet implemented |

### Data Layer

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| 30-well demo dataset | `scripts/seed_*.py` | **[C]** | Synthetically generated |
| 173 historical events | `scripts/seed_events.py` | **[C]** | Modelled on Assam-Arakan field patterns |
| Formation stratigraphic table | `models/well.py::Formation` | **[C]** | Domain-representative depth ranges |
| Haversine distance calculation | `services/similarity_service.py` | **[A]** | Correct geodetic formula |

### Real-Time Telemetry

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| WebSocket manager | `realtime/websocket_manager.py` | **[A]** | Real WebSocket broadcast (`/ws/telemetry/{id}`, `/ws/well/{id}`) |
| Drilling stream simulator | `simulator/drilling_stream.py` | **[B]** | Physics-grounded simulation with Gaussian noise, hydrostatic drift & dynamic progression |
| Scenario Engine (4 Scenarios) | `simulator/drilling_stream.py` | **[B]** | Completed Phase 2: Normal Drilling, Lost Circulation, Gas Kick Influx, Stuck Pipe Pack-off |
| Telemetry Provenance Metadata | `simulator/drilling_stream.py`, `schemas/simulator.py` | **[A]** | Completed Phase 2: Explicit `provenance` block on every packet with `[B]` classification |
| Simulator Control REST API | `api/simulator.py` | **[A]** | Completed Phase 2: RBAC-enforced configure, reset, status, scenarios, and manual tick |
| Broadcast loop | `realtime/stream_handler.py` | **[A]** | Real async broadcasting to well and global channels |

### Risk Intelligence

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| Tier 1 Deterministic Physics Engine | `ml/physics_engine.py` | **[A]** | Completed Phase 3: Teale MSE, hydraulic balance, overbalance/fracture margins, pressure/flow deltas |
| Teale MSE formula | `ml/physics_engine.py::calculate_teale_mse` | **[A]** | Completed Phase 3: Axial + rotational components in MPa & psi |
| Hydraulic Balance & Pore Pressure | `ml/physics_engine.py::calculate_hydraulic_balance` | **[A]** | Completed Phase 3: Hubbert-Willis fracture gradient, BHP, overbalance margin |
| Tier 2 Rolling Statistical Engine | `ml/statistical_engine.py` | **[A]** | Completed Phase 3: Rolling Z-scores (SPP, torque, flow, ROP, MSE) + Isolation Forest anomaly detection |
| Hybrid Risk Aggregation | `ml/inference.py` | **[A]** | Completed Phase 3: Blended physics-informed and statistical probabilities with calibrated confidence |
| Supervised ML Benchmark Models | `artifacts/models/*.joblib`, `scripts/train_models.py` | **[D]** | Completed Phase 3: 5-fold GroupKFold by well_id cross-validation with zero target leakage |
| Evaluation Framework & Metrics | `artifacts/evaluation/model_metrics.json` | **[A]** | Completed Phase 3: Honest GroupKFold cross-validated evaluation metrics (no false 100% claims) |
| Calibrated Confidence Score | `ml/inference.py` | **[A]** | Completed Phase 3: Derived from physics/statistical agreement & sample buffer (bounded 0.45–0.88) |
| Real SHAP explainability | `ml/shap_explainer.py::ShapExplainerEngine` | **[D]** | Completed Phase 7: TreeExplainer exact additive Shapley attributions for supervised benchmark models |

### Explainability / XAI

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| Engineering physics warnings | `ml/explainability.py::generate_engineering_warnings()` | **[A]** | Completed Phase 7: Deterministic mechanics (Teale MSE, ECD, hydraulic balance), strictly separated from ML attribution |
| Tree SHAP value attribution | `ml/shap_explainer.py::ShapExplainerEngine` | **[D]** | Completed Phase 7: Exact additive Shapley feature attributions (phi_i) satisfying efficiency E[f(x)] + sum(phi_i) = f(x) |
| Risk Explainability API Endpoint | `api/risk.py::explain_risk_endpoint` | **[A]** | Completed Phase 7: RBAC-enforced (/api/risk/explain) returning both physics warnings and ML SHAP decomposition |

### Document Intelligence

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| Multi-strategy PDF extraction | `ai/extractor.py::DocumentExtractor` | **[A]** | Completed Phase 5: Cascade from pdfplumber (primary) to pypdf (fallback) to plain text |
| Tabular matrix extraction | `ai/extractor.py` | **[A]** | Completed Phase 5: pdfplumber page.extract_tables() parsing with empty row/col sanitation |
| Physical parameter parsing | `ai/extractor.py::extract_drilling_parameters` | **[A]** | Completed Phase 5: Extracts WOB, RPM, Torque, Mud Weight, SPP, Flow Rate, ROP |
| Depth interval & scalar depth | `ai/extractor.py` | **[A]** | Completed Phase 5: Resolves interval boundaries [start_depth, end_depth] with scalar fallback |
| Entity & narrative extraction | `ai/extractor.py` | **[A]** | Completed Phase 5: Well name, formation, event taxonomy, severity, cause, impact, mitigation, lessons |
| Field provenance mask | `ai/extractor.py` | **[A]** | Completed Phase 5: `extracted_fields_mask` tracks which fields were parsed vs defaulted |
| Calibrated confidence scoring | `ai/extractor.py` | **[A]** | Completed Phase 5: Calibrated from genuinely extracted fields; quality rating HIGH/MED/LOW/FALLBACK |
| Document upload & ingestion API | `api/documents.py`, `services/document_service.py` | **[A]** | Completed Phase 5: RBAC-enforced (/api/documents/upload), chunks, entities, and quality reports |

### Search & Retrieval

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| TF-IDF keyword search | `ai/embeddings.py::KeywordSearchEngine` | **[A]** | Real keyword search with (1,2)-gram TF-IDF and cosine similarity |
| Dense vector embeddings (384-dim) | `ai/dense_retrieval.py::DenseVectorEmbedder` | **[A]** | Completed Phase 6: 384-dim continuous semantic embeddings (neural sentence-transformers or calibrated dense projector) |
| Dense vector index & cache | `ai/dense_retrieval.py::DenseVectorStore` | **[A]** | Completed Phase 6: In-memory dot-product cosine indexing + joblib disk persistence |
| Hybrid dense/sparse retrieval | `ai/dense_retrieval.py::HybridSearchEngine` | **[A]** | Completed Phase 6: Convex combination (alpha * dense + (1-alpha) * sparse) + depth proximity boost |
| Transparent retrieval provenance | `schemas/search.py`, `ai/dense_retrieval.py` | **[A]** | Completed Phase 6: Exposes dense_score, sparse_score, hybrid_score, and retrieval_method |

### RAG Assistant

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| Pluggable RAG Router | `ai/rag_assistant.py::PluggableRAGAssistant` | **[A]** | Completed Phase 6: Dynamic provider resolution with automatic offline fallback |
| Offline structured evidence retrieval | `ai/rag_assistant.py::OfflineStructuredRetrievalProvider` | **[A]** | Completed Phase 6: Deterministic briefing assembly, structured citations, low-evidence refusal |
| LLM-grounded generation (Gemini) | `ai/rag_assistant.py::GeminiRAGProvider` | **[D]** | Completed Phase 6: Grounded in offset evidence via REST API when GEMINI_API_KEY is present |
| LLM-grounded generation (OpenAI) | `ai/rag_assistant.py::OpenAIRAGProvider` | **[D]** | Completed Phase 6: Grounded in offset evidence via REST API when OPENAI_API_KEY is present |
| Strict Evidence Guard | `ai/rag_assistant.py` | **[A]** | Completed Phase 6: Refuses to fabricate responses if evidence similarity is below 0.12 threshold |

### Recommendations

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| Dynamic evidence-grounded recommendations | `services/recommendation_service.py` | **[A]** | Completed Phase 8: Active hazard integration + hybrid vector retrieval of offset mitigations |
| Zero hardcoded recommendation strings | `services/recommendation_service.py` | **[A]** | Completed Phase 8: Fully dynamic titles, summaries, prioritized operational action steps, physics precautions |
| Evidence citations & provenance | `services/recommendation_service.py`, `schemas/alert.py` | **[A]** | Completed Phase 8: Tracks well names, depths, source documents, pages, and calibrated confidence |
| Recommendation REST Endpoints | `api/recommendations.py` | **[A]** | Completed Phase 8: GET /{well_id} (with depth/hazard overrides & cache bypass) and POST /generate |

### Analytics

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| Knowledge graph builder | `services/analytics_service.py::get_knowledge_graph` | **[A]** | Real relationship topology |
| Risk heatmap (event density) | `services/analytics_service.py::get_risk_heatmap` | **[A]** | DB event counts per zone |
| What-if simulation sandbox | `services/analytics_service.py::run_whatif_simulation` | **[B]** | Physics-bounded parameter sweep |
| Daily drilling report | `services/analytics_service.py::generate_daily_intelligence_report` | **[A] fixed** | Phase 0: computed date + risk values |
| Predictive timeline | `services/analytics_service.py::get_predictive_timeline` | **[A] fixed** | Phase 0: dynamic labels from DB |
| Hardcoded date 2026-03-15 | analytics_service.py | ❌ **REMOVED** | Phase 0: `datetime.now()` |
| Hardcoded 86%/82%/16% risk | analytics_service.py | ❌ **REMOVED** | Phase 0: computed from risk engine |
| NPT cost intelligence | `services/analytics_service.py::get_npt_intelligence` | **[A]** | DB event-based NPT calculation |

### Similarity Engine

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| Haversine distance score | `services/similarity_service.py` | **[A]** | Completed Phase 4: Great-circle geodetic formula with linear and exponential variogram decay |
| Depth interval overlap (IoU) | `services/similarity_service.py` | **[A]** | Completed Phase 4: Penetrated depth IoU + active drilling window penetration coverage |
| Stratigraphic formation overlap | `services/similarity_service.py` | **[A]** | Completed Phase 4: Jaccard similarity of penetrated stratigraphic units |
| Lithology rock-class Jaccard | `services/similarity_service.py` | **[A]** | Completed Phase 4: Jaccard similarity of extracted geological rock classes (sandstone, shale, clay, limestone, etc.) |
| Regional geological continuity | `services/similarity_service.py` | **[A]** | Completed Phase 4: Structural continuity multiplier (1.00 same field, 0.85 same basin, 0.65 inter-basin) |
| Reservoir horizon & fluid match | `services/similarity_service.py` | **[A]** | Completed Phase 4: Target penetration Jaccard + fluid compatibility + depth horizon alignment |
| Trajectory profile alignment | `services/similarity_service.py` | **[A]** | Completed Phase 4: Vertical vs Deviated vs Horizontal inclination classification with DLS penalty |
| Historical incident correlation | `services/similarity_service.py` | **[A]** | Completed Phase 4: Severity-weighted hazard frequency vector cosine similarity + incident-free parity |
| Transparent breakdown & disclosure | `services/similarity_service.py`, `schemas/well.py` | **[A]** | Completed Phase 4: Full inspectable sub-scores, formula disclosure, method details, and provenance metadata |

### Authentication

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| JWT creation + JOSE decode | `core/security.py` | **[A]** | Real |
| Login bypass (driller no-token) | `api/auth.py:14-18` | ❌ → **[D] Phase 1** | Will be removed Phase 1 |
| bcrypt password hashing | `core/security.py` | **[D] Phase 1** | Currently SHA-256 with static salt |
| RBAC route enforcement | `api/*.py` | **[D] Phase 1** | Not currently enforced |
| Frontend login bypass | `authContext.tsx:39` | ❌ → **[D] Phase 1** | `demo_token_123` hardcoded |

---

## Frontend Subsystem Classification

| Subsystem | File | Classification | Notes |
|-----------|------|----------------|-------|
| React + Vite SPA build | `frontend/src/` | **[A]** | Real build (TypeScript + Vite bundled clean) |
| Leaflet well map | `pages/NearbyWellsMapPage.tsx` | **[A]** | Real Leaflet map dynamic to selected well & radius |
| Risk dashboard charts | `pages/RiskAnalyticsPage.tsx` | **[A]** | Real chart data from API |
| SHAP Explainability UI | `pages/RiskAnalyticsPage.tsx` | **[A]** | Real Tree SHAP exact feature attributions & physics separation |
| WebSocket telemetry stream | `services/websocket.ts` | **[A]** | Real WebSocket with dynamic wellId reconnect |
| Real JWT Auth & RBAC UI | `store/authContext.tsx` | **[A]** | Completed Phase 1: Real JWT bearer tokens & role restrictions |
| Active Well Context Provider | `store/wellContext.tsx` | **[A]** | Completed Phase 9: Global reactive well, depth, formation, and live telemetry |
| Role-Based UI Gating | Across pages | **[A]** | Completed Phase 9: Viewer role read-only alerts, uploads, and sandbox |

---

## Data Provenance Format

Every API response includes or should include the following fields when data provenance is material:

```json
{
  "data_source": "synthetic_demo_dataset | live_witsml_feed | uploaded_document",
  "retrieval_method": "tfidf_keyword_cosine | dense_vector_cosine | database_query",
  "is_demo_prediction": true,
  "risk_engine_tier": "tier1_physics | tier2_statistical | supervised_ml_benchmark",
  "extraction_quality": "HIGH | MEDIUM | LOW | FALLBACK_DOMINATED",
  "extracted_fields_mask": {"depth": true, "formation": false, ...}
}
```

---

## Known Remaining Limitations (Phase 0)

1. **ML models**: `artifacts/models/*.joblib` trained with target leakage — used as benchmark only, not primary risk engine
2. **Similarity constants**: 0.90/0.70/0.95 not mathematically derived — Phase 4
3. **Authentication**: No bcrypt, no token enforcement — Phase 1
4. **Dense retrieval**: TF-IDF only — Phase 6
5. **SHAP**: No real SHAP computation — Phase 7
6. **Simulator scenarios**: Single-scenario only — Phase 2
7. **LLM generation**: No online RAG — Phase 6
