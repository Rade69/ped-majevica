# 🚀 Deployment Guide - PED Majevica

Ovaj dokument objašnjava kako deploy-ovati PED Majevica web aplikaciju na **Render.com**.

---

## 📋 Preduslovi

- ✅ GitHub nalog
- ✅ Projekat push-ovan na GitHub
- ✅ Render.com nalog (besplatan)

---

## 🎯 Render.com Deployment (PREPORUČENO)

### **Zašto Render?**
- ✅ **Besplatan tier** za male projekte
- ✅ Automatski PostgreSQL
- ✅ Automatski HTTPS/SSL
- ✅ Auto-deploy sa GitHub push-om
- ✅ Jednostavan setup

---

## 📝 Korak-po-Korak Uputstvo

### **Korak 1: Priprema**

Proveri da su svi fajlovi push-ovani na GitHub:

```bash
git status
git add .
git commit -m "Prepare for deployment"
git push origin master
```

### **Korak 2: Kreiraj Render nalog**

1. Idi na https://render.com
2. Klikni **"Get Started for Free"**
3. Uloguj se sa GitHub nalogom
4. Odobri pristup repozitorijumu

### **Korak 3: Deploy sa Blueprint (render.yaml)**

1. **Na Render Dashboard-u:**
   - Klikni **"New +"** → **"Blueprint"**
   
2. **Poveži GitHub Repo:**
   - Odaberi **"ped-majevica"** repozitorijum
   - Render će automatski detektovati `render.yaml`

3. **Kreiraj Blueprint:**
   - Klikni **"Apply"**
   - Render će kreirati:
     - ✅ Web Service (Flask backend)
     - ✅ PostgreSQL Database

4. **Generiši SECRET_KEY:**
   - Render će automatski generisati `SECRET_KEY`
   - DATABASE_URL se automatski povezuje

5. **Sačekaj deployment:**
   - Trajanje: ~5-10 minuta
   - Pratite logove u realtime

### **Korak 4: Inicijalizuj bazu podataka**

Nakon što se deployment završi:

1. **Otvori Shell na Render-u:**
   - Idi na web service
   - Klikni **"Shell"** tab
   - Pokreni:

```bash
cd backend
flask db upgrade
python migrate_json_to_db.py  # Importuj početne podatke
```

2. **Kreiraj admin korisnika (automatski):**
   - Admin se automatski kreira pri prvom startovanju
   - **Username:** `admin`
   - **Password:** `admin123` (promeni odmah!)

### **Korak 5: Verifikacija**

1. **Otvori app URL:**
   - `https://ped-majevica-backend.onrender.com`

2. **Testiraj:**
   - ✅ Glavna stranica se učitava
   - ✅ Login radi
   - ✅ Admin panel pristupačan

---

## 🔧 Environment Variables (Render)

Render automatski postavlja:

| Varijabla | Vrednost | Izvor |
|-----------|----------|-------|
| `DATABASE_URL` | PostgreSQL URL | Auto (iz database servisa) |
| `SECRET_KEY` | Random string | Auto-generisan |
| `FLASK_ENV` | `production` | render.yaml |
| `PYTHON_VERSION` | `3.11.0` | render.yaml |

---

## 🔄 Automatski Re-Deploy

Svaki `git push` na `master` branch automatski pokreće re-deploy:

```bash
git add .
git commit -m "Update features"
git push origin master
# Render automatski deploy-uje novu verziju
```

---

## 🗄️ Database Backup

### **Ručni backup:**

```bash
# Na Render Shell-u
pg_dump $DATABASE_URL > backup_$(date +%F).sql
```

### **Automatski backup:**
- Render **besplatni tier**: nema automatske backups
- Render **platni tier** ($7/mes): dnevni automatski backups

---

## 🐛 Troubleshooting

### Problem: "Application failed to start"

**Rešenje:**
1. Proveri logove na Render dashboard-u
2. Proveri da su sve dependencies u `requirements.txt`
3. Proveri `wsgi.py` entry point

### Problem: "Database connection failed"

**Rešenje:**
1. Proveri da je PostgreSQL servis aktivan
2. Proveri da `DATABASE_URL` environment varijabla postoji
3. Pokreni `flask db upgrade` u shell-u

### Problem: "Static files not loading"

**Rešenje:**
1. Proveri da je `npm run build` izvršen u build step-u
2. Proveri putanje u HTML fajlovima (`/assets/...`)

---

## 💰 Troškovi

### **Besplatni Tier:**
- ✅ Web Service: **Besplatno** (sa limitima)
  - Spins down nakon 15 min neaktivnosti
  - Restart traje ~30 sekundi
- ✅ PostgreSQL: **Besplatno 90 dana**, zatim $7/mesec
  - 1GB storage
  - 97 connections

### **Paid Tier:**
- Web Service: **$7/mesec**
  - Bez spin down-a
  - Brži
- PostgreSQL: **$7/mesec**
  - Dnevni backups

**Ukupno za production:** ~$14/mesec

---

## 🔒 Security Checklist

Pre produkcije:

- [ ] Promeni admin password
- [ ] Postavi jak `SECRET_KEY` (32+ karaktera)
- [ ] Omogući HTTPS (automatski na Render)
- [ ] Proveri CORS postavke
- [ ] Omogući rate limiting
- [ ] Postavi monitoring

---

## 📚 Dodatni Resursi

- [Render.com Docs](https://render.com/docs)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [PostgreSQL na Render](https://render.com/docs/databases)

---

## 🆘 Podrška

Ako imaš problema sa deployment-om:

1. Proveri [Render Status Page](https://status.render.com)
2. Pretraži [Render Community](https://community.render.com)
3. Kontaktiraj Render Support (odgovaraju za ~24h)

---

**Made with ❤️ for PED Majevica 1988** 🏔️
