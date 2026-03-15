# 🚀 DEPLOYMENT CENTER - PED Majevica 1988

**Centralno mjesto za sve deployment operacije!**

---

## 📁 STRUKTURA FAJLOVA

```
deployment/
├── README.md                    # ⭐ START OVDJE!
│
├── configs/                     # Konfiguracije
│   ├── gunicorn.conf.py         # Gunicorn (WSGI server)
│   ├── pedmajevica.service      # Systemd service
│   ├── pedmajevica.nginx.conf   # Nginx config
│   ├── nginx-pedmajevica.conf   # Nginx (VPS)
│   └── pedmajevica.service      # Systemd (VPS)
│
├── scripts/                     # Skripte
│   ├── deploy-to-vps.sh         # ⭐ GLAVNA DEPLOY SKRIPTA
│   ├── backup-production.sh     # Backup database + files
│   ├── setup-app.sh             # Setup aplikacije
│   ├── setup-nginx.sh           # Setup Nginx
│   ├── setup-ssl.sh             # Setup SSL
│   ├── install.sh               # Instalacija dependency-ja
│   └── backup.sh                # VPS backup
│
└── docs/                        # Dokumentacija
    ├── DEPLOY_CHECKLIST.md      # ⭐ BRZA CHECKLISTA (10 koraka)
    ├── DEPLOYMENT_COMPLETE_GUIDE.md  # Detaljno uputstvo
    └── PRIPREMA_ZA_DEPLOY.md    # Priprema
```

---

## 🎯 BRZI START

### 1. Kreiraj VPS na Hetzneru

```
https://console.hetzner.cloud/
└─ Server Type: CPX11 (2 vCPU, 2GB RAM)
└─ Image: Ubuntu 22.04 LTS
└─ Location: Falkenstein
└─ Cijena: ~€4.50/mjesec
```

### 2. Pokreni Deploy

```bash
cd /home/radovan/Downloads/ped-majevica-main/deployment
./scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

### 3. Konfiguriši .env

```bash
ssh pedadmin@<VPS_IP>
cd /var/www/ped-majevica/backend
cp .env.production .env
nano .env
# Ažuriraj: SECRET_KEY, DATABASE_URL
```

### 4. SSL

```bash
sudo certbot --nginx -d pedmajevica.org -d www.pedmajevica.org
```

### 5. Testiraj

```
https://pedmajevica.org
```

---

## 📋 DOKUMENTACIJA

### 🚀 Za Deploy:

1. **docs/DEPLOY_CHECKLIST.md** - Brza checklista (10 koraka)
2. **docs/DEPLOYMENT_COMPLETE_GUIDE.md** - Kompletno uputstvo (30+ strana)
3. **docs/PRIPREMA_ZA_DEPLOY.md** - Šta je spremno

### 🔧 Za Konfiguraciju:

1. **configs/gunicorn.conf.py** - Gunicorn settings
2. **configs/pedmajevica.service** - Systemd service
3. **configs/pedmajevica.nginx.conf** - Nginx config

### 📜 Za Skripte:

1. **scripts/deploy-to-vps.sh** - Automatski deploy
2. **scripts/backup-production.sh** - Automatski backup
3. **scripts/setup-ssl.sh** - SSL instalacija

---

## 🔧 KORISNE KOMANDE

### Deploy:
```bash
./scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

### Backup:
```bash
./scripts/backup-production.sh
```

### Copy Configs:
```bash
scp configs/gunicorn.conf.py pedadmin@<VPS_IP>:/var/www/ped-majevica/backend/
scp configs/pedmajevica.service pedadmin@<VPS_IP>:/tmp/
scp configs/pedmajevica.nginx.conf pedadmin@<VPS_IP>:/tmp/
```

### SSL:
```bash
./scripts/setup-ssl.sh pedmajevica.org
```

---

## ✅ CHECKLISTA

### Prije Deploy-a:
- [ ] VPS kreiran
- [ ] SSH radi
- [ ] Domain pointing na VPS
- [ ] .env.production spreman

### Tokom Deploy-a:
- [ ] Deploy skripta pokrenuta
- [ ] Fajlovi sync-ovani
- [ ] Database kreirana
- [ ] Migracije pokrenute

### Nakon Deploy-a:
- [ ] SSL instaliran
- [ ] HTTPS radi
- [ ] Login radi
- [ ] Admin radi
- [ ] Backup konfigurisan

---

## 🐛 HELP

### Problem: Nešto ne radi?

1. **Provjeri logove:**
   ```bash
   sudo journalctl -u pedmajevica -n 50
   sudo tail -f /var/log/nginx/pedmajevica-error.log
   ```

2. **Restartuj servise:**
   ```bash
   sudo systemctl restart pedmajevica
   sudo systemctl restart nginx
   ```

3. **Provjeri dokumentaciju:**
   - `docs/DEPLOYMENT_COMPLETE_GUIDE.md` - Troubleshooting sekcija

---

## 📞 LINKOVI

- **Hetzner Console:** https://console.hetzner.cloud/
- **Certbot:** https://certbot.eff.org/
- **Gunicorn Docs:** https://docs.gunicorn.org/
- **Nginx Docs:** https://nginx.org/en/docs/

---

## 🎉 SREĆAN DEPLOY!

**Status:** ✅ SPREMAN  
**Vrijeme:** ~30 minuta  
**Težina:** Srednja

**Pitanja?** Pogledaj `docs/DEPLOYMENT_COMPLETE_GUIDE.md`
