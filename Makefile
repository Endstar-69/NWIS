.PHONY: help setup demo-data seed train backend frontend dev test clean

help:
	@echo "NWIS - Nearby Wells Intelligence System"
	@echo "Available commands:"
	@echo "  make setup        - Install backend and frontend dependencies"
	@echo "  make demo-data    - Generate synthetic Assam-Arakan drilling dataset"
	@echo "  make seed         - Seed database with synthetic wells and historical events"
	@echo "  make train        - Train Mud Loss, Stuck Pipe, and Kick ML models"
	@echo "  make backend      - Run FastAPI backend development server"
	@echo "  make frontend     - Run Vite React frontend development server"
	@echo "  make test         - Run backend and ML test suites"
	@echo "  make demo         - Run complete end-to-end automated demo scenario"

setup:
	python -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

demo-data:
	python scripts/generate_demo_data.py

seed:
	python scripts/seed_database.py

train:
	python scripts/train_models.py

ingest:
	python scripts/ingest_documents.py

backend:
	python -m uvicorn backend.app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	pytest backend/tests -v

demo:
	python scripts/run_demo.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
