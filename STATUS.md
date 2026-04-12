# Status Projekta — PED Majevica 1988

**Datum:** 2026-04-11
**Verifikacija koda:** 2026-04-11

---

## ✅ Šta je stvarno implementirano (verificirano u kodu)

### Sigurnost (Kritično — završeno)
- [x] Hardcodovane lozinke uklonjene — `os.getenv()` bez default vrijednosti
- [x] Password reset tokeni — itsdangerous sa `user_id`, `email`, `created_at`, 1h expiry
- [x] CSRF token rotacija — `rotate_csrf_token()` nakon svake validacije
- [x] Auto-migracija SQL — uklonjena (samo komentar u kodu)
- [x] Model commit-i — `update_last_login()` više ne commit-a
- [x] Cookie settings — dinamički na osnovu `FLASK_ENV`
- [x] CLI komande — `flask reset-admin-password`, `flask list-admins`
- [x] Auth route-i koriste `password_reset_service` (ne plain user_id)
- [x] Email servis — Flask-Mail za password reset, graceful fallback na logging
- [x] Backup skripta — `scripts/backup_db.py` (SQLite + PostgreSQL, gzip, cleanup)

### Frontend
- [x] API_CONFIG — automatsko određivanje environmenta (localhost vs produkcija)
- [x] CSRF token se šalje u write zahtjevima (`X-CSRFToken` header)
- [x] `credentials: 'include'` za cross-origin
- [x] blog.js i trails.js — credentials za GET zahtjeve
- [x] Paginacija na blogu — koristi backend `?page=&per_page=` API
- [x] Hardcoded localhost fallback URL-ovi uklonjeni

### Backend funkcionalnosti
- [x] Redis caching sa graceful fallback (`cache_response` decorator)
- [x] RBAC dekoratori — `admin_required`, `editor_required`, `role_required`
- [x] Swagger/OpenAPI — `/api/docs`, `/api/redoc`, `/api/openapi.json`
- [x] Paginacija na backendu — posts, events, trails (`?page=&per_page=`, max 50)
- [x] Rate limiting — testiran na login endpointu (429 nakon 6. zahtjeva)
- [x] Image optimization — WebP, srcset, lazy loading
- [x] SEO — meta tags, sitemap, structured data, Open Graph

### CI/CD
- [x] GitHub Actions — realni deploy koraci (Netlify CLI + Render API curl)
- [x] Security scanning — `safety check` i `npm audit --audit-level=high` bez `|| true`
- [x] Backend testovi — 10 test fajlova (auth, API, integration, admin, routes, **csrf**)
- [x] E2E testovi — Playwright (`frontend/tests/e2e.spec.js`)
- [x] CSRF testovi — 9 testova (`backend/tests/test_csrf.py`), svi prolaze ✅

---

## ⚠️ Djelomično implementirano

| Stavka | Šta fali | Dokaz iz koda |
|--------|----------|---------------|
| **Events paginacija na frontendu** | `events.js` učitava iz JSON fajla, ne koristi API | `events.js` — fetch iz `/assets/data/plan_aktivnosti.json` |
| **Trails paginacija na frontendu** | `trails.js` učitava sve odjednom, mali broj zapisa | `trails.js` — nema `?page=` parametre |

---

## ❌ Nije implementirano

| Stavka | Status |
|--------|--------|
| API versioning (`/api/v1/`) | Nema |
| API error handling standardizacija | Nema |
| API endpoint konvencija | Neki sa `/`, neki bez |
| Monitoring (Sentry, structured logging) | Osnovno Python logging |
| Email verifikacija | Namjerno izostavljeno — admin-only app (4 korisnika) |

---

## 📊 Tehnički Stack

| Komponenta | Tehnologija |
|------------|-------------|
| Backend | Python 3, Flask 3 |
| ORM | Flask-SQLAlchemy + Flask-Migrate (Alembic) |
| Auth | Flask-Login + Flask-Bcrypt |
| Serijalizacija | Marshmallow |
| Rate limiting | Flask-Limiter |
| CORS | Flask-CORS |
| Cache | Redis |
| Frontend | Vanilla JS, Tailwind CSS |
| CI/CD | GitHub Actions |
| Hosting (frontend) | Netlify |
| Hosting (backend) | Render.com |
| DB (dev) | SQLite |
| DB (prod) | PostgreSQL |

---

## 🔐 Admin Nalozi

4 admin korisnika: `radovan`, `aleksandar`, `srecko`, `milojko`
Lozinke se postavljaju isključivo kroz environment varijable.
Za detalje pogledati `ADMIN_PASSWORD_GUIDE.md`.
