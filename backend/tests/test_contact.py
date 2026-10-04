"""Testovi za kontakt formu (/api/contact) i poruke u adminu."""
from app.extensions import db
from app.models.contact_message import ContactMessage

VALID = {
    "name": "Marko Marković",
    "email": "marko@example.com",
    "subject": "Prijava za izlet",
    "message": "Zanima me izlet na Orlovac sljedeće sedmice.",
    "membership_interest": True,
}


def _count(app):
    with app.app_context():
        return ContactMessage.query.count()


class TestPublicSubmit:
    def test_valid_message_is_saved_and_acknowledged(self, app, client, mocker):
        send = mocker.patch("app.services.contact_service.send_email_async", return_value=True)
        r = client.post("/api/contact", json=VALID)
        assert r.status_code == 201 and r.get_json()["success"] is True
        assert _count(app) == 1
        with app.app_context():
            m = ContactMessage.query.one()
            assert (m.name, m.email, m.is_read, m.membership_interest) == ("Marko Marković", "marko@example.com", False, True)
        # društvo dobija e-mail, a odgovor ide direktno posjetiocu
        args, kwargs = send.call_args
        assert args[1] == ["pedmajevica88@gmail.com"]
        assert kwargs["reply_to"] == "marko@example.com"

    def test_email_failure_does_not_lose_the_message(self, app, client, mocker):
        mocker.patch("app.services.contact_service.send_email_async", side_effect=RuntimeError("smtp down"))
        r = client.post("/api/contact", json=VALID)
        assert r.status_code == 201
        assert _count(app) == 1

    def test_notification_escapes_html(self, app, client, mocker):
        send = mocker.patch("app.services.contact_service.send_email_async", return_value=True)
        client.post("/api/contact", json={**VALID, "message": "<script>alert(1)</script> poruka dovoljno duga"})
        html_body = send.call_args[0][2]
        assert "<script>" not in html_body and "&lt;script&gt;" in html_body

    def test_invalid_data_is_rejected(self, app, client):
        for bad in (
            {**VALID, "email": "nije-email"},
            {**VALID, "name": "A"},
            {**VALID, "message": "kratko"},
            {**VALID, "message": "x" * 3001},
            {**VALID, "name": "Ime\nsa novim redom"},
            {**VALID, "subject": "Tema\r\nBcc: zlikovac@example.com"},
            {"name": "Samo ime"},
        ):
            r = client.post("/api/contact", json=bad)
            assert r.status_code == 400, bad
        assert _count(app) == 0

    def test_non_json_body_is_rejected(self, client):
        assert client.post("/api/contact", data="x", content_type="text/plain").status_code == 400

    def test_honeypot_discards_silently(self, app, client, mocker):
        send = mocker.patch("app.services.contact_service.send_email_async", return_value=True)
        r = client.post("/api/contact", json={**VALID, "website": "http://spam.example"})
        assert r.status_code == 201  # robot misli da je uspjelo
        assert _count(app) == 0
        send.assert_not_called()

    def test_unknown_fields_are_ignored(self, app, client, mocker):
        mocker.patch("app.services.contact_service.send_email_async", return_value=True)
        r = client.post("/api/contact", json={**VALID, "is_read": True, "id": 99})
        assert r.status_code == 201
        with app.app_context():
            m = ContactMessage.query.one()
            assert m.is_read is False and m.id != 99


class TestAdminInbox:
    def _seed(self, app):
        with app.app_context():
            for i in range(3):
                db.session.add(ContactMessage(name=f"Posjetilac {i}", email=f"p{i}@example.com", message="Poruka broj %d dovoljno duga" % i))
            db.session.commit()

    def test_requires_admin(self, app, client, regular_user):
        assert client.get("/api/contact").status_code == 401
        client.post("/api/login", json={"username": "planinar", "password": "user123"})
        assert client.get("/api/contact").status_code == 403
        assert client.put("/api/contact/1/read", json={}).status_code == 403
        assert client.delete("/api/contact/1").status_code == 403

    def test_list_read_and_delete(self, app, logged_in_client):
        self._seed(app)
        data = logged_in_client.get("/api/contact").get_json()["data"]
        assert data["unread"] == 3 and len(data["messages"]) == 3
        first = data["messages"][0]["id"]

        assert logged_in_client.put(f"/api/contact/{first}/read", json={"is_read": True}).status_code == 200
        assert logged_in_client.get("/api/contact").get_json()["data"]["unread"] == 2
        assert len(logged_in_client.get("/api/contact?unread=1").get_json()["data"]["messages"]) == 2

        assert logged_in_client.delete(f"/api/contact/{first}").status_code == 200
        assert logged_in_client.get("/api/contact").get_json()["data"]["pagination"]["total"] == 2

    def test_missing_message_is_404(self, logged_in_client):
        assert logged_in_client.put("/api/contact/999/read", json={}).status_code == 404
        assert logged_in_client.delete("/api/contact/999").status_code == 404
