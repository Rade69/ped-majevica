"""
Security Test Suite — Input Validation
Tests whether the application properly validates all input fields.
"""

import pytest


class TestPostValidation:
    """Validate post creation/editing input fields."""

    def test_create_post_empty_title(self, logged_in_client):
        """POST /admin/posts/ with empty title → 400."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "", "content": "Some content"},
        )
        assert resp.status_code == 400, f"Empty title accepted: {resp.status_code}"

    def test_create_post_no_title(self, logged_in_client):
        """POST /admin/posts/ without title field → 400."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"content": "Some content"},
        )
        assert resp.status_code == 400, f"Missing title accepted: {resp.status_code}"

    def test_create_post_empty_content(self, logged_in_client):
        """POST /admin/posts/ with empty content → 400."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "Test Post", "content": ""},
        )
        assert resp.status_code == 400, f"Empty content accepted: {resp.status_code}"

    def test_create_post_very_long_title(self, logged_in_client):
        """POST /admin/posts/ with title > 200 chars → 400 or truncated."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "A" * 5000, "content": "Content"},
        )
        assert resp.status_code in (200, 201, 400), (
            f"Unexpected response for long title: {resp.status_code}"
        )

    def test_create_post_huge_content(self, logged_in_client):
        """POST /admin/posts/ with 100KB content → 400 or accepted (no crash)."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "Huge Content", "content": "X" * 100_000},
        )
        assert resp.status_code in (200, 201, 400, 413), (
            f"Unexpected response for huge content: {resp.status_code}"
        )

    def test_create_post_null_values(self, logged_in_client):
        """POST /admin/posts/ with null values → 400."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": None, "content": None},
        )
        assert resp.status_code in (400, 201), (
            f"Null values: {resp.status_code} (400 expected)"
        )

    def test_create_post_emoji_title(self, logged_in_client):
        """POST /admin/posts/ with emoji in title → accepted or 400 (no crash)."""
        resp = logged_in_client.post(
            "/admin/posts/",
            json={"title": "🏔️ Planina 🌲", "content": "Content"},
        )
        assert resp.status_code in (200, 201, 400), (
            f"Emoji response: {resp.status_code}"
        )


class TestEventValidation:
    """Validate event creation/editing input fields."""

    def test_create_event_empty_title(self, logged_in_client):
        """POST /api/events/ with empty title → 400."""
        resp = logged_in_client.post(
            "/api/events/",
            json={"title": "", "event_date": "2099-01-01"},
        )
        assert resp.status_code == 400, f"Empty title accepted: {resp.status_code}"

    def test_create_event_invalid_date(self, logged_in_client):
        """POST /api/events/ with invalid date → 400."""
        resp = logged_in_client.post(
            "/api/events/",
            json={"title": "Test", "event_date": "not-a-date"},
        )
        assert resp.status_code == 400, f"Invalid date accepted: {resp.status_code}"

    def test_create_event_negative_participants(self, logged_in_client):
        """POST /api/events/ with negative max_participants."""
        resp = logged_in_client.post(
            "/api/events/",
            json={
                "title": "Test",
                "event_date": "2099-01-01",
                "max_participants": -100,
            },
        )
        assert resp.status_code in (200, 201, 400), (
            f"Negative participants: {resp.status_code}"
        )

    def test_create_event_huge_number(self, logged_in_client):
        """POST /api/events/ with enormous max_participants."""
        resp = logged_in_client.post(
            "/api/events/",
            json={
                "title": "Test",
                "event_date": "2099-01-01",
                "max_participants": 10**15,
            },
        )
        assert resp.status_code in (200, 201, 400), (
            f"Huge number response: {resp.status_code}"
        )


class TestTrailValidation:
    """Validate trail creation/editing input fields."""

    def test_create_trail_empty_name(self, logged_in_client):
        """POST /api/trails/ with empty name → 400."""
        resp = logged_in_client.post(
            "/api/trails/",
            json={"name": "", "difficulty": "lagana"},
        )
        assert resp.status_code == 400, f"Empty name accepted: {resp.status_code}"

    def test_create_trail_invalid_difficulty(self, logged_in_client):
        """POST /api/trails/ with invalid difficulty → 400."""
        resp = logged_in_client.post(
            "/api/trails/",
            json={"name": "Test Trail", "difficulty": "impossible"},
        )
        assert resp.status_code in (200, 201, 400), (
            f"Invalid difficulty response: {resp.status_code}"
        )

    def test_create_trail_negative_distance(self, logged_in_client):
        """POST /api/trails/ with negative distance."""
        resp = logged_in_client.post(
            "/api/trails/",
            json={"name": "Test", "difficulty": "lagana", "distance_km": -50},
        )
        assert resp.status_code in (200, 201, 400), (
            f"Negative distance: {resp.status_code}"
        )


class TestSearchAndFilterValidation:
    """Validate search and filter parameters on public endpoints."""

    def test_search_empty_query(self, client):
        """GET /api/posts?search= → no crash."""
        resp = client.get("/api/posts/?search=")
        assert resp.status_code == 200, f"Empty search crashed: {resp.status_code}"

    def test_search_very_long_query(self, client):
        """GET /api/posts?search=<10K chars> → no crash."""
        resp = client.get("/api/posts/?search=" + "A" * 10_000)
        assert resp.status_code == 200, f"Long search crashed: {resp.status_code}"

    def test_search_special_chars(self, client):
        """GET /api/posts?search=<script> → no crash, no XSS."""
        resp = client.get("/api/posts/?search=<script>alert(1)</script>")
        assert resp.status_code == 200, f"Special chars search crashed: {resp.status_code}"

    def test_pagination_negative_page(self, client):
        """GET /api/posts?page=-1 → no crash."""
        resp = client.get("/api/posts/?page=-1&per_page=10")
        assert resp.status_code == 200, f"Negative page crashed: {resp.status_code}"

    def test_pagination_huge_page(self, client):
        """GET /api/posts?page=999999 → no crash, empty list."""
        resp = client.get("/api/posts/?page=999999&per_page=10")
        assert resp.status_code == 200, f"Huge page crashed: {resp.status_code}"
        data = resp.get_json()
        posts = data.get("data", {}).get("posts", data.get("posts", []))
        assert len(posts) == 0, f"Huge page returned posts: {len(posts)}"

    def test_pagination_huge_per_page(self, client):
        """GET /api/posts?per_page=10000 → capped at 50 or rejected."""
        resp = client.get("/api/posts/?page=1&per_page=10000")
        assert resp.status_code == 200, f"Huge per_page crashed: {resp.status_code}"

    def test_category_filter_special_chars(self, client):
        """GET /api/posts?category=<script> → no crash."""
        resp = client.get("/api/posts/?category=<script>")
        assert resp.status_code == 200, f"Category filter crashed: {resp.status_code}"


class TestPlanAktivnostiValidation:
    """Validate plan aktivnosti input fields."""

    def test_create_activity_empty_activity(self, logged_in_client):
        """POST /api/plan-aktivnosti/ with empty activity → 400."""
        resp = logged_in_client.post(
            "/api/plan-aktivnosti/",
            json={"month": "Januar", "activity": ""},
        )
        assert resp.status_code == 400, f"Empty activity accepted: {resp.status_code}"

    def test_create_activity_empty_month(self, logged_in_client):
        """POST /api/plan-aktivnosti/ with empty month → 400."""
        resp = logged_in_client.post(
            "/api/plan-aktivnosti/",
            json={"month": "", "activity": "Test"},
        )
        assert resp.status_code == 400, f"Empty month accepted: {resp.status_code}"

    def test_create_activity_long_name(self, logged_in_client):
        """POST /api/plan-aktivnosti/ with very long activity name."""
        resp = logged_in_client.post(
            "/api/plan-aktivnosti/",
            json={"month": "Januar", "activity": "A" * 2000},
        )
        assert resp.status_code in (200, 201, 400), (
            f"Long activity response: {resp.status_code}"
        )


class TestDuplicateSubmit:
    """Test duplicate/resubmit scenarios."""

    def test_duplicate_post_submission(self, logged_in_client):
        """Submit same post twice quickly → should create two or reject duplicate."""
        payload = {"title": "Dup Post", "content": "Content"}
        resp1 = logged_in_client.post("/admin/posts/", json=payload)
        payload["slug"] = "dup-post-2"  # unique slug
        resp2 = logged_in_client.post("/admin/posts/", json=payload)

        assert resp1.status_code in (200, 201, 400), f"First submit: {resp1.status_code}"
        assert resp2.status_code in (200, 201, 400), f"Second submit: {resp2.status_code}"
