"""
NWIS Pytest Shared Fixtures — Phase 1 RBAC and Authentication.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token


@pytest.fixture(scope="session")
def admin_token():
    return create_access_token({"sub": "admin", "role": "Admin", "user_id": 4})


@pytest.fixture(scope="session")
def driller_token():
    return create_access_token({"sub": "driller", "role": "Drilling Engineer", "user_id": 1})


@pytest.fixture(scope="session")
def supervisor_token():
    return create_access_token({"sub": "supervisor", "role": "Supervisor", "user_id": 3})


@pytest.fixture(scope="session")
def geologist_token():
    return create_access_token({"sub": "geologist", "role": "Geologist", "user_id": 2})


@pytest.fixture(scope="session")
def viewer_token():
    return create_access_token({"sub": "viewer", "role": "Viewer", "user_id": 5})


@pytest.fixture(scope="session")
def driller_headers(driller_token):
    return {"Authorization": f"Bearer {driller_token}"}


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def supervisor_headers(supervisor_token):
    return {"Authorization": f"Bearer {supervisor_token}"}


@pytest.fixture(scope="session")
def geologist_headers(geologist_token):
    return {"Authorization": f"Bearer {geologist_token}"}


@pytest.fixture(scope="session")
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture
def unauthenticated_client():
    return TestClient(app)


@pytest.fixture
def auth_client(driller_headers):
    c = TestClient(app)
    c.headers.update(driller_headers)
    return c
