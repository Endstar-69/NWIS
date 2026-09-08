# Production Multi-Stage Dockerfile for NWIS Backend FastAPI Engine
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for compilation, geospatial libraries, and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psycopg2-binary>=2.9.9

# Copy project modules
COPY backend/ /app/backend/
COPY simulator/ /app/simulator/
COPY artifacts/ /app/artifacts/
COPY data/ /app/data/
COPY scripts/ /app/scripts/
COPY documents/ /app/documents/

# Expose backend ASGI port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/system/status || exit 1

# Auto-seed database if fresh, then launch production Uvicorn ASGI server
CMD ["sh", "-c", "python scripts/seed_database.py && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
