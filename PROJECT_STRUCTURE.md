# 📁 PED Majevica 1988 - Struktura Projekta

Organizovana struktura fajlova za PED Majevica web aplikaciju.

---

## 🏗️ Trenutna Struktura

```
ped-majevica-main/
│
├── 📄 README.md                      # Glavna dokumentacija
├── 📄 .gitignore                     # Git ignore pravila
├── 📄 .hintrc                        # Web hint konfiguracija
│
├── 📂 docs/                          # Dokumentacija
│   ├── ADMIN_USERS_GUIDE.md          # Uputstvo za administratore
│   ├── IMAGE_GUIDE.md                # Vodič za slike
│   └── deployment/                   # Deployment dokumentacija
│       ├── CUSTOM_DOMAIN_SETUP.md
│       ├── DEPLOYMENT.md
│       └── DEPLOYMENT_GUIDE.md
│
├── 📂 deployment/                    # Deployment fajlovi
│   ├── vps/                          # VPS deployment
│   │   ├── backup.sh
│   │   ├── deploy.sh
│   │   ├── install.sh
│   │   ├── nginx-pedmajevica.conf
│   │   ├── pedmajevica.service
│   │   ├── setup-app.sh
│   │   ├── setup-nginx.sh
│   │   ├── setup-ssl.sh
│   │   └── VPS-DEPLOYMENT.md
│   ├── netlify/                      # Netlify konfiguracija
│   │   └── netlify.toml
│   └── render/                       # Render konfiguracija
│       └── render.yaml
│
├── 📂 backend/                       # Python Flask Backend
│   ├── 📄 README.md                  # Backend dokumentacija
│   ├── 📄 requirements.txt           # Python dependency-ji
│   ├── 📄 requirements-dev.txt       # Test dependency-ji
│   ├── 📄 pytest.ini                 # Pytest konfiguracija
│   ├── 📄 .env                       # Environment varijable (ne commit-uj)
│   ├── 📄 .env.example               # Environment template
│   ├── 📄 .python-version            # Python verzija
│   ├── 📄 run.py                     # Entry point za development
│   ├── 📄 wsgi.py                    # Entry point za production
│   ├── 📄 runtime.txt                # Runtime konfiguracija
│   │
│   ├── 📂 app/                       # Flask aplikacija
│   │   ├── __init__.py               # Application factory
│   │   ├── config.py                 # Konfiguracija
│   │   ├── extensions.py             # Flask ekstenzije
│   │   ├── models/                   # Database modeli
│   │   ├── routes/                   # HTTP rute
│   │   ├── schemas/                  # Marshmallow schemas
│   │   ├── services/                 # Business logika
│   │   └── utils/                    # Pomoćne funkcije
│   │
│   ├── 📂 data/                      # Podaci (JSON, seed)
│   │   ├── blog_posts.json
│   │   ├── trails.json
│   │   └── plan_akica_2026.JSON
│   │
│   ├── 📂 scripts/                   # Skripte i alati
│   │   ├── CLEANUP_OLD_FILES.sh
│   │   ├── create_admin.py
│   │   ├── create_admin_simple.py
│   │   ├── import_data.py
│   │   ├── migrate_events.py
│   │   ├── migrate_json.py
│   │   ├── migrate_json_to_db.py
│   │   ├── migrate_trails.py
│   │   ├── run_tests.sh
│   │   ├── seed_trails_events.py
│   │   └── startup.sh
│   │
│   ├── 📂 tests/                     # Testovi
│   │   ├── conftest.py               # Test fixture-ovi
│   │   ├── test_routes.py            # Frontend rute testovi
│   │   ├── test_api.py               # API testovi
│   │   ├── test_auth.py              # Auth testovi
│   │   ├── test_auth_extended.py     # Prošireni auth testovi
│   │   ├── test_admin.py             # Admin panel testovi
│   │   ├── test_production.py        # Production testovi
│   │   └── README.md                 # Test dokumentacija
│   │
│   ├── 📂 migrations/                # Alembic migracije
│   ├── 📂 instance/                  # Instance podaci (gitignore)
│   │   └── ped.db
│   └── 📂 .pytest_cache/             # Pytest cache (gitignore)
│
└── 📂 frontend/                      # Frontend (HTML/CSS/JS)
    ├── 📄 package.json               # Node.js dependency-ji
    ├── 📄 tailwind.config.js         # Tailwind CSS konfiguracija
    │
    ├── 📂 pages/                     # HTML stranice
    │   ├── index.html                # Početna stranica
    │   ├── galerija.html             # Galerija
    │   ├── login.html                # Login
    │   ├── admin.html                # Admin panel
    │   └── uclanite-se.html          # Učlanjenje
    │
    ├── 📂 js/                        # JavaScript moduli
    │   ├── app.js                    # Glavna aplikacija
    │   ├── auth.js                   # Autentifikacija
    │   ├── blog.js                   # Blog funkcionalnosti
    │   ├── events.js                 # Kalendar događaja
    │   ├── gallery.js                # Galerija
    │   ├── membership.js             # Članstvo
    │   ├── parallax.js               # Parallax efekti
    │   ├── posts.js                  # Postovi
    │   ├── theme.js                  # Dark mode
    │   ├── trails.js                 # Staze
    │   ├── transliterator.js         # Ćirilica/Latinica
    │   └── trial.js                  # Trial funkcije
    │
    └── 📂 assets/                    # Statički resursi
        ├── 📂 css/                   # Stilovi
        │   ├── input.css             # Tailwind input
        │   ├── output.css            # Tailwind output (generated)
        │   ├── output.min.css        # Minified output
        │   ├── admin.css             # Admin stilovi
        │   ├── animations.css        # Animacije
        │   └── style-optimized.css   # Optimizovani stilovi
        │
        ├── 📂 js/                    # Asset JS (config)
        │   └── config.js
        │
        ├── 📂 images/                # Slike
        │   ├── icons/                # Ikonice
        │   ├── logo/                 # Logo fajlovi
        │   ├── hero/                 # Hero sekcija
        │   ├── gallery/              # Galerija slike
        │   ├── trails/               # Slike staza
        │   ├── blog/                 # Blog slike
        │   └── optimized/            # Optimizovane slike
        │
        ├── 📂 data/                  # JSON podaci
        │   ├── blog.js
        │   ├── events.js
        │   └── plan_aktivnosti.json
        │
        └── 📂 pdf/                   # PDF dokumenti
            └── pristupnica-2025-12-29.pdf
```

---

## 📋 Opis Foldera

### Root (`/`)
- **README.md** - Glavna dokumentacija projekta
- **.gitignore** - Pravila za ignorisane fajlove u Git-u
- **.hintrc** - Konfiguracija za web linting

### Dokumentacija (`/docs`)
Sva dokumentacija je organizovana u ovom folderu:
- **ADMIN_USERS_GUIDE.md** - Uputstvo za administratore
- **IMAGE_GUIDE.md** - Vodič za korišćenje slika
- **deployment/** - Dokumentacija za deployment

### Deployment (`/deployment`)
Fajlovi potrebni za deployment na različite platforme:
- **vps/** - Skripte i konfiguracija za VPS
- **netlify/** - Netlify konfiguracija
- **render/** - Render konfiguracija

### Backend (`/backend`)
Python Flask backend aplikacija:
- **app/** - Glavna Flask aplikacija
- **data/** - JSON podaci i seed fajlovi
- **scripts/** - Pomoćne skripte i alati
- **tests/** - Test suite
- **migrations/** - Database migracije
- **instance/** - Lokalni podaci (baza)

### Frontend (`/frontend`)
Frontend web aplikacija:
- **pages/** - HTML stranice
- **js/** - JavaScript moduli
- **assets/** - Statički resursi (CSS, slike, podaci)

---

## 🔄 Nedavne Promene

### ✅ Organizovano (2026-03-15)

1. **Kreirani novi folderi:**
   - `/docs/` - Centralizovana dokumentacija
   - `/docs/deployment/` - Deployment dokumentacija
   - `/backend/scripts/` - Sve skripte na jednom mestu
   - `/frontend/assets/pdf/` - PDF dokumenti
   - `/deployment/netlify/` - Netlify konfiguracija
   - `/deployment/render/` - Render konfiguracija

2. **Premješteni fajlovi:**
   - `package.json` → `/frontend/package.json`
   - `tailwind.config.js` → `/frontend/tailwind.config.js`
   - `netlify.toml` → `/deployment/netlify/netlify.toml`
   - `render.yaml` → `/deployment/render/render.yaml`
   - Svi `.md` fajlovi → `/docs/`
   - Sve skripte (`.sh`, `.py`) → `/backend/scripts/`
   - `plan_akica_2026.JSON` → `/backend/data/`

3. **Obrisani nepotrebni fajlovi:**
   - `frontend/assets/package.kson` (greška u kucanju)
   - `frontend/assets/images/gallery/127.0.0.1_5500_.png` (localhost screenshot)
   - `frontend/assets/images/icons/logo-2.png` (duplikat)
   - `frontend/assets/images/trails/mediainfo-gui-*.rpm` (pogrešan tip fajla)

4. **Renamirani fajlovi:**
   - `hero/ChatGPT Image*.png` → `hero/hero-mountains.png`
   - `gallery/dan planina.jpg` → `gallery/dan-planina.jpg`
   - `data/Приступница*.pdf` → `pdf/pristupnica-2025-12-29.pdf`

5. **Ažuriran `.gitignore`:**
   - Dodat `__pycache__/`
   - Dodat `.pytest_cache/`
   - Dodat `instance/*.db`

---

## 📝 Napomene

### Fajlovi koji se NE commit-uju
Ovi fajlovi/folderi su u `.gitignore`:
- `backend/instance/*.db` - SQLite baza
- `backend/__pycache__/` - Python cache
- `backend/.pytest_cache/` - Pytest cache
- `backend/.env` - Environment varijable
- `frontend/node_modules/` - Node dependency-ji
- `frontend/assets/css/output*.css` - Generisani Tailwind

### Fajlovi koji se generišu
Ovi fajlovi se generišu tokom build-a:
- `frontend/assets/css/output.css` - Tailwind build
- `frontend/assets/css/output.min.css` - Minified Tailwind

---

## 🚀 Quick Commands

```bash
# Backend
cd backend
python run.py                    # Pokreni development server
./scripts/run_tests.sh           # Pokreni testove
pip install -r requirements.txt  # Instaliraj dependency-je

# Frontend
cd frontend
npm install                      # Instaliraj Node dependency-je
npm run dev                      # Tailwind watch mode
npm run build                    # Production build

# Deployment
cd deployment/vps
./deploy.sh                      # Deploy na VPS
```

---

**Poslednje ažuriranje:** 2026-03-15
**Verzija:** 2.0.0
