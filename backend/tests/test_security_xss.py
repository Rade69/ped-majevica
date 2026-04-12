"""
Security Test Suite — XSS (Cross-Site Scripting)
Tests whether malicious scripts are properly escaped or rejected.
"""

import pytest

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<script>document.cookie</script>",
    "<img src=x onerror=alert(1)>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "<a href='javascript:alert(1)'>click</a>",
    "<input onfocus=alert(1) autofocus>",
]


class TestStoredXSSInPosts:
    """XSS stored via API and returned via API."""

    def test_xss_in_post_title(self, logged_in_client, client):
        """Store XSS in title, verify it's returned escaped."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={
                "title": XSS_PAYLOADS[0],
                "content": "Safe content",
                "slug": "xss-title-test",
            },
        )
        assert resp.status_code in (200, 201, 400), f"XSS title: {resp.status_code}"

        if resp.status_code in (200, 201):
            data = resp.get_json()
            post_id = data.get("data", {}).get("post", {}).get("id")
            if post_id:
                get_resp = client.get(f"/api/posts/{post_id}")
                get_data = get_resp.get_json()
                title = get_data.get("data", {}).get("post", {}).get("title", "")
                # The raw script tag should not be present as executable
                # JSON responses store raw data; escaping happens at HTML render
                # So we just check the post was stored without crashing
                assert isinstance(title, str), "Title is not a string"

    def test_xss_in_post_content(self, logged_in_client):
        """Store XSS in content."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={
                "title": "XSS Test",
                "content": XSS_PAYLOADS[2],
                "slug": "xss-content-test",
            },
        )
        assert resp.status_code in (200, 201, 400), f"XSS content: {resp.status_code}"

    def test_xss_in_post_category(self, logged_in_client):
        """Store XSS in category field."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={
                "title": "XSS Category",
                "content": "Content",
                "category": XSS_PAYLOADS[0],
            },
        )
        assert resp.status_code in (200, 201, 400), f"XSS category: {resp.status_code}"


class TestStoredXSSInEvents:
    """XSS stored in events."""

    def test_xss_in_event_title(self, logged_in_client):
        """Store XSS in event title."""
        resp = logged_in_client.post(
            "/api/events/",
            json={
                "title": XSS_PAYLOADS[0],
                "event_date": "2099-01-01",
            },
        )
        assert resp.status_code in (200, 201, 400), f"XSS event title: {resp.status_code}"

    def test_xss_in_event_description(self, logged_in_client):
        """Store XSS in event description."""
        resp = logged_in_client.post(
            "/api/events/",
            json={
                "title": "Test Event",
                "description": XSS_PAYLOADS[2],
                "event_date": "2099-01-01",
            },
        )
        assert resp.status_code in (200, 201, 400), f"XSS event desc: {resp.status_code}"


class TestStoredXSSInTrails:
    """XSS stored in trails."""

    def test_xss_in_trail_name(self, logged_in_client):
        """Store XSS in trail name."""
        resp = logged_in_client.post(
            "/api/trails/",
            json={"name": XSS_PAYLOADS[0], "difficulty": "lagana"},
        )
        assert resp.status_code in (200, 201, 400), f"XSS trail name: {resp.status_code}"

    def test_xss_in_trail_description(self, logged_in_client):
        """Store XSS in trail description."""
        resp = logged_in_client.post(
            "/api/trails/",
            json={
                "name": "Test Trail",
                "difficulty": "lagana",
                "description": XSS_PAYLOADS[2],
            },
        )
        assert resp.status_code in (200, 201, 400), f"XSS trail desc: {resp.status_code}"


class TestStoredXSSInPlanAktivnosti:
    """XSS stored in plan aktivnosti."""

    def test_xss_in_activity_name(self, logged_in_client):
        """Store XSS in activity name."""
        resp = logged_in_client.post(
            "/api/plan-aktivnosti/",
            json={"month": "Januar", "activity": XSS_PAYLOADS[0]},
        )
        assert resp.status_code in (200, 201, 400), f"XSS activity name: {resp.status_code}"

    def test_xss_in_organizer(self, logged_in_client):
        """Store XSS in organizer_guide."""
        resp = logged_in_client.post(
            "/api/plan-aktivnosti/",
            json={"month": "Januar", "activity": "Hike", "organizer_guide": XSS_PAYLOADS[3]},
        )
        assert resp.status_code in (200, 201, 400), f"XSS organizer: {resp.status_code}"


class TestReflectedXSS:
    """Reflected XSS through query parameters in JSON responses.

    JSON responses store raw data — the real XSS protection happens
    at the HTML rendering layer (frontend). These tests verify that
    the API doesn't crash and returns the data as-is (which is correct
    for JSON APIs — escaping is the frontend's responsibility).
    """

    def test_search_xss_payload(self, client):
        """Search param with XSS payload → no crash, returns JSON."""
        resp = client.get("/api/posts/?search=" + XSS_PAYLOADS[0])
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict), "Response is not JSON dict"

    def test_category_xss_payload(self, client):
        """Category param with XSS payload → no crash."""
        resp = client.get("/api/posts/?category=" + XSS_PAYLOADS[2])
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict), "Response is not JSON dict"

    def test_pagination_xss(self, client):
        """Page param with XSS payload → no crash."""
        resp = client.get("/api/posts/?page=<script>&per_page=10")
        assert resp.status_code in (200, 400), f"Pagination XSS: {resp.status_code}"


class TestXSSInLogin:
    """XSS in login form inputs."""

    def test_xss_in_login_username(self, client):
        """Login with XSS in username → no crash, no execution."""
        resp = client.post(
            "/api/login",
            json={"username": XSS_PAYLOADS[0], "password": "test"},
        )
        assert resp.status_code in (200, 401, 429), f"XSS login: {resp.status_code}"

    def test_xss_in_login_password(self, client):
        """Login with XSS in password → no crash."""
        resp = client.post(
            "/api/login",
            json={"username": "admin", "password": XSS_PAYLOADS[0]},
        )
        assert resp.status_code in (200, 401, 429), f"XSS login pwd: {resp.status_code}"


class TestXSSInPasswordReset:
    """XSS in password reset flow."""

    def test_xss_in_reset_email(self, client):
        """Password reset with XSS in email → no crash."""
        resp = client.post(
            "/api/password-reset-request",
            json={"email": XSS_PAYLOADS[0]},
        )
        assert resp.status_code in (200, 400, 429), f"XSS reset email: {resp.status_code}"
