import pytest
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for tests
            "RATELIMIT_ENABLED": False,  # Disable rate limiting for tests
        }
    )

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            user = User(
                username="admin",
                email="admin@pedmajevica.ba",
                role="admin",
            )
            user.set_password("admin123")
            db.session.add(user)
            db.session.commit()

        yield client

        with app.app_context():
            db.drop_all()


def test_login_success(client):
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    assert response.json["success"] is True


def test_login_fail_wrong_password(client):
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json["success"] is False


def test_admin_requires_login(client):
    response = client.get("/admin", follow_redirects=False)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_rate_limited(client):
    for _ in range(5):
        client.post(
            "/api/login",
            json={"username": "admin", "password": "wrongpassword"},
        )

    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "wrongpassword"},
    )

    assert response.status_code == 429
