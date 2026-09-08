"""
NWIS Core Security Module — Phase 1 Implementation.

CLASSIFICATION: [A] Real Implementation.

Phase 1 changes:
  - Uses native `bcrypt` (v5+) directly for constant-time password hashing and verification.
    Replaces SHA-256 + static salt ("nwis_oil_salt_2026") with per-password bcrypt salt (rounds=12).
  - verify_password() safely handles encoding and invalid hash strings.
  - JWT token generation, signature validation, and claim decoding.
  - Role hierarchy and inline permission check helpers.

RBAC Role Matrix:
  Admin:            Full access — all GET/POST/PUT/DELETE including user management
  Drilling Engineer: GET + POST /risk/predict + POST /alerts/ack + POST /documents/upload
  Supervisor:       GET + POST /alerts/ack
  Geologist:        GET all read routes + POST /search/*
  Viewer:           GET read-only — no write, predict, or acknowledge
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import jwt, JWTError
from fastapi import HTTPException, status
from backend.app.core.config import settings

# Role hierarchy — higher ordinal = more privilege
ROLE_HIERARCHY: dict[str, int] = {
    "Viewer": 0,
    "Geologist": 1,
    "Supervisor": 2,
    "Drilling Engineer": 3,
    "Admin": 4,
}


def get_password_hash(password: str) -> str:
    """
    Returns a bcrypt hash of the password using 12 salt rounds (OWASP recommended minimum).
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash using constant-time check.
    Returns False if hash is malformed or does not match.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT access token.
    Token payload includes:
      sub       — username (subject claim)
      role      — RBAC role string
      user_id   — integer DB primary key
      exp       — expiry timestamp
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes and validates a JWT token. Returns None if invalid or expired.
    Callers should raise HTTP 401 when None is returned.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def check_role_permission(user_role: str, minimum_role: str) -> None:
    """
    Raises HTTP 403 if user_role does not meet minimum_role requirement.
    Call this inside route handlers that have already resolved the current user.

    Example:
        check_role_permission(current_user.role, "Admin")
    """
    user_level = ROLE_HIERARCHY.get(user_role, -1)
    required_level = ROLE_HIERARCHY.get(minimum_role, 999)
    if user_level < required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {minimum_role}, your role: {user_role}"
        )
