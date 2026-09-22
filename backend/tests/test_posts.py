import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.post import Post


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # admin user
            user = User(
                username="admin",
                password_hash="$2b$12$pPCud2zJesGxLFYNzBJ6AuXKU5cdpD5hul6hCMEZKQNZW6JunlXFS",
                role="admin",
            )
            db.session.add(user)
            db.session.commit()

            # login user (session-based)
            client.post(
                "/api/login",
                json={"username": "admin", "password": "admin123"},
            )

        yield client

        with app.app_context():
            db.drop_all()


def test_create_post(client):
    response = client.post(
        "/api/posts/",
        json={
            "title": "Prvi post",
            "slug": "prvi-post",
            "content": "Ovo je sadržaj posta",
            "published": True,
        },
    )

    assert response.status_code == 201
    assert "id" in response.json["data"]


def test_list_posts(client):
    with client.application.app_context():
        post = Post(title="Test", slug="test", content="Content")
        db.session.add(post)
        db.session.commit()

    response = client.get("/api/posts/")

    assert response.status_code == 200
    posts = response.json["data"]["posts"]
    assert len(posts) == 1
    assert posts[0]["title"] == "Test"


def test_update_post(client):
    with client.application.app_context():
        post = Post(title="Old title", slug="old-title", content="Old content")
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    response = client.put(
        f"/api/posts/{post_id}",
        json={
            "title": "New title",
            "content": "New content",
        },
    )

    assert response.status_code == 200
    assert response.json["success"] is True


def test_delete_post(client):
    with client.application.app_context():
        post = Post(title="To delete", slug="to-delete", content="Delete me")
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    response = client.delete(f"/api/posts/{post_id}")

    assert response.status_code == 200
    assert response.json["success"] is True

    with client.application.app_context():
        assert Post.query.get(post_id) is None
