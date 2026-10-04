"""Testovi za robots.txt, sitemap.xml, favicon i osnovne SEO oznake."""
import re


def test_robots_txt_served(client):
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert r.mimetype == "text/plain"
    body = r.get_data(as_text=True)
    assert "Sitemap: https://pedmajevica.org/sitemap.xml" in body
    assert "Disallow: /admin" in body and "Disallow: /api/" in body


def test_sitemap_lists_only_public_pages(client):
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.mimetype == "application/xml"
    urls = re.findall(r"<loc>([^<]+)</loc>", r.get_data(as_text=True))
    assert "https://pedmajevica.org/" in urls
    assert "https://pedmajevica.org/galerija" in urls
    assert "https://pedmajevica.org/uclanite-se" in urls
    assert not any("admin" in u or "login" in u for u in urls)


def test_favicon_served_and_small(client):
    for path in ("/favicon.png", "/favicon.ico"):
        r = client.get(path)
        assert r.status_code == 200
        assert r.mimetype == "image/png"
        assert len(r.data) < 200_000  # nije vise 800 KB


def test_logo_is_optimized(client):
    r = client.get("/assets/images/icons/logo-2.png")
    assert r.status_code == 200
    assert len(r.data) < 200_000


def test_public_pages_have_canonical_and_open_graph(client):
    for path, canonical in (
        ("/", "https://pedmajevica.org/"),
        ("/galerija", "https://pedmajevica.org/galerija"),
        ("/uclanite-se", "https://pedmajevica.org/uclanite-se"),
    ):
        html = client.get(path).get_data(as_text=True)
        assert f'<link rel="canonical" href="{canonical}">' in html, path
        assert 'property="og:title"' in html and 'property="og:image"' in html, path


def _make_post(app):
    from app.extensions import db
    from app.models.post import Post
    with app.app_context():
        post = Post(title="Dugacak clanak", slug="dugacak-clanak", content="x" * 1000,
                    content_html="<p>" + "x" * 1000 + "</p>", content_text="x" * 1000,
                    preview="Kratak izvod", category="savjeti", published=True)
        db.session.add(post)
        db.session.commit()
        return post.id


def test_posts_list_lite_omits_full_text(app, client):
    _make_post(app)
    full = client.get("/api/posts?per_page=5").get_json()["data"]["posts"][0]
    lite = client.get("/api/posts?per_page=5&lite=1").get_json()["data"]["posts"][0]
    assert full["content_html"] and full["content"]
    assert lite["content"] is None and lite["content_html"] is None
    assert len(lite["content_text"]) <= 300
    assert lite["title"] == full["title"] and lite["id"] == full["id"] and lite["preview"] == "Kratak izvod"


def test_single_post_still_returns_full_text(app, client):
    post_id = _make_post(app)
    data = client.get(f"/api/posts/{post_id}").get_json()
    data = data.get("data", data)
    data = data.get("post", data)
    assert data["content_html"] and len(data["content_text"]) == 1000
