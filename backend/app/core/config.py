import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Nearby Wells Intelligence System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    SECRET_KEY: str = "nwis_oil_india_hackathon_super_secret_jwt_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/nwis.db"

    AI_DEMO_MODE: bool = True
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"
    TOP_K: int = 5
    MAX_CONTEXT_TOKENS: int = 2048
    MAX_HISTORY_MESSAGES: int = 10
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    DATA_DIR: str = str(BASE_DIR / "data")
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")
    DEMO_DATA_DIR: str = str(BASE_DIR / "data" / "demo")
    MODELS_DIR: str = str(BASE_DIR / "artifacts" / "models")
    EVAL_DIR: str = str(BASE_DIR / "artifacts" / "evaluation")
    DOCS_DIR: str = str(BASE_DIR / "documents")

    ACTIVE_WELL_ID: str = "WELL-001"
    SIMULATOR_TICK_SECONDS: float = 2.0

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure critical directories exist
for path_str in [settings.DATA_DIR, settings.UPLOAD_DIR, settings.DEMO_DATA_DIR, settings.MODELS_DIR, settings.EVAL_DIR, settings.DOCS_DIR]:
    Path(path_str).mkdir(parents=True, exist_ok=True)
