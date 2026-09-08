#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  NWIS - Nearby Wells Intelligence System Setup (Linux/macOS)"
echo "=========================================================="

echo -e "\n[1/5] Creating Python virtual environment (.venv)..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

echo -e "\n[2/5] Installing backend dependencies..."
pip install -r backend/requirements.txt

echo -e "\n[3/5] Generating synthetic Assam-Arakan drilling dataset..."
export PYTHONPATH="."
export PYTHONIOENCODING="utf-8"
python scripts/generate_demo_data.py

echo -e "\n[4/5] Seeding database & training ML risk models..."
python scripts/seed_database.py
python scripts/train_models.py
python scripts/ingest_documents.py

echo -e "\n[5/5] Installing React frontend dependencies..."
cd frontend
npm install
cd ..

echo "=========================================================="
echo "  NWIS Setup Completed Successfully!"
echo "=========================================================="
echo -e "\nTo start the Backend:"
echo "  source .venv/bin/activate"
echo "  uvicorn backend.app.main:app --reload --port 8000"
echo -e "\nTo start the Frontend:"
echo "  cd frontend && npm run dev"
