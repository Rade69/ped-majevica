# 🚀 Deployment Options for PED Majevica

Ovaj folder sadrži deployment konfiguracije za različite platforme.

---

## 📂 Dostupne Opcije

### **1. VPS Deployment** (Hetzner Cloud) ⭐ **ODABRANO**

- **Folder:** `vps/`
- **Dokumentacija:** [VPS-DEPLOYMENT.md](vps/VPS-DEPLOYMENT.md)
- **Platforma:** Hetzner Cloud (Frankfurt)
- **Cijena:** €54/godišnje
- **Domen:** pedmajevica.org

**Prednosti:**
- ✅ Potpuna kontrola
- ✅ Jeftino
- ✅ PostgreSQL uključen
- ✅ Automatske skripte za sve

**Uključuje:**
- `install.sh` - Automatska instalacija svih dependencies
- `setup-app.sh` - Podešavanje Flask aplikacije
- `setup-nginx.sh` - Nginx i systemd konfiguracija  
- `setup-ssl.sh` - SSL certifikat (Let's Encrypt)
- `deploy.sh` - Update aplikacije sa GitHub-a
- `backup.sh` - Automatski database backup

---

### **2. Render.com Deployment** (Managed Platform)

- **Dokumentacija:** [../DEPLOYMENT.md](../DEPLOYMENT.md)
- **Cijena:** $0 free tier (sa limitima) ili $14/mesec
- **Config:** [../render.yaml](../render.yaml)

**Prednosti:**
- ✅ Jednostavno (samo povezati GitHub)
- ✅ Automatski deployment
- ✅ Ne treba server administracija

**Nedostaci:**
- ❌ Skuplje dugoročno
- ❌ Free tier ima spin-down

---

## 🎯 Preporuka

Za budžet **€75/godišnje** i postojeći domen **pedmajevica.org**:

➡️ **Koristi VPS deployment** (Hetzner Cloud)

Ukupni troškovi:
- Hetzner VPS: **€54/god**
- Domen: **€12/god** (već kupljen)
- **Ukupno: €66/god** ✅

---

## 📚 Quick Start

### VPS Deployment:

```bash
# 1. Kupi Hetzner VPS (CX11, Frankfurt)
# 2. Poveži pedmajevica.org sa VPS IP-jem
# 3. SSH na VPS
ssh root@TVOJ_VPS_IP

# 4. Kloniraj repo
cd /tmp
git clone https://github.com/Rade69/ped-majevica.git
cd ped-majevica/deployment/vps

# 5. Pokreni instalaciju
sudo bash install.sh

# 6. Prati uputstva u VPS-DEPLOYMENT.md
```

---

## 🔒 Security

Sve skripte uključuju:
- ✅ UFW firewall
- ✅ Fail2ban protection
- ✅ SSL/HTTPS automatski
- ✅ Systemd hardening
- ✅ Automatic backups

---

## 📞 Podrška

- **VPS Issues:** [Hetzner Docs](https://docs.hetzner.com/)
- **App Issues:** GitHub Issues ili deployment dokumentacija

---

Made with ❤️ for PED Majevica 1988 🏔️
