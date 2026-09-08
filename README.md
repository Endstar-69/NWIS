# Nearby Wells Intelligence System (NWIS)
### OIL India Limited — Intelligent Wellsite Decision Support Platform

> **“Turning historical drilling knowledge into proactive wellsite intelligence.”**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5.1-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![Tests](https://img.shields.io/badge/Pytest-106%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](https://pytest.org)
[![Netlify Status](https://img.shields.io/badge/Netlify-Ready-00C7B7.svg?logo=netlify&logoColor=white)](https://www.netlify.com)

---

## 📌 Executive Summary

The **Nearby Wells Intelligence System (NWIS)** is an AI/ML-enabled decision-support platform engineered to integrate with OIL India's **eRTMAC** (enhanced Real-Time Monitoring and Analytics Centre) vision.

During drilling operations, critical institutional memory from previous wells (Daily Drilling Reports, Well Completion Reports, and offset logs) is frequently locked in unstructured PDFs or legacy databases. NWIS solves this by:
1. **Correlating spatial and stratigraphic offset wells** relative to an active rig in real time.
2. **Extracting structured event knowledge** from legacy drilling reports (PDF & TXT) with confidence metrics.
3. **Predicting upcoming drilling risks** (Mud Loss, Stuck Pipe, Kick) using physics-informed Random Forest ML models with Explainable AI (XAI) feature importance.
4. **Delivering grounded, evidence-backed recommendations** with zero hallucination guardrails to support drilling superintendents and engineers.

---

## 🚀 Key Modules & Capabilities

| Module | Core Functionality |
| :--- | :--- |
| **Executive Overview** | Real-time active well KPIs (Depth, ROP, WOB, Torque, SPP, Mud Weight, ECD), offset summary, active alerts, and fleet status. |
| **Active Well Intelligence** | Live telemetry streaming charts, instantaneous ML risk indicators, and evidence-linked mitigations. |
| **Geospatial Offset Search** | Interactive Leaflet map with configurable radius rings (1–50 km), well marker clustering, and multi-factor offset similarity scoring. |
| **Well Comparison Engine** | Side-by-side stratigraphy, casing program, cementing, and historical event correlation across multiple offset wells. |
| **Document Intelligence** | Automated extraction pipeline for DDR and WCR reports (PDF/TXT) parsing depth, formation, incident taxonomy, symptoms, and mitigations with confidence scoring. |
| **Grounded AI Assistant & Search** | Dual-mode hybrid keyword & vector semantic search with strict citation of historical records and zero hallucination guardrails. Powered by Google Gemini with deterministic offline fallback. |
| **ML Risk Prediction** | Random Forest models for Mud Loss, Stuck Pipe, and Kick with Explainable AI (XAI) feature attribution. |
| **Proactive Alert Engine** | Multi-level alerts (`INFO`, `WATCH`, `HIGH`, `CRITICAL`) with one-click engineer acknowledgment and audit logging. |
| **Real-Time eRTMAC Simulator** | Live WebSocket telemetry generator simulating depth progression and parameter variations. |

---

## 🏗️ Architecture & Technology Stack

```text
[Frontend: Vite + React 18 + TS + Tailwind CSS]
                     │
       REST / WebSocket (JSON)
                     │
                     ▼
[Backend: FastAPI + SQLAlchemy + Pydantic v2]
   ├── Geospatial Engine (Haversine & Multi-Factor Similarity)
   ├── ML Inference Engine (Random Forest Models in artifacts/models/)
   ├── Document Intelligence (PyPDF / Heuristic Entity Extractor)
   ├── Vector Knowledge Search (Dense 384-d Cosine Similarity)
   ├── Dedicated LLM Service (Google Gemini + Deterministic Fallback)
   └── Real-Time WebSocket Telemetry Stream
                     │
                     ▼
[Relational Database: SQLite (local default) / PostgreSQL + PostGIS (Docker)]
```

---

## 🌐 Netlify Deployment Guide (Frontend)

NWIS is pre-configured for one-click or Git-based deployment on [Netlify](https://www.netlify.com).

### Method 1: Git-Connected Netlify Deployment (Recommended)

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete industrial NWIS release"
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
   git branch -M main
   git push -u origin main
   ```
2. Log in to [Netlify](https://app.netlify.com) and click **"Add new site" > "Import an existing project"**.
3. Select your GitHub repository.
4. Netlify will automatically detect `netlify.toml`:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist` (or `frontend/dist`)
5. **Environment Variables**:
   Under **Site configuration > Environment variables**, add:
   ```env
   VITE_API_URL=https://your-backend-api.onrender.com
   ```
   *(Or point to your deployed FastAPI backend URL on Render, Railway, AWS ECS, or Fly.io)*.
6. Click **Deploy Site**. Netlify will build the SPA and handle all client-side routes via `_redirects`.

### Method 2: Netlify CLI Direct Deploy

```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Navigate to frontend directory
cd frontend

# Build production bundle
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=dist
```

---

## ⚡ Local Quick Start Guide (Windows PowerShell)

### Prerequisites
- **Python 3.10+** (Python 3.11 or 3.12 recommended)
- **Node.js 18+** & npm

### Step 1: Clone & Setup Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 2: Initialize Data, Seed Database & Train ML Models

```powershell
# 1. Generate realistic synthetic drilling data
python scripts/generate_demo_data.py

# 2. Seed the relational database
python scripts/seed_database.py

# 3. Ingest sample PDF/TXT drilling reports into Knowledge Base
python scripts/ingest_documents.py

# 4. Train and evaluate all 3 ML risk models
python scripts/train_models.py
```

### Step 3: Start the Backend Server

```powershell
# Run FastAPI on http://localhost:8000
uvicorn backend.app.main:app --reload --port 8000
```

### Step 4: Start the Frontend Application (New Terminal)

```powershell
cd frontend

# Install frontend dependencies
npm install

# Launch Vite dev server on http://localhost:5173
npm run dev
```

---

## 🐧 Local Quick Start Guide (Linux / macOS)

```bash
# 1. Setup Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 2. Data & ML Pipeline
python3 scripts/generate_demo_data.py
python3 scripts/seed_database.py
python3 scripts/ingest_documents.py
python3 scripts/train_models.py

# 3. Start Backend
uvicorn backend.app.main:app --reload --port 8000 &

# 4. Start Frontend
cd frontend
npm install
npm run dev
```

---

## 🔑 Default Login Credentials

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Drilling Engineer** *(Default)* | `engineer` | `engineer123` | Full telemetry, active well, alerts, recommendations |
| **Administrator** | `admin` | `admin123` | User management, system status, audit logs |
| **Geologist** | `geologist` | `geologist123` | Stratigraphy, lithology correlation, offset logs |
| **Supervisor** | `supervisor` | `supervisor123` | Executive dashboard, high-level alert oversight |
| **Viewer** | `viewer` | `viewer123` | Read-only access |

---

## ⚙️ Environment Variables Reference

### Backend (`.env`)
```env
# Application Settings
ENVIRONMENT=development
PROJECT_NAME="Nearby Wells Intelligence System"
API_V1_STR=/api
SECRET_KEY=nwis-oil-india-secure-secret-key-2024
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Database (Default: SQLite)
DATABASE_URL=sqlite:///./data/nwis.db

# LLM & AI Services
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash

# CORS Allowed Origins
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://*.netlify.app"]
```

### Frontend (`frontend/.env` or Netlify Environment)
```env
# URL pointing to the FastAPI backend
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Running Automated Tests

Run the full pytest suite for the backend:
```powershell
pytest backend/tests/ -v
```
*Result: 106/106 automated tests passing across authentication/RBAC, risk prediction, SHAP explainability, hybrid search, RAG grounding, simulator, and unified LLM search.*

Run the automated end-to-end terminal demo:
```powershell
python scripts/run_demo.py
```

---

## 🐳 Docker Deployment

To launch the full stack with Docker Compose:
```bash
docker-compose up --build
```
- **Frontend**: `http://localhost:3000`
- **Backend API Docs**: `http://localhost:8000/docs`
- **PostgreSQL / PostGIS**: `localhost:5432`

---

## ⚠️ Prototype Limitations & Disclaimers

1. **Synthetic Dataset**: All records in `data/demo/` represent synthetic scenarios modeled after the Assam-Arakan basin. They do **not** represent real confidential OIL India well logs.
2. **Decision Support Only**: ML risk probabilities and recommendations are decision-support outputs and do not issue autonomous drilling commands.
3. **Telemetry Simulator**: Live data streaming operates via a local simulator mimicking eRTMAC WITSML/OPC-UA data feeds.
