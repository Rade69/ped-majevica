# Deployment Guide - PED Majevica 1988

## Architecture Overview

- **Frontend**: Static site hosted on Netlify (CDN)
- **Backend**: Python Flask API hosted on Render.com
- **Database**: PostgreSQL on Render.com (or SQLite for development)
- **File Storage**: Local filesystem (for development) / Cloud storage (for production - TODO)

## Environment Variables

### Backend (Render.com)

Create the following environment variables in your Render.com dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions and CSRF | `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `FLASK_ENV` | Environment (production/development) | `production` |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, WARNING) | `INFO` |
| `REDIS_URL` | Redis connection URL (optional, for caching) | `redis://...` |
| `ADMIN_RADOVAN_PASSWORD` | Admin password for user 'radovan' | `strong-password` |
| `ADMIN_ALEKSANDAR_PASSWORD` | Admin password for user 'aleksandar' | `strong-password` |
| `ADMIN_SRECKO_PASSWORD` | Admin password for user 'srecko' | `strong-password` |
| `ADMIN_MILOJKO_PASSWORD` | Admin password for user 'milojko` | `strong-password` |

### Frontend (Netlify)

Netlify environment variables (set in Netlify dashboard):

| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL (optional) | `https://ped-majevica-backend.onrender.com` |

## Deployment Steps

### 1. Backend Deployment (Render.com)

1. **Create a new Web Service** on Render.com
2. **Connect your GitHub repository**
3. **Configure service**:
   - **Name**: `ped-majevica-backend`
   - **Environment**: `Python`
   - **Build Command**: 
     ```bash
     cd backend
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd backend
     flask db upgrade
     gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run:app
     ```
4. **Add Environment Variables** (see above)
5. **Create PostgreSQL database** on Render.com and connect it to the service
6. **Deploy**

### 2. Frontend Deployment (Netlify)

1. **Create a new site from Git** on Netlify
2. **Connect your GitHub repository**
3. **Configure build settings**:
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend`
4. **Add environment variables** (optional)
5. **Configure custom domain** (if applicable)
6. **Deploy**

### 3. Database Migrations

After deployment, run database migrations if needed:

```bash
# Local development
cd backend
flask db upgrade

# On Render.com, migrations run automatically via start command
```

## Security Checklist

- [ ] **SECRET_KEY** is strong and unique
- [ ] **Database credentials** are secure (not hardcoded)
- [ ] **Admin passwords** are set via environment variables
- [ ] **CORS** is properly configured for production domains only
- [ ] **CSRF protection** is enabled
- [ ] **Rate limiting** is enabled for API endpoints
- [ ] **HTTPS** is enforced (automatic on Render/Netlify)
- [ ] **Security headers** are set (Netlify configuration)

## Monitoring and Maintenance

### Logs

- **Render.com**: View logs in the dashboard
- **Netlify**: View deploy logs and function logs

### Backups

- **Database**: Render.com PostgreSQL has automatic backups (daily for paid plans)
- **Manual backup**:
  ```bash
  pg_dump DATABASE_URL > backup.sql
  ```

### Scaling

- **Backend**: Upgrade Render.com plan for more resources
- **Frontend**: Netlify CDN automatically scales
- **Database**: Upgrade PostgreSQL plan on Render.com

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL is running
- Check network connectivity

#### 2. CSRF Token Errors
- Ensure `SECRET_KEY` is set
- Verify frontend is sending `X-CSRFToken` header
- Check CORS configuration allows frontend domain

#### 3. Admin Users Not Created
- Check `ADMIN_*_PASSWORD` environment variables are set
- Verify database tables exist (run migrations)

#### 4. Static Files Not Loading
- Check Netlify redirects configuration
- Verify file paths are correct

#### 5. API Calls Fail with CORS Errors
- Verify CORS origins include frontend domain
- Check `credentials: 'include'` in frontend fetch calls
- Ensure backend sends `Access-Control-Allow-Credentials: true`

## Emergency Procedures

### Rollback Deployment

**Render.com**:
1. Go to service dashboard
2. Navigate to "Deploys"
3. Select previous successful deploy
4. Click "Rollback to this deploy"

**Netlify**:
1. Go to site dashboard
2. Navigate to "Deploys"
3. Find previous deploy
4. Click "Publish deploy"

### Database Recovery

1. **From backup**:
   ```bash
   psql DATABASE_URL < backup.sql
   ```

2. **Manual recovery**:
   - Connect to database via `psql`
   - Restore missing data manually

## Contact Information

- **Project Maintainer**: Radovan Stojanović
- **Backend Issues**: Check Render.com logs
- **Frontend Issues**: Check Netlify logs
- **GitHub Repository**: [PED Majevica 1988](https://github.com/your-repo/ped-majevica)

---

*Last updated: April 2026*