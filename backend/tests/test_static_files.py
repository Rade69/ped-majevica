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
