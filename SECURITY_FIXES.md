# Sigurnosne Popravke — PED Majevica 1988

**Datum:** 2026-04-11

---

## 🚨 Kritični popravci (uradjeno)

### 1. Hardcodovane admin lozinke
**Fajl:** `backend/app/services/user_service.py`
- **Problem:** Default lozinke su bile vidljive u kodu kao fallback kada env varijable nisu postavljene.
- **Popravka:** Uklonjene default vrijednosti. Aplikacija preskače kreiranje admina ako `ADMIN_*_PASSWORD` env varijable nisu postavljene. Dodan warning u logove.

### 2. Password reset token (bio samo user_id)
**Fajlovi:** `backend/app/services/password_reset_service.py`, `backend/app/routes/auth.py`
- **Problem:** Token je bio običan `user_id` string — bilo ko je mogao pogoditi i resetovati lozinku.
- **Popravka:** Kreiran `password_reset_service.py` sa kriptografski potpisanim tokenima (`itsdangerous.URLSafeTimedSerializer`). Token sadrži `user_id`, `email`, `created_at` i ističe nakon 1h.

### 3. Password reset ne šalje email
- **Stanje:** Placeholder — token se loguje u server logove.
- **Rješenje:** Umjesto email servisa, kreirane CLI komande za admin reset:
  - `flask reset-admin-password` — interaktivni reset
  - `flask list-admins` — lista svih admin korisnika
- **Dokumentacija:** `ADMIN_PASSWORD_GUIDE.md`

### 4. CSRF token rotacija
**Fajl:** `backend/app/utils/csrf.py`
- **Problem:** Token se nije mijenjao tokom sesije.
- **Popravka:** Dodana `rotate_csrf_token()` — token se rotira nakon svake validacije.

### 5. CORS — nesigurne HTTP domene
**Fajl:** `backend/app/__init__.py`
- **Problem:** CORS lista je uključivala `http://pedmajevica.org` (bez HTTPS).
- **Popravka:** Uklonjene sve HTTP domene iz produkcije. Ostavljeni samo `localhost`/`127.0.0.1` za development i HTTPS domene za produkciju.

### 6. Auto-migracija (direktni ALTER TABLE)
**Fajl:** `backend/app/__init__.py`
- **Problem:** Aplikacija je direktno izvršavala `ALTER TABLE` SQL komande.
- **Popravka:** Uklonjen auto-migracija kod. Sve promjene sheme moraju ići kroz `flask db migrate` / `flask db upgrade` (Alembic).

### 7. Model metode sa direktnim commit-ima
**Fajlovi:** `backend/app/models/user.py`, `backend/app/routes/auth.py`
- **Problem:** `User.update_last_login()` je pozivao `db.session.commit()` unutar modela.
- **Popravka:** Uklonjen `commit()` iz modela. Commit se vrši u route handleru nakon poziva metode.

### 8. Cookie settings — nisu environment-sensitive
**Fajl:** `backend/app/config.py`
- **Problem:** `SESSION_COOKIE_SECURE = True` i `SameSite = "None"` su bili fiksni — onemogućavali su HTTP development.
- **Popravka:** Dinamičko podešavanje na osnovu `FLASK_ENV`:
  - **Produkcija:** `Secure=True`, `SameSite=None`
  - **Development:** `Secure=False`, `SameSite=Lax`

---

## 🌐 Frontend API konfiguracija (uradjeno)

**Fajlovi:** `frontend/assets/js/config.js`, `frontend/js/api.js`, `frontend/js/blog.js`, `frontend/js/trails.js`

- **Problem:** Hardcodovani API URL-ovi (`http://127.0.0.1:5000`, Render.com URL), bez CSRF tokena, `credentials: "same-origin"` za cross-origin.
- **Popravka:**
  - `API_CONFIG` automatski određuje environment (localhost vs produkcija)
  - CSRF token se šalje u svim write zahtjevima
  - `credentials: 'include'` za cross-origin autentifikaciju
  - Fallback mehanizam ako `API_CONFIG` nije učitan

---

## 📋 Preostali problemi (nisu kritični)

| Problem | Status | Prioritet |
|---------|--------|-----------|
| Email slanje za password reset | Placeholder (loguje token) | Srednji |
| Paginacija na frontendu | Backend podržava, frontend ne koristi | Nizak |
| Redis cache fallback | Disable ako nije dostupan | Nizak |
| CDN za statičke fajlove | Netlify je CDN za frontend | Nizak |
| Backup strategija | Render.com ima backup za PostgreSQL | Srednji |
| Monitoring / alerting | Osnovno logovanje | Nizak |

---

## 🔑 Admin korisnici

Postoje 4 admin naloga. Lozinke se postavljaju **isključivo** kroz environment varijable:

```
ADMIN_RADOVAN_PASSWORD=...
ADMIN_ALEKSANDAR_PASSWORD=...
ADMIN_SRECKO_PASSWORD=...
ADMIN_MILOJKO_PASSWORD=...
```

Za reset: `flask reset-admin-password --username <ime>`
Za listu: `flask list-admins`

Detalji u `ADMIN_PASSWORD_GUIDE.md`.
