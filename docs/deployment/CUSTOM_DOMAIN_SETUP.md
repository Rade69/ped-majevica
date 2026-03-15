# 🌐 Custom Domain Setup - pedmajevica.org

## 📋 Pregled

Ovaj vodič te provodi kroz povezivanje custom domena **pedmajevica.org** (kupljenog na Namecheap) sa Netlify hostingom.

---

## 1️⃣ Netlify - Dodavanje Custom Domena

### Korak 1: Dodaj Glavni Domen

1. Otvori [Netlify Dashboard](https://app.netlify.com/)
2. Izaberi sajt: **ped-majevica**
3. Idi na **Domain management** (levo u meniju)
4. Klikni **"Add custom domain"**
5. Unesi: `pedmajevica.org`
6. Klikni **"Verify"**
7. Netlify će reći da domen već postoji → klikni **"Yes, add domain"**

### Korak 2: Dodaj WWW Varijantu

1. Klikni **"Add domain alias"**
2. Unesi: `www.pedmajevica.org`
3. Klikni **"Save"**

---

## 2️⃣ Namecheap - DNS Konfiguracija

### Korak 1: Otvori DNS Settings

1. Otvori [Namecheap Dashboard](https://www.namecheap.com)
2. Idi na **Domain List**
3. Izaberi `pedmajevica.org` → klikni **"Manage"**
4. Klikni na **"Advanced DNS"** tab

### Korak 2: Obriši Postojeće Rekorde

Obriši sve postojeće:
- A Records
- CNAME Records (osim onih za email ako ih imaš)

### Korak 3: Dodaj Nove DNS Rekorde

#### A Record za Root Domen (@)

Dodaj **jednu** ili **sve četiri** IP adrese za redundanciju:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | `@` | `75.2.60.5` | Automatic |
| A Record | `@` | `99.83.190.102` | Automatic |
| A Record | `@` | `13.224.60.136` | Automatic |
| A Record | `@` | `13.224.60.14` | Automatic |

**Napomena:** `@` označava root domen (pedmajevica.org)

#### CNAME Record za WWW

| Type | Host | Value | TTL |
|------|------|-------|-----|
| CNAME Record | `www` | `ped-majevica.netlify.app` | Automatic |

### Korak 4: Sačuvaj Promene

1. Klikni **"Save all changes"** (dugme dole)
2. DNS propagacija može trajati **5 minuta do 48 sati** (obično 15-30 min)

---

## 3️⃣ Provera DNS Propagacije

### Online Alati:

Koristi ove alate da proveriš da li se DNS promenio:

1. **DNS Checker**: https://dnschecker.org/
   - Unesi: `pedmajevica.org`
   - Izaberi: A Record
   - Trebalo bi da vidiš Netlify IP adrese

2. **What's My DNS**: https://whatsmydns.net/
   - Unesi: `pedmajevica.org`
   - Trebalo bi da vidiš Netlify IP adrese širom sveta

### Komandna Linija:

```bash
# Linux/Mac - proveri A record
dig pedmajevica.org +short

# Trebalo bi da vidiš:
# 75.2.60.5
# 99.83.190.102
# 13.224.60.136
# 13.224.60.14

# Proveri CNAME record za www
dig www.pedmajevica.org +short

# Trebalo bi da vidiš:
# ped-majevica.netlify.app
# [Netlify IP adrese]
```

```bash
# Windows - proveri A record
nslookup pedmajevica.org

# Trebalo bi da vidiš Netlify IP adrese
```

---

## 4️⃣ HTTPS/SSL Certifikat (Automatski)

### Netlify Automatski Provizionira SSL

1. U Netlify Dashboard-u, idi na **Domain management** → **HTTPS**
2. Klikni **"Verify DNS configuration"**
3. Kada DNS bude propagiran, Netlify će automatski:
   - ✅ Kreirati besplatan **Let's Encrypt SSL certifikat**
   - ✅ Konfigurisati **HTTPS**
   - ✅ Redirectovati **HTTP → HTTPS**

### Vremenska Linija:

- **DNS propagacija**: 5-30 minuta (može do 48h)
- **SSL provizioniranje**: 5-10 minuta nakon DNS propagacije
- **Ukupno**: Obično **15-45 minuta**

### Status Provere:

U Netlify Dashboard-u → **Domain management**:
- ✅ **"Netlify DNS"** ili **"External DNS"** - zeleno = DNS OK
- ✅ **"HTTPS"** sekcija:
  - **"Certificate"**: Let's Encrypt certificate = SSL aktivan
  - **"Force HTTPS"**: ON = automatski redirect

---

## 5️⃣ Finalni Test

### Kada DNS i SSL Budu Aktivni:

1. **Otvori u browseru**:
   ```
   https://pedmajevica.org
   https://www.pedmajevica.org
   ```

2. **Proveri redirekciju**:
   ```
   http://pedmajevica.org → https://pedmajevica.org ✅
   http://www.pedmajevica.org → https://www.pedmajevica.org ✅
   ```

3. **Proveri SSL certifikat**:
   - Klikni na **"katanac"** ikonicu u browser address bar-u
   - Trebalo bi da vidiš: **"Connection is secure"**
   - Certifikat izdat od: **Let's Encrypt**

4. **Proveri Blog API**:
   - Otvori **Console** (F12)
   - Idi na Blog stranicu
   - Trebao bi da vidiš:
     ```
     📚 Blog: Fetching from: https://ped-majevica.onrender.com/api/posts
     📚 Blog: Response status: 200
     📚 Blog: Total posts: 26
     ```

---

## 6️⃣ Troubleshooting

### Problem: "DNS_PROBE_FINISHED_NXDOMAIN"

**Uzrok:** DNS još nije propagiran ili su rekorde pogrešni

**Rešenje:**
1. Sačekaj 15-30 minuta
2. Proveri DNS rekorde na Namecheap-u
3. Koristi https://dnschecker.org/ da proveriš status

### Problem: "Your connection is not private" (SSL Error)

**Uzrok:** SSL certifikat još nije provizioniran

**Rešenje:**
1. Sačekaj da DNS u potpunosti propagira
2. U Netlify → Domain management → HTTPS → klikni **"Verify DNS configuration"**
3. Sačekaj 5-10 minuta
4. Hard refresh browser (Ctrl+Shift+R)

### Problem: Blog članci se ne učitavaju na custom domenu

**Uzrok:** CORS ne dozvoljava novi domen

**Rešenje:**
1. Proveri `backend/app/__init__.py` - domen bi trebalo da je već dodat:
   ```python
   "origins": [
       "https://ped-majevica.netlify.app",
       "https://pedmajevica.org",
       "https://www.pedmajevica.org"
   ]
   ```
2. Ako nije, dodaj i deployuj backend na Render
3. Hard refresh frontend (Ctrl+Shift+R)

### Problem: Stari Netlify subdomen (.netlify.app) još radi

**Ovo je normalno!** Netlify ne briše subdomen. Možeš:

1. **Ostaviti ga aktivnim** (dobro za backup)
2. **Onemogućiti ga** (advanced):
   - Netlify Dashboard → Domain management
   - Izaberi subdomen → Options → Remove

---

## 📊 DNS Records Rezime

### Finalna Konfiguracija:

```
pedmajevica.org
├── A Record: @ → 75.2.60.5 (Netlify)
├── A Record: @ → 99.83.190.102 (Netlify)
├── A Record: @ → 13.224.60.136 (Netlify)
├── A Record: @ → 13.224.60.14 (Netlify)
└── CNAME Record: www → ped-majevica.netlify.app
```

### Email Rekorde (Ako Ih Imaš):

**Čuvaj** postojeće MX i TXT rekorde za email:
- MX records (mail servers)
- TXT records (SPF, DKIM)
- CNAME records za email (ako ih imaš)

**Ne diraj** ove rekorde kada menjaš A i CNAME za web hosting!

---

## ✅ Uspešan Setup Checklist

- [ ] A rekorde dodati na Namecheap (4 IP adrese)
- [ ] CNAME rekord dodat za www
- [ ] DNS propagacija završena (dnschecker.org)
- [ ] Netlify detektovao DNS promene
- [ ] SSL certifikat provizioniran (zelena bravica)
- [ ] HTTPS radi za oba domena (sa i bez www)
- [ ] HTTP redirectuje na HTTPS
- [ ] Blog članci se učitavaju sa backend-a
- [ ] Console ne prikazuje CORS errore
- [ ] Custom domen radi u svim browserima

---

## 🎯 Očekivani Rezultat

Posle uspešnog setup-a:

```
https://pedmajevica.org         ✅ Radi (sa SSL)
https://www.pedmajevica.org     ✅ Radi (sa SSL)
http://pedmajevica.org          ✅ Redirectuje na HTTPS
http://www.pedmajevica.org      ✅ Redirectuje na HTTPS

Backend API:
https://ped-majevica.onrender.com/api/posts  ✅ Dostupan
CORS:                                         ✅ Dozvoljava pedmajevica.org
```

---

## 📚 Dodatni Resursi

- [Netlify Custom Domains Docs](https://docs.netlify.com/domains-https/custom-domains/)
- [Netlify HTTPS/SSL Docs](https://docs.netlify.com/domains-https/https-ssl/)
- [Namecheap DNS Management](https://www.namecheap.com/support/knowledgebase/article.aspx/319/2237/how-can-i-set-up-an-a-address-record-for-my-domain/)
- [DNS Checker Tool](https://dnschecker.org/)

---

**Datum kreiranja**: 12. Januar 2026
**Autor**: Claude Sonnet 4.5
**Projekat**: PED Majevica 1988
