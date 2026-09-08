# NWIS Windows Automated Setup Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  NWIS - Nearby Wells Intelligence System Setup (Windows)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Create Python Virtual Environment
Write-Host "`n[1/5] Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# 2. Install Python Dependencies
Write-Host "`n[2/5] Installing backend dependencies..." -ForegroundColor Yellow
.\.venv\Scripts\pip.exe install -r backend\requirements.txt

# 3. Generate Synthetic Demo Data
Write-Host "`n[3/5] Generating synthetic Assam-Arakan drilling dataset..." -ForegroundColor Yellow
$env:PYTHONPATH="."
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe scripts\generate_demo_data.py

# 4. Seed Database & Train ML Models
Write-Host "`n[4/5] Seeding database & training ML risk models..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe scripts\seed_database.py
.\.venv\Scripts\python.exe scripts\train_models.py
.\.venv\Scripts\python.exe scripts\ingest_documents.py

# 5. Install Frontend Dependencies
Write-Host "`n[5/5] Installing React frontend dependencies..." -ForegroundColor Yellow
cd frontend
npm install
cd ..

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  NWIS Setup Completed Successfully!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "`nTo start the Backend:" -ForegroundColor White
Write-Host "  .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "`nTo start the Frontend:" -ForegroundColor White
Write-Host "  cd frontend; npm run dev" -ForegroundColor Cyan
