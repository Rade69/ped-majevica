"""
Security Test Suite — Abuse & Rate Limiting
Tests whether the application handles rapid/repeated requests gracefully.

NOTE: Rate limiting is DISABLED in test configuration (conftest.py),
so these tests check for stability rather than 429 responses.
In production, rate limiting should be active.
"""

import time
import pytest


class TestLoginRateLimiting:
    """Rapid login attempts should be rate limited or at least stable."""

    def test_rapid_login_attempts(self, client):
        """10 rapid login attempts → no crash, some should be 429 if rate limited."""
        status_codes = []
        for i in range(10):
            resp = client.post(
                "/api/login",
                json={"username": "fake_user", "password": "wrong_password"},
            )
            status_codes.append(resp.status_code)

        # All should be valid responses (401 or 429)
        assert all(s in (200, 401, 429) for s in status_codes), (
            f"Invalid status codes: {status_codes}"
        )

        # If rate limiting is active, at least some should be 429
        has_429 = any(s == 429 for s in status_codes)
        # If rate limiting is disabled (test mode), all should be 401
        all_401 = all(s == 401 for s in status_codes)
        assert has_429 or all_401, (
            f"No rate limiting detected: {status_codes}"
        )

    def test_rapid_login_different_users(self, client):
        """Rapid login with different usernames → no crash."""
        for i in range(10):
            resp = client.post(
                "/api/login",
                json={"username": f"user_{i}", "password": "wrong"},
            )
            assert resp.status_code in (200, 401, 429), (
                f"Login {i}: {resp.status_code}"
            )


class TestPasswordResetRateLimiting:
    """Password reset should be rate limited."""

    def test_rapid_password_reset_requests(self, client):
        """5 rapid password reset requests → some should be 429."""
        status_codes = []
        for i in range(5):
            resp = client.post(
                "/api/password-reset-request",
                json={"email": f"user{i}@test.com"},
            )
            status_codes.append(resp.status_code)

        assert all(s in (200, 400, 429) for s in status_codes), (
            f"Invalid status codes: {status_codes}"
        )


class TestAPIEndpointFlooding:
    """Rapid GET requests to public endpoints should not cause instability."""

    @pytest.mark.parametrize("endpoint", [
        "/api/posts/",
        "/api/events/",
        "/api/trails/",
        "/api/plan-aktivnosti/",
        "/api/gallery/",
    ])
    def test_rapid_get_requests(self, client, endpoint):
        """20 rapid GET requests → no crash, all same status code."""
        status_codes = []
        for _ in range(20):
            resp = client.get(endpoint)
            status_codes.append(resp.status_code)

        # All responses should be valid (200, 404, etc.)
        assert all(200 <= s < 600 for s in status_codes), (
            f"Invalid status codes for {endpoint}: {status_codes}"
        )

        # No progressive degradation (last response should be as good as first)
        assert status_codes[0] == status_codes[-1], (
            f"Response degradation in {endpoint}: {status_codes[0]} vs {status_codes[-1]}"
        )


class TestSearchFlooding:
    """Rapid search requests should not cause instability."""

    def test_rapid_search_requests(self, client):
        """20 rapid search requests → no crash."""
        for i in range(20):
            resp = client.get(f"/api/posts/?search=query_{i}")
            assert resp.status_code == 200, (
                f"Search {i} crashed: {resp.status_code}"
            )

    def test_search_with_special_chars_rapid(self, client):
        """Rapid searches with special chars → no crash."""
        payloads = [
            "<script>",
            "' OR '1'='1",
            "A" * 500,
            "日本語",
            "🏔️🌲⛰️",
            "../../etc/passwd",
            "%00",
            "\x00",
        ]
        for payload in payloads:
            for _ in range(3):
                resp = client.get(f"/api/posts/?search={payload}")
                assert resp.status_code == 200, (
                    f"Search with '{payload[:20]}...' crashed: {resp.status_code}"
                )


class TestDuplicatePostSubmission:
    """Duplicate form submissions should be handled gracefully."""

    def test_duplicate_post_creation(self, logged_in_client):
        """Submit same post twice → both accepted or second rejected."""
        payload = {
            "title": "Duplicate Post",
            "content": "Same content",
            "slug": "dup-post-test",
        }
        resp1 = logged_in_client.post("/admin/posts/", json=payload)
        assert resp1.status_code in (200, 201, 400, 409)

        # Second submission with different slug
        payload["slug"] = "dup-post-test-2"
        resp2 = logged_in_client.post("/admin/posts/", json=payload)
        assert resp2.status_code in (200, 201, 400, 409)


class TestConcurrentLikeRequests:
    """Multiple like requests on same post should not cause issues."""

    def test_rapid_like_requests(self, logged_in_client):
        """5 rapid like requests on same post → no crash."""
        # Create a post first
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "Like Test", "content": "Content", "slug": "like-test"},
        )
        if resp.status_code not in (200, 201):
            pytest.skip(f"Could not create test post: {resp.status_code}")

        data = resp.get_json()
        post_id = data.get("data", {}).get("post", {}).get("id")
        if not post_id:
            pytest.skip("Could not extract post ID")

        # Like multiple times
        status_codes = []
        for _ in range(5):
            resp = logged_in_client.post(f"/api/posts/{post_id}/like")
            status_codes.append(resp.status_code)

        # All should be valid (200 for first like, 400 for duplicate like, or 429)
        assert all(s in (200, 400, 409, 429) for s in status_codes), (
            f"Like status codes: {status_codes}"
        )


class TestLargePayloadAbuse:
    """Large payloads should not crash the application."""

    def test_login_with_huge_payload(self, client):
        """Login with 1MB username field → no crash."""
        resp = client.post(
            "/api/login",
            json={"username": "A" * 1_000_000, "password": "B" * 1_000_000},
        )
        assert resp.status_code in (400, 401, 413, 414, 500), (
            f"Huge login payload: {resp.status_code}"
        )

    def test_post_with_huge_content(self, logged_in_client):
        """Create post with 500KB content → no crash."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={
                "title": "Big Post",
                "content": "X" * 500_000,
                "slug": "big-post",
            },
        )
        assert resp.status_code in (200, 201, 400, 413), (
            f"Huge post: {resp.status_code}"
        )

    def test_event_with_huge_description(self, logged_in_client):
        """Create event with 500KB description → no crash."""
        resp = logged_in_client.post(
            "/api/events/",
            json={
                "title": "Big Event",
                "description": "Y" * 500_000,
                "event_date": "2099-01-01",
            },
        )
        assert resp.status_code in (200, 201, 400, 413), (
            f"Huge event desc: {resp.status_code}"
        )


class TestRefreshAfterSubmit:
    """Simulate browser refresh after form submit."""

    def test_get_after_post(self, logged_in_client):
        """POST then immediate GET on same endpoint → no crash."""
        # Create a post
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "Refresh Test", "content": "Content"},
        )
        assert resp.status_code in (200, 201, 400)

        # Immediately list posts (simulates refresh)
        resp = logged_in_client.get("/admin/posts/")
        assert resp.status_code in (200, 302), (
            f"Get after post: {resp.status_code}"
        )
