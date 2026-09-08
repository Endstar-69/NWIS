# NWIS REST & WebSocket API Reference

The Nearby Wells Intelligence System (NWIS) exposes an OpenAPI 3.0 compliant REST and WebSocket API via FastAPI.

Interactive Swagger UI is available at:
`http://localhost:8000/docs`

---

## 1. Authentication Endpoints

### `POST /api/auth/login`
Authenticates user credentials and returns a JWT access token.

- **Request Body**:
```json
{
  "username": "engineer",
  "password": "engineer123"
}
```

- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "engineer",
    "full_name": "Drilling Engineer",
    "role": "Drilling Engineer",
    "email": "engineer@nwis-oil.demo"
  }
}
```

### `GET /api/auth/me`
Returns current authenticated user details from bearer token.

---

## 2. Wells & Geospatial Endpoints

### `GET /api/wells`
Lists all wells with optional search, field filter, and pagination.
- **Query Params**: `skip` (int), `limit` (int), `field` (str), `status` (str)

### `GET /api/wells/{id}`
Returns well metadata, surface coordinates, target depth, active status, and casing/cementing summaries.

### `GET /api/wells/{id}/nearby`
Calculates offset wells within a spatial radius, ranked by multi-factor similarity score.
- **Query Params**:
  - `radius_km` (float, default: `25.0`)
  - `current_depth` (float, optional)
- **Response**:
```json
[
  {
    "well": {
      "id": 2,
      "well_name": "DEMO-W002",
      "field_name": "Dikom",
      "latitude": 27.4950,
      "longitude": 95.0320,
      "total_depth": 3950.0
    },
    "distance_km": 4.12,
    "similarity_score": 0.88,
    "historical_events_count": 8,
    "loss_events_count": 3,
    "stuck_pipe_events_count": 2,
    "kick_events_count": 1
  }
]
```

### `GET /api/wells/{id}/trajectory`
Retrieves directional survey stations (Measured Depth, Inclination, Azimuth, TVD, Northing, Easting).

### `GET /api/wells/{id}/events`
Returns all historical drilling incidents associated with the specified well.

### `GET /api/wells/compare`
Multi-well correlation endpoint returning side-by-side casing, lithology, and incident comparisons.
- **Query Params**: `well_ids` (comma-separated IDs e.g. `1,2,3`)

---

## 3. Formations & Stratigraphy

### `GET /api/formations`
Returns stratigraphy markers, typical depth windows, pore pressure gradients, fracture gradients, and historical risk ratings for the basin.

---

## 4. Historical Event Knowledge Repository

### `GET /api/events`
Returns paginated drilling events with filtering.
- **Query Params**: `event_type`, `formation`, `severity`, `min_depth`, `max_depth`, `skip`, `limit`

### `GET /api/events/{id}`
Returns complete event dossier including cause, observed symptoms, mitigation, lessons learned, and source document reference.

---

## 5. Document Intelligence

### `POST /api/documents/upload`
Uploads a Daily Drilling Report (DDR) or Well Completion Report (WCR) in PDF or TXT format and triggers entity extraction.
- **Form Data**: `file` (binary), `well_id` (optional int)

### `GET /api/documents`
Lists ingested drilling documents and their processing status.

### `GET /api/documents/{id}`
Returns extracted text chunks, structured events, and extraction confidence score.

---

## 6. Knowledge Search & RAG Assistant

### `POST /api/search`
Dual-mode keyword and vector search over historical drilling incidents.
- **Request Body**:
```json
{
  "query": "mud loss LCM pill Barail Sandstone",
  "search_type": "hybrid",
  "formation": "Barail Sandstone",
  "min_depth": 3300,
  "max_depth": 3600,
  "limit": 10
}
```

### `POST /api/search/assistant`
RAG AI Assistant answering operational questions grounded strictly in retrieved historical evidence.
- **Request Body**:
```json
{
  "query": "What mitigation actions were taken for stuck pipe incidents in Kopili Formation around 3600m?"
}
```

---

## 7. ML Risk Prediction

### `POST /api/risk/predict`
Calculates real-time risk probabilities for Mud Loss, Stuck Pipe, and Kick based on telemetry parameters and offset event density.
- **Request Body**:
```json
{
  "depth": 3422.0,
  "formation": "Barail Sandstone",
  "rop": 18.5,
  "wob": 24.0,
  "rpm": 115.0,
  "torque": 15.2,
  "standpipe_pressure": 2720.0,
  "flow_rate": 510.0,
  "mud_weight": 1.28,
  "ecd": 1.34,
  "hook_load": 142.0
}
```

### `GET /api/risk/{well_id}`
Returns the latest ML risk evaluation for an active well.

---

## 8. Alerts & Recommendations

### `GET /api/alerts`
Retrieves active and historical proactive alerts.
- **Query Params**: `well_id`, `status` (`NEW`, `ACKNOWLEDGED`, `RESOLVED`), `severity`

### `POST /api/alerts/{id}/acknowledge`
Acknowledge an active alert by alert ID.

### `GET /api/recommendations/{well_id}`
Generates decision-support operational recommendations synthesized from offset historical evidence and current risk state.

---

## 9. Real-Time Telemetry WebSocket

### `WS /ws/well/{well_id}`
Establishes bidirectional live telemetry streaming. The server pushes real-time drilling telemetry ticks, calculated rolling deltas, and live ML risk evaluations at 1 Hz.
