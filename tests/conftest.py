import os
import sys
import tempfile

import pytest

# Configure before the app is imported: database.py and security.py read
# these at import time. CI overrides DATABASE_URL with a Postgres service.
_tmpdir = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmpdir}/test.db")
os.environ.setdefault("SECRET_KEY", "test-only-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.models import Priority  # noqa: E402
from app.routers import tasks as tasks_router  # noqa: E402


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def stub_nlp(monkeypatch):
    """Replace the 1.6 GB zero-shot model with a deterministic stub."""

    def fake_priority(text: str) -> Priority:
        lowered = text.lower()
        if "crash" in lowered or "outage" in lowered:
            return Priority.critical
        if "bug" in lowered:
            return Priority.high
        return Priority.low

    monkeypatch.setattr(tasks_router, "get_priority_from_nlp", fake_priority)


@pytest.fixture
def client():
    return TestClient(app)


def register_and_login(client, name: str) -> dict:
    email = f"{name}@example.com"
    r = client.post("/auth/register", json={"email": email, "username": name, "password": "pw-" + name})
    assert r.status_code == 200, r.text
    r = client.post("/auth/login", json={"email": email, "password": "pw-" + name})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
