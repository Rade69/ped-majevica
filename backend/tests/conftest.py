"""
PED Majevica 1988 - Test Configuration & Fixtures
==================================================
Ovaj fajl sadrži zajedničke fixture-ove i konfiguraciju za sve testove.

Usage:
    pytest tests/                    # Pokreni sve testove
    pytest tests/ -v                 # Verbose output
    pytest tests/ --cov=app          # Sa code coverage
    pytest tests/test_routes.py -v   # Pokreni specifičan fajl
"""

import pytest
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.post import Post
from app.models.event import Event
from app.models.trail import Trail
from app.models.gallery import GalleryImage
from pathlib import Path
import os


@pytest.fixture(scope="session")
def app():
    """
    Kreiraj Flask aplikaciju za testiranje.
    Koristi SQLite in-memory bazu za brze testove.
    """
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-for-ped-majevica-1988",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,  # Onemogući CSRF za testove
        "RATELIMIT_ENABLED": False,  # Onemogući rate limiting za testove
        "SERVER_NAME": "localhost:5000",
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Test client za Flask aplikaciju.
    Omogućava simulaciju HTTP zahteva.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner(app):
    """
    CLI runner za testiranje komandne linije.
    """
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    """
    Kreiraj admin korisnika za testove.
    Osigurava da tabele postoje i da admin već ne postoji.
    """
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.has_table('user'):
            db.create_all()

        existing = User.query.filter_by(username="admin").first()
        if existing:
            return existing

        user = User(
            username="admin",
            email="admin@pedmajevica.ba",
            role="admin"
        )
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def regular_user(app):
    """
    Kreiraj običnog korisnika za testove.
    """
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.has_table('user'):
            db.create_all()

        existing = User.query.filter_by(username="planinar").first()
        if existing:
            return existing

        user = User(
            username="planinar",
            email="planinar@pedmajevica.ba",
            role="user"
        )
        user.set_password("user123")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def logged_in_client(client, admin_user):
    """
    Test client sa ulogovanim admin korisnikom.
    """
    client.post(
        "/api/login",
        json={"username": "admin", "password": "admin123"}
    )
    return client


@pytest.fixture
def sample_post(app):
    """
    Kreiraj testni post/članak.
    """
    with app.app_context():
        post = Post(
            title="Test Članak",
            slug="test-clanak",
            content="Ovo je sadržaj testnog članka.",
            category="vesti",
            published=True
        )
        db.session.add(post)
        db.session.commit()
        return post


@pytest.fixture
def sample_event(app):
    """
    Kreiraj testni događaj.
    """
    with app.app_context():
        event = Event(
            title="Test Događaj",
            description="Opis testnog događaja",
            event_date="2026-04-15",
            location="Majevica",
            published=True
        )
        db.session.add(event)
        db.session.commit()
        return event


@pytest.fixture
def sample_trail(app):
    """
    Kreiraj testnu planinarsku stazu.
    """
    with app.app_context():
        trail = Trail(
            name="Test Staza",
            description="Opis testne staze",
            difficulty="srednja",
            distance_km=10.5,
            duration_hours=4,
            published=True
        )
        db.session.add(trail)
        db.session.commit()
        return trail


@pytest.fixture
def sample_gallery_image(app):
    """
    Kreiraj testnu sliku za galeriju.
    """
    with app.app_context():
        image = GalleryImage(
            title="Test Slika",
            description="Opis testne slike",
            category="priroda",
            published=True,
            order=1
        )
        db.session.add(image)
        db.session.commit()
        return image


@pytest.fixture(scope="function")
def fresh_db(app):
    """
    Fixture za testove koji zahtevaju svežu bazu.
    Briše i ponovo kreira sve tabele.
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db
        db.drop_all()
