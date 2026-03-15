# 🚀 Hybrid Deployment Guide

**Backend:** Render.com (Flask + PostgreSQL)
**Frontend:** Netlify (Static HTML/CSS/JS)

---

## ✅ Prerequisites

- [ ] GitHub account
- [ ] Render.com account (sign up with GitHub)
- [ ] Netlify account (sign up with GitHub)
- [ ] GitHub repo pushed (already done ✓)

---

## 📋 Part 1: Deploy Backend to Render.com

### Step 1: Create Render Account

1. Go to: https://render.com
2. Click **"Get Started for Free"**
3. Sign up with GitHub account
4. Authorize Render to access your GitHub repos

### Step 2: Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Fill in:
   ```
   Name: ped-majevica-db
   Database: ped_majevica
   User: (auto-generated)
   Region: Frankfurt (EU Central)
   Plan: Free
   ```
3. Click **"Create Database"**
4. Wait 2-3 minutes for database to provision
5. **Copy the Internal Database URL** (you'll need this)

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `Rade69/ped-majevica`
3. Fill in:
   ```
   Name: ped-majevica-backend
   Region: Frankfurt (EU Central)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app
   Plan: Free
   ```

### Step 4: Add Environment Variables

Click **"Environment"** → **"Add Environment Variable"**

Add these variables:

```bash
FLASK_ENV=production
SECRET_KEY=<generate-random-32-char-string>
DATABASE_URL=<paste-internal-database-url-from-step-2>
LOG_LEVEL=INFO
```

**To generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for initial deployment
3. **Copy your backend URL:** `https://ped-majevica-backend.onrender.com`

### Step 6: Run Database Migrations

1. In Render dashboard, go to your web service
2. Click **"Shell"** tab
3. Run these commands:
   ```bash
   flask db upgrade
   python migrate_json_to_db.py
   ```

**Backend is now LIVE!** 🎉

Test it: `https://ped-majevica-backend.onrender.com/api/posts`

---

## 📋 Part 2: Deploy Frontend to Netlify

### Step 1: Update API Configuration

1. Open `frontend/assets/js/config.js`
2. Replace `PRODUCTION_API` with your Render backend URL:
   ```javascript
   PRODUCTION_API: 'https://ped-majevica-backend.onrender.com',
   ```
3. Commit and push changes:
   ```bash
   git add frontend/assets/js/config.js
   git commit -m "Update production API URL"
   git push origin main
   ```

### Step 2: Create Netlify Account

1. Go to: https://netlify.com
2. Click **"Sign up"**
3. Sign up with GitHub account
4. Authorize Netlify to access your repos

### Step 3: Deploy Site

1. Click **"Add new site"** → **"Import an existing project"**
2. Choose **"GitHub"**
3. Select repository: `Rade69/ped-majevica`
4. Configure build settings:
   ```
   Base directory: (leave empty)
   Build command: npm run build
   Publish directory: frontend
   ```
5. Click **"Deploy site"**

### Step 4: Configure Custom Domain (Optional)

1. In Netlify dashboard, go to **"Domain settings"**
2. Click **"Add custom domain"**
3. Enter: `pedmajevica.org`
4. Follow DNS configuration instructions from Netlify
5. In Namecheap, update DNS records:
   ```
   Type: CNAME
   Host: www
   Value: <your-netlify-subdomain>.netlify.app

   Type: A
   Host: @
   Value: 75.2.60.5 (Netlify IP)
   ```

**Frontend is now LIVE!** 🎉

---

## 🧪 Testing the Deployment

### Test Backend API

```bash
# Test posts endpoint
curl https://ped-majevica-backend.onrender.com/api/posts

# Should return JSON array of posts
```

### Test Frontend

1. Visit: `https://<your-site>.netlify.app`
2. Check:
   - [ ] Homepage loads
   - [ ] Articles display (from backend)
   - [ ] Trails display (from backend)
   - [ ] Events display (from backend)
   - [ ] Dark mode works
   - [ ] Navigation works

### Test Admin Panel

1. Visit: `https://<your-site>.netlify.app/pages/admin.html`
2. Login:
   - Username: `admin`
   - Password: `admin123`
3. Test creating a new post

---

## 📊 Deployment URLs

After deployment, you'll have:

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | `https://ped-majevica-backend.onrender.com` | Flask + PostgreSQL |
| **Frontend** | `https://<your-site>.netlify.app` | Static HTML/CSS/JS |
| **Custom Domain** | `https://pedmajevica.org` | Production site |

---

## 🔧 Common Issues

### Backend shows "Application failed to respond"

**Cause:** Database migrations not run
**Fix:**
```bash
# In Render Shell
flask db upgrade
```

### Frontend can't fetch data

**Cause:** CORS or wrong API URL
**Fix:**
1. Check `frontend/assets/js/config.js` has correct `PRODUCTION_API`
2. Check browser console for CORS errors
3. Verify backend is running

### "Free instance will spin down with inactivity"

**Expected behavior:** Render free tier sleeps after 15min inactivity
**Effect:** First request takes ~30s to wake up
**Solution:** Upgrade to paid tier ($7/month) or accept the delay

---

## 💰 Costs

- **Render.com Free Tier:**
  - ✅ 750 hours/month free
  - ✅ Free PostgreSQL (1GB storage)
  - ⚠️ App sleeps after 15min inactivity

- **Netlify Free Tier:**
  - ✅ 100GB bandwidth/month
  - ✅ Unlimited sites
  - ✅ Automatic HTTPS
  - ✅ Global CDN

**Total cost: $0/month** (with sleep limitation)

---

## 📝 Next Steps

After successful deployment:

1. **Change admin password:**
   - Login to admin panel
   - Change default password (`admin123`)

2. **Add real content:**
   - Upload real images
   - Write real blog posts
   - Add real trail data

3. **Monitor logs:**
   - Check Render logs for errors
   - Check Netlify deploy logs

4. **Upgrade when ready:**
   - Render: $7/month (no sleep)
   - Domain: $9/year (Namecheap)

---

**Need help?** Check troubleshooting or ask in Render/Netlify support!
