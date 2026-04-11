"""
CSRF Protection Tests
=====================
Testira da CSRF zaštita stvarno radi kada je uključena.

Flask-WTF CSRFProtect je globalni CSRF mehanizam.
Kada je WTF_CSRF_ENABLED=True, svi POST/PUT/DELETE zahtjevi
mora imati validan CSRF token.
"""

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app_csrf_enabled():
    """App sa uključenim CSRF-om za testiranje zaštite."""
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-csrf-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": True,
        "RATELIMIT_ENABLED": False,
        "SERVER_NAME": "localhost:5000",
    })

    with app.app_context():
        db.create_all()
        user = User(username="admin", email="admin@pedmajevica.ba", role="admin")
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app_csrf_enabled):
    """Test client sa CSRF-om uključenim."""
    with app_csrf_enabled.test_client() as c:
        yield c


def _get_session_csrf_token(client):
    """Dobij CSRF token sa /api/csrf-token endpointa."""
    response = client.get("/api/csrf-token")
    if response.status_code == 200:
        data = response.get_json()
        return data.get("csrf_token")
    return None


# --- 1. CSRF endpoint ---

def test_csrf_token_endpoint_returns_token(client):
    """GET /api/csrf-token mora vratiti validan CSRF token."""
    response = client.get("/api/csrf-token")
    assert response.status_code == 200
    data = response.get_json()
    assert "csrf_token" in data
    assert len(data["csrf_token"]) > 0


# --- 2. POST bez CSRF tokena → odbijen ---

def test_post_without_csrf_token_is_rejected(client):
    """POST bez CSRF tokena mora biti odbijen."""
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code in (400, 403)


# --- 3. POST sa pogrešnim CSRF tokenom → odbijen ---

def test_post_with_invalid_csrf_token_is_rejected(client):
    """POST sa pogrešnim CSRF tokenom mora biti odbijen."""
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "admin123"},
        headers={"X-CSRFToken": "invalid-token-here"},
    )
    assert response.status_code in (400, 403)


# --- 4. POST sa validnim CSRF tokenom → prolazi ---

def test_post_with_valid_csrf_token_succeeds(client):
    """POST sa validnim CSRF tokenom mora proći."""
    csrf_token = _get_session_csrf_token(client)
    assert csrf_token is not None

    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "admin123"},
        headers={"X-CSRFToken": csrf_token},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


# --- 5. GET nije blokiran CSRF-om ---

def test_get_requests_not_blocked_by_csrf(client):
    """GET zahtjevi ne smiju zahtijevati CSRF token."""
    response = client.get("/api/posts")
    assert response.status_code not in (400, 403)


# --- 6. Custom CSRF utils — validacija i rotacija ---

def test_csrf_token_validation_rejects_invalid(app_csrf_enabled):
    """validate_csrf_token mora odbiti pogrešan token."""
    from app.utils.csrf import validate_csrf_token
    with app_csrf_enabled.test_request_context():
        from flask import session
        session["csrf_token"] = "real-token"
        assert validate_csrf_token("wrong-token") is False
        assert validate_csrf_token(None) is False
        assert validate_csrf_token("") is False


def test_csrf_token_validation_accepts_valid(app_csrf_enabled):
    """validate_csrf_token mora prihvatiti ispravan token."""
    from app.utils.csrf import validate_csrf_token
    with app_csrf_enabled.test_request_context():
        from flask import session
        session["csrf_token"] = "my-token"
        assert validate_csrf_token("my-token") is True


def test_csrf_token_rotation(app_csrf_enabled):
    """rotate_csrf_token mora promijeniti token u session-u."""
    from app.utils.csrf import validate_csrf_token, rotate_csrf_token
    with app_csrf_enabled.test_request_context():
        from flask import session
        session["csrf_token"] = "old-token"
        old = session["csrf_token"]

        rotate_csrf_token()

        new = session["csrf_token"]
        assert old != new
        assert validate_csrf_token(old) is False
        assert validate_csrf_token(new) is True


# --- 7. CSRF štiti i druge write endpoint-e ---

def test_post_endpoint_protected_by_csrf(client):
    """Drugi POST endpoint mora biti CSRF zaštićen."""
    response = client.post(
        "/api/password-reset-request",
        json={"email": "test@example.com"},
    )
    # CSRF zaštita mora odbiti zahtjev (400 od Flask-WTF)
    assert response.status_code in (400, 403)
