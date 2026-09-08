"""
NWIS Authentication & Authorization API — Phase 1 Implementation.

CLASSIFICATION: [A] Real Implementation.

Phase 1 changes:
  - REMOVED: login bypass (lines 14-18 in old version) that returned the 'driller'
    user when no token was provided. Any tokenless request now raises HTTP 401.
  - get_current_user() is the primary auth dependency injected into protected routes.
  - get_current_active_user() additionally checks user.is_active flag.
  - Role-gated dependencies (require_admin, require_engineer, require_supervisor,
    require_geologist) added for use in route Depends() chains.

RBAC Role Matrix:
  Admin:            Full access — all GET/POST/PUT/DELETE including user management
  Drilling Engineer: GET + POST /risk/predict + POST /alerts/ack + POST /documents/upload
  Supervisor:       GET + POST /alerts/ack
  Geologist:        GET all read routes + POST /search/*
  Viewer:           GET read-only — no write, predict, or acknowledge
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import (
    verify_password, create_access_token, decode_access_token, check_role_permission
)
from backend.app.models.user import User
from backend.app.schemas.auth import Token, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# auto_error=True — unauthenticated requests are rejected with 401 before reaching the handler
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Phase 1: Primary authentication dependency.

    Phase 1 fix: The login bypass (returning 'driller' when no token provided)
    has been removed. `auto_error=True` means FastAPI raises HTTP 401 before
    this function is called if the Authorization header is absent or malformed.

    Raises HTTP 401 if:
      - Token is missing (handled by OAuth2PasswordBearer with auto_error=True)
      - Token signature is invalid or expired (JWTError caught in decode_access_token)
      - 'sub' claim is missing from payload
      - Username in 'sub' does not exist in the database
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exc

    username: str = payload["sub"]
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exc
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Raises HTTP 403 if the account has been deactivated."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")
    return current_user


# ── Role-gated dependencies ────────────────────────────────────────────────────

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Requires Admin role. Raises HTTP 403 otherwise."""
    check_role_permission(current_user.role, "Admin")
    return current_user


def require_engineer(current_user: User = Depends(get_current_active_user)) -> User:
    """Requires Drilling Engineer role or higher."""
    check_role_permission(current_user.role, "Drilling Engineer")
    return current_user


def require_supervisor(current_user: User = Depends(get_current_active_user)) -> User:
    """Requires Supervisor role or higher."""
    check_role_permission(current_user.role, "Supervisor")
    return current_user


def require_geologist(current_user: User = Depends(get_current_active_user)) -> User:
    """Requires Geologist role or higher."""
    check_role_permission(current_user.role, "Geologist")
    return current_user


# ── Auth routes ────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 password flow login. Returns a signed JWT token on success.
    Raises HTTP 401 on incorrect credentials.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role
    )


@router.post("/login-json", response_model=Token)
def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    JSON body login (for frontend fetch calls).
    Identical validation logic to the OAuth2 form endpoint.
    """
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Returns the authenticated user's profile. Requires any valid token."""
    return current_user
