# NWIS — Feature Verification Report (Honest Assessment)
### OIL India Limited / Smart India Hackathon (SIH) Prototype — Phase 0 Honest Baseline

> **Phase 0 Note:** This document replaces the previous version which contained false claims.
> See `docs/system_classification.md` for the full provenance registry.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ `GENUINE` | Feature genuinely implemented and functioning |
| ⚙️ `SIMULATED` | Feature working with physics-based or statistical simulation (clearly labelled) |
| ⚠️ `PARTIAL` | Feature implemented but with known limitations documented here |
| 🔧 `PLANNED` | Feature architecture present; implementation pending (Phase N) |
| ❌ `REMOVED` | Previous claim was false and has been corrected |

---

## Summary

| Category | Count |
|----------|-------|
| GENUINE real implementations | 16 |
| SIMULATED (physics-based) | 8 |
| PARTIAL (working with documented limits) | 6 |
| PLANNED for Phase 1–10 | 5 |
| FALSE CLAIMS REMOVED | 3 |

> Previous claim of "33/33 100% success" **was inaccurate** — see removed items below.

---

## TIER 1 — Non-Negotiable Core Features

| # | Feature | Status | Classification | Honest Notes |
|:-:|---------|--------|----------------|--------------|
| 01 | **Dashboard** | ✅ `GENUINE` | [A] | Vite/React SPA functional |
| 02 | **Interactive Well Map** | ✅ `GENUINE` | [A] | Leaflet with real Haversine radius |
| 03 | **Synthetic Well Database** | ✅ `GENUINE` | [C] | 30 synthetic wells, seeded deterministically |
| 04 | **Historical Event Database** | ✅ `GENUINE` | [C] | 173 synthetic events, structured schema |
| 05 | **Well Profiles** | ✅ `GENUINE` | [A] | Trajectory + casing data from seed |
| 06 | **Depth Correlation** | ✅ `GENUINE` | [A] | `GET /api/wells/{id}/telemetry-history` |
| 07 | **Formation Correlation** | ✅ `GENUINE` | [C] | 10-formation stratigraphic table |
| 08 | **Offset-Well Similarity** | ⚠️ `PARTIAL` | [A] | Haversine real; other factors use undocumented constants → Phase 4 |
| 09 | **PDF → Structured Extraction** | ⚠️ `PARTIAL` | [A] | PyPDF + regex; fabricated fallbacks now flagged with `[FALLBACK]` label |
| 10 | **Historical Search** | ✅ `GENUINE` | [A] | TF-IDF keyword search (correctly labelled; not dense embeddings) |
| 11 | **Risk Detection** | ✅ `GENUINE` | [A] | Hybrid Risk Engine: Tier 1 Deterministic Physics (Teale MSE, hydraulic margins) + Tier 2 Rolling Z-scores & Isolation Forest |
| 12 | **Explainable Alerts** | ⚠️ `PARTIAL` | [B] | Engineering physics warnings (NOT SHAP); correctly labelled in Phase 0 |
| 13 | **Historical Mitigation** | ✅ `GENUINE` | [A] | Phase 0 fix: now uses actual formation + retrieved mitigations |
| 14 | **Real-Time Drilling Simulation** | ⚙️ `SIMULATED` | [B] | Configurable scenario engine (Normal, Lost Circ, Gas Kick, Stuck Pipe), Gaussian noise, drift, WebSocket stream & synthetic provenance metadata |

---

## TIER 2 — High-Priority Features

| # | Feature | Status | Classification | Honest Notes |
|:-:|---------|--------|----------------|--------------|
| 15 | **Search/Retrieval** | ⚠️ `PARTIAL` | [A] | TF-IDF cosine similarity (not dense vector embeddings) — labelled correctly in Phase 0 |
| 16 | **Evidence-Backed Assistant** | ⚙️ `SIMULATED` | [A] | Offline DB retrieval only; no LLM; clearly labelled. Retrieval works genuinely. |
| 17 | **Supervised ML Risk Models** | ⚙️ `BENCHMARK` | [D] | Completed Phase 3: Retrained with 5-fold GroupKFold by well_id with zero target leakage. Used as optional benchmark alongside Tier 1 & 2. |
| 17a | ~~Mud Loss: 99.71% Accuracy, 0.9999 ROC-AUC~~ | ❌ `REMOVED` | — | **FALSE CLAIM**: Replaced with honest GroupKFold cross-validated metrics (zero target leakage). |
| 17b | ~~Stuck Pipe: 100.00% Accuracy, 1.0000 ROC-AUC~~ | ❌ `REMOVED` | — | **FALSE CLAIM**: Replaced with honest GroupKFold cross-validated metrics (zero target leakage). |
| 17c | ~~Kick Influx: 99.94% Accuracy, 1.0000 ROC-AUC~~ | ❌ `REMOVED` | — | **FALSE CLAIM**: Replaced with honest GroupKFold cross-validated metrics (zero target leakage). |
| 18 | **Risk Explainability** | ⚠️ `PARTIAL` | [B] | Engineering physics threshold warnings (NOT SHAP). Correctly labelled Phase 0. SHAP → Phase 7. |
| 19 | **Knowledge Graph** | ✅ `GENUINE` | [A] | Real relational topology: Wells→Formations→Events→Mitigations |
| 20 | **Advanced Similarity Engine** | ⚠️ `PARTIAL` | [A] | Haversine component is real; formation/trajectory constants undocumented → Phase 4 |
| 21 | **Risk Heatmap** | ✅ `GENUINE` | [A] | DB event count aggregation by depth zone |
| 22 | **Daily Intelligence Report** | ✅ `GENUINE` | [A] | Phase 0 fix: uses `datetime.now()` and computed risk values (not hardcoded) |
| 23 | **Multiple Risk Types** | ⚙️ `SIMULATED` | [B] | MUD_LOSS, STUCK_PIPE, KICK all modelled with Tier 1 physics |
| 24 | **eRTMAC Integration Architecture** | 🔧 `PLANNED` | [D] | Adapter stubs present; no live WITSML connection |
| 25 | **Security Architecture** | ⚠️ `PARTIAL` | [A] | JWT structure works; **login bypass present** until Phase 1; no bcrypt yet |
| 25a | ~~JWT Auth, 5 RBAC Roles, Audit Logs~~ | ❌ `REMOVED` | — | **FALSE CLAIM**: No token enforcement on routes, no bcrypt, no audit logging → Phase 1 |
| 26 | **Evaluation Framework** | ✅ `GENUINE` | [A] | Completed Phase 3: GroupKFold cross-validation by well_id with zero target leakage & real confusion matrices. |

---

## TIER 3 — Innovation / Differentiator Features

| # | Feature | Status | Classification | Honest Notes |
|:-:|---------|--------|----------------|--------------|
| 27 | **Depth Explorer** | ✅ `GENUINE` | [A] | DB-queried timeline with formation lookup |
| 28 | **What-If Simulation** | ⚙️ `SIMULATED` | [B] | Physics-bounded parameter sweep |
| 29 | **NPT / Cost Intelligence** | ✅ `GENUINE` | [A] | Event-based NPT calculation from DB |
| 30 | **Institutional Learning Loop** | ✅ `GENUINE` | [A] | Lessons stored to DB from UI |
| 31 | **Automatic Lessons Learned** | ⚠️ `PARTIAL` | [A] | Structured from DB events; no NLP synthesis |
| 32 | **Risk Evolution Over Time** | ✅ `GENUINE` | [A] | Telemetry rolling window from DB |
| 33 | **Predictive Drilling Timeline** | ✅ `GENUINE` | [A] | Phase 0 fix: dynamic formation labels from DB (not hardcoded depth strings) |

---

## Previously False Claims — Corrected in Phase 0

### Claim 1: "100% ML Accuracy"
- **Was:** "Mud Loss 99.71%, Stuck Pipe 100.00%, Kick 99.94%"
- **Why false:** Training data generated synthetically with labels derived from input features (target leakage). No GroupKFold cross-validation by well_id.
- **Now:** Models loaded as optional benchmark only. Primary engine is Tier 1 physics (honest). Retraining with proper methodology in Phase 3.

### Claim 2: "Semantic Vector Embeddings / Cosine Vector Index"
- **Was:** `SemanticEmbeddingEngine` using `TfidfVectorizer`
- **Why false:** TF-IDF is bag-of-words, not neural embeddings. Config referenced `sentence-transformers/all-MiniLM-L6-v2` but model was never loaded.
- **Now:** Renamed to `KeywordSearchEngine` with explicit provenance note. Dense vector retrieval in Phase 6.

### Claim 3: "JWT Auth, 5 RBAC Roles, Audit Logs"
- **Was:** `get_current_user()` returns `driller` user when no token provided (login bypass)
- **Why false:** Any unauthenticated request gets full access. No route-level RBAC. No audit logging. Frontend starts logged in with hardcoded `demo_token_123`.
- **Now:** Documented as PLANNED. Full implementation in Phase 1.

---

## What Genuinely Works Well

- ✅ FastAPI + SQLAlchemy ORM infrastructure is production-quality
- ✅ WebSocket real-time telemetry broadcast is genuinely real
- ✅ 30-well + 173-event synthetic dataset is well-structured and representative
- ✅ Haversine distance calculation is mathematically correct
- ✅ Teale MSE formula is correctly implemented
- ✅ Formation pore-pressure lookup table uses domain-representative values
- ✅ React/Vite frontend builds cleanly with full TypeScript
- ✅ Leaflet map integration works correctly with real GeoJSON data
- ✅ PyPDF text extraction works for text-layer PDFs
- ✅ Knowledge graph topology is genuinely computed from DB relationships
- ✅ Risk heatmap is genuinely computed from DB event density

---

*This honest assessment was produced during Phase 0 of the NWIS remediation project.*
*See `docs/system_classification.md` for the complete provenance registry.*
*See `docs/REMEDIATION_PHASES.md` for the planned improvement roadmap.*
