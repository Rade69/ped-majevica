# 🚀 DEPLOYMENT CENTER - PED Majevica 1988

**Sve što trebaš za deploy na Hetzner VPS je u ovom folderu!**

---

## 📁 STRUKTURA

```
deployment/
├── README.md                    # ⭐ OVO PROČITAJ PRVO!
├── configs/                     # Konfiguracijski fajlovi
│   ├── gunicorn.conf.py         # Gunicorn WSGI server
│   ├── pedmajevica.service      # Systemd service
│   ├── pedmajevica.nginx.conf   # Nginx reverse proxy
│   ├── nginx-pedmajevica.conf   # Nginx (VPS verzija)
│   └── pedmajevica.service      # Systemd (VPS verzija)
│
├── scripts/                     # Skripte za deploy
│   ├── deploy-to-vps.sh         # ⭐ Glavna deploy skripta
│   ├── backup-production.sh     # Backup skripta
│   ├── setup-app.sh             # Setup aplikacije
│   ├── setup-nginx.sh           # Setup Nginx
│   ├── setup-ssl.sh             # Setup SSL
│   ├── install.sh               # Instalacija dependency-ja
│   └── backup.sh                # VPS backup skripta
│
└── docs/                        # Dokumentacija
    ├── DEPLOY_CHECKLIST.md      # ⭐ Brza checklista (10 koraka)
    ├── DEPLOYMENT_COMPLETE_GUIDE.md  # Detaljno uputstvo
    └── PRIPREMA_ZA_DEPLOY.md    # Priprema za deploy
```

---

## 🎯 BRZI DEPLOY (5 KORAKA)

### 1. Kreiraj VPS na Hetzneru

```
Tip: CPX11 (2 vCPU, 2GB RAM)
Image: Ubuntu 22.04 LTS
Location: Falkenstein
```

### 2. Pokreni Deploy Skriptu

```bash
cd /home/radovan/Downloads/ped-majevica-main/deployment
./scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

### 3. Konfiguriši .env na VPS-u

```bash
ssh pedadmin@<VPS_IP>
cd /var/www/ped-majevica/backend
cp .env.production .env
nano .env  # Ažuriraj SECRET_KEY i DATABASE_URL
```

### 4. Instaliraj SSL

```bash
sudo certbot --nginx -d pedmajevica.org -d www.pedmajevica.org
```

### 5. Testiraj

```
Otvori: https://pedmajevica.org
Testiraj: Login, Admin, Upload
```

---

## 📋 DETALJNA UPUTSTVA

### Za Brzi Deploy:
👉 **docs/DEPLOY_CHECKLIST.md** (10 koraka)

### Za Kompletni Deploy:
👉 **docs/DEPLOYMENT_COMPLETE_GUIDE.md** (sve faze)

### Za Pripremu:
👉 **docs/PRIPREMA_ZA_DEPLOY.md** (šta je spremno)

---

## 🔧 KONFIGURACIJSKI FAJLOVI

### Gunicorn (WSGI Server)

**Lokalno:** `configs/gunicorn.conf.py`
**Na VPS-u:** `/var/www/ped-majevica/backend/gunicorn.conf.py`

```bash
# Kopiraj na VPS
scp configs/gunicorn.conf.py pedadmin@<VPS_IP>:/var/www/ped-majevica/backend/
```

### Systemd Service

**Lokalno:** `configs/pedmajevica.service`
**Na VPS-u:** `/etc/systemd/system/pedmajevica.service`

```bash
# Kopiraj na VPS (sa sudo)
sudo scp configs/pedmajevica.service pedadmin@<VPS_IP>:/etc/systemd/system/
```

### Nginx Konfiguracija

**Lokalno:** `configs/pedmajevica.nginx.conf`
**Na VPS-u:** `/etc/nginx/sites-available/pedmajevica`

```bash
# Kopiraj na VPS (sa sudo)
sudo scp configs/pedmajevica.nginx.conf pedadmin@<VPS_IP>:/etc/nginx/sites-available/pedmajevica
```

---

## 📜 SKRIPTE

### deploy-to-vps.sh ⭐

**Glavna deploy skripta!**

```bash
# Usage
./scripts/deploy-to-vps.sh <VPS_IP> <USERNAME>

# Example
./scripts/deploy-to-vps.sh 123.45.67.89 pedadmin
```

**Šta radi:**
- ✅ Sync-uje sve fajlove na VPS
- ✅ Build-uje frontend (Tailwind CSS)
- ✅ Instalira Python dependency-je
- ✅ Pokreće migracije
- ✅ Postavlja permisije
- ✅ Restartuje servise

### backup-production.sh

**Automatski backup**

```bash
# Manualni backup
./scripts/backup-production.sh

# Automatski (cron)
sudo crontab -e
# Dodaj: 0 2 * * * /usr/local/bin/backup-production.sh
```

### setup-ssl.sh

**SSL sertifikat**

```bash
# Na VPS-u
./scripts/setup-ssl.sh pedmajevica.org
```

---

## 🎯 DEPLOY CHECKLIST

### Prije Deploy-a:
- [ ] VPS kreiran na Hetzneru
- [ ] SSH key konfigurisan
- [ ] Domain pointing na VPS IP
- [ ] .env.production ažuriran

### Tokom Deploy-a:
- [ ] Deploy skripta pokrenuta
- [ ] Fajlovi sync-ovani
- [ ] Database kreirana
- [ ] Migracije pokrenute
- [ ] Servisi restartovani

### Nakon Deploy-a:
- [ ] SSL instaliran
- [ ] HTTPS radi
- [ ] Login funkcionalan
- [ ] Admin panel dostupan
- [ ] Backup konfigurisan
- [ ] Monitoring aktivan

---

## 🐛 TROUBLESHOOTING

### Problem: Deploy skripta ne radi

```bash
# Provjeri da li je executable
chmod +x scripts/deploy-to-vps.sh

# Provjeri SSH konekciju
ssh pedadmin@<VPS_IP>

# Pokreni sa debug output-om
bash -x scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

### Problem: Gunicorn ne radi

```bash
# Na VPS-u
sudo systemctl status pedmajevica
sudo journalctl -u pedmajevica -n 50
sudo systemctl restart pedmajevica
```

### Problem: Nginx ne radi

```bash
# Na VPS-u
sudo nginx -t
sudo systemctl status nginx
sudo tail -f /var/log/nginx/pedmajevica-error.log
```

---

## 📞 KORISNE KOMANDE

### Deploy:
```bash
./scripts/deploy-to-vps.sh <VPS_IP> pedadmin
```

### Backup:
```bash
./scripts/backup-production.sh
```

### Setup SSL:
```bash
./scripts/setup-ssl.sh pedmajevica.org
```

### Copy Configs:
```bash
scp configs/gunicorn.conf.py pedadmin@<VPS_IP>:/var/www/ped-majevica/backend/
scp configs/pedmajevica.service pedadmin@<VPS_IP>:/tmp/
scp configs/pedmajevica.nginx.conf pedadmin@<VPS_IP>:/tmp/
```

---

## 📊 STATUS

| Komponenta | Lokacija | Status |
|------------|----------|--------|
| **Configs** | `deployment/configs/` | ✅ Spremno |
| **Scripts** | `deployment/scripts/` | ✅ Spremno |
| **Docs** | `deployment/docs/` | ✅ Spremno |
| **Deploy** | `scripts/deploy-to-vps.sh` | ✅ Spremno |

---

## 🎉 SVE JE SPREMNO!

1. **Otvori:** `docs/DEPLOY_CHECKLIST.md`
2. **Prati:** 10 koraka
3. **Pokreni:** `./scripts/deploy-to-vps.sh`
4. **Gotovo!** 🚀

---

**Deploy Center Status:** ✅ 100% SPREMAN  
**Vrijeme do Deploy-a:** ~30 minuta  
**Težina:** Srednja (prati uputstva)
