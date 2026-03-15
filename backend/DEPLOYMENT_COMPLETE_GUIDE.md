# 🚀 PED Majevica 1988 - Deployment Guide

Kompletan vodič za deploy na Hetzner VPS.

---

## 📋 Sadržaj

1. [Priprema Prije Deploy-a](#priprema-prije-deploy-a)
2. [Kreiranje VPS-a](#kreiranje-vps-a)
3. [Osnovna Konfiguracija VPS-a](#osnovna-konfiguracija-vps-a)
4. [Instalacija Dependency-ja](#instalacija-dependency-ja)
5. [Database Setup](#database-setup)
6. [Deploy Aplikacije](#deploy-aplikacije)
7. [SSL Sertifikat](#ssl-sertifikat)
8. [Monitoring & Backup](#monitoring--backup)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Priprema Prije Deploy-a

### Šta Trebaš Imati:

- ✅ **Hetzner Cloud Account** - https://console.hetzner.cloud/
- ✅ **Domain** - pedmajevica.org (već imaš)
- ✅ **SSH Key** - generisan i dodat na Hetzner
- ✅ **Email** - za SSL sertifikat i domain notifications

### Generisanje SSH Ključa (ako nemaš):

```bash
# Generiši novi SSH key
ssh-keygen -t ed25519 -C "pedmajevica-vps"

# Ili koristi RSA (stariji sistemi)
ssh-keygen -t rsa -b 4096 -C "pedmajevica-vps"

# Dodaj na Hetzner Cloud Console
# Projects > Security > Add SSH Key
```

---

## 🖥️ Kreiranje VPS-a

### 1. Uloguj se na Hetzner Cloud Console

https://console.hetzner.cloud/

### 2. Kreiraj Project (ako nemaš)

- Projects > Create Project
- Name: `PED Majevica`

### 3. Kreiraj Server

**Preporučene postavke:**

| Setting | Value |
|---------|-------|
| **Server Type** | CPX11 (2 vCPU, 2GB RAM) |
| **Image** | Ubuntu 22.04 LTS |
| **Location** | Falkenstein (FSN1) |
| **SSH Key** | Tvoj SSH key |
| **Name** | pedmajevica-web |

**Cijena:** ~€4.50/mjesec

### 4. Zabilježi Podatke

```
VPS IP: <IP_ADRESA>
Username: root
SSH Key: <TVOJ_KEY>
```

---

## 🔧 Osnovna Konfiguracija VPS-a

### 1. SSH Konekcija

```bash
# Prvi login kao root
ssh root@<VPS_IP>
```

### 2. Kreiraj Novog User-a

```bash
# Kreiraj user-a
adduser pedadmin
# (unesi jaku lozinku)

# Dodaj u sudo grupu
usermod -aG sudo pedadmin

# Kopiraj SSH key za novog user-a
mkdir -p /home/pedadmin/.ssh
cp /root/.ssh/authorized_keys /home/pedadmin/.ssh/
chown -R pedadmin:pedadmin /home/pedadmin/.ssh
chmod 700 /home/pedadmin/.ssh
chmod 600 /home/pedadmin/.ssh/authorized_keys
```

### 3. Testiraj Novi Login

```bash
# Otvori NOVI terminal i testiraj
ssh pedadmin@<VPS_IP>

# Ako radi, nastavi. Ako ne, riješi problem prvo!
```

### 4. Onemogući Root Login

```bash
# Uredi SSH konfiguraciju
sudo nano /etc/ssh/sshd_config
```

**Izmjeni ove linije:**

```ini
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

**Restartuj SSH:**

```bash
sudo systemctl restart sshd
```

### 5. Konfiguriši Firewall

```bash
# Instaliraj UFW (ako nije)
sudo apt update
sudo apt install -y ufw

# Konfiguriši pravila
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Omogući firewall
sudo ufw enable
sudo ufw status
```

### 6. Postavi Timezone

```bash
sudo timedatectl set-timezone Europe/Berlin
timedatectl status
```

---

## 📦 Instalacija Dependency-ja

### 1. Update Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instaliraj Potrebne Pakete

```bash
# Python i development
sudo apt install -y python3 python3-pip python3-venv python3-dev

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Nginx
sudo apt install -y nginx

# Certbot (SSL)
sudo apt install -y certbot python3-certbot-nginx

# Node.js (za frontend build)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Git i utility-i
sudo apt install -y git curl wget vim htop net-tools fail2ban rsync
```

### 3. Verifikuj Instalacije

```bash
python3 --version    # Treba: Python 3.10+
node --version       # Treba: v18.x
psql --version       # Treba: psql 14+
nginx -v             # Treba: nginx 1.18+
```

---

## 🗄️ Database Setup

### 1. Startuj PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Kreiraj Database i User-a

```bash
# Uđi u PostgreSQL
sudo -u postgres psql
```

**U psql promptu:**

```sql
-- Kreiraj database
CREATE DATABASE pedmajevica;

-- Kreiraj user-a (ZAMIJENI LOZINKU!)
CREATE USER pedadmin WITH PASSWORD 'JAKA_LOZINKA_OVDJE_123!';

-- Postavi permissions
ALTER ROLE pedadmin SET client_encoding TO 'utf8';
ALTER ROLE pedadmin SET default_tablespace = '';
ALTER ROLE pedadmin SET search_path TO public;
GRANT ALL PRIVILEGES ON DATABASE pedmajevica TO pedadmin;

-- Izađi iz psql
\q
```

### 3. Grantuj Permissions na Šemu

```bash
sudo -u postgres psql -d pedmajevica -c "GRANT ALL ON SCHEMA public TO pedadmin;"
```

### 4. Zabilježi Kredencijale

```
Database: pedmajevica
User: pedadmin
Password: [tvoja_lozinka]
Host: localhost
Port: 5432
```

---

## 🚀 Deploy Aplikacije

### 1. Pripremi Direktorijsku Strukturu

```bash
# Kreiraj direktorijum
sudo mkdir -p /var/www/ped-majevica
sudo chown -R pedadmin:pedadmin /var/www/ped-majevica
```

### 2. Kloniraj Repository

```bash
# Kao pedadmin (preko SSH!)
cd /var/www/ped-majevica
git clone <TVOJ_GIT_REPO_URL> .

# ILI kopiraj fajlove ako nemaš Git repo
# Sa lokalnog računara:
# ./backend/scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

### 3. Konfiguriši Python Virtual Environment

```bash
cd /var/www/ped-majevica/backend

# Kreiraj venv
python3 -m venv venv

# Aktiviraj
source venv/bin/activate

# Instaliraj dependency-je
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Konfiguriši .env Fajl

```bash
cd /var/www/ped-majevica/backend

# Kopiraj production template
cp .env.production .env

# Uredi .env
nano .env
```

**Ažuriraj ove vrijednosti:**

```ini
SECRET_KEY=<generiši-novu-jaku-lozinku>
DATABASE_URL=postgresql://pedadmin:TVOJA_LOZINKA@localhost:5432/pedmajevica
DEBUG=False
MAIL_USERNAME=tvoj-email@gmail.com
MAIL_PASSWORD=tvoj-app-password
```

**Generiši SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Pokreni Migracije

```bash
cd /var/www/ped-majevica/backend
source venv/bin/activate

# Pokreni migracije
flask db upgrade

# Kreiraj admin user-a
python3 scripts/create_admin.py
```

### 6. Konfiguriši Gunicorn

```bash
# Kreiraj log direktorijum
sudo mkdir -p /var/log/pedmajevica
sudo chown -R pedadmin:pedadmin /var/log/pedmajevica

# Kreiraj uploads direktorijum
sudo mkdir -p /var/www/ped-majevica/backend/uploads
sudo chown -R pedadmin:pedadmin /var/www/ped-majevica/backend/uploads
```

### 7. Konfiguriši Systemd Service

```bash
# Kopiraj service fajl (sa lokalnog računara)
# backend/pedmajevica.service -> /etc/systemd/system/pedmajevica.service

# Ili kreiraj direktno na VPS-u:
sudo nano /etc/systemd/system/pedmajevica.service
```

**Sadržaj fajla:** (vidi `backend/pedmajevica.service`)

```bash
# Reload i startuj service
sudo systemctl daemon-reload
sudo systemctl enable pedmajevica
sudo systemctl start pedmajevica

# Verifikuj status
sudo systemctl status pedmajevica
```

### 8. Konfiguriši Nginx

```bash
# Kopiraj Nginx konfiguraciju
sudo nano /etc/nginx/sites-available/pedmajevica
```

**Sadržaj:** (vidi `backend/pedmajevica.nginx.conf`)

```bash
# Enable sajt
sudo ln -s /etc/nginx/sites-available/pedmajevica /etc/nginx/sites-enabled/

# Remove default
sudo rm /etc/nginx/sites-enabled/default

# Testiraj konfiguraciju
sudo nginx -t

# Restartuj Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 9. Build-uj Frontend

```bash
cd /var/www/ped-majevica/frontend

# Instaliraj Node dependency-je
npm install

# Build-uj production CSS
npm run build

# Postavi permisije
sudo chown -R www-data:www-data /var/www/ped-majevica/frontend
```

---

## 🔒 SSL Sertifikat

### 1. Instaliraj Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Dobavi Sertifikat

```bash
# Za oba domain-a
sudo certbot --nginx -d pedmajevica.org -d www.pedmajevica.org
```

**Certbot će pitati:**

1. Email adresa - unesi validnu
2. Terms of Service - prihvati (A)
3. EFF newsletter - po izboru
4. Redirect HTTP to HTTPS - izaberi **YES (2)**

### 3. Verifikuj SSL

```bash
# Provjeri sertifikate
sudo certbot certificates

# Testiraj HTTPS
curl -I https://pedmajevica.org
```

### 4. Auto-Renewal

```bash
# Testiraj renewal
sudo certbot renew --dry-run

# Certbot automatski kreira systemd timer
sudo systemctl list-timers | grep certbot
```

---

## 📊 Monitoring & Backup

### 1. Konfiguriši Backup

```bash
# Kopiraj backup skriptu
sudo cp /var/www/ped-majevica/backend/scripts/backup-production.sh /usr/local/bin/pedmajevica-backup.sh
sudo chmod +x /usr/local/bin/pedmajevica-backup.sh

# Kreiraj backup direktorijum
sudo mkdir -p /var/backups/pedmajevica
sudo chown pedadmin:pedadmin /var/backups/pedmajevica

# Testiraj backup
sudo /usr/local/bin/pedmajevica-backup.sh
```

### 2. Dodaj Cron Job

```bash
# Uredi crontab
sudo crontab -e

# Dodaj liniju (daily backup at 2 AM)
0 2 * * * /usr/local/bin/pedmajevica-backup.sh >> /var/log/pedmajevica-backup.log 2>&1
```

### 3. Instaliraj Fail2Ban

```bash
# Instaliraj
sudo apt install -y fail2ban

# Konfiguriši
sudo nano /etc/fail2ban/jail.local
```

**Dodaj:**

```ini
[sshd]
enabled = true
port = ssh
maxretry = 3

[nginx-limit-req]
enabled = true
port = http,https
maxretry = 10
```

```bash
# Restartuj
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

### 4. UptimeRobot Monitoring

1. Otvori https://uptimerobot.com/
2. Kreiraj nalog
3. Add Monitor:
   - Type: HTTPS
   - URL: https://pedmajevica.org
   - Interval: 5 minutes
4. Postavi email alerts

---

## 🐛 Troubleshooting

### Problem: Gunicorn ne radi

```bash
# Provjeri status
sudo systemctl status pedmajevica

# Pogledaj logove
sudo journalctl -u pedmajevica -n 50

# Restartuj
sudo systemctl restart pedmajevica
```

### Problem: Nginx ne radi

```bash
# Testiraj konfiguraciju
sudo nginx -t

# Provjeri status
sudo systemctl status nginx

# Logovi
sudo tail -f /var/log/nginx/pedmajevica-error.log
```

### Problem: Database connection failed

```bash
# Provjeri da li PostgreSQL radi
sudo systemctl status postgresql

# Testiraj konekciju
psql -h localhost -U pedadmin -d pedmajevica

# Provjeri .env
cat /var/www/ped-majevica/backend/.env | grep DATABASE_URL
```

### Problem: 502 Bad Gateway

```bash
# Gunicorn ne radi - provjeri
sudo systemctl status pedmajevica

# Port 8000 nije dostupan
sudo netstat -tulpn | grep 8000

# Restartuj sve
sudo systemctl restart pedmajevica
sudo systemctl restart nginx
```

### Problem: SSL ne radi

```bash
# Provjeri sertifikate
sudo certbot certificates

# Renew sertifikate
sudo certbot renew

# Restartuj Nginx
sudo systemctl restart nginx
```

---

## ✅ Finalna Checklist

### Prije Launch-a:

- [ ] VPS kreiran i dostupan
- [ ] SSH konfigurisan (root login disabled)
- [ ] Firewall uključen (UFW)
- [ ] PostgreSQL instaliran i konfigurisan
- [ ] Database kreirana
- [ ] .env konfigurisan (SECRET_KEY, DATABASE_URL)
- [ ] Gunicorn service radi
- [ ] Nginx konfigurisan i radi
- [ ] SSL sertifikat instaliran
- [ ] HTTPS redirect radi
- [ ] Backup skripta radi
- [ ] Fail2Ban instaliran
- [ ] Monitoring (UptimeRobot) aktivan

### Testiranje:

- [ ] https://pedmajevica.org radi
- [ ] Login funkcionalan
- [ ] Admin panel dostupan
- [ ] Upload slika radi
- [ ] Mobile responsive radi
- [ ] SSL Labs rating A ili bolje
- [ ] PageSpeed score >80

---

## 📞 Support

**Korisni Linkovi:**

- Hetzner Docs: https://docs.hetzner.cloud/
- Ubuntu Server Guide: https://ubuntu.com/server/docs
- Flask Deployment: https://flask.palletsprojects.com/en/2.3.x/deploying/
- Gunicorn Docs: https://docs.gunicorn.org/
- Nginx Docs: https://nginx.org/en/docs/

**Log Locations:**

```bash
# Application logs
/var/log/pedmajevica/gunicorn-error.log
/var/log/pedmajevica/gunicorn-access.log

# Nginx logs
/var/log/nginx/pedmajevica-error.log
/var/log/nginx/pedmajevica-access.log

# System logs
/var/log/syslog
/var/log/auth.log
```

---

**Deploy Date:** [DATE]  
**Deployed By:** [YOUR NAME]  
**VPS IP:** [IP ADDRESS]  
**Domain:** pedmajevica.org
