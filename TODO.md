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
- [x] CORS — HTTP domene uklonjene iz produkcije (localhost ostavljen za dev)
- [x] Cookie settings — environment-sensitive
- [ ] Email verifikacija — fajl ne postoji u kodu, TODO_PLAN lažno označen ✅

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

---

## 🟡 DJELOMIČNO / PLACEHOLDER

### CORS — nema env-based filtering
- **Status:** Svi origins (uključujući HTTP localhost) su u jednoj listi
- **Potrebno:** Razdvojiti development i production origins na osnovu `FLASK_ENV`
- **Fajl:** `backend/app/__init__.py`

### Password reset email slanje
- **Status:** Token se generiše i loguje, ali se **ne šalje email**
- **Razlog:** Nije potrebno za 4 admina — CLI komande su alternativa
- **Ako zatreba:** Integrisati SMTP ili SendGrid

### Paginacija na posts route-u
- **Status:** `backend/app/routes/posts.py` koristi `.all()` bez paginacije
- **Potrebno:** Dodati `?page=` i `?per_page=` parametre kao u events/trails

### Paginacija na frontendu
- **Status:** Backend podržava `?page=&per_page=`, frontend JS ne koristi
- **Potrebno:** Ažurirati `api.js`, `blog.js`, `events.js` da podržavaju paginaciju

### CI/CD deployment
- **Status:** Koraci su dodani u `.github/workflows/ci.yml` ali **nisu testirani u produkciji**
- **Potrebno:** Čuvati Netlify i Render tokene u GitHub Secrets, testirati push na main

### Hardcoded fallback URL-ovi
- **Status:** `blog.js` i `trails.js` imaju hardcoded `http://localhost:5000` u fallback granama
- **Potrebno:** Ukloniti ili zamijeniti sa `window.API_CONFIG?.DEVELOPMENT_API`

### API standardizacija
- **Status:** Neki endpointi sa `/`, neki bez
- **Potrebno:** Ujednačiti konvenciju (`/api/posts/` vs `/api/posts`)

### Email verifikacija
- **Status:** `backend/app/services/email_verification.py` **ne postoji**
- **Potrebno:** Kreirati servis ili ukloniti iz dokumentacije

---

## 🔴 PREOSTALO ZA RAD

### Srednji prioritet
- [ ] **Email servis** — SMTP / SendGrid integracija za password reset
- [ ] **Paginacija na posts.py** — dodati `?page=&per_page=` u `list_posts`
- [ ] **Frontend paginacija** — koristiti backend paginaciju u JS modulima
- [ ] **CORS env-based filtering** — razdvojiti dev/production origins
- [ ] **Backup strategija** — skripta za backup baze + automatizacija
- [ ] **Email verifikacija** — kreirati servis ili maknuti iz TODO liste
- [ ] **CI/CD testiranje** — verificirati deploy sa pravim tokenima

### Nizak prioritet
- [ ] **API versioning** — `/api/v1/` šema
- [ ] **API error handling** — standardizovani error response-i
- [ ] **Monitoring** — Sentry za error tracking, structured logging
- [ ] **CDN za backend** — Cloudflare za API i statičke fajlove
- [ ] **Ukloniti hardcoded fallback URL-ove** — iz blog.js i trails.js
- [ ] **Newsletter** — double opt-in sistem
- [ ] **User profili** — istorija aktivnosti
- [ ] **GPX hosting** — download GPX fajlova za staze
- [ ] **Komentari** — na blog postovima
- [ ] **Social sharing** — Facebook, Twitter integracija

---

## 📊 Redosled realizacije (preporuka)

```
FAZA 1 (odmah):        FAZA 2 (1-2 sedmice):     FAZA 3 (1-2 mjeseca):
┌─────────────────┐    ┌─────────────────┐       ┌─────────────────┐
│ CORS filtering  │    │ Email servis    │       │ Monitoring      │
│ Posts paginacija│    │ Backup skripta  │       │ API versioning  │
│ Frontend pagin. │    │ Email verific.  │       │ Novi feature-i  │
│ CI/CD test      │    │                 │       │                 │
│ Hardcoded URL-ovi│   │                 │       │                 │
└─────────────────┘    └─────────────────┘       └─────────────────┘
```

---

*Napomena: Ovaj fajl zamjenjuje stare ANALIZA_SAŽETAK.md, REZIME_SREDNJI_PRIORITET.md, SREDNJI_PRIORITET_SAŽETAK.md, API_CONFIG_PROMENE.md i TODO_PLAN.md.*
