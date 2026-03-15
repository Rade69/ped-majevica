# 🚀 PED Majevica - Deploy Checklist

Brza referenca za deploy na Hetzner VPS.

---

## 📦 Šta Je Pripremljeno

### ✅ Backend Fajlovi:

| Fajl | Lokacija | Svrha |
|------|----------|-------|
| `.env.production` | `backend/` | Template za production .env |
| `gunicorn.conf.py` | `backend/` | Gunicorn konfiguracija |
| `pedmajevica.service` | `backend/` | Systemd service template |
| `pedmajevica.nginx.conf` | `backend/` | Nginx konfiguracija |
| `requirements.txt` | `backend/` | Production dependency-ji |
| `DEPLOYMENT_COMPLETE_GUIDE.md` | `backend/` | Kompletno uputstvo |

### ✅ Skripte:

| Skripta | Lokacija | Svrha |
|---------|----------|-------|
| `backup-production.sh` | `backend/scripts/` | Automatski backup |
| `deploy-to-vps.sh` | `backend/scripts/` | Deploy na VPS |
| `run_tests.sh` | `backend/scripts/` | Pokreni testove |

---

## 🎯 Brzi Deploy (10 Koraka)

### 1. Kreiraj VPS na Hetzneru

```
Server Type: CPX11 (2 vCPU, 2GB RAM)
Image: Ubuntu 22.04 LTS
Location: Falkenstein (FSN1)
```

### 2. SSH Konekcija

```bash
ssh root@<VPS_IP>
```

### 3. Kreiraj User-a

```bash
adduser pedadmin
usermod -aG sudo pedadmin
mkdir -p /home/pedadmin/.ssh
cp /root/.ssh/authorized_keys /home/pedadmin/.ssh/
chown -R pedadmin:pedadmin /home/pedadmin/.ssh
chmod 700 /home/pedadmin/.ssh
chmod 600 /home/pedadmin/.ssh/authorized_keys
```

### 4. Instaliraj Pakete

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib libpq-dev
sudo apt install -y nginx
sudo apt install -y certbot python3-certbot-nginx
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo apt install -y git curl wget vim htop fail2ban rsync
```

### 5. Database Setup

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE pedmajevica;
CREATE USER pedadmin WITH PASSWORD 'JAKA_LOZINKA';
GRANT ALL PRIVILEGES ON DATABASE pedmajevica TO pedadmin;
\q
```

### 6. Deploy Aplikacije

```bash
# Koristi deploy skriptu sa lokalnog računara
cd backend
./scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

**ILI ručno:**

```bash
# Kreiraj direktorijum
sudo mkdir -p /var/www/ped-majevica
sudo chown -R pedadmin:pedadmin /var/www/ped-majevica

# Kopiraj fajlove (scp ili git clone)
```

### 7. Konfiguriši .env

```bash
cd /var/www/ped-majevica/backend
cp .env.production .env
nano .env  # Ažuriraj SECRET_KEY i DATABASE_URL
```

### 8. Pokreni Migracije

```bash
source venv/bin/activate
flask db upgrade
python3 scripts/create_admin.py
```

### 9. Konfiguriši Services

```bash
# Kopiraj service fajlove
sudo cp pedmajevica.service /etc/systemd/system/
sudo cp pedmajevica.nginx.conf /etc/nginx/sites-available/pedmajevica

# Enable link
sudo ln -s /etc/nginx/sites-available/pedmajevica /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Startuj
sudo systemctl daemon-reload
sudo systemctl enable pedmajevica
sudo systemctl start pedmajevica
sudo nginx -t && sudo systemctl restart nginx
```

### 10. SSL Sertifikat

```bash
sudo certbot --nginx -d pedmajevica.org -d www.pedmajevica.org
```

---

## ✅ Provjeri Da Li Radi

```bash
# Testiraj HTTPS
curl -I https://pedmajevica.org

# Provjeri services
sudo systemctl status pedmajevica
sudo systemctl status nginx

# Pogledaj logove
sudo tail -f /var/log/pedmajevica/gunicorn-error.log
sudo tail -f /var/log/nginx/pedmajevica-error.log
```

---

## 🔧 Korisne Komande

### Systemd

```bash
sudo systemctl status pedmajevica    # Status
sudo systemctl restart pedmajevica   # Restart
sudo systemctl stop pedmajevica      # Stop
sudo journalctl -u pedmajevica -f    # Logovi
```

### Nginx

```bash
sudo nginx -t                        # Test config
sudo systemctl restart nginx         # Restart
sudo tail -f /var/log/nginx/*.log    # Logovi
```

### Database

```bash
sudo -u postgres psql -d pedmajevica # PSQL prompt
psql -h localhost -U pedadmin        # Konekcija
```

### Backup

```bash
sudo /usr/local/bin/pedmajevica-backup.sh  # Manualni backup
```

---

## 📊 Monitoring

### UptimeRobot

- URL: https://uptimerobot.com/
- Add: https://pedmajevica.org
- Interval: 5 min
- Email alerts: ON

### SSL Labs

- URL: https://www.ssllabs.com/ssltest/
- Domain: pedmajevica.org
- Target: A+ rating

### PageSpeed

- URL: https://pagespeed.web.dev/
- URL: https://pedmajevica.org
- Target: >80 score

---

## 🐛 Najčešći Problemi

### 502 Bad Gateway

```bash
# Gunicorn ne radi
sudo systemctl status pedmajevica
sudo systemctl restart pedmajevica
```

### SSL Errors

```bash
# Renew certifikate
sudo certbot renew
sudo systemctl restart nginx
```

### Database Connection Failed

```bash
# Provjeri PostgreSQL
sudo systemctl status postgresql

# Test konekciju
psql -h localhost -U pedadmin -d pedmajevica
```

---

## 📞 Support

**Detaljno uputstvo:** `DEPLOYMENT_COMPLETE_GUIDE.md`

**Log Locations:**

```
/var/log/pedmajevica/gunicorn-error.log
/var/log/pedmajevica/gunicorn-access.log
/var/log/nginx/pedmajevica-error.log
/var/log/nginx/pedmajevica-access.log
```

---

**Deploy Status:** [ ] Not Started [ ] In Progress [ ] Complete  
**Deploy Date:** [DATE]  
**Deployed By:** [NAME]  
**VPS IP:** [IP]
