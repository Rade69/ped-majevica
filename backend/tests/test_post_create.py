"""Dodavanje clanka kroz admin: tacno onaj oblik podataka koji salje admin forma."""
import pytest

from app.models.post import Post

CATEGORIES = ["oprema", "ishrana", "savjeti", "putopisi", "sjecanja", "ostalo"]


def admin_form_payload(category, title="Moj clanak"):
    """Polja koja salje forma u admin.html (saveArticle)."""
    return {
        "title": title, "slug": "moj-clanak", "category": category,
        "content_html": "<p>Tekst članka.</p>", "content_markdown": "<p>Tekst članka.</p>",
        "content_text": "Tekst članka.", "preview": "Tekst", "word_count": 2,
        "image_count": 1, "images": ["/assets/images/blog/slika.webp"], "published": True,
    }


@pytest.mark.parametrize("category", CATEGORIES)
def test_admin_can_create_post_in_every_category(app, logged_in_client, category):
    r = logged_in_client.post("/api/posts", json=admin_form_payload(category, f"Clanak {category}"))
    assert r.status_code == 201, r.get_json()
    with app.app_context():
        post = Post.query.filter_by(title=f"Clanak {category}").one()
        assert post.category == category
        assert post.content_html == "<p>Tekst članka.</p>"
        assert post.images == ["/assets/images/blog/slika.webp"]
        assert post.published is True


def test_new_memory_is_listed_under_its_category(app, logged_in_client, client):
    logged_in_client.post("/api/posts", json=admin_form_payload("sjecanja", "Sjećanje na druga"))
    data = client.get("/api/posts?category=sjecanja").get_json()["data"]
    assert [p["title"] for p in data["posts"]] == ["Sjećanje na druga"]


def test_unknown_category_is_rejected(app, logged_in_client):
    r = logged_in_client.post("/api/posts", json=admin_form_payload("nepostoji"))
    assert r.status_code == 400
    with app.app_context():
        assert Post.query.count() == 0


def test_missing_title_or_content_is_rejected(logged_in_client):
    bad = admin_form_payload("ostalo")
    bad["title"] = ""
    assert logged_in_client.post("/api/posts", json=bad).status_code == 400
    bad = admin_form_payload("ostalo")
    bad.update(content_html="", content_markdown="")
    assert logged_in_client.post("/api/posts", json=bad).status_code == 400


def test_legacy_content_field_still_works(logged_in_client):
    r = logged_in_client.post("/api/posts", json={"title": "Stari oblik", "content": "Tekst starog oblika.", "category": "ostalo"})
    assert r.status_code == 201


def test_blog_and_admin_offer_the_memories_category():
    from pathlib import Path
    frontend = Path(__file__).resolve().parents[2] / "frontend"
    assert 'value="sjecanja"' in (frontend / "pages" / "index.html").read_text(encoding="utf-8")
    assert (frontend / "pages" / "admin.html").read_text(encoding="utf-8").count('value="sjecanja"') == 2
    assert "'sjecanja'" in (frontend / "js" / "blog.js").read_text(encoding="utf-8")
