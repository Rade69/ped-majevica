# ✅ Organizacija Projekta - Završeno

## 📊 Rezime Organizacije

Datum: **2026-03-15**

---

## 🎯 Šta Je Urađeno

### 1. ✅ Kreirani Novi Folderi

```
/
├── docs/                    # Centralizovana dokumentacija
│   └── deployment/          # Deployment dokumentacija
├── backend/
│   └── scripts/             # Sve skripte na jednom mestu
├── frontend/
│   └── assets/
│       └── pdf/             # PDF dokumenti
└── deployment/
    ├── netlify/             # Netlify konfiguracija
    └── render/              # Render konfiguracija
```

### 2. ✅ Premješteni Fajlovi

| Iz | U | Fajlovi |
|---|---|---------|
| `/` | `/frontend/` | `package.json`, `tailwind.config.js` |
| `/` | `/deployment/netlify/` | `netlify.toml` |
| `/` | `/deployment/render/` | `render.yaml` |
| `/` | `/docs/` | `ADMIN_USERS_GUIDE.md`, `IMAGE_GUIDE.md` |
| `/` | `/docs/deployment/` | `CUSTOM_DOMAIN_SETUP.md`, `DEPLOYMENT.md`, `DEPLOYMENT_GUIDE.md` |
| `/backend/` | `/backend/scripts/` | Sve `.sh` i `.py` skripte |
| `/backend/` | `/backend/data/` | `plan_akica_2026.JSON` |
| `/frontend/assets/data/` | `/frontend/assets/pdf/` | `pristupnica-2025-12-29.pdf` |

### 3. ✅ Obrisani Nepotrebni Fajlovi

- ❌ `frontend/assets/package.kson` (typo fajl)
- ❌ `frontend/assets/images/gallery/127.0.0.1_5500_.png` (localhost screenshot)
- ❌ `frontend/assets/images/icons/logo-2.png` (duplikat)
- ❌ `frontend/assets/images/trails/mediainfo-gui-*.rpm` (pogrešan tip fajla)

### 4. ✅ Renamirani Fajlovi

| Stari Naziv | Novi Naziv |
|------------|------------|
| `hero/ChatGPT Image Jan 18, 2026, 02_50_45 PM.png` | `hero/hero-mountains.png` |
| `gallery/dan planina.jpg` | `gallery/dan-planina.jpg` |
| `data/Приступница 2025-12-29.pdf` | `pdf/pristupnica-2025-12-29.pdf` |

### 5. ✅ Ažuriran .gitignore

Dodato:
- `__pycache__/`
- `.pytest_cache/`
- `instance/*.db`

---

## 📁 Konačna Struktura

```
ped-majevica-main/
│
├── 📄 README.md                        # Glavna dokumentacija
├── 📄 PROJECT_STRUCTURE.md             # Detaljna struktura
├── 📄 .gitignore                       # Git ignore
├── 📄 .hintrc                          # Web hint config
│
├── 📂 docs/                            # ✅ NOVO - Dokumentacija
│   ├── ADMIN_USERS_GUIDE.md
│   ├── IMAGE_GUIDE.md
│   └── deployment/                     # ✅ NOVO
│       ├── CUSTOM_DOMAIN_SETUP.md
│       ├── DEPLOYMENT.md
│       └── DEPLOYMENT_GUIDE.md
│
├── 📂 deployment/                      # Deployment fajlovi
│   ├── vps/                            # VPS skripte
│   ├── netlify/                        # ✅ NOVO
│   │   └── netlify.toml
│   └── render/                         # ✅ NOVO
│       └── render.yaml
│
├── 📂 backend/
│   ├── 📄 run.py                       # Development entry point
│   ├── 📄 wsgi.py                      # Production entry point
│   ├── 📄 requirements.txt
│   ├── 📄 requirements-dev.txt
│   ├── 📄 pytest.ini
│   ├── 📄 .env
│   ├── 📄 .env.example
│   ├── 📄 .python-version
│   ├── 📄 runtime.txt
│   │
│   ├── 📂 app/                         # Flask aplikacija
│   ├── 📂 data/                        # JSON podaci
│   │   └── plan_akica_2026.JSON       # ✅ PREMJESTENO
│   ├── 📂 scripts/                     # ✅ NOVO - Skripte
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
│   ├── 📂 tests/                       # Test suite
│   ├── 📂 migrations/                  # Alembic migracije
│   └── 📂 instance/                    # Local podaci (gitignore)
│
└── 📂 frontend/
    ├── 📄 package.json                 # ✅ PREMJESTENO
    ├── 📄 tailwind.config.js           # ✅ PREMJESTENO
    │
    ├── 📂 pages/                       # HTML stranice
    ├── 📂 js/                          # JavaScript moduli
    │
    └── 📂 assets/
        ├── 📂 css/                     # Stilovi
        ├── 📂 js/                      # Config JS
        ├── 📂 images/                  # Slike
        ├── 📂 data/                    # JSON podaci
        └── 📂 pdf/                     # ✅ NOVO - PDF dokumenti
            └── pristupnica-2025-12-29.pdf
```

---

## 📈 Benefiti Organizacije

### ✅ Preglednost
- Svi fajlovi su na logičnim mjestima
- Lako snalaženje u projektu
- Jasna hijerarhija

### ✅ Održavanje
- Lakše dodavanje novih funkcionalnosti
- Jednostavnije brisanje nepotrebnih fajlova
- Bolja dokumentacija

### ✅ Deployment
- Razdvojene konfiguracije po platformama
- Jasne instrukcije za deployment
- Skripte na jednom mjestu

### ✅ Testiranje
- Test suite organizovan u `/backend/tests/`
- Clear test documentation
- Easy to run tests

---

## 🚀 Kako Koristiti

### Pokretanje Backend-a

```bash
cd backend
python run.py  # Development
# ili
gunicorn wsgi:app  # Production
```

### Pokretanje Frontend-a

```bash
cd frontend
npm install
npm run dev  # Development watch
npm run build  # Production build
```

### Pokretanje Testova

```bash
cd backend
./scripts/run_tests.sh  # Svi testovi
# ili
./scripts/run_tests.sh frontend  # Samo frontend testovi
./scripts/run_tests.sh coverage  # Sa coverage report-om
```

### Deployment

```bash
cd deployment/vps
./deploy.sh  # Deploy na VPS
```

---

## 📝 Sledeci Koraci

### Preporučeno:
1. ✅ Pregledati sve skripte u `/backend/scripts/` i testirati
2. ✅ Provjeriti da li svi linkovi u dokumentaciji rade
3. ✅ Ažurirati CI/CD pipeline sa novom strukturom
4. ✅ Testirati deployment sa novom strukturom

### Opciono:
1. Konsolidovati CSS fajlove u `/frontend/assets/css/`
2. Konvertovati `.js` data fajlove u `.json` ako su JSON
3. Dodati više testova za kritične funkcionalnosti

---

## 📧 Kontakt

Za pitanja o organizaciji projekta:
- Email: radovan1969@gmail.com

---

**Organizacija završena:** 2026-03-15  
**Verzija:** 2.0.0  
**Status:** ✅ SVE KOMPLETNO
