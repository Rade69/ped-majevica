# 🚀 PED Majevica - Deployment Guide

## 📋 Sadržaj
1. [Pregled Arhitekture](#pregled-arhitekture)
2. [Backend Deployment (Render.com)](#backend-deployment-rendercom)
3. [Frontend Deployment (Netlify)](#frontend-deployment-netlify)
4. [Konfigurisanje API Komunikacije](#konfigurisanje-api-komunikacije)
5. [Rešavanje Problema](#rešavanje-problema)
6. [Maintenance i Monitoring](#maintenance-i-monitoring)

---

## 🏗️ Pregled Arhitekture

### Hybrid Deployment Strategy

- **Backend**: Render.com (Flask + PostgreSQL)
- **Frontend**: Netlify (Statički HTML/CSS/JS)
- **Domain**: pedmajevica.org (Namecheap)

### Troškovi (godišnje):
- Render.com: Free tier ($0)
- Netlify: Free tier ($0)
- Domain: ~$12/godišnje
- PostgreSQL: Free tier ($0)
- **Ukupno**: ~$12/godišnje

---

## 🗄️ Backend Deployment (Render.com)

### Korak 1: Kreiranje PostgreSQL Baze

1. Idi na [Render Dashboard](https://dashboard.render.com/)
2. Klikni **"New +"** → **"PostgreSQL"**
3. Podešavanja:
   - **Name**: `ped-majevica-db`
   - **Database**: `pedmajevica` (bez underscora!)
   - **Region**: Frankfurt (EU Central)
   - **Plan**: Free
4. Klikni **"Create Database"**
5. Kopiraj **Database URL** (External Database URL)

### Korak 2: Priprema Backend Koda

#### 2.1. Kreiranje Python Version Fajlova

```bash
# Kreiraj .python-version za Render
echo "3.11.8" > backend/.python-version

# Kreiraj runtime.txt za backup
echo "python-3.11.8" > backend/runtime.txt

# Commit promene
git add backend/.python-version backend/runtime.txt
git commit -m "Add Python version specification for Render"
git push origin main
```

#### 2.2. Kreiranje Startup Script-a

Kreiraj `backend/startup.sh`:

```bash
#!/bin/bash

# Startup script for Render deployment
# Runs migrations before starting the server

echo "🚀 Starting PED Majevica Backend..."

# Run database migrations
echo "📦 Running database migrations..."
flask db upgrade

# Optional: Run JSON data migration (only if needed)
if [ -f "migrate_json_to_db.py" ]; then
    echo "📥 Migrating JSON data to database..."
    python migrate_json_to_db.py
fi

# Start Gunicorn server
echo "🌐 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app
```

```bash
# Učini executable i commituj
chmod +x backend/startup.sh
git add backend/startup.sh
git commit -m "Add startup script with automatic database migrations"
git push origin main
```

#### 2.3. CORS Konfiguracija

Ažuriraj `backend/app/__init__.py`:

```python
# CORS - Allow Netlify frontend to access API
cors.init_app(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://ped-majevica.netlify.app",  # Tvoj Netlify domen
            "https://pedmajevica.org",
            "https://www.pedmajevica.org"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

```bash
git add backend/app/__init__.py
git commit -m "Fix CORS to allow Netlify domain explicitly"
git push origin main
```

### Korak 3: Kreiranje Web Service na Render

1. Idi na [Render Dashboard](https://dashboard.render.com/)
2. Klikni **"New +"** → **"Web Service"**
3. Povezivanje sa GitHub repozitorijumom:
   - Izaberi **"Connect a repository"**
   - Autorizuj Render pristup GitHub-u
   - Izaberi `ped-majevica` repozitorijum

4. **Podešavanja Web Service-a:**

   - **Name**: `ped-majevica`
   - **Region**: Frankfurt (EU Central)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     bash startup.sh
     ```
   - **Plan**: Free

5. **Environment Variables** (klikni "Add Environment Variable"):

   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | `EZnqSt2XbgdayiDQNwBsWdrj0vidHzQ2HOGDjssaF9A` |
   | `DATABASE_URL` | *(Paste from PostgreSQL)* |
   | `LOG_LEVEL` | `INFO` |

6. Klikni **"Create Web Service"**

### Korak 4: Verifikacija Backend-a

Nakon deployment-a (može trajati 2-3 minuta):

```bash
# Testiraj API endpoint u browseru:
https://ped-majevica.onrender.com/api/posts
```

Trebao bi da vidiš JSON sa blog člancima.

---

## 🌐 Frontend Deployment (Netlify)

### Korak 1: Priprema Frontend Koda

#### 1.1. CSS Popravke

Ažuriraj `frontend/assets/css/input.css` da koristi validne Tailwind boje:

```css
/* Filter Buttons - Fixed blue-light references */
.filter-btn {
  @apply px-6 py-2.5 rounded-full font-medium transition-all duration-300;
  @apply border-2 border-gray-300 dark:border-gray-600;
  @apply hover:border-primary-blue dark:hover:border-blue-400;  /* Changed from blue-light */
}

.filter-btn.active {
  @apply bg-primary-blue text-white border-primary-blue;
  @apply dark:bg-blue-500 dark:border-blue-500;  /* Changed from blue-light */
}
```

```bash
# Rebuild CSS
npm run build

git add frontend/assets/css/
git commit -m "Fix Tailwind CSS undefined color classes"
git push origin main
```

#### 1.2. Netlify Konfiguracija

Ažuriraj `netlify.toml`:

```toml
[build]
  # Build command
  command = "npm run build"

  # Publish directory (frontend files)
  publish = "frontend"

  # Ignore backend files (Netlify shouldn't process Python)
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- backend/"

  # Build environment
  [build.environment]
    NODE_VERSION = "18"
    # Disable Python auto-detection
    PYTHON_VERSION = ""

# ============================================
# REDIRECTS & REWRITES
# ============================================

# Root redirect to index.html
[[redirects]]
  from = "/"
  to = "/pages/index.html"
  status = 200

# Specific page redirects
[[redirects]]
  from = "/uclanite-se"
  to = "/pages/uclanite-se.html"
  status = 200

[[redirects]]
  from = "/o-nama"
  to = "/pages/o-nama.html"
  status = 200

[[redirects]]
  from = "/staze"
  to = "/pages/staze.html"
  status = 200

[[redirects]]
  from = "/blog"
  to = "/pages/blog.html"
  status = 200

[[redirects]]
  from = "/kontakt"
  to = "/pages/kontakt.html"
  status = 200

[[redirects]]
  from = "/admin"
  to = "/pages/admin.html"
  status = 200

# All other routes redirect to index.html (for SPA routing)
[[redirects]]
  from = "/*"
  to = "/pages/index.html"
  status = 200
```

```bash
# Obriši runtime.txt iz root-a (nije potreban za Netlify)
rm runtime.txt

git add -A
git commit -m "Remove root runtime.txt and configure Netlify to ignore Python"
git push origin main
```

### Korak 2: Povezivanje sa Netlify

1. Idi na [Netlify Dashboard](https://app.netlify.com/)
2. Klikni **"Add new site"** → **"Import an existing project"**
3. Izaberi **"GitHub"**
4. Autorizuj Netlify pristup GitHub-u
5. Izaberi `ped-majevica` repozitorijum
6. **Build Settings** (automatski detektovani iz `netlify.toml`):
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend`
7. Klikni **"Deploy site"**

### Korak 3: Konfigurisanje Site Settings

Nakon deployment-a:

1. Idi na **Site settings**
2. **Site details** → **Change site name** → `ped-majevica`
3. Sada će tvoj sajt biti dostupan na: `https://ped-majevica.netlify.app`

---

## 🔗 Konfigurisanje API Komunikacije

### Korak 1: Kreiranje API Config Fajla

Kreiraj `frontend/assets/js/config.js`:

```javascript
/**
 * ============================================
 * API CONFIGURATION
 * ============================================
 * Centralized API endpoint configuration
 * Supports both development and production
 */

const API_CONFIG = {
  // Production backend URL (Render.com)
  PRODUCTION_API: 'https://ped-majevica.onrender.com',

  // Development backend URL (local Flask server)
  DEVELOPMENT_API: 'http://127.0.0.1:5000',

  // Auto-detect environment
  get BASE_URL() {
    // If running on localhost, use development API
    if (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1') {
      return this.DEVELOPMENT_API;
    }

    // Otherwise use production API
    return this.PRODUCTION_API;
  },

  // API endpoints
  ENDPOINTS: {
    POSTS: '/api/posts',
    TRAILS: '/api/trails',
    EVENTS: '/api/events',
    LOGIN: '/api/login',
    LOGOUT: '/api/logout',
  },

  // Helper method to get full URL
  getUrl(endpoint) {
    return this.BASE_URL + endpoint;
  }
};

// Export for use in other scripts
window.API_CONFIG = API_CONFIG;
```

```bash
git add frontend/assets/js/config.js
git commit -m "Create API configuration for frontend-backend communication"
git push origin main
```

### Korak 2: Ažuriranje blog.js

Ažuriraj `frontend/js/blog.js` da koristi API_CONFIG:

```javascript
// Inicijalizacija
async function initBlog() {
    console.log('📚 Blog: Inicijalizacija...');
    try {
        // Use API_CONFIG for correct backend URL
        const apiUrl = window.API_CONFIG ? window.API_CONFIG.getUrl(window.API_CONFIG.ENDPOINTS.POSTS) : '/api/posts';
        console.log('📚 Blog: Fetching from:', apiUrl);
        const response = await fetch(apiUrl);
        console.log('📚 Blog: Response status:', response.status);
        const data = await response.json();
        // ... rest of code
    } catch (error) {
        console.error('Greška pri učitavanju članaka:', error);
        showError();
    }
}
```

```bash
git add frontend/js/blog.js
git commit -m "Fix blog.js to use API_CONFIG for backend URL"
git push origin main
```

### Korak 3: Dodavanje config.js u index.html

Ažuriraj `frontend/pages/index.html` da učita config.js **PRE** blog.js:

```html
<!-- Transliterator Script -->
<script src="/js/transliterator.js"></script>

<!-- API Configuration - Must load first -->
<script src="/assets/js/config.js"></script>

<script src="/js/trial.js"></script>
<script src="/js/membership.js"></script>
<script src="/js/blog.js?v=5"></script>
<script src="/js/parallax.js"></script>
<script src="/js/app.js"></script>
```

```bash
git add frontend/pages/index.html
git commit -m "Add config.js script before blog.js to fix API configuration"
git push origin main
```

---

## 🐛 Rešavanje Problema

### Problem 1: Python 3.13 Incompatibility Error

**Error:**
```
ImportError: undefined symbol: _PyInterpreterState_Get
```

**Uzrok:** Render koristi Python 3.13 koji je inkompatibilan sa psycopg2-binary 2.9.9

**Rešenje:**
```bash
# Kreiraj .python-version fajl
echo "3.11.8" > backend/.python-version

git add backend/.python-version
git commit -m "Add .python-version for Render Python version control"
git push origin main

# Na Render Dashboard-u:
# Manual Deploy → Clear build cache & deploy
```

### Problem 2: Netlify Pokušava Instalirati Python

**Error:**
```
python-build: definition not found: python-3.11.8
```

**Uzrok:** Netlify detektuje `runtime.txt` u root-u

**Rešenje:**
```bash
# Obriši runtime.txt iz root-a
rm runtime.txt

# Ažuriraj netlify.toml da ignoriše Python
# (dodaj PYTHON_VERSION = "" u [build.environment])

git add -A
git commit -m "Remove root runtime.txt and configure Netlify to ignore Python"
git push origin main
```

### Problem 3: CORS Policy Error

**Error:**
```
Access to fetch at 'https://ped-majevica.onrender.com/api/posts'
from origin 'https://ped-majevica.netlify.app' has been blocked by CORS policy
```

**Uzrok:** Backend ne dozvoljava Netlify domen

**Rešenje:**

Ažuriraj `backend/app/__init__.py`:

```python
cors.init_app(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://ped-majevica.netlify.app",  # Eksplicitno dodaj Netlify domen
            "https://pedmajevica.org",
            "https://www.pedmajevica.org"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

```bash
git add backend/app/__init__.py
git commit -m "Fix CORS to allow Netlify domain explicitly"
git push origin main

# Na Render Dashboard-u:
# Manual Deploy → Deploy latest commit
```

### Problem 4: config.js Nije Učitan

**Simptom:** Blog ne prikazuje članke, konzola pokazuje `Fetching from: /api/posts`

**Uzrok:** `config.js` se učitava posle `blog.js`

**Rešenje:**

Dodaj `config.js` **PRE** `blog.js` u `index.html`:

```html
<!-- API Configuration - Must load first -->
<script src="/assets/js/config.js"></script>

<script src="/js/blog.js?v=5"></script>  <!-- Povećaj verziju za cache bust -->
```

```bash
git add frontend/pages/index.html
git commit -m "Add config.js script before blog.js to fix API configuration"
git push origin main
```

---

## 📊 Maintenance i Monitoring

### Render.com Logovi

```bash
# Na Render Dashboard-u:
# 1. Otvori Web Service
# 2. Klikni "Logs" tab
# 3. Filtriraj po tipu:
#    - Build logs: vidi build proces
#    - Deploy logs: vidi deployment status
#    - Service logs: vidi runtime errors
```

### Netlify Logovi

```bash
# Na Netlify Dashboard-u:
# 1. Otvori sajt
# 2. Klikni "Deploys" tab
# 3. Klikni na deployment da vidiš detalje
# 4. "Deploy log" prikazuje build process
```

### Database Migracije

Ako dodaješ nove modele ili menjaš postojeće:

```bash
# Lokalno kreiraj migraciju
cd backend
flask db migrate -m "Description of changes"
flask db upgrade

# Commituj i pushuj
git add backend/migrations/
git commit -m "Add database migration: Description"
git push origin main

# Render će automatski pokrenuti migracije kroz startup.sh
```

### Performance Napomene

**Render Free Tier:**
- Backend će se "uspavati" nakon 15 minuta neaktivnosti
- Prvi API poziv će trajati 30-50 sekundi (cold start)
- Ovo je normalno za free tier

**Kako smanjiti cold start:**
- Koristi cron job (external) da "pinga" backend svakih 10 minuta
- Ili upgrade na plaćeni plan ($7/mesec) za 24/7 uptime

### Browser Cache

Ako frontend izmene nisu vidljive:

```bash
# Hard refresh:
# Windows/Linux: Ctrl + Shift + R
# Mac: Cmd + Shift + R

# Ili dodaj cache busting query string:
<script src="/js/blog.js?v=6"></script>  <!-- Povećaj broj -->
```

---

## ✅ Deployment Checklist

Pre svakog deployment-a:

### Backend Changes:
- [ ] Kreiraj/testiraj lokalno
- [ ] Ažuriraj migracije ako je potrebno
- [ ] Commituj i pushuj na GitHub
- [ ] Render auto-deploy ili manual deploy
- [ ] Proveri logs za errore
- [ ] Testiraj API endpoint direktno

### Frontend Changes:
- [ ] Rebuild CSS ako je potrebno: `npm run build`
- [ ] Testiraj lokalno (Live Server)
- [ ] Commituj i pushuj na GitHub
- [ ] Netlify auto-deploy
- [ ] Hard refresh sajt
- [ ] Proveri konzolu za errore

### CORS Promene:
- [ ] Ažuriraj `backend/app/__init__.py`
- [ ] Deployuj backend
- [ ] Hard refresh frontend
- [ ] Testiraj API pozive u konzoli

---

## 🎯 Finalni Status

✅ **Backend**: https://ped-majevica.onrender.com
✅ **Frontend**: https://ped-majevica.netlify.app
✅ **Database**: PostgreSQL na Render.com
✅ **API Komunikacija**: CORS konfigurisan
✅ **Blog Članci**: 26 članaka učitano iz baze

---

## 📚 Korisni Resursi

- [Render Documentation](https://render.com/docs)
- [Netlify Documentation](https://docs.netlify.com/)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

## 🆘 Dodatna Pomoć

Ako naiđeš na probleme:

1. **Proveri Logove**:
   - Render: Dashboard → Logs
   - Netlify: Dashboard → Deploys → Deploy log
   - Browser: F12 → Console tab

2. **Testiraj Direktno**:
   - Backend API: `https://ped-majevica.onrender.com/api/posts`
   - Frontend: Hard refresh (Ctrl+Shift+R)

3. **GitHub Issues**:
   - Otvori issue u repozitorijumu
   - Priloži logs i screenshots

---

**Datum kreiranja**: 12. Januar 2026
**Autor**: Claude Sonnet 4.5
**Projekat**: PED Majevica 1988
