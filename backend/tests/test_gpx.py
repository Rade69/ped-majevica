"""GPX fajl staze: dodavanje (urednik), preuzimanje (svi), provjera ispravnosti."""
import io

import pytest

from app.extensions import db
from app.models.trail import Trail

GPX = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<gpx version="1.1" creator="test" xmlns="http://www.topografix.com/GPX/1/1">'
    b'<trk><name>Staza</name><trkseg>'
    b'<trkpt lat="44.5" lon="18.9"><ele>300</ele></trkpt>'
    b'<trkpt lat="44.51" lon="18.91"><ele>320</ele></trkpt>'
    b'</trkseg></trk></gpx>'
)


@pytest.fixture
def trail_id(app):
    with app.app_context():
        trail = Trail(name="Velika staza - Tavna", difficulty="Srednja", published=True)
        db.session.add(trail)
        db.session.commit()
        return trail.id


def trails(client):
    body = client.get("/api/trails").get_json()
    body = body.get("data", body)
    return body["trails"]


def upload(client, trail_id, data=GPX, name="staza.gpx"):
    return client.post(f"/api/trails/{trail_id}/gpx", data={"file": (io.BytesIO(data), name)}, content_type="multipart/form-data")


def test_editor_uploads_and_anyone_downloads(client, logged_in_client, trail_id):
    r = upload(logged_in_client, trail_id)
    assert r.status_code == 200
    summary = r.get_json()["data"]
    assert summary["points"] == 2 and summary["filename"] == "velika-staza-tavna.gpx"

    # javni posjetilac (nakon odjave) preuzima isti fajl
    client.get("/logout")
    d = client.get(f"/api/trails/{trail_id}/gpx")
    assert d.status_code == 200 and d.data == GPX
    assert d.mimetype == "application/gpx+xml"
    assert 'attachment; filename="velika-staza-tavna.gpx"' in d.headers["Content-Disposition"]


def test_trail_list_exposes_download_url_without_loading_file(client, logged_in_client, trail_id):
    before = trails(client)[0]
    assert before["has_gpx"] is False and not before["gpx_file_url"]
    upload(logged_in_client, trail_id)
    after = trails(client)[0]
    assert after["has_gpx"] is True and after["gpx_file_url"] == f"/api/trails/{trail_id}/gpx"
    assert "gpx_data" not in after


def test_replace_and_remove(client, logged_in_client, trail_id):
    upload(logged_in_client, trail_id)
    newer = GPX.replace(b'lat="44.5"', b'lat="44.6"')
    assert upload(logged_in_client, trail_id, newer).status_code == 200
    assert client.get(f"/api/trails/{trail_id}/gpx").data == newer
    assert logged_in_client.delete(f"/api/trails/{trail_id}/gpx").status_code == 200
    assert client.get(f"/api/trails/{trail_id}/gpx").status_code == 404
    assert trails(client)[0]["has_gpx"] is False


INVALID = {
    "prazno": (b"", "prazno.gpx"),
    "nije-xml": (b"ovo nije xml", "x.gpx"),
    "html": (b'<?xml version="1.0"?><html><body/></html>', "html.gpx"),
    "bez-tacaka": (b'<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk></trk></gpx>', "bez-tacaka.gpx"),
    "xml-bomba": (b'<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY a "aaaa">]><gpx><wpt lat="1" lon="1"/></gpx>', "bomba.gpx"),
    "pogresan-nastavak": (GPX, "pogresan-nastavak.txt"),
    "prevelik": (GPX + b" " * (5 * 1024 * 1024), "prevelik.gpx"),
}


@pytest.mark.parametrize("case", list(INVALID))
def test_invalid_files_are_rejected(app, logged_in_client, trail_id, case):
    data, name = INVALID[case]
    assert upload(logged_in_client, trail_id, data, name).status_code == 400
    with app.app_context():
        assert db.session.get(Trail, trail_id).has_gpx is False


def test_missing_file_and_missing_trail(logged_in_client, trail_id):
    assert logged_in_client.post(f"/api/trails/{trail_id}/gpx", data={}, content_type="multipart/form-data").status_code == 400
    assert upload(logged_in_client, 99999).status_code == 404


def test_only_editors_can_change_gpx(client, regular_user, trail_id):
    assert upload(client, trail_id).status_code in (401, 403)
    client.post("/api/login", json={"username": "planinar", "password": "user123"})
    assert upload(client, trail_id).status_code == 403
    assert client.delete(f"/api/trails/{trail_id}/gpx").status_code == 403


def test_unpublished_trail_gpx_hidden_from_public(app, client, logged_in_client, trail_id):
    upload(logged_in_client, trail_id)
    with app.app_context():
        db.session.get(Trail, trail_id).published = False
        db.session.commit()
    assert logged_in_client.get(f"/api/trails/{trail_id}/gpx").status_code == 200  # urednik vidi
    logged_in_client.get("/logout")
    assert client.get(f"/api/trails/{trail_id}/gpx").status_code == 404  # javnost ne vidi
