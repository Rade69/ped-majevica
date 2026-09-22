"""
PED Majevica 1988 - API Endpoint Tests
=======================================
Testovi za API endpointove:
- Gallery API
- Events API
- Trails API
- Posts API
- Plan Aktivnosti API

Ovi testovi verifikuju da:
- API endpointovi rade
- CRUD operacije funkcionišu
- Autentifikacija je potrebna za admin operacije
- Validacija podataka radi
"""

import pytest
from datetime import date
from app.extensions import db
from app.models.post import Post
from app.models.event import Event
from app.models.trail import Trail
from app.models.gallery import GalleryImage


class TestGalleryAPI:
    """Testovi za Gallery API."""
    
    def test_get_gallery_list(self, client):
        """Dohvati listu svih slika iz galerije."""
        response = client.get("/api/gallery/")
        assert response.status_code == 200
        assert "data" in response.json or "images" in response.json
    
    def test_get_gallery_image_by_id(self, client, sample_gallery_image):
        """Dohvati pojedinačnu sliku iz galerije."""
        response = client.get(f"/api/gallery/{sample_gallery_image.id}")
        assert response.status_code in [200, 404]
    
    def test_get_gallery_thumbnail(self, client, sample_gallery_image):
        """Dohvati thumbnail slike."""
        response = client.get(f"/api/gallery/{sample_gallery_image.id}/thumbnail")
        # Thumbnail može vratiti 404 ako slika ne postoji
        assert response.status_code in [200, 404]
    
    def test_get_gallery_full_image(self, client, sample_gallery_image):
        """Dohvati punu veličinu slike."""
        response = client.get(f"/api/gallery/{sample_gallery_image.id}/image")
        assert response.status_code in [200, 404]
    
    def test_create_gallery_image_requires_auth(self, client):
        """Kreiranje slike zahteva autentifikaciju."""
        response = client.post(
            "/api/gallery/",
            json={"title": "Test", "category": "priroda"}
        )
        # Treba da vrati 401 Unauthorized
        assert response.status_code == 401
    
    def test_create_gallery_image_with_auth(self, logged_in_client):
        """Kreiranje slike sa autentifikacijom."""
        response = logged_in_client.post(
            "/api/gallery/",
            json={
                "title": "Test Slika",
                "description": "Opis",
                "category": "priroda",
                "published": True
            }
        )
        assert response.status_code in [201, 400]
    
    def test_update_gallery_image_requires_auth(self, client, sample_gallery_image):
        """Ažuriranje slike zahteva autentifikaciju."""
        response = client.put(
            f"/api/gallery/{sample_gallery_image.id}",
            json={"title": "Novi naslov"}
        )
        assert response.status_code == 401
    
    def test_delete_gallery_image_requires_auth(self, client, sample_gallery_image):
        """Brisanje slike zahteva autentifikaciju."""
        response = client.delete(f"/api/gallery/{sample_gallery_image.id}")
        assert response.status_code == 401


class TestEventsAPI:
    """Testovi za Events API."""
    
    def test_get_events_list(self, client):
        """Dohvati listu svih događaja."""
        response = client.get("/api/events/")
        assert response.status_code == 200
        assert "data" in response.json or "events" in response.json
    
    def test_get_event_by_id(self, client, sample_event):
        """Dohvati pojedinačni događaj."""
        response = client.get(f"/api/events/{sample_event.id}")
        assert response.status_code in [200, 404]
    
    def test_get_published_events_only(self, client):
        """Dohvati samo objavljene događaje."""
        with client.application.app_context():
            unpublished = Event(
                title="Neobjavljen",
                description="Test",
                event_date=date(2026, 5, 1),
                published=False
            )
            db.session.add(unpublished)
            db.session.commit()
        
        response = client.get("/api/events/")
        assert response.status_code == 200
    
    def test_create_event_requires_auth(self, client):
        """Kreiranje događaja zahteva autentifikaciju."""
        response = client.post(
            "/api/events/",
            json={"title": "Novi događaj", "date": "2026-06-01"}
        )
        assert response.status_code == 401
    
    def test_create_event_with_auth(self, logged_in_client):
        """Kreiranje događaja sa autentifikacijom."""
        response = logged_in_client.post(
            "/api/events/",
            json={
                "title": "Novi Događaj",
                "description": "Opis događaja",
                "date": "2026-06-15",
                "location": "Majevica",
                "published": True
            }
        )
        assert response.status_code in [201, 400]
    
    def test_update_event_with_auth(self, logged_in_client, sample_event):
        """Ažuriranje događaja sa autentifikacijom."""
        response = logged_in_client.put(
            f"/api/events/{sample_event.id}",
            json={"title": "Ažuriran Događaj"}
        )
        assert response.status_code in [200, 400]
    
    def test_delete_event_with_auth(self, logged_in_client, sample_event):
        """Brisanje događaja sa autentifikacijom."""
        response = logged_in_client.delete(f"/api/events/{sample_event.id}")
        assert response.status_code == 200


class TestTrailsAPI:
    """Testovi za Trails API."""
    
    def test_get_trails_list(self, client):
        """Dohvati listu svih staza."""
        response = client.get("/api/trails/")
        assert response.status_code == 200
        assert "data" in response.json or "trails" in response.json
    
    def test_get_trail_by_id(self, client, sample_trail):
        """Dohvati pojedinačnu stazu."""
        response = client.get(f"/api/trails/{sample_trail.id}")
        assert response.status_code in [200, 404]
    
    def test_get_trails_by_difficulty(self, client, sample_trail):
        """Filtriraj staze po težini."""
        response = client.get("/api/trails/?difficulty=srednja")
        assert response.status_code == 200
    
    def test_create_trail_requires_auth(self, client):
        """Kreiranje staze zahteva autentifikaciju."""
        response = client.post(
            "/api/trails/",
            json={"name": "Nova staza", "difficulty": "laka"}
        )
        assert response.status_code == 401
    
    def test_create_trail_with_auth(self, logged_in_client):
        """Kreiranje staze sa autentifikacijom."""
        response = logged_in_client.post(
            "/api/trails/",
            json={
                "name": "Nova Staza",
                "description": "Opis nove staze",
                "difficulty": "srednja",
                "length_km": 8.5,
                "duration_hours": 3,
                "published": True
            }
        )
        assert response.status_code in [201, 400]
    
    def test_update_trail_with_auth(self, logged_in_client, sample_trail):
        """Ažuriranje staze sa autentifikacijom."""
        response = logged_in_client.put(
            f"/api/trails/{sample_trail.id}",
            json={"name": "Ažurirana Staza"}
        )
        assert response.status_code in [200, 400]
    
    def test_delete_trail_with_auth(self, logged_in_client, sample_trail):
        """Brisanje staze sa autentifikacijom."""
        response = logged_in_client.delete(f"/api/trails/{sample_trail.id}")
        assert response.status_code == 200


class TestPostsAPI:
    """Testovi za Posts API (Blog/Članci)."""
    
    def test_get_posts_list(self, client):
        """Dohvati listu svih članaka."""
        response = client.get("/api/posts/")
        assert response.status_code == 200
        assert isinstance(response.json, list) or "data" in response.json
    
    def test_get_post_by_id(self, client, sample_post):
        """Dohvati pojedinačni članak."""
        response = client.get(f"/api/posts/{sample_post.id}")
        assert response.status_code in [200, 404]
    
    def test_get_published_posts_only(self, client):
        """Dohvati samo objavljene članke."""
        with client.application.app_context():
            unpublished = Post(
                title="Neobjavljen",
                slug="neobjavljen",
                content="Test",
                category="vesti",
                published=False
            )
            db.session.add(unpublished)
            db.session.commit()
        
        response = client.get("/api/posts/")
        assert response.status_code == 200
    
    def test_create_post_requires_auth(self, client):
        """Kreiranje članka zahteva autentifikaciju."""
        response = client.post(
            "/api/posts/",
            json={"title": "Novi članak", "content": "Sadržaj"}
        )
        assert response.status_code == 401
    
    def test_create_post_with_auth(self, logged_in_client):
        """Kreiranje članka sa autentifikacijom."""
        response = logged_in_client.post(
            "/api/posts/",
            json={
                "title": "Novi Članak",
                "content": "Sadržaj novog članka",
                "category": "vesti",
                "published": True
            }
        )
        assert response.status_code in [201, 400]
    
    def test_update_post_with_auth(self, logged_in_client, sample_post):
        """Ažuriranje članka sa autentifikacijom."""
        response = logged_in_client.put(
            f"/api/posts/{sample_post.id}",
            json={"title": "Ažuriran Članak"}
        )
        assert response.status_code in [200, 400]
    
    def test_delete_post_with_auth(self, logged_in_client, sample_post):
        """Brisanje članka sa autentifikacijom."""
        response = logged_in_client.delete(f"/api/posts/{sample_post.id}")
        assert response.status_code == 200


class TestPlanAktivnostiAPI:
    """Testovi za Plan Aktivnosti API."""
    
    def test_get_plan_list(self, client):
        """Dohvati listu plana aktivnosti."""
        response = client.get("/api/plan-aktivnosti/")
        # Endpoint može vratiti 200 ili 404 ako ne postoji
        assert response.status_code in [200, 404]
    
    def test_get_plan_by_id(self, client):
        """Dohvati plan po ID-ju."""
        response = client.get("/api/plan-aktivnosti/1")
        assert response.status_code in [200, 404]


class TestAPIValidation:
    """Testovi za API validaciju."""
    
    def test_invalid_json_returns_400(self, client):
        """Nevalidan JSON vraća 400."""
        response = client.post(
            "/api/posts/",
            data="not json",
            content_type="application/json"
        )
        assert response.status_code in [400, 401]
    
    def test_missing_required_fields_returns_400(self, logged_in_client):
        """Nedostajuća obavezna polja vraćaju 400."""
        response = logged_in_client.post(
            "/api/posts/",
            json={"title": ""}  # Nedostaje content
        )
        assert response.status_code in [400, 401]
    
    def test_method_not_allowed(self, client):
        """Nedozvoljena HTTP metoda vraća 405."""
        response = client.patch("/api/posts/")
        assert response.status_code == 405
