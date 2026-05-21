from collections.abc import Generator
from pathlib import Path
import shutil
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httpx

from api.config import get_settings
from api.database import Base, get_db
from api.main import app
from api.models import User

# Define the client fixture for testing the auth routes
@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    test_dir = Path(".test_runtime") / str(uuid.uuid4())
    test_dir.mkdir(parents=True, exist_ok=True)
    test_engine = create_engine(
        f"sqlite:///{test_dir / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    testing_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(get_settings(), "upload_dir", test_dir / "uploads")
    monkeypatch.setattr(get_settings(), "database_url", f"sqlite:///{test_dir / 'test.db'}")
    monkeypatch.setattr(get_settings(), "google_client_id", "test-client-id")
    monkeypatch.setattr(get_settings(), "google_client_secret", "test-client-secret")
    monkeypatch.setattr(get_settings(), "frontend_url", "http://localhost:5173")
    
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()
        if test_dir.exists():
            shutil.rmtree(test_dir, ignore_errors=True)

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

class MockHttpxClient:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def post(self, url, data=None, **kwargs):
        if url == "https://oauth2.googleapis.com/token":
            return MockResponse({"access_token": "mock-access-token"})
        return MockResponse({}, status_code=404)

    def get(self, url, **kwargs):
        if "userinfo" in url or "googleapis.com/oauth2/v3/userinfo" in url:
            return MockResponse({
                "email": "test-google-user@example.com",
                "sub": "google-id-12345",
                "name": "Google Test User"
            })
        return MockResponse({}, status_code=404)

def test_google_login_redirect(client: TestClient):
    response = client.get("/api/v1/auth/google", follow_redirects=False)
    assert response.status_code == 307
    location = response.headers.get("location")
    assert "accounts.google.com" in location
    assert "client_id=test-client-id" in location
    assert "response_type=code" in location

def test_google_callback_success(client: TestClient, monkeypatch):
    monkeypatch.setattr(httpx, "Client", MockHttpxClient)

    # Call callback endpoint with authorization code
    response = client.get("/api/v1/auth/google/callback?code=mock-code", follow_redirects=False)
    assert response.status_code == 307
    location = response.headers.get("location")
    assert "http://localhost:5173/oauth-callback?token=" in location

def test_google_callback_error_param(client: TestClient):
    response = client.get("/api/v1/auth/google/callback?error=access_denied", follow_redirects=False)
    assert response.status_code == 307
    location = response.headers.get("location")
    assert "http://localhost:5173/login?error=access_denied" in location

def test_google_callback_missing_code(client: TestClient):
    response = client.get("/api/v1/auth/google/callback")
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing authorization code."
