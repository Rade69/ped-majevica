# 🚀 VPS Deployment Guide - pedmajevica.org

Kompletno uputstvo za deployment PED Majevica aplikacije na Hetzner VPS.

---

## 📋 Preduslovi

- ✅ Hetzner Cloud nalog
- ✅ Domen **pedmajevica.org** (kupljen)
- ✅ SSH pristup VPS-u
- ✅ Email za SSL certifikat notifikacije

---

## 🖥️ KORAK 1: Kreiraj Hetzner VPS

### 1.1 Registruj se na Hetzner Cloud

1. Idi na: https://console.hetzner.cloud/
2. Registruj se sa email-om
3. Verifikuj email

### 1.2 Kreiraj Cloud Project

1. Klikni **"New Project"**
2. Naziv: `ped-majevica`

### 1.3 Kreiraj Server

1. Klikni **"Add Server"**
2. **Location:** Frankfurt (najbliže BiH)
3. **Image:** Ubuntu 22.04
4. **Type:** Shared vCPU → **CX11** (€4.51/mes)
5. **SSH Key:** 
   - Generiši SSH key na svom računaru:
     ```bash
     ssh-keygen -t ed25519 -C "tvoj-email@example.com"
     cat ~/.ssh/id_ed25519.pub
     ```
   - Kopiraj public key i dodaj na Hetzner
6. **Name:** `pedmajevica-server`
7. Klikni **"Create & Buy Now"**

### 1.4 Sačuvaj IP adresu

Nakon kreiranja, dobi ćeš **IP adresu** (npr. `116.203.x.x`). Sačuvaj je!

---

## 🌐 KORAK 2: Poveži Domen sa VPS-om

### 2.1 Namecheap DNS Podešavanja

1. Uloguj se na Namecheap
2. Idi na **Domain List** → **Manage** pored pedmajevica.org
3. Klikni **Advanced DNS**
4. Dodaj **A Records**:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | `TVOJ_VPS_IP` | Automatic |
| A Record | www | `TVOJ_VPS_IP` | Automatic |

5. Sačuvaj izmene

### 2.2 Proveri DNS Propagaciju

```bash
# Proveri DNS (može trajati 5-60 minuta)
nslookup pedmajevica.org
```

---

## 🔧 KORAK 3: Inicijalna VPS Konfiguracija

### 3.1 Konektuj se na VPS

```bash
ssh root@TVOJ_VPS_IP
```

### 3.2 Ažuriraj hostname

```bash
hostnamectl set-hostname pedmajevica
```

### 3.3 Kreiraj non-root korisnika (opciono ali preporučeno)

```bash
adduser deploy
usermod -aG sudo deploy
```

---

## 📦 KORAK 4: Automatska Instalacija

### 4.1 Kloniraj projekat privremeno

```bash
cd /tmp
git clone https://github.com/Rade69/ped-majevica.git
cd ped-majevica/deployment/vps
```

### 4.2 Pokreni instalaciju

```bash
sudo bash install.sh
```

Ova skripta instalira:
- ✅ Python 3, pip, venv
- ✅ PostgreSQL
- ✅ Nginx
- ✅ Certbot (SSL)
- ✅ Firewall (UFW)
- ✅ Fail2ban (security)

**Trajanje:** ~5-10 minuta

---

## 🚀 KORAK 5: Postavi Aplikaciju

### 5.1 Kloniraj projekat u production direktorijum

```bash
cd /var/www
sudo git clone https://github.com/Rade69/ped-majevica.git pedmajevica
cd pedmajevica
```

### 5.2 Kopiraj deployment skripte

```bash
sudo cp deployment/vps/* /root/
```

### 5.3 Setup aplikacije

```bash
sudo bash /root/setup-app.sh
```

Ova skripta:
- ✅ Kreira Python virtual environment
- ✅ Instalira dependencies
- ✅ Kreira .env fajl
- ✅ Pokreće database migrations
- ✅ Builda frontend CSS

**Trajanje:** ~3-5 minuta

---

## 🌐 KORAK 6: Setup Nginx i Systemd

```bash
sudo bash /root/setup-nginx.sh
```

Ova skripta:
- ✅ Instalira systemd service
- ✅ Konfiguriše Nginx
- ✅ Startuje Flask aplikaciju
- ✅ Omogućava auto-start nakon reboot-a

**Provera:** Otvori `http://TVOJ_VPS_IP` u browseru

---

## 🔒 KORAK 7: Setup SSL (HTTPS)

```bash
sudo bash /root/setup-ssl.sh
```

Unesi email za Let's Encrypt notifikacije.

**Rezultat:** SSL certifikat instaliran, sajt dostupan na `https://pedmajevica.org`

---

## ✅ KORAK 8: Verifikacija

### 8.1 Proveri da sve radi

```bash
# Proveri Flask aplikaciju
sudo systemctl status pedmajevica

# Proveri Nginx
sudo systemctl status nginx

# Proveri logove
sudo tail -f /var/log/pedmajevica/error.log
```

### 8.2 Otvori sajt

- **Frontend:** https://pedmajevica.org
- **Admin:** https://pedmajevica.org/admin
- **Login:** https://pedmajevica.org/login

**Default admin kredencijali:**
- Username: `admin`
- Password: `admin123`

⚠️ **ODMAH promeni password!**

---

## 🔄 KORAK 9: Deploy Updates

Kada push-uješ izmene na GitHub:

```bash
cd /var/www/pedmajevica
sudo bash /root/deploy.sh
```

Ova skripta automatski:
- ✅ Povlači najnoviji kod
- ✅ Ažurira dependencies
- ✅ Pokreće migrations
- ✅ Builda frontend
- ✅ Restartuje aplikaciju

---

## 💾 KORAK 10: Automatski Backup

### 10.1 Kreiraj Cron Job

```bash
sudo crontab -e
```

Dodaj liniju (backup svaki dan u 3:00 AM):

```
0 3 * * * /root/backup.sh >> /var/log/backup.log 2>&1
```

### 10.2 Manuelni Backup

```bash
sudo bash /root/backup.sh
```

Backup se čuva u `/var/backups/pedmajevica/`

---

## 🔧 Troubleshooting

### Problem: Sajt ne radi

```bash
# Proveri da li Flask radi
sudo systemctl status pedmajevica

# Proveri logove
sudo journalctl -u pedmajevica -n 50

# Restartuj
sudo systemctl restart pedmajevica
```

### Problem: 502 Bad Gateway

```bash
# Proveri da li socket postoji
ls -la /var/www/pedmajevica/pedmajevica.sock

# Proveri permissions
sudo chown -R www-data:www-data /var/www/pedmajevica

# Restartuj sve
sudo systemctl restart pedmajevica nginx
```

### Problem: Database connection error

```bash
# Proveri PostgreSQL
sudo systemctl status postgresql

# Testir aj konekciju
sudo -u postgres psql -d ped_majevica
```

### Problem: SSL certifikat истекао

```bash
# Manuelni renewal
sudo certbot renew

# Proveri auto-renewal
sudo certbot renew --dry-run
```

---

## 📊 Monitoring

### Proveri resource usage

```bash
# CPU i RAM
htop

# Disk space
df -h

# Logovi
sudo tail -f /var/log/nginx/pedmajevica-access.log
```

---

## 🔒 Security Checklist

- [ ] Promenio admin password
- [ ] SSH key authentication (disable password login)
- [ ] UFW firewall enabled
- [ ] Fail2ban running
- [ ] PostgreSQL remote access disabled
- [ ] SSL certificate installed
- [ ] Regular backups configured

---

## 💰 Troškovi

- **Hetzner VPS CX11:** €4.51/mesečno = **€54/godišnje**
- **pedmajevica.org domen:** ~€12/godišnje
- **Ukupno:** **€66/godišnje** ✅

---

## 📞 Podrška

- **Hetzner Support:** https://docs.hetzner.com/
- **Flask Docs:** https://flask.palletsprojects.com/
- **Nginx Docs:** https://nginx.org/en/docs/
- **Let's Encrypt:** https://letsencrypt.org/docs/

---

**Made with ❤️ for PED Majevica 1988** 🏔️
