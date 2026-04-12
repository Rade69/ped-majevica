# 📋 TODO Plan — PED Majevica 1988

**Datum:** 2026-04-11

---

## ✅ ZAVRŠENO

### Sigurnost Backend-a
- [x] Email polje u User modelu
- [x] `last_login` timestamp
- [x] RBAC (ADMIN, EDITOR, USER, GUEST)
- [x] Password reset endpoint-i (token generacija i validacija)
- [x] Hardcodovane lozinke — uklonjene
- [x] CSRF zaštita + rotacija tokena
- [x] CORS — env-based filtering
- [x] Cookie settings — environment-sensitive
- [x] Email servis — Flask-Mail za password reset
- [x] Email verifikacija — nije potrebna (admin-only app, 4 korisnika)

### API Sigurnost
- [x] Rate limiting na write operacije
- [x] Autentifikacija za lajkove
- [x] Input validacija (Marshmallow schema)

### Frontend
- [x] Inline JavaScript izvučen iz HTML-a u module
- [x] Shared moduli: modal, gallery, validation
- [x] API_CONFIG — automatsko određivanje environmenta
- [x] CSRF token u write zahtjevima
- [x] `credentials: 'include'` za cross-origin
- [x] Image optimization (WebP, srcset, lazy loading)
- [x] CDN konfiguracija
- [x] Hardcoded localhost fallback URL-ovi uklonjeni
- [x] Paginacija na blogu — koristi backend API

### Testiranje
- [x] Backend testovi — 10 fajlova (auth, API, integration, admin, routes, **csrf**)
- [x] Integration testovi (`tests/test_api_integration.py`)
- [x] E2E testovi (`frontend/tests/e2e.spec.js`) — Playwright
- [x] CI/CD security scanning
- [x] CSRF testiranje — 9 testova (`tests/test_csrf.py`), svi prolaze ✅

### CI/CD
- [x] GitHub Actions workflow
- [x] Netlify deploy korak
- [x] Render deploy korak
- [x] Security scanning — fail na high/critical

### Performanse
- [x] Redis caching (`backend/app/utils/cache.py`)
- [x] Paginacija na backendu (posts, events, trails)
- [x] Image optimization (WebP konverzija)
- [x] Lazy loading za slike

### SEO
- [x] Meta tags za sve stranice
- [x] Sitemap.xml i robots.txt
- [x] Structured data (Schema.org)
- [x] Open Graph i Twitter cards

### Dokumentacija
- [x] OpenAPI/Swagger
- [x] Contributing guide
- [x] Setup instrukcije
- [x] Deployment guide
- [x] Admin password guide
- [x] Security fixes pregled
- [x] Backup skripta — `scripts/backup_db.py`

---

## 🟡 DJELOMIČNO

### Events paginacija na frontendu
- **Status:** `events.js` učitava iz JSON fajla, ne koristi API
- **Napomena:** Mali broj događaja, paginacija nije kritična

### Trails paginacija na frontendu
- **Status:** `trails.js` učitava sve odjednom, nema `?page=` parametre
- **Napomena:** Mali broj staza (< 20), paginacija nije kritična

### API standardizacija
- **Status:** Neki endpointi sa `/`, neki bez
- **Potrebno:** Ujednačiti konvenciju (`/api/posts/` vs `/api/posts`)

---

## 🔴 PREOSTALO ZA RAD

### Srednji prioritet
- [ ] **CI/CD testiranje** — verificirati deploy sa pravim Netlify/Render tokenima
- [ ] **Monitoring** — Sentry za error tracking, structured logging

### Nizak prioritet
- [ ] **API versioning** — `/api/v1/` šema
- [ ] **API error handling** — standardizovani error response-i
- [ ] **Newsletter** — double opt-in sistem
- [ ] **User profili** — istorija aktivnosti
- [ ] **GPX hosting** — download GPX fajlova za staze
- [ ] **Komentari** — na blog postovima
- [ ] **Social sharing** — Facebook, Twitter integracija

---

## 📊 Redosled realizacije (preporuka)

```
FAZA 1 (završeno):       FAZA 2 (preostalo):        FAZA 3 (budućnost):
┌─────────────────┐    ┌─────────────────┐       ┌─────────────────┐
│ CORS filtering  │    │ CI/CD test      │       │ Monitoring      │
│ Email servis    │    │                 │       │ API versioning  │
│ Backup skripta  │    │                 │       │ Novi feature-i  │
│ Paginacija      │    │                 │       │                 │
│ Hardcoded URL-ovi│   │                 │       │                 │
└─────────────────┘    └─────────────────┘       └─────────────────┘
```

---

*Napomena: Ovaj fajl zamjenjuje stare ANALIZA_SAŽETAK.md, REZIME_SREDNJI_PRIORITET.md, SREDNJI_PRIORITET_SAŽETAK.md, API_CONFIG_PROMENE.md i TODO_PLAN.md.*
