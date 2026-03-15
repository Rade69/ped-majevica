# ⚡ Hybrid Deployment - Quick Start

**5-Minute Setup Guide**

---

## 🎯 What You Need

- [ ] GitHub account with `ped-majevica` repo
- [ ] 15 minutes of time
- [ ] Internet connection

---

## 📍 Step-by-Step (Super Quick)

### 1️⃣ Deploy Backend (Render.com)

```bash
1. Go to: https://render.com
2. Sign up with GitHub
3. New + → PostgreSQL → Name: ped-majevica-db → Create
4. New + → Web Service → Connect ped-majevica repo
5. Settings:
   - Name: ped-majevica-backend
   - Root Directory: backend
   - Build: pip install -r requirements.txt
   - Start: gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app
6. Environment Variables:
   FLASK_ENV=production
   SECRET_KEY=<generate random string>
   DATABASE_URL=<copy from PostgreSQL dashboard>
7. Create Web Service → Wait 5-10 minutes
8. Copy URL: https://ped-majevica-backend.onrender.com
```

### 2️⃣ Update Frontend Config

```bash
# Open frontend/assets/js/config.js
# Line 12: Change to your Render URL
PRODUCTION_API: 'https://ped-majevica-backend.onrender.com',

# Commit and push
git add frontend/assets/js/config.js
git commit -m "Update production API URL"
git push origin main
```

### 3️⃣ Deploy Frontend (Netlify)

```bash
1. Go to: https://netlify.com
2. Sign up with GitHub
3. Add new site → Import from GitHub
4. Select: ped-majevica repo
5. Settings:
   - Build: npm run build
   - Publish: frontend
6. Deploy site
7. Visit: https://<your-site>.netlify.app
```

### 4️⃣ Run Database Migrations

```bash
# In Render.com dashboard:
1. Go to your web service
2. Click "Shell" tab
3. Run:
   flask db upgrade
   python migrate_json_to_db.py
```

---

## ✅ Done!

Your site is now live:
- **Backend:** https://ped-majevica-backend.onrender.com/api/posts
- **Frontend:** https://<your-site>.netlify.app

---

## 🔥 Pro Tips

1. **Test backend first:**
   ```bash
   curl https://ped-majevica-backend.onrender.com/api/posts
   ```

2. **Change admin password:**
   - Login: admin / admin123
   - Change immediately!

3. **Free tier limitations:**
   - Backend sleeps after 15min
   - First request takes ~30s to wake up

---

**Total time:** 15 minutes
**Total cost:** $0
