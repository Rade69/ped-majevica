"""Regresioni testovi: izmjena sadrzaja samo za admina/urednika; nepostojeci id = 404; health."""
import re

import pytest

# Rute koje smiju svi prijavljeni korisnici ili su javne (ostale moraju biti samo za admina/urednika)
OPEN_FOR_LOGGED_IN = ("/like", "/api/change-password")
SKIP_PREFIXES = ("/api/login", "/login", "/logout", "/api/logout", "/api/password-reset", "/static")


def _write_rules(app):
    rules = []
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith(SKIP_PREFIXES) or any(x in rule.rule for x in OPEN_FOR_LOGGED_IN):
            continue
        for method in sorted(rule.methods - {"GET", "HEAD", "OPTIONS"}):
            rules.append((method, re.sub(r"<[^>]+>", "1", rule.rule)))
    return rules


def test_there_are_write_routes_to_check(app):
    assert len(_write_rules(app)) >= 20


def test_anonymous_cannot_use_any_write_route(app, client):
    for method, path in _write_rules(app):
        r = client.open(path, method=method, json={})
        assert r.status_code in (401, 403, 302), f"{method} {path} -> {r.status_code}"


def test_regular_user_cannot_use_any_write_route(app, client, regular_user):
    client.post("/api/login", json={"username": "planinar", "password": "user123"})
    for method, path in _write_rules(app):
        r = client.open(path, method=method, json={})
        assert r.status_code in (403, 302), f"{method} {path} -> {r.status_code}"


@pytest.mark.parametrize("method,path", [
    ("PUT", "/api/posts/999"), ("DELETE", "/api/posts/999"),
    ("PUT", "/api/events/999"), ("DELETE", "/api/events/999"),
    ("PUT", "/api/trails/999"), ("DELETE", "/api/trails/999"),
    ("PUT", "/api/gallery/999"), ("DELETE", "/api/gallery/999"),
    ("PUT", "/api/plan-aktivnosti/999"), ("DELETE", "/api/plan-aktivnosti/999"),
    ("GET", "/api/posts/999"), ("GET", "/api/events/999"), ("GET", "/api/trails/999"),
])
def test_missing_id_is_404_not_500(logged_in_client, method, path):
    r = logged_in_client.open(path, method=method, json={})
    assert r.status_code == 404, f"{method} {path} -> {r.status_code}"


def test_like_on_missing_post_is_404(logged_in_client):
    assert logged_in_client.post("/api/posts/999/like").status_code == 404


def test_health_endpoint(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok", "database": "ok"}


def test_years_are_computed_not_hardcoded():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[2] / "frontend" / "pages" / "index.html").read_text(encoding="utf-8")
    assert 'data-years-since="1988"' in html
    assert "preko 35 godina" not in html and ">35+<" not in html


def test_admin_dashboard_page_requires_editor_role(client, regular_user):
    assert client.get("/admin/dashboard").status_code == 302  # neprijavljen -> prijava
    client.post("/api/login", json={"username": "planinar", "password": "user123"})
    assert client.get("/admin/dashboard").status_code == 403  # obican korisnik


def test_admin_dashboard_page_for_admin(logged_in_client):
    assert logged_in_client.get("/admin/dashboard").status_code == 200
