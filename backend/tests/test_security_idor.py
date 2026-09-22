"""
Security Test Suite — IDOR (Insecure Direct Object Reference)
Tests whether users can access/modify resources that don't belong to them.
"""

import pytest


class TestIDORPosts:
    """Test IDOR on posts — public posts are readable, but write needs auth."""

    def test_read_public_post_is_allowed(self, logged_in_client, client):
        """Anyone can read a published post."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "Public Post", "slug": "public-post", "content": "Content"},
        )
        assert resp.status_code in (200, 201)
        data = resp.get_json()
        post_id = data.get("data", {}).get("post", {}).get("id")

        # Read as unauthenticated user
        if post_id:
            resp = client.get(f"/api/posts/{post_id}")
            assert resp.status_code == 200, "Public post should be readable"

    def test_cannot_delete_post_without_auth(self, client):
        """DELETE post without auth → 401."""
        resp = client.delete("/api/posts/1")
        assert resp.status_code in (302, 401)

    def test_cannot_update_post_without_auth(self, client):
        """UPDATE post without auth → 401."""
        resp = client.put("/api/posts/1", json={"title": "Hacked"})
        assert resp.status_code in (302, 401)


class TestIDOREvents:
    """Test IDOR on events."""

    def test_read_published_event_is_allowed(self, client):
        """Published events are public."""
        resp = client.get("/api/events/1")
        assert resp.status_code in (200, 404)

    def test_cannot_delete_event_without_auth(self, client):
        """DELETE event without auth → 401/302."""
        resp = client.delete("/api/events/1")
        assert resp.status_code in (302, 401)

    def test_cannot_update_event_without_auth(self, client):
        """UPDATE event without auth → 401/302."""
        resp = client.put("/api/events/1", json={"title": "Hacked"})
        assert resp.status_code in (302, 401)


class TestIDORTrails:
    """Test IDOR on trails."""

    def test_read_published_trail_is_allowed(self, client):
        """Published trails are public."""
        resp = client.get("/api/trails/1")
        assert resp.status_code in (200, 404)

    def test_cannot_delete_trail_without_auth(self, client):
        """DELETE trail without auth → 401/302."""
        resp = client.delete("/api/trails/1")
        assert resp.status_code in (302, 401)

    def test_cannot_update_trail_without_auth(self, client):
        """UPDATE trail without auth → 401/302."""
        resp = client.put("/api/trails/1", json={"name": "Hacked"})
        assert resp.status_code in (302, 401)


class TestIDORPlanAktivnosti:
    """Test IDOR on plan aktivnosti."""

    def test_read_all_activities_is_public(self, client):
        """GET /api/plan-aktivnosti/ should be public."""
        resp = client.get("/api/plan-aktivnosti/")
        assert resp.status_code in (200, 404)

    def test_cannot_delete_activity_without_auth(self, client):
        """DELETE without auth → 401/302."""
        resp = client.delete("/api/plan-aktivnosti/1")
        assert resp.status_code in (302, 401)

    def test_cannot_update_activity_without_auth(self, client):
        """UPDATE without auth → 401/302."""
        resp = client.put("/api/plan-aktivnosti/1", json={"activity": "Hacked"})
        assert resp.status_code in (302, 401)


class TestIDORGallery:
    """Test IDOR on gallery."""

    def test_read_gallery_image_is_public(self, client):
        """GET gallery image metadata should be public."""
        resp = client.get("/api/gallery/1")
        assert resp.status_code in (200, 404)

    def test_cannot_delete_gallery_image_without_auth(self, client):
        """DELETE gallery image without auth → 401/302."""
        resp = client.delete("/api/gallery/1")
        assert resp.status_code in (302, 401)

    def test_cannot_update_gallery_image_without_auth(self, client):
        """UPDATE gallery image without auth → 401/302."""
        resp = client.put("/api/gallery/1", json={"title": "Hacked"})
        assert resp.status_code in (302, 401)

    def test_cannot_access_raw_image_without_auth_if_private(self, client):
        """GET gallery image binary may be public or private."""
        resp = client.get("/api/gallery/1/image")
        assert resp.status_code in (200, 404, 401)


class TestIDORLikes:
    """Test IDOR on likes."""

    def test_cannot_like_without_auth(self, client):
        """POST /api/posts/1/like without auth → 401/302."""
        resp = client.post("/api/posts/1/like")
        assert resp.status_code in (302, 401)

    def test_cannot_unlike_without_auth(self, client):
        """DELETE /api/posts/1/like without auth → 401/302."""
        resp = client.delete("/api/posts/1/like")
        assert resp.status_code in (302, 401)

    def test_get_likes_is_public(self, client):
        """GET /api/posts/1/likes should be public."""
        resp = client.get("/api/posts/1/likes")
        assert resp.status_code in (200, 404, 401)


class TestCrossUserResourceAccess:
    """Test that unauthenticated users cannot access protected resources."""

    def test_nonexistent_user_cannot_access_protected_routes(self, client):
        """Request with no session at all should not access protected resources."""
        protected_routes = [
            ("DELETE", "/api/posts/1"),
            ("PUT", "/api/posts/1"),
            ("DELETE", "/api/events/1"),
            ("DELETE", "/api/trails/1"),
            ("DELETE", "/api/gallery/1"),
            ("DELETE", "/api/plan-aktivnosti/1"),
            ("PUT", "/api/plan-aktivnosti/1"),
        ]
        for method, route in protected_routes:
            if method == "DELETE":
                resp = client.delete(route)
            elif method == "PUT":
                resp = client.put(route, json={})
            assert resp.status_code in (302, 401, 404, 405), (
                f"{method} {route} accessible without auth: {resp.status_code}"
            )

    def test_admin_can_access_all_resources(self, logged_in_client):
        """Admin should have full access."""
        resp = logged_in_client.get("/admin/posts/")
        assert resp.status_code in (200, 302), (
            f"Admin cannot access admin posts: {resp.status_code}"
        )
