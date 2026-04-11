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

### Frontend
- [x] API_CONFIG — automatsko određivanje environmenta (localhost vs produkcija)
- [x] CSRF token se šalje u write zahtjevima (`X-CSRFToken` header)
- [x] `credentials: 'include'` za cross-origin
- [x] blog.js i trails.js — credentials za GET zahtjeve

### CI/CD
- [x] GitHub Actions — realni deploy koraci (Netlify CLI + Render API curl)
- [x] Security scanning — `safety check` i `npm audit --audit-level=high` bez `|| true`
- [x] Backend testovi — 10 test fajlova (auth, API, integration, admin, routes, **csrf**)
- [x] E2E testovi — Playwright (`frontend/tests/e2e.spec.js`)
- [x] CSRF testovi — 9 testova (`backend/tests/test_csrf.py`), svi prolaze ✅

### Backend funkcionalnosti
- [x] Redis caching sa graceful fallback (`cache_response` decorator)
- [x] RBAC dekoratori — `admin_required`, `editor_required`, `role_required`
- [x] Swagger/OpenAPI — `/api/docs`, `/api/redoc`, `/api/openapi.json`
- [x] Paginacija na backendu — events, trails, api routes (`?page=&per_page=`, max 50)
- [x] Rate limiting — testiran na login endpointu (429 nakon 6. zahtjeva)
- [x] Image optimization — WebP, srcset, lazy loading
- [x] SEO — meta tags, sitemap, structured data, Open Graph

---

## ⚠️ Djelomično implementirano

| Stavka | Šta fali | Dokaz iz koda |
|--------|----------|---------------|
| **CORS HTTP domene** | localhost HTTP unosi su u istoj listi kao produkcija — nema env-based filtering | `backend/app/__init__.py` — svi origins u jednoj listi |
| **Paginacija na posts** | `backend/app/routes/posts.py` — `list_posts` koristi `.all()` bez page/per_page | `posts.py` linija ~20 |
| **Hardcoded fallback URL-ovi** | `blog.js` i `trails.js` imaju hardcoded `http://localhost:5000` u fallback granama | Defanzivni kod, ali nije čist |
| **Email verifikacija** | Fajl `backend/app/services/email_verification.py` **NE POSTOJI** | Grep search — 0 rezultata |

---

## ❌ Nije implementirano

| Stavka | Status |
|--------|--------|
| Password reset email slanje | Placeholder — token se samo loguje |
| Email servis (SMTP/SendGrid) | Nema konfiguracije |
| Paginacija na frontendu | Backend podržava, frontend JS ne koristi |
| API versioning (`/api/v1/`) | Nema |
| API error handling standardizacija | Nema |
| API endpoint konvencija | Neki sa `/`, neki bez |
| Backup skripta | Nema |
| Monitoring (Sentry, structured logging) | Osnovno Python logging |

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
