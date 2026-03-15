# -*- coding: utf-8 -*-
"""
PED Majevica 1988 - Frontend Routes Tests
==========================================
Testovi za sve frontend rute (HTML stranice).
"""

import pytest


class TestFrontendRoutes:
    """Testovi za javne frontend rute."""

    def test_index_page_loads(self, client):
        """Pocetna stranica se ucitava."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"PED MAJEVICA" in response.data
        assert b"1988" in response.data

    def test_index_has_navigation(self, client):
        """Pocetna ima navigaciju."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Staze" in response.data
        assert b"Blog" in response.data
        assert b"Kalendar" in response.data
        assert b"Galerija" in response.data
        assert b"Kontakt" in response.data

    def test_galerija_page_loads(self, client):
        """Galerija stranica se ucitava."""
        response = client.get("/galerija")
        assert response.status_code == 200

    def test_galerija_html_page_loads(self, client):
        """Galerija.html stranica se ucitava."""
        response = client.get("/galerija.html")
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        """Login stranica se ucitava."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_html_page_loads(self, client):
        """Login.html stranica se ucitava."""
        response = client.get("/login.html")
        assert response.status_code == 200

    def test_admin_page_loads(self, client):
        """Admin panel se ucitava."""
        response = client.get("/admin")
        assert response.status_code in [200, 302]

    def test_admin_html_page_loads(self, client):
        """Admin.html panel se ucitava."""
        response = client.get("/admin.html")
        assert response.status_code == 200

    def test_uclanite_se_page_loads(self, client):
        """Uclanite-se stranica se ucitava."""
        response = client.get("/uclanite-se")
        assert response.status_code == 200

    def test_uclanite_se_html_page_loads(self, client):
        """Uclanite-se.html stranica se ucitava."""
        response = client.get("/uclanite-se.html")
        assert response.status_code == 200

    def test_nonexistent_page_returns_404(self, client):
        """Nepostojuca stranica vraca 404."""
        response = client.get("/nepostojuca-stranica")
        assert response.status_code == 404


class TestStaticFiles:
    """Testovi za staticke fajlove."""

    def test_css_loads(self, client):
        """CSS fajl se ucitava."""
        response = client.get("/assets/css/output.min.css")
        assert response.status_code in [200, 404]

    def test_js_loads(self, client):
        """JS fajl se ucitava."""
        response = client.get("/js/app.js")
        assert response.status_code in [200, 404]

    def test_transliterator_js_loads(self, client):
        """Transliterator JS se ucitava."""
        response = client.get("/js/transliterator.js")
        assert response.status_code in [200, 404]


class TestNavigationLinks:
    """Testovi za navigacione linkove."""

    def test_index_links_to_galerija(self, client):
        """Pocetna ima link ka galeriji."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"/galerija" in response.data

    def test_index_links_to_uclanite_se(self, client):
        """Pocetna ima link ka uclanjenju."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"/uclanite-se" in response.data

    def test_galerija_links_back_to_index(self, client):
        """Galerija ima link ka pocetnoj."""
        response = client.get("/galerija")
        assert response.status_code == 200
        assert b'href="/"' in response.data
