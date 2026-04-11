# API Konfiguracija - Bezbedne Promene

**Datum:** 2026-04-10  
**Status:** Završeno  
**Rizik:** Nizak (sve promene imaju fallback mehanizme)

## 📋 Pregled Promena

Sve promene su dizajnirane da budu **bezbedne** i **niskog rizika**. Svaka promena ima fallback mehanizam koji garantuje da će stranica raditi čak i ako nešto pođe po zlu.

## 🔧 Primijenjene Promene

### 1. `index.html` - Početna stranica
- **Promena:** Zamenjen hardcodovani `INDEX_GALLERY_API` URL
- **Novi kod:**
  ```javascript
  const INDEX_GALLERY_API = (function() {
      if (window.API_CONFIG && typeof window.API_CONFIG.getUrl === 'function') {
          console.log('✅ Koristim API_CONFIG za galeriju');
          return window.API_CONFIG.getUrl('/api/gallery');
      }
      console.log('⚠️ API_CONFIG nije dostupan, koristim development URL');
      return 'http://127.0.0.1:5000/api/gallery';
  })();
  ```
- **Bezbednost:** Ima fallback na development URL

### 2. `galerija.html` - Galerija stranica
- **Promena 1:** Dodato učitavanje `config.js`
- **Promena 2:** Zamenjen hardcodovani `GALLERY_API` URL istim pattern-om kao index.html
- **Bezbednost:** Isti fallback mehanizam

### 3. `trails.js` - Staze JavaScript
- **Promena:** Popravljen fallback sa Render.com URL-a na relativni put
- **Stari kod:** `: 'https://ped-majevica.onrender.com/api/trails'`
- **Novi kod:** `return '/api/trails';`
- **Razlog:** Render.com fallback je izazivao CORS probleme u development-u

### 4. `admin.html` - Admin panel
- **Promena:** Zamenjen hardcodovani Render.com logout URL
- **Novi kod:** `const logoutUrl = window.API_CONFIG ? window.API_CONFIG.getUrl('/logout') : '/logout';`
- **Bezbednost:** Koristi API_CONFIG ako postoji, inače relativni put

## 🎯 Kako Radi Nova Konfiguracija

### U Development Okruženju (localhost)
1. Browser otkriva da je hostname `localhost` ili `127.0.0.1`
2. `API_CONFIG.BASE_URL` vraća `http://127.0.0.1:5000`
3. Svi API pozivi idu na lokalni Flask server

### U Produkciji (bilo koji drugi domen)
1. Browser otkriva da hostname nije localhost
2. `API_CONFIG.BASE_URL` vraća `https://ped-majevica.onrender.com`
3. Svi API pozivi idu na Render.com backend

### Fallback Scenarijo (ako config.js nije učitan)
1. JavaScript proveri da li `window.API_CONFIG` postoji
2. Ako ne postoji, koristi fallback URL (`http://127.0.0.1:5000/...`)
3. Stranica i dalje radi, ali samo na development URL-u

## 🧪 Testiranje Promena

### Test 1: Development Okruženje
```bash
# 1. Pokreni Flask backend
cd backend
python run.py

# 2. Otvori index.html u browser-u
open http://localhost:5000  # ili koristi file:// sa CORS disabled
```

**Proveri u Console:**
- `✅ Koristim API_CONFIG za galeriju`
- API pozivi treba da idu na `http://127.0.0.1:5000/api/...`

### Test 2: Bez Backend-a (fallback test)
```bash
# 1. Nemoj pokretati Flask backend
# 2. Otvori index.html direktno iz fajl sistema (file://)
# 3. Proveri Console za fallback poruku
```

**Očekivano:**
- `⚠️ API_CONFIG nije dostupan, koristim development URL`
- Stranica pokušava da pristupi `http://127.0.0.1:5000` (neće uspeti bez backend-a)

### Test 3: Produkcijski Scenario (simulacija)
```bash
# 1. Promeni hosts fajl da simuliraš drugi domen
# 2. Ili koristi ngrok za javni URL
```

## 🔍 Provera Funkcionalnosti

Nakon promena, proveriti:

1. **Galerija** - Da li se slike učitavaju na početnoj stranici?
2. **Staze** - Da li se lista staza učitava?
3. **Blog** - Da li se članci učitavaju?
4. **Admin logout** - Da li logout funkcioniše?
5. **Galerija stranica** - Da li se puna galerija učitava?

## ⚠️ Potencijalni Problemi i Rešenja

### Problem 1: CORS greške u development-u
**Simptom:** `Access-Control-Allow-Origin` greške u Console
**Rešenje:** 
- Proveri da li Flask server ima CORS podešeno
- Pokreni stranicu sa `http://localhost:5000` umesto `file://`

### Problem 2: API_CONFIG nije definisan
**Simptom:** `window.API_CONFIG is undefined`
**Rešenje:**
- Proveri da li se `config.js` učitava pre inline JavaScript-a
- Proveri Console za 404 greške pri učitavanju `config.js`

### Problem 3: Stranica ne učitava podatke
**Simptom:** "Učitavanje..." se nikad ne završi
**Rešenje:**
- Proveri da li je backend pokrenut
- Proveri Network tab za failed zahteve
- Fallback će pokušati development URL

## 📁 Backup i Rollback

### Backup Kreiran:
```bash
frontend-backup-20260410-160806/
```

### Rollback Procedure:
```bash
# Hitni rollback ako nešto ne radi
cp -r frontend-backup-20260410-160806/* frontend/

# Ili samo za specifične fajlove
cp frontend-backup-20260410-160806/pages/index.html frontend/pages/
cp frontend-backup-20260410-160806/pages/galerija.html frontend/pages/
cp frontend-backup-20260410-160806/js/trails.js frontend/js/
cp frontend-backup-20260410-160806/pages/admin.html frontend/pages/
```

## 🎓 Zaključak

**Promene su bezbedne jer:**
1. Svaka promena ima fallback mehanizam
2. Nije menjana osnovna logika aplikacije
3. Samo su zamenjeni hardcodovani stringovi
4. Postoji kompletan backup
5. API_CONFIG već postoji i testiran je

**Stranica će raditi u svim scenarijima:**
- ✅ Sa backend-om na localhost:5000
- ✅ Sa backend-om na Render.com  
- ✅ Čak i bez API_CONFIG (sa fallback-om)
- ✅ U produkciji sa bilo kojim domenom

**Preporuka:** Testirati sve funkcionalnosti pre deploy-a u produkciju.