"""
Integration tests for API endpoints
"""

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.post import Post


@pytest.fixture
def app():
    """Create test application"""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_client(client, app):
    """Create authenticated test client"""
    with app.app_context():
        # Create test user
        user = User(username="testuser", email="test@test.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Login
        client.post(
            "/login",
            data={"username": "testuser", "password": "password123"},
            follow_redirects=True,
        )

    return client


class TestPostsAPI:
    """Test posts API endpoints"""

    def test_get_posts_empty(self, client):
        """Test getting posts when none exist"""
        response = client.get("/api/posts")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "posts" in data["data"]

    def test_get_posts_with_pagination(self, client, app):
        """Test pagination parameters"""
        with app.app_context():
            # Create test posts
            for i in range(15):
                post = Post(title=f"Test Post {i}", content=f"Content {i}")
                db.session.add(post)
            db.session.commit()

        response = client.get("/api/posts?page=1&per_page=5")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]["posts"]) == 5
        assert data["data"]["pagination"]["total"] == 15
        assert data["data"]["pagination"]["pages"] == 3

    def test_get_post_by_id(self, client, app):
        """Test getting single post"""
        with app.app_context():
            post = Post(title="Test", content="Content")
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        response = client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["title"] == "Test"

    def test_get_post_not_found(self, client):
        """Test 404 for non-existent post"""
        response = client.get("/api/posts/99999")
        assert response.status_code == 404


class TestLikesAPI:
    """Test likes API endpoints"""

    def test_like_requires_auth(self, client, app):
        """Test that liking requires authentication"""
        with app.app_context():
            post = Post(title="Test", content="Content")
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        response = client.post(f"/api/posts/{post_id}/like")
        assert response.status_code == 401

    def test_like_post(self, auth_client, app):
        """Test liking a post"""
        with app.app_context():
            post = Post(title="Test", content="Content")
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        response = auth_client.post(f"/api/posts/{post_id}/like")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["user_has_liked"] is True

    def test_unlike_post(self, auth_client, app):
        """Test unliking a post"""
        with app.app_context():
            post = Post(title="Test", content="Content")
            post.likes_count = 1
            db.session.add(post)
            db.session.commit()
            post_id = post.id

            # Add like
            from app.models.like import Like
            from flask_login import current_user

            like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(like)
            db.session.commit()

        response = auth_client.delete(f"/api/posts/{post_id}/like")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["user_has_liked"] is False


class TestEventsAPI:
    """Test events API endpoints"""

    def test_get_events(self, client):
        """Test getting events list"""
        response = client.get("/api/events")
        assert response.status_code == 200

    def test_get_events_pagination(self, client, app):
        """Test events pagination"""
        with app.app_context():
            from app.models.event import Event
            from datetime import date

            for i in range(12):
                event = Event(
                    title=f"Event {i}", description="Test", event_date=date(2026, 1, 1)
                )
                db.session.add(event)
            db.session.commit()

        response = client.get("/api/events?page=1&per_page=5")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["events"]) == 5
        assert data["pagination"]["total"] == 12


class TestTrailsAPI:
    """Test trails API endpoints"""

    def test_get_trails(self, client):
        """Test getting trails list"""
        response = client.get("/api/trails")
        assert response.status_code == 200

    def test_get_trails_pagination(self, client, app):
        """Test trails pagination"""
        with app.app_context():
            from app.models.trail import Trail

            for i in range(8):
                trail = Trail(
                    name=f"Trail {i}", description="Test trail", distance_km=10
                )
                db.session.add(trail)
            db.session.commit()

        response = client.get("/api/trails?page=1&per_page=3")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["trails"]) == 3
        assert data["pagination"]["total"] == 8
