# -*- coding: utf-8 -*-
"""
PED Majevica 1988 - Authentication Tests
=========================================
Testovi za autentifikaciju i autorizaciju.
"""

import pytest
from app.extensions import db
from app.models.user import User


class TestLogin:
    """Testovi za login funkcionalnost."""

    def test_login_with_valid_credentials(self, client, admin_user):
        """Login sa ispravnim podacima uspeva."""
        response = client.post(
            "/api/login", json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        assert response.json["success"] is True

    def test_login_with_invalid_credentials(self, client, admin_user):
        """Login sa pogresnom lozinkom ne uspeva."""
        response = client.post(
            "/api/login", json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code in [401, 400]
        assert response.json["success"] is False

    def test_login_with_nonexistent_user(self, client):
        """Login sa nepostojecim korisnikom ne uspeva."""
        response = client.post(
            "/api/login", json={"username": "nepostojeci", "password": "password123"}
        )
        assert response.status_code in [401, 400]

    def test_login_with_empty_username(self, client, admin_user):
        """Login sa praznim username ne uspeva."""
        response = client.post(
            "/api/login", json={"username": "", "password": "admin123"}
        )
        assert response.status_code in [400, 401]

    def test_login_with_empty_password(self, client, admin_user):
        """Login sa praznom lozinkom ne uspeva."""
        response = client.post("/api/login", json={"username": "admin", "password": ""})
        assert response.status_code in [400, 401]

    def test_login_page_loads(self, client):
        """Login stranica se ucitava."""
        response = client.get("/login")
        assert response.status_code == 200


class TestSessionManagement:
    """Testovi za upravljanje sesijom."""

    def test_unauthorized_access_redirects_to_login(self, client):
        """Neautorizovani pristup redirectuje na login."""
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")

    def test_api_unauthorized_returns_json(self, client):
        """Neautorizovani API zahtev vraca JSON."""
        response = client.get("/api/posts/1")
        assert response.status_code == 401


class TestPasswordSecurity:
    """Testovi za sigurnost lozinki."""

    def test_password_is_hashed(self, app, admin_user):
        """Lozinka je hash-ovana u bazi."""
        with app.app_context():
            user = User.query.filter_by(username="admin").first()
            assert user.password_hash.startswith("$2b$")

    def test_password_hash_is_unique(self, app, admin_user, regular_user):
        """Svaki korisnik ima jedinstven hash."""
        with app.app_context():
            assert admin_user.password_hash != regular_user.password_hash


class TestRoleBasedAccess:
    """Testovi za pristup baziran na ulogama."""

    def test_admin_user_has_admin_role(self, app, admin_user):
        """Admin korisnik ima admin ulogu."""
        with app.app_context():
            assert admin_user.role == "admin"

    def test_regular_user_has_user_role(self, app, regular_user):
        """Obican korisnik ima user ulogu."""
        with app.app_context():
            assert regular_user.role == "user"
