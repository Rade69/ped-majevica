# 📘 KORAK-PO-KORAK: Od Kupovine VPS-a do Live Sajta

**Kompletno uputstvo za deployment pedmajevica.org na Hetzner VPS**

Procijenjeno vrijeme: **2-3 sata** (prva instalacija)

---

# 📋 PRIPREMA (prije kupovine VPS-a)

## ✅ Šta ti treba:

- [ ] Email adresa (za Hetzner nalog)
- [ ] Kartica ili PayPal (plaćanje Hetzner-a)
- [ ] Email (za SSL certifikat notifikacije)
- [ ] 2-3 sata vremena
- [ ] Ovaj dokument otvoren

---

# FAZA 1: KUPOVINA I SETUP HETZNER VPS-a

## KORAK 1.1: Kreiraj Hetzner Cloud nalog

**Trajanje:** 5 minuta

1. **Otvori browser** i idi na: https://console.hetzner.cloud/

2. **Klikni** "Sign Up" (gornji desni ugao)

3. **Unesi podatke:**
   - Email: `tvoj-email@example.com`
   - Password: (jak password, sačuvaj ga!)
   - Klikni checkboxes (prihvati uslove)
   
4. **Klikni** "Sign Up"

5. **Otvori email** i klikni verification link

6. **Uloguj se** na Hetzner Cloud Console

---

## KORAK 1.2: Dodaj način plaćanja

**Trajanje:** 3 minute

1. **Klikni** na svoje ime (gornji desni ugao)
2. **Odaberi** "Billing"
3. **Klikni** "Payment Methods" → "Add payment method"
4. **Unesi** karticu ili dodaj PayPal
5. **Sačuvaj**

---

## KORAK 1.3: Kreiraj Cloud Project

**Trajanje:** 2 minute

1. **Na glavnoj stranici**, klikni **"New Project"**
2. **Naziv projekta:** `ped-majevica`
3. **Klikni** "Create Project"

---

## KORAK 1.4: Generiši SSH ključ (na tvom računaru)

**Trajanje:** 5 minuta

**NA TVOM RAČUNARU** (Linux/Mac terminal ili Windows PowerShell):

```bash
# Otvori terminal
# Generiši SSH key
ssh-keygen -t ed25519 -C "tvoj-email@example.com"

# Pritisnite Enter 3 puta (ostavite sve default)
# Output će biti:
# Your public key has been saved in /home/radovan/.ssh/id_ed25519.pub
```

**Pročitaj public key:**
```bash
cat ~/.ssh/id_ed25519.pub
```

**Izgled:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJd... tvoj-email@example.com
```

**KOPIRAJ** ceo ovaj tekst (selektuj i Ctrl+C)

---

## KORAK 1.5: Dodaj SSH key na Hetzner

**Trajanje:** 2 minute

1. **U Hetzner Console**, klikni **"Security"** (lijevi meni)
2. **Klikni** "SSH Keys" tab
3. **Klikni** "Add SSH Key"
4. **Naziv:** `moj-laptop`
5. **Public Key:** Paste-uj ključ koji si kopirao
6. **Klikni** "Add SSH Key"

---

## KORAK 1.6: Kreiraj Server (VPS)

**Trajanje:** 10 minuta (čekanje da se kreira)

1. **Idi na** "Servers" (lijevi meni)
2. **Klikni** "Add Server"

**PAŽLJIVO popuni:**

| Opcija | Šta odabrati |
|--------|--------------|
| **Location** | Frankfurt, Germany (eu-central) |
| **Image** | Ubuntu → **22.04** |
| **Type** | Shared vCPU → **CX11** (2 vCPU, 2GB RAM) |
| **Networking** | Ostaviti default (Public IPv4 & IPv6) |
| **SSH Keys** | ✅ Štikliraj ključ koji si dodao (`moj-laptop`) |
| **Volumes** | Ne dodavaj ništa |
| **Firewalls** | Ne dodavaj ništa (podesićemo UFW) |
| **Backups** | Opciono (€0.60/mes extra) |
| **Placement groups** | Preskoči |
| **Labels** | Preskoči |
| **Cloud config** | Preskoči |
| **Name** | `pedmajevica-server` |

3. **Klikni** "Create & Buy Now"

4. **SAČEKAJ** 1-2 minute dok se server kreira

5. **Kada se server kreira**, videćeš:
   ```
   Server: pedmajevica-server
   Status: Running ✅
   IPv4: 116.203.x.x  ← OVO JE TVOJ VPS IP!
   ```

**SAČUVAJ IP ADRESU!** Trebaće ti u sledećim koracima.

**Primjer:** Ako je IP `116.203.45.78`, zapiši negde:
```
VPS IP: 116.203.45.78
```

---

# FAZA 2: POVEZIVANJE DOMENA SA VPS-om

## KORAK 2.1: Podesi DNS na Namecheap

**Trajanje:** 5 minuta

1. **Uloguj se** na Namecheap: https://www.namecheap.com/myaccount/login/

2. **Klikni** "Domain List" (lijevi meni)

3. **Pored pedmajevica.org** klikni **"Manage"**

4. **Klikni tab** "Advanced DNS"

5. **Ukloni** sve postojeće A Records i CNAME Records (ako ih ima)

6. **Dodaj NOVI A Record:**
   - Klikni "Add New Record"
   - **Type:** A Record
   - **Host:** `@`
   - **Value:** `TVOJ_VPS_IP` (npr. 116.203.45.78)
   - **TTL:** Automatic
   
7. **Dodaj DRUGI A Record (za www):**
   - Klikni "Add New Record"
   - **Type:** A Record
   - **Host:** `www`
   - **Value:** `TVOJ_VPS_IP` (isti kao gore)
   - **TTL:** Automatic

8. **Klikni** "Save all changes" (zeleno dugme)

**Kako treba da izgleda:**
```
Type       Host    Value            TTL
A Record   @       116.203.45.78    Automatic
A Record   www     116.203.45.78    Automatic
```

---

## KORAK 2.2: Proveri DNS propagaciju

**Trajanje:** 5-60 minuta (čekanje)

DNS propagacija može trajati **5-60 minuta**. Možeš provjeriti da li radi:

**NA TVOM RAČUNARU:**
```bash
# Proveri DNS
nslookup pedmajevica.org

# Ako vidiš tvoj VPS IP - RADI! ✅
# Ako vidiš "can't find" - SAČEKAJ još 10-20 min
```

**Kada vidiš:**
```
Server:  8.8.8.8
Address: 8.8.8.8#53

Non-authoritative answer:
Name:    pedmajevica.org
Address: 116.203.45.78  ← TVOJ IP
```

**DNS je spreman!** ✅ Možeš nastaviti.

---

# FAZA 3: PRVA KONEKCIJA NA VPS

## KORAK 3.1: Konektuj se na VPS

**Trajanje:** 2 minute

**NA TVOM RAČUNARU (terminal):**

```bash
ssh root@TVOJ_VPS_IP
```

**Primjer:**
```bash
ssh root@116.203.45.78
```

**Šta će se desiti:**
1. Prvi put će pitati:
   ```
   The authenticity of host '116.203.45.78' can't be established.
   ED25519 key fingerprint is SHA256:...
   Are you sure you want to continue connecting (yes/no/[fingerprint])?
   ```
   
2. **Unesi:** `yes` i Enter

3. **Konektovan si!** Videćeš:
   ```
   root@pedmajevica-server:~#
   ```

**SADA SI NA VPS-u!** 🎉

---

## KORAK 3.2: Ažuriraj hostname

**Trajanje:** 1 minuta

**NA VPS-u (preko SSH):**

```bash
hostnamectl set-hostname pedmajevica
```

Nema output-a, to je OK.

---

# FAZA 4: AUTOMATSKA INSTALACIJA SERVERA

## KORAK 4.1: Kloniraj projekat (privremeno)

**Trajanje:** 2 minute

**NA VPS-u:**

```bash
# Idi u /tmp folder
cd /tmp

# Kloniraj GitHub repo
git clone https://github.com/Rade69/ped-majevica.git

# Idi u deployment folder
cd ped-majevica/deployment/vps

# Proveri da su skripte tu
ls -la
```

**Trebaš videti:**
```
install.sh
setup-app.sh
setup-nginx.sh
setup-ssl.sh
deploy.sh
backup.sh
```

Ako vidiš ove fajlove - nastavi! ✅

---

## KORAK 4.2: Pokreni automatsku instalaciju

**Trajanje:** 10-15 minuta

**NA VPS-u:**

```bash
bash install.sh
```

**Šta će se desiti:**

Skripta će automatski instalirati:
- ✅ Python 3, pip, venv
- ✅ PostgreSQL (baza podataka)
- ✅ Nginx (web server)
- ✅ Certbot (za SSL)
- ✅ UFW firewall
- ✅ Fail2ban (security)

**PRAĆENJE:**
```
============================================
  PED Majevica - VPS Setup
============================================

✅ Running as root
📦 Updating system packages...
📦 Installing essential packages...
🗄️  Configuring PostgreSQL...
🔒 Configuring firewall...
...
============================================
  ✅ Installation Complete!
============================================
```

**Ako vidiš "✅ Installation Complete!" - ODLIČNO!** 🎉

---

# FAZA 5: POSTAVLJANJE APLIKACIJE

## KORAK 5.1: Kloniraj projekat u production folder

**Trajanje:** 2 minute

**NA VPS-u:**

```bash
# Idi u web root
cd /var/www

# Kloniraj projekat
git clone https://github.com/Rade69/ped-majevica.git pedmajevica

# Idi u projekat
cd pedmajevica

# Proveri strukturu
ls -la
```

**Trebaš videti:**
```
backend/
frontend/
deployment/
data/
README.md
...
```

---

## KORAK 5.2: Kopiraj deployment skripte

**Trajanje:** 1 minuta

**NA VPS-u:**

```bash
cp deployment/vps/* /root/

# Proveri da su kopirane
ls -la /root/*.sh
```

---

## KORAK 5.3: Postavi aplikaciju

**Trajanje:** 5-10 minuta

**NA VPS-u:**

```bash
bash /root/setup-app.sh
```

**Šta će se desiti:**

1. Kreira Python virtual environment
2. Instalira sve Python dependencies (iz requirements.txt)
3. Kreira `.env` fajl sa production podešavanjima
4. Pokreće database migrations
5. Pita te: "Do you want to import initial data? (y/n)"
   - **Unesi:** `y` (yes)
   - Ovo importuje test blog članke

**Output:**
```
🚀 Setting up Flask application...
📦 Creating Python virtual environment...
📦 Installing Python dependencies...
⚙️  Creating .env configuration...
✅ .env file created
🗄️  Running database migrations...
Do you want to import initial data? (y/n) y
📚 Importing initial data...
✅ Application setup complete!
```

**Ako vidiš "✅ Application setup complete!" - SUPER!** 🎉

---

## KORAK 5.4: Promeni PostgreSQL password

**Trajanje:** 2 minute

**Važno za security!**

**NA VPS-u:**

```bash
# Otvori .env fajl
nano /var/www/pedmajevica/backend/.env
```

**Promeni liniju:**
```
DATABASE_URL=postgresql://peduser:changeme123@localhost:5432/ped_majevica
```

**U nešto bezbednije (izmisli jak password):**
```
DATABASE_URL=postgresql://peduser:Mo7jJakPass$2026@localhost:5432/ped_majevica
```

**Sačuvaj:**
- Pritisni `Ctrl + O` (save)
- Pritisni Enter
- Pritisni `Ctrl + X` (exit)

**Promeni password u PostgreSQL-u:**
```bash
sudo -u postgres psql -c "ALTER USER peduser WITH PASSWORD 'Mo7jJakPass$2026';"
```

(Koristi isti password kao u .env)

---

# FAZA 6: NGINX I SYSTEMD SETUP

## KORAK 6.1: Postavi Nginx i Systemd

**Trajanje:** 3 minute

**NA VPS-u:**

```bash
bash /root/setup-nginx.sh
```

**Šta će se desiti:**

1. Kreira systemd service (Flask app se pokreće automatski)
2. Konfiguriše Nginx (web server)
3. Startuje Flask aplikaciju
4. Testira Nginx config

**Output:**
```
🔧 Setting up Nginx and Systemd...
📁 Creating log directories...
🔒 Setting permissions...
⚙️  Installing systemd service...
● pedmajevica.service - PED Majevica Flask Application
   Loaded: loaded
   Active: active (running) ✅
🌐 Installing Nginx configuration...
🧪 Testing Nginx configuration...
nginx: configuration file /etc/nginx/nginx.conf test is successful ✅
🔄 Restarting Nginx...
✅ Nginx and Systemd setup complete!
```

---

## KORAK 6.2: Proveri da radi

**Trajanje:** 1 minuta

**U BROWSERU:**

Otvori: `http://TVOJ_VPS_IP`

**Primjer:** `http://116.203.45.78`

**Šta očekuješ:**
- ✅ Vidiš PED Majevica sajt!
- ✅ Navigacija radi
- ⚠️ Veza nije bezbedna (HTTP, ne HTTPS - to ćemo sad srediti)

**Ako vidiš sajt - ODLIČNO!** 🎉

**Ako ne vidiš:**
```bash
# Proveri status aplikacije
sudo systemctl status pedmajevica

# Proveri logove
sudo tail -f /var/log/pedmajevica/error.log
```

---

# FAZA 7: SSL CERTIFIKAT (HTTPS)

## KORAK 7.1: Postavi SSL

**Trajanje:** 5 minuta

**VAŽNO:** DNS mora biti postavljen (provjeri da `pedmajevica.org` pokazuje na VPS IP)

**NA VPS-u:**

```bash
bash /root/setup-ssl.sh
```

**Šta će se desiti:**

1. Pita te za email:
   ```
   Enter your email for Let's Encrypt notifications: 
   ```
   **Unesi:** `tvoj-email@example.com`

2. Let's Encrypt dobavlja certifikat
3. Nginx se automatski konfiguriše za HTTPS
4. Testira auto-renewal

**Output:**
```
🔒 Setting up SSL certificate...
📜 Obtaining SSL certificate...
Requesting a certificate for pedmajevica.org and www.pedmajevica.org
Successfully received certificate. ✅
🧪 Testing auto-renewal...
Congratulations, all simulated renewals succeeded ✅

============================================
  ✅ SSL Certificate Installed!
============================================

Your site is now available at:
  https://pedmajevica.org
```

---

## KORAK 7.2: Proveri HTTPS

**U BROWSERU:**

Otvori: `https://pedmajevica.org`

**Šta očekuješ:**
- ✅ Sajt se učitava
- ✅ Zelena katanac ikona u browseru
- ✅ "Connection is secure"

**Testiraj:**
- https://pedmajevica.org (glavna stranica)
- https://pedmajevica.org/login (login)
- https://pedmajevica.org/admin (admin panel - treba login)

**Ako sve radi - BRAVO!** 🎉🎉🎉

---

# FAZA 8: FINALNE POSTAVKE

## KORAK 8.1: Promeni admin password

**Trajanje:** 2 minute

**OBAVEZNO!** Default password je nesiguran.

1. **Otvori:** https://pedmajevica.org/login

2. **Uloguj se:**
   - Username: `admin`
   - Password: `admin123`

3. **U admin panelu**, promeni password
   (trenutno mora da se uradi preko baze)

**NA VPS-u:**

```bash
# Konektuj se na PostgreSQL
sudo -u postgres psql -d ped_majevica

# Promeni password (generiše se hash)
# Prvo, instaliraj bcrypt Python modul ako nije
```

**Ili jednostavnije - dodaj novog admin korisnika preko Python shell-a:**

```bash
cd /var/www/pedmajevica/backend
source /var/www/pedmajevica/venv/bin/activate
python3 -c "
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User

app = create_app()
with app.app_context():
    # Promeni admin password
    admin = User.query.filter_by(username='admin').first()
    admin.password_hash = bcrypt.generate_password_hash('NoviJakPassword2026!').decode('utf-8')
    db.session.commit()
    print('✅ Password changed!')
"
```

**Promeni** `NoviJakPassword2026!` sa svojim jakim passwordom!

---

## KORAK 8.2: Podesi automatski backup

**Trajanje:** 3 minute

**NA VPS-u:**

```bash
# Otvori crontab
crontab -e
```

**Ako pita koji editor, odaberi** `nano` (opcija 1)

**Dodaj na kraju fajla:**
```
# Daily database backup at 3:00 AM
0 3 * * * /root/backup.sh >> /var/log/backup.log 2>&1
```

**Sačuvaj:**
- Pritisni `Ctrl + O`
- Enter
- Pritisni `Ctrl + X`

**Testiraj backup manuelno:**
```bash
bash /root/backup.sh
```

**Output:**
```
💾 Creating backup...
🗄️  Backing up database...
🗑️  Cleaning old backups...
✅ Backup complete: /var/backups/pedmajevica/db_2026-01-11_15-30-45.sql.gz
```

---

# ✅ GOTOVO! SAJT JE LIVE!

## 🎉 Čestitamo! Tvoj sajt je sada online:

- **Frontend:** https://pedmajevica.org
- **Admin Panel:** https://pedmajevica.org/admin
- **API:** https://pedmajevica.org/api/

---

# 📋 POST-DEPLOYMENT CHECKLIST

Prođi kroz ovu listu i štikliraj:

- [ ] Sajt se učitava na https://pedmajevica.org
- [ ] SSL certifikat radi (zeleni katanac)
- [ ] Login radi (admin/NoviJakPassword)
- [ ] Admin panel pristupačan
- [ ] Promjenio admin password sa default-a
- [ ] PostgreSQL password promjenjen
- [ ] Automatski backup podešen (cron job)
- [ ] Firewall aktivan (UFW)
- [ ] DNS pokazuje na VPS IP

---

# 🔄 KAKO AŽURIRATI SAJT (BUDUĆNOST)

Kada praviš izmjene i želiš da deploy-uješ:

## Na svom računaru (lokalno):

```bash
# Commit izmjene
git add .
git commit -m "Nova funkcionalnost"
git push origin master
```

## Na VPS-u:

```bash
ssh root@TVOJ_VPS_IP
bash /root/deploy.sh
```

**Deploy skripta automatski:**
- ✅ Povlači najnoviji kod sa GitHub-a
- ✅ Ažurira Python dependencies
- ✅ Pokreće database migrations
- ✅ Builda frontend CSS
- ✅ Restartuje aplikaciju

**Trajanje:** 1-2 minute! 🚀

---

# 🆘 TROUBLESHOOTING

## Problem: Sajt ne učitava

**Provjeri:**
```bash
# Status Flask aplikacije
sudo systemctl status pedmajevica

# Status Nginx-a
sudo systemctl status nginx

# Logovi
sudo tail -f /var/log/pedmajevica/error.log
sudo tail -f /var/log/nginx/pedmajevica-error.log
```

**Restart svega:**
```bash
sudo systemctl restart pedmajevica
sudo systemctl restart nginx
```

---

## Problem: SSL ne radi

**Provjeri DNS:**
```bash
nslookup pedmajevica.org
# Mora pokazivati na VPS IP!
```

**Ponovo pokreni SSL setup:**
```bash
bash /root/setup-ssl.sh
```

---

## Problem: Database greška

**Provjeri PostgreSQL:**
```bash
sudo systemctl status postgresql

# Test konekcija
sudo -u postgres psql -d ped_majevica -c "SELECT 1;"
```

---

# 📞 PODRŠKA

- **Hetzner:** https://docs.hetzner.com/
- **Let's Encrypt:** https://letsencrypt.org/docs/
- **Flask:** https://flask.palletsprojects.com/
- **Nginx:** https://nginx.org/en/docs/

---

# 💰 MJESEČNI TROŠKOVI

- **Hetzner VPS CX11:** €4.51/mjesečno
- **SSL:** €0 (Let's Encrypt)
- **Backup storage:** €0 (na VPS-u)

**Ukupno:** **€4.51/mjesečno** = **€54/godišnje** ✅

---

**Made with ❤️ for PED Majevica 1988** 🏔️

**Sretno sa deployment-om!** 🚀
