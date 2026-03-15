# ⚡ BRZA DEPLOY REFERENCA

**Za kompletan deploy - idi u `deployment/` folder!**

---

## 🚀 5 KORAKA DO PRODUKCIJE

### 1️⃣ VPS (10 min)
```
https://console.hetzner.cloud/
→ CPX11, Ubuntu 22.04, Falkenstein
```

### 2️⃣ Deploy (5 min)
```bash
cd deployment
./scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

### 3️⃣ Konfiguracija (5 min)
```bash
ssh pedadmin@<VPS_IP>
cd /var/www/ped-majevica/backend
cp .env.production .env
nano .env  # SECRET_KEY, DATABASE_URL
```

### 4️⃣ SSL (5 min)
```bash
sudo certbot --nginx -d pedmajevica.org
```

### 5️⃣ Test (10 min)
```
https://pedmajevica.org
→ Login, Admin, Upload
```

---

## 📁 GDJE ŠTA NAĆI

| Šta Trebaš | Folder | Fajl |
|------------|--------|------|
| **Deploy skripta** | `deployment/scripts/` | `deploy-to-vps.sh` ⭐ |
| **Backup skripta** | `deployment/scripts/` | `backup-production.sh` |
| **Gunicorn config** | `deployment/configs/` | `gunicorn.conf.py` |
| **Nginx config** | `deployment/configs/` | `pedmajevica.nginx.conf` |
| **Systemd config** | `deployment/configs/` | `pedmajevica.service` |
| **Brza checklista** | `deployment/docs/` | `DEPLOY_CHECKLIST.md` ⭐ |
| **Detaljno uputstvo** | `deployment/docs/` | `DEPLOYMENT_COMPLETE_GUIDE.md` |

---

## 🔧 KOMANDE

### Deploy:
```bash
cd deployment
./scripts/deploy-to-vps.sh <IP> pedadmin
```

### Backup:
```bash
./scripts/backup-production.sh
```

### SSL:
```bash
./scripts/setup-ssl.sh pedmajevica.org
```

---

## 📞 HELP

- **Detaljno:** `deployment/docs/DEPLOYMENT_COMPLETE_GUIDE.md`
- **Brzo:** `deployment/docs/DEPLOY_CHECKLIST.md`
- **Center:** `deployment/README.md`

---

**SREĆAN DEPLOY! 🚀**
