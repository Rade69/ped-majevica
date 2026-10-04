"""Testovi za uređivanje blokova sadržaja (/api/content)."""
import pytest

from app.extensions import db
from app.models.content_block import ContentBlock, ContentRevision
from app.services import content_service


def _put(client, key, html, page="index"):
    return client.put(f"/api/content/{page}/{key}", json={"html": html})


class TestPublicRead:
    def test_empty_page_returns_no_blocks(self, client):
        r = client.get("/api/content/index")
        assert r.status_code == 200
        assert r.get_json()["data"]["blocks"] == {}

    def test_unknown_page_is_404(self, client):
        assert client.get("/api/content/nepoznata").status_code == 404


class TestAuthorization:
    def test_anonymous_cannot_save(self, client):
        assert _put(client, "hero_subtitle", "x").status_code in (401, 403)

    def test_regular_user_cannot_save(self, client, regular_user):
        client.post("/api/login", json={"username": "planinar", "password": "user123"})
        assert _put(client, "hero_subtitle", "x").status_code in (401, 403)

    def test_anonymous_cannot_read_history_or_reset(self, client):
        assert client.get("/api/content/index/k/history").status_code in (401, 403)
        assert client.delete("/api/content/index/k").status_code in (401, 403)


class TestSaveAndRead:
    def test_admin_saves_and_public_reads(self, logged_in_client):
        r = _put(logged_in_client, "hero_subtitle", "<p>Novi <strong>tekst</strong></p>")
        assert r.status_code == 200
        blocks = logged_in_client.get("/api/content/index").get_json()["data"]["blocks"]
        assert blocks["hero_subtitle"] == "<p>Novi <strong>tekst</strong></p>"

    def test_classes_are_kept_for_styling(self, logged_in_client):
        _put(logged_in_client, "k", '<span class="text-primary-red font-bold">1988</span>')
        blocks = logged_in_client.get("/api/content/index").get_json()["data"]["blocks"]
        assert 'class="text-primary-red font-bold"' in blocks["k"]

    def test_dangerous_html_is_stripped(self, logged_in_client):
        evil = (
            '<p onclick="x()">a</p><script>alert(1)</script>'
            '<a href="javascript:alert(1)">l</a>'
            '<img src=x onerror="alert(1)">'
            '<iframe src="https://evil"></iframe>'
            '<div style="position:fixed">s</div>'
        )
        _put(logged_in_client, "k", evil)
        saved = logged_in_client.get("/api/content/index").get_json()["data"]["blocks"]["k"]
        for bad in ("<script", "onclick", "onerror", "javascript:", "<iframe", "style="):
            assert bad not in saved

    def test_links_to_https_are_allowed(self, logged_in_client):
        _put(logged_in_client, "k", '<a href="https://example.org/x">l</a>')
        saved = logged_in_client.get("/api/content/index").get_json()["data"]["blocks"]["k"]
        assert 'href="https://example.org/x"' in saved

    @pytest.mark.parametrize("key", ["Veliko", "ima razmak", "a/b", "", "x" * 65])
    def test_invalid_key_rejected(self, logged_in_client, key):
        r = logged_in_client.put(f"/api/content/index/{key}", json={"html": "x"})
        assert r.status_code in (400, 404)

    def test_unknown_page_rejected(self, logged_in_client):
        assert _put(logged_in_client, "k", "x", page="nepoznata").status_code == 400

    def test_missing_html_rejected(self, logged_in_client):
        r = logged_in_client.put("/api/content/index/k", json={})
        assert r.status_code == 400

    def test_too_long_rejected(self, logged_in_client):
        r = _put(logged_in_client, "k", "a" * (content_service.MAX_HTML_LENGTH + 1))
        assert r.status_code == 400


class TestResetAndHistory:
    def test_reset_returns_to_original(self, logged_in_client):
        _put(logged_in_client, "k", "<p>a</p>")
        assert logged_in_client.delete("/api/content/index/k").status_code == 200
        blocks = logged_in_client.get("/api/content/index").get_json()["data"]["blocks"]
        assert "k" not in blocks

    def test_history_and_restore(self, logged_in_client):
        _put(logged_in_client, "k", "<p>prva</p>")
        _put(logged_in_client, "k", "<p>druga</p>")
        revs = logged_in_client.get("/api/content/index/k/history").get_json()["data"]["revisions"]
        assert [r["html"] for r in revs] == ["<p>druga</p>", "<p>prva</p>"]

        first_id = revs[1]["id"]
        r = logged_in_client.post(f"/api/content/index/k/restore/{first_id}")
        assert r.status_code == 200
        blocks = logged_in_client.get("/api/content/index").get_json()["data"]["blocks"]
        assert blocks["k"] == "<p>prva</p>"

    def test_restore_unknown_revision_is_404(self, logged_in_client):
        _put(logged_in_client, "k", "<p>a</p>")
        assert logged_in_client.post("/api/content/index/k/restore/99999").status_code == 404

    def test_history_is_capped(self, logged_in_client, app):
        for i in range(content_service.MAX_REVISIONS + 5):
            _put(logged_in_client, "k", f"<p>{i}</p>")
        with app.app_context():
            block = ContentBlock.query.filter_by(page="index", key="k").one()
            assert ContentRevision.query.filter_by(block_id=block.id).count() == content_service.MAX_REVISIONS

    def test_blocks_are_per_page(self, logged_in_client):
        _put(logged_in_client, "k", "<p>a</p>", page="index")
        galerija = logged_in_client.get("/api/content/galerija").get_json()["data"]["blocks"]
        assert galerija == {}


class TestPageMarkup:
    """Označeni blokovi u HTML stranicama moraju odgovarati pravilima API-ja."""

    PAGES_DIR = __import__("pathlib").Path(__file__).resolve().parents[2] / "frontend" / "pages"
    FILES = {"index": "index.html", "galerija": "galerija.html", "uclanite-se": "uclanite-se.html"}

    def _keys(self, page):
        import re
        html = (self.PAGES_DIR / self.FILES[page]).read_text(encoding="utf-8")
        return re.findall(r'data-cms="([^"]*)"', html), html

    @pytest.mark.parametrize("page", ["index", "galerija", "uclanite-se"])
    def test_keys_are_valid_and_unique(self, page):
        keys, _ = self._keys(page)
        assert keys, f"{page}: nema označenih blokova"
        assert len(keys) == len(set(keys)), f"{page}: ponovljen ključ"
        for key in keys:
            assert content_service.KEY_RE.match(key), f"{page}: neispravan ključ {key!r}"

    @pytest.mark.parametrize("page", ["index", "galerija", "uclanite-se"])
    def test_page_loads_content_script(self, page):
        _, html = self._keys(page)
        assert f'src="/js/content.js" data-page="{page}"' in html
        assert page in content_service.ALLOWED_PAGES

    def test_every_block_has_label(self):
        import re
        for page in self.FILES:
            _, html = self._keys(page)
            tags = re.findall(r"<[a-z0-9]+[^>]*data-cms=[^>]*>", html)
            for tag in tags:
                assert "data-cms-label=" in tag, tag[:80]
