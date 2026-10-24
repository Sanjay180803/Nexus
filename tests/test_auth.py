from conftest import register_and_login


def test_register_login_and_me(client):
    headers = register_and_login(client, "alice")
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "alice"
    assert r.json()["email"] == "alice@example.com"
    assert "hashed_password" not in r.json()


def test_duplicate_email_rejected(client):
    register_and_login(client, "alice")
    r = client.post("/auth/register", json={"email": "alice@example.com", "username": "other", "password": "x"})
    assert r.status_code == 400


def test_duplicate_username_rejected(client):
    register_and_login(client, "alice")
    r = client.post("/auth/register", json={"email": "new@example.com", "username": "alice", "password": "x"})
    assert r.status_code == 400


def test_wrong_password_rejected(client):
    register_and_login(client, "alice")
    r = client.post("/auth/login", json={"email": "alice@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_password_is_hashed(client):
    from app.database import SessionLocal
    from app.models.models import User

    register_and_login(client, "alice")
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == "alice").one()
        assert user.hashed_password != "pw-alice"
        assert user.hashed_password.startswith("$2")


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_garbage_token_rejected(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401
