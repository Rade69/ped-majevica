"""
Security Test Suite — Auth Bypass
Tests whether unauthenticated/underprivileged users can access protected resources.
"""

import pytest


class TestAdminRoutesWithoutAuth:
    """Admin routes MUST redirect or return 401/403 without authentication."""

    def test_admin_dashboard_no_session(self, client):
        """GET /admin/dashboard without session → redirect or 401."""
        resp = client.get("/admin/dashboard", follow_redirects=False)
        assert resp.status_code in (302, 401, 301), (
            f"Admin dashboard accessible without auth: {resp.status_code}"
        )

    def test_admin_posts_list_no_auth(self, client):
        """GET /admin/posts/ without session → 401/302."""
        resp = client.get("/admin/posts/", follow_redirects=False)
        assert resp.status_code in (302, 401), (
            f"/admin/posts/ accessible without auth: {resp.status_code}"
        )

    def test_admin_posts_create_no_auth(self, client):
        """POST /admin/posts/ without session → 401/302."""
        resp = client.post(
            "/admin/posts/",
            json={"title": "Hacker Post", "content": "Hacked", "slug": "hacker"},
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"POST /admin/posts/ without auth: {resp.status_code}"
        )

    def test_admin_posts_delete_no_auth(self, client):
        """DELETE /admin/posts/1 without session → 401/302."""
        resp = client.delete("/admin/posts/1", follow_redirects=False)
        assert resp.status_code in (302, 401), (
            f"DELETE /admin/posts/1 without auth: {resp.status_code}"
        )

    def test_admin_posts_update_no_auth(self, client):
        """PUT /admin/posts/1 without session → 401/302."""
        resp = client.put(
            "/admin/posts/1",
            json={"title": "Hacked"},
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"PUT /admin/posts/1 without auth: {resp.status_code}"
        )

    def test_admin_events_create_no_auth(self, client):
        """POST /api/events/ without session → 401."""
        resp = client.post(
            "/api/events/",
            json={"title": "Hacked", "event_date": "2099-01-01"},
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"POST /api/events/ without auth: {resp.status_code}"
        )

    def test_admin_trails_create_no_auth(self, client):
        """POST /api/trails/ without session → 401."""
        resp = client.post(
            "/api/trails/",
            json={"name": "Hacked Trail", "difficulty": "lagana"},
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"POST /api/trails/ without auth: {resp.status_code}"
        )

    def test_admin_gallery_create_no_auth(self, client):
        """POST /api/gallery/ without session → 401."""
        resp = client.post(
            "/api/gallery/",
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"POST /api/gallery/ without auth: {resp.status_code}"
        )

    def test_admin_gallery_delete_no_auth(self, client):
        """DELETE /api/gallery/1 without session → 401."""
        resp = client.delete("/api/gallery/1", follow_redirects=False)
        assert resp.status_code in (302, 401), (
            f"DELETE /api/gallery/1 without auth: {resp.status_code}"
        )

    def test_admin_plan_aktivnosti_create_no_auth(self, client):
        """POST /api/plan-aktivnosti/ without session → 401."""
        resp = client.post(
            "/api/plan-aktivnosti/",
            json={"month": "Januar", "activity": "Hacked"},
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"POST /api/plan-aktivnosti/ without auth: {resp.status_code}"
        )

    def test_admin_plan_aktivnosti_import_no_auth(self, client):
        """POST /api/plan-aktivnosti/import without session → 401."""
        resp = client.post(
            "/api/plan-aktivnosti/import",
            json=[],
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"POST /api/plan-aktivnosti/import without auth: {resp.status_code}"
        )

    def test_admin_plan_aktivnosti_delete_all_no_auth(self, client):
        """DELETE /api/plan-aktivnosti/all without session → 401."""
        resp = client.delete("/api/plan-aktivnosti/all", follow_redirects=False)
        assert resp.status_code in (302, 401), (
            f"DELETE /api/plan-aktivnosti/all without auth: {resp.status_code}"
        )


class TestLikeEndpointsWithoutAuth:
    """Like/unlike endpoints require authentication."""

    def test_like_post_no_auth(self, client):
        """POST /api/posts/1/like without session → 401."""
        resp = client.post("/api/posts/1/like", follow_redirects=False)
        assert resp.status_code in (302, 401), (
            f"POST like without auth: {resp.status_code}"
        )

    def test_unlike_post_no_auth(self, client):
        """DELETE /api/posts/1/like without session → 401."""
        resp = client.delete("/api/posts/1/like", follow_redirects=False)
        assert resp.status_code in (302, 401), (
            f"DELETE unlike without auth: {resp.status_code}"
        )


class TestChangePasswordWithoutAuth:
    """Password change endpoints require authentication."""

    def test_change_password_no_auth(self, client):
        """POST /api/change-password without session → 401/302."""
        resp = client.post(
            "/api/change-password",
            json={
                "current_password": "old",
                "new_password": "newpass123",
                "confirm_password": "newpass123",
            },
            follow_redirects=False,
        )
        assert resp.status_code in (302, 401), (
            f"change-password without auth: {resp.status_code}"
        )


class TestDebugEndpointsWithoutAuth:
    """Debug endpoints MUST be blocked or return 403 without auth."""

    def test_debug_auth_no_auth(self, client):
        """GET /api/debug/auth should NOT be publicly accessible."""
        resp = client.get("/api/debug/auth")
        # Accept 404 if the endpoint doesn't exist (best), or 401/403
        assert resp.status_code in (401, 403, 404, 405), (
            f"/api/debug/auth is publicly accessible: {resp.status_code}"
        )

    def test_debug_auth_response_no_secrets(self, client):
        """Even if debug endpoint exists, it must not leak SECRET_KEY."""
        resp = client.get("/api/debug/auth")
        if resp.status_code == 200:
            data = resp.get_json() or {}
            body = str(data).lower()
            assert "secret" not in body or resp.status_code in (401, 403), (
                "Debug endpoint may leak secret key"
            )
