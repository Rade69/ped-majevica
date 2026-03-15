# 📋 TODO Plan - PED Majevica 1988 Poboljšanja

## 🔴 VISOK PRIORITET (Urgentno - 1-2 nedelje)

### 1. Sigurnost Backend-a
- [x] 1.1 Dodati `email` polje u User model ✅
- [x] 1.2 Dodati `last_login` timestamp za praćenje prijava ✅
- [x] 1.3 Implementirati role-based access control (RBAC) ✅
  - [x] Admin - pun pristup ✅
  - [x] Editor - može uređivati sadržaj ✅
  - [x] User - samo čitanje ✅
- [x] 1.4 Dodati email verifikaciju pri registraciji ✅ (`backend/app/services/email_verification.py`)
- [x] 1.5 Implementirati password reset funkcionalnost ✅

### 2. API Sigurnost
- [x] 2.1 Dodati rate limiting na sve write operacije (POST, PUT, DELETE) ✅
- [x] 2.2 Implementirati autentifikaciju za lajkove ✅
- [x] 2.3 Dodati CSRF zaštitu ✅ (`backend/app/utils/csrf.py`)
- [x] 2.4 Validacija input-a na server strani ✅ (Marshmallow schema)

### 1.4-1.5 Password Reset
- [x] Password reset request endpoint ✅
- [x] Password reset confirm endpoint ✅  
- [x] Change password (authenticated) endpoint ✅

### 3. Refaktor Frontend koda
- [x] 3.1 Izdvojiti sav inline JavaScript iz `index.html` u module ✅
- [x] 3.2 Kreirati shared moduli za: ✅
  - [x] Modal system (`frontend/js/utils/modal.js`) ✅
  - [x] Gallery system (`frontend/js/utils/gallery.js`) ✅
  - [x] Form validation (`frontend/js/utils/validation.js`) ✅
- [ ] 3.3 Srediti konzistentnost - koristiti postojeće JS fajlove (`api.js`, `app.js`, itd.)

---

## ✅ ZAVRŠENO (Mart 2026)

1. **User Model** (`backend/app/models/user.py`)
   - Dodato: email, last_login, is_active, first_name, last_name
   - Dodato: UserRole enum (ADMIN, EDITOR, USER, GUEST)
   - Dodato: helper metode (is_admin(), is_editor(), update_last_login())

2. **Migracija** (`backend/migrations/versions/enhanced_user_model.py`)
   - Kreirana Alembic migracija za nove kolone

3. **Auth Routes** (`backend/app/routes/auth.py`)
   - Ažuriran login da čuva role u session
   - Dodata provera is_active statusa
   - Dodato ažuriranje last_login timestampa

4. **RBAC Decorators** (`backend/app/utils/decorators.py`)
   - `role_required(*roles)` - generalni decorator
   - `admin_required` - samo za admine
   - `editor_required` - za admine i editore
   - `json_required` - provera JSON content-type

---

## 🟡 SREDNJI PRIORITET (2-4 nedelje)

### 4. Testiranje
- [x] 4.1 Povećati coverage testova (cilj: 80%+) ✅
- [x] 4.2 Dodati integracione testove za API endpoint-e ✅ (`backend/tests/test_api_integration.py`)
- [x] 4.3 Dodati E2E testove sa Cypress/Playwright ✅ (`frontend/tests/e2e.spec.js`)
- [x] 4.4 Setup automated testing u CI/CD ✅

### 5. CI/CD Pipeline
- [x] 5.1 Kreirati GitHub Actions workflow ✅ (`.github/workflows/ci.yml`)
- [x] 5.2 Automatski testovi na svaki push ✅
- [ ] 5.3 Automatski deployment na staging
- [x] 5.4 Dodati code quality checks (linting, formatting) ✅

### 6. Performanse i Optimizacija
- [x] 6.1 Implementirati Redis caching za API responses ✅ (`backend/app/utils/cache.py`)
- [x] 6.2 Dodati paginaciju na sve liste (posts, events, trails) ✅
- [x] 6.3 Optimizovati slike: ✅
  - [x] Automatska konverzija u WebP ✅
  - [x] Responsive image sizes (srcset) ✅ (`frontend/js/utils/imageOptimizer.js`)
  - [x] Lazy loading za sve slike ✅
- [x] 6.4 CDN za statičke fajlove ✅ (`frontend/js/utils/cdn.js`)

### 7. API Poboljšanja
- [ ] 7.1 Standardizovati endpoint-e (konvencija: sa `/` na kraju)
- [x] 7.2 Dodati OpenAPI/Swagger dokumentaciju ✅ (`backend/app/utils/swagger.py`)
- [ ] 7.3 Implementirati proper error handling
- [ ] 7.4 Dodati versioning API-ja (`/api/v1/`)

---

## 🟢 NIZAK PRIORITET (1-2 meseca)

### 8. Novi Feature-i
- [ ] 8.1 Newsletter sistem sa double opt-in
- [ ] 8.2 User profiles sa istorijom aktivnosti
- [ ] 8.3 GPX file hosting i download za staze
- [ ] 8.4 Komentari na blog postovima
- [ ] 8.5 Social sharing integracija

### 9. SEO i Marketing
- [x] 9.1 Meta tags za sve stranice ✅
- [x] 9.2 Sitemap.xml i robots.txt ✅ (`frontend/sitemap.xml`, `frontend/robots.txt`)
- [x] 9.3 Structured data (Schema.org) ✅ (`frontend/js/seo.js`)
- [x] 9.4 Open Graph i Twitter cards ✅

### 10. Dokumentacija
- [x] 10.1 API dokumentacija (Swagger) ✅
- [x] 10.2 Contributing guide ✅ (`CONTRIBUTING.md`)
- [x] 10.3 Setup instructions za nove developere ✅ (`SETUP.md`)

---

## 📊 Redosled realizacije

```
NEDELJA 1-2:      NEDELJA 3-4:       NEDELJA 5-8:        NEDELJA 9-12:
┌──────────────┐  ┌──────────────┐   ┌──────────────┐    ┌──────────────┐
│ 1. Sigurnost │  │ 4. Testiranje│   │ 6. Performanse│    │ 8. Novi      │
│ 2. API Sigur.│  │ 5. CI/CD     │   │ 7. API pobolj.│    │    Feature-i │
│ 3. Refactoring│ │              │   │              │    │ 9. SEO       │
└──────────────┘  └──────────────┘   └──────────────┘    └──────────────┘
```

---

## 🎯 Kratkoročni ciljevi (Sledeća 2 meseca)

### Mesec 1 - Sigurnost i Stabilnost
1. User model proširen sa email, last_login
2. RBAC implementacija
3. Rate limiting na svim endpointima
4. Inline JS izvučen iz HTML-a

### Mesec 2 - Kvalitet i Performanse
1. Povećan test coverage
2. CI/CD pipeline
3. Paginacija na listama
4. Image optimization

---

## 💡 Napomene

- **MVP pristup**: Fokusirati se na sigurnost pre novih feature-a
- **Iterativni razvoj**: Male, česte release-e umesto velikih
- **Dokumentacija**: Ažurirati posle svake veće promene
- **Monitoring**: Dodati logging i error tracking (Sentry)

---

*Generisano: Mart 2026*
