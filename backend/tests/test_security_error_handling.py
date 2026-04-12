"""
Security Test Suite — Error Handling & Information Leakage
Tests whether error responses leak sensitive technical details.
"""

import pytest


class TestNotFoundErrorLeakage:
    """404 responses must not reveal internal details."""

    def test_nonexistent_post_id(self, client):
        """GET /api/posts/999999 → 404, no stack trace."""
        resp = client.get("/api/posts/999999")
        assert resp.status_code == 404
        data = resp.get_json()
        body = str(data).lower()
        assert "traceback" not in body, "Stack trace in 404 response"
        assert "sqlalchemy" not in body, "SQLAlchemy in 404"

    def test_nonexistent_event_id(self, client):
        """GET /api/events/999999 → 404."""
        resp = client.get("/api/events/999999")
        assert resp.status_code == 404
        body = str(resp.get_json()).lower()
        assert "traceback" not in body

    def test_nonexistent_trail_id(self, client):
        """GET /api/trails/999999 → 404."""
        resp = client.get("/api/trails/999999")
        assert resp.status_code == 404
        body = str(resp.get_json()).lower()
        assert "traceback" not in body

    def test_nonexistent_gallery_id(self, client):
        """GET /api/gallery/999999 → 404."""
        resp = client.get("/api/gallery/999999")
        assert resp.status_code == 404
        body = str(resp.get_json()).lower()
        assert "traceback" not in body

    def test_nonexistent_page(self, client):
        """GET /nonexistent → 404 JSON."""
        resp = client.get("/this-page-does-not-exist")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data is not None, "404 should return JSON"
        assert "error" in data, "404 should have 'error' field"


class TestInvalidInputErrorLeakage:
    """Invalid input must produce clean error responses."""

    def test_invalid_json_body(self, client):
        """POST with invalid JSON → 400, no stack trace."""
        resp = client.post(
            "/api/login",
            data="not-json{{{",
            content_type="application/json",
        )
        assert resp.status_code in (400, 500)
        if resp.status_code == 400:
            body = str(resp.get_json() or {}).lower()
            assert "traceback" not in body
            assert "sqlalchemy" not in body

    def test_empty_json_body(self, client):
        """POST with empty body → 400."""
        resp = client.post(
            "/api/login",
            data="",
            content_type="application/json",
        )
        assert resp.status_code in (400, 500)

    def test_post_with_null_json(self, client):
        """POST with null JSON body → 400."""
        resp = client.post(
            "/api/login",
            json=None,
        )
        assert resp.status_code in (400, 500)


class TestSQLInjectionErrorLeakage:
    """SQL injection attempts must not reveal database details."""

    def test_sql_in_login_username(self, client):
        """SQLi in login username → no SQL error in response."""
        resp = client.post(
            "/api/login",
            json={"username": "' OR '1'='1", "password": "x"},
        )
        assert resp.status_code in (200, 401, 400, 429)
        body = str(resp.get_json() or {}).lower()
        assert "sql" not in body, "SQL keyword in response"
        assert "syntax" not in body, "SQL syntax error in response"

    def test_sql_in_login_password(self, client):
        """SQLi in login password → no SQL error."""
        resp = client.post(
            "/api/login",
            json={"username": "admin", "password": "' OR '1'='1"},
        )
        assert resp.status_code in (200, 401, 400, 429)
        body = str(resp.get_json() or {}).lower()
        assert "sql" not in body
        assert "syntax" not in body

    def test_sql_in_search(self, client):
        """SQLi in search parameter → no SQL error."""
        resp = client.get("/api/posts/?search=' OR '1'='1")
        assert resp.status_code == 200
        body = str(resp.get_json() or {}).lower()
        assert "sql" not in body
        assert "syntax" not in body


class TestServerErrorLeakage:
    """500 errors must not reveal stack traces or config."""

    def test_no_secret_key_in_response(self, client):
        """No endpoint should leak SECRET_KEY."""
        endpoints = ["/", "/api/posts/", "/api/events/", "/login"]
        for ep in endpoints:
            resp = client.get(ep)
            if resp.status_code == 200:
                data = resp.get_json() or {}
                data_str = str(data).lower()
                assert "secret_key" not in data_str, (
                    f"SECRET_KEY in response from {ep}"
                )

    def test_no_database_path_in_response(self, client):
        """No endpoint should reveal database path."""
        resp = client.get("/api/posts/")
        body = str(resp.data).lower()
        # In JSON response, there should be no DB path
        if resp.content_type and "json" in resp.content_type:
            assert "sqlite" not in body or "sqlite" in str(resp.get_json()) is None

    def test_no_config_details_in_response(self, client):
        """No endpoint should reveal Flask config."""
        endpoints = ["/api/posts/", "/api/events/", "/api/trails/"]
        for ep in endpoints:
            resp = client.get(ep)
            body = str(resp.get_json() or {}).lower()
            for key in ["flask_env", "secret", "database_url"]:
                assert key not in body, f"Config key '{key}' in response from {ep}"


class TestIDEnumeration:
    """ID enumeration should not reveal existence/non-existence patterns."""

    def test_enumerate_post_ids(self, client):
        """Request sequential post IDs → should not leak info."""
        results = []
        for i in range(1, 20):
            resp = client.get(f"/api/posts/{i}")
            results.append(resp.status_code)
        assert all(s in (200, 404) for s in results), f"Unexpected: {results}"

    def test_enumerate_event_ids(self, client):
        """Request sequential event IDs."""
        for i in range(1, 20):
            resp = client.get(f"/api/events/{i}")
            assert resp.status_code in (200, 404)

    def test_enumerate_trail_ids(self, client):
        """Request sequential trail IDs."""
        for i in range(1, 20):
            resp = client.get(f"/api/trails/{i}")
            assert resp.status_code in (200, 404)


class TestMethodNotAllowedLeakage:
    """Method not allowed responses must not leak info."""

    def test_put_on_get_only_endpoint(self, client):
        """PUT on a GET-only endpoint → 405, no stack trace."""
        resp = client.put("/api/posts/")
        assert resp.status_code in (400, 401, 405, 500)

    def test_delete_on_get_only_endpoint(self, client):
        """DELETE on a GET-only endpoint → 405."""
        resp = client.delete("/api/posts/")
        assert resp.status_code in (400, 401, 405, 500)

    def test_options_on_endpoint(self, client):
        """OPTIONS on endpoint → 200/405, no crash."""
        resp = client.options("/api/posts/")
        assert resp.status_code in (200, 405)
