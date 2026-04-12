"""
Security Test Suite — Endpoint Exposure
Tests whether sensitive endpoints leak information or are unnecessarily exposed.
"""

import pytest


class TestDebugEndpoints:
    """Debug endpoints should not be accessible in production or leak secrets."""

    def test_debug_auth_endpoint(self, client):
        """GET /api/debug/auth should NOT be publicly accessible or leak nothing."""
        resp = client.get("/api/debug/auth")

        if resp.status_code == 200:
            data = resp.get_json() or {}
            body = str(data).lower()

            assert "secret" not in body or "secret_key" not in body, (
                f"Debug endpoint leaks secret: {data}"
            )
            assert "postgresql" not in body and "sqlite" not in body, (
                f"Debug endpoint leaks DB URL: {data}"
            )
            assert "$2b$" not in body, (
                f"Debug endpoint leaks password hash: {data}"
            )
        else:
            assert resp.status_code in (401, 403, 404, 405), (
                f"Debug endpoint unexpected status: {resp.status_code}"
            )

    def test_debug_auth_response_no_secrets(self, client):
        """Even if debug endpoint exists, it must not leak SECRET_KEY."""
        resp = client.get("/api/debug/auth")
        if resp.status_code == 200:
            data = resp.get_json() or {}
            body = str(data).lower()
            assert "secret_key" not in body, "Debug endpoint leaks SECRET_KEY"


class TestCSRFTokenEndpoint:
    """CSRF token endpoint should only return the token, nothing else."""

    def test_csrf_token_response_structure(self, client):
        """GET /api/csrf-token should return only the token."""
        resp = client.get("/api/csrf-token")
        assert resp.status_code == 200

        data = resp.get_json()
        assert "csrf_token" in data, "CSRF endpoint missing csrf_token"

        body = str(data).lower()
        assert "secret" not in body, "CSRF response contains 'secret'"
        assert "password" not in body, "CSRF response contains 'password'"

    def test_csrf_token_is_not_empty(self, client):
        """CSRF token should be a non-empty string."""
        resp = client.get("/api/csrf-token")
        data = resp.get_json()
        token = data.get("csrf_token", "")
        assert isinstance(token, str), "CSRF token is not a string"
        assert len(token) > 0, "CSRF token is empty"


class TestPasswordHashExposure:
    """Password hashes must never appear in API responses."""

    def test_login_response_does_not_expose_password(self, client):
        """Login response should not include password hash."""
        resp = client.post(
            "/api/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert resp.status_code == 200
        data = resp.get_json() or {}
        body = str(data).lower()
        assert "password_hash" not in body, "Password hash in login response"
        assert "$2b$" not in body, "Bcrypt hash in login response"

    def test_post_response_does_not_expose_author_password(self, logged_in_client, client):
        """Post response should not include author's password."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "Password Test", "content": "Test"},
        )
        if resp.status_code in (200, 201):
            data = resp.get_json()
            post_id = data.get("data", {}).get("post", {}).get("id")
            if post_id:
                get_resp = client.get(f"/api/posts/{post_id}")
                if get_resp.status_code == 200:
                    get_data = get_resp.get_json() or {}
                    body = str(get_data).lower()
                    assert "$2b$" not in body, "Password hash in post response"


class TestConfigExposure:
    """Flask config must not leak through API responses."""

    @pytest.mark.parametrize("endpoint", [
        "/api/posts/",
        "/api/events/",
        "/api/trails/",
        "/api/plan-aktivnosti/",
        "/api/gallery/",
        "/",
    ])
    def test_no_config_leak_in_public_endpoints(self, client, endpoint):
        """Public endpoints should not expose Flask config."""
        resp = client.get(endpoint)

        if resp.status_code in (200, 201):
            body = str(resp.data).lower()
            for config_key in ["secret_key", "database_url", "sqlalchemy",
                              "flask_env", "mail_password", "csrf_secret"]:
                assert config_key not in body, (
                    f"Config key '{config_key}' in response from {endpoint}"
                )


class TestErrorResponseContent:
    """Error responses should be clean and not reveal internals."""

    def test_404_response_is_clean(self, client):
        """404 responses should only contain 'error' field."""
        resp = client.get("/nonexistent-page")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data, "404 missing 'error' field"
        assert len(data) <= 2, f"404 response has too many fields: {data}"

    def test_401_response_is_clean(self, client):
        """401 responses should be user-friendly."""
        resp = client.delete("/api/posts/1")
        if resp.status_code == 401:
            data = resp.get_json() or {}
            body = str(data).lower()
            assert "traceback" not in body, "Traceback in 401"
            assert "sqlalchemy" not in body, "SQLAlchemy in 401"


class TestVersionExposure:
    """Server version info should not be exposed."""

    def test_no_flask_version_in_headers(self, client):
        """Response should not expose Flask/Werkzeug version in headers."""
        resp = client.get("/")
        server_header = resp.headers.get("Server", "")
        assert "flask" not in server_header.lower(), (
            f"Flask exposed in Server header: {server_header}"
        )
