# 📋 Manual Security Test Scenarios — PED Majevica 1988

**Datum:** 2026-04-11
**Namjena:** Scenariji koji se ne mogu (lako) automatizovati

---

## 1. Autentikacija

### 1.1 Login sa specijalnim karakterima
**Koraci:**
1. Otvori `/login`
2. Username: `admin' OR '1'='1`
3. Password: `anything`
4. Klikni Login

**Očekivano:** Login neuspio, generička poruka "Pogrešan username ili lozinka"
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 1.2 Login sa praznim poljima
**Koraci:**
1. Otvori `/login`
2. Ostavi oba polja prazna
3. Klikni Login

**Očekivano:** Validacijska greška, ne 500
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 1.3 Brzi login pokušaji (rate limiting)
**Koraci:**
1. Otvori browser konzolu
2. Pošalji 10 POST zahtjeva na `/api/login` u roku od 5 sekundi
3. Pratiti response kodove

**Očekivano:** Nakon 5-6 pokušaja, 429 Too Many Requests
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 1.4 Logout pa Back button
**Koraci:**
1. Uloguj se kao admin
2. Otvori `/admin/dashboard`
3. Klikni Logout
4. Pritisni Back dugme u browseru

**Očekivano:** Redirect na login ili poruka da je sesija istekla
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 2. Admin Panel

### 2.1 Direktan pristup admin URL-u
**Koraci:**
1. Odjaviti se
2. U URL baru upisati: `http://localhost:5000/admin/dashboard`
3. Pritisnuti Enter

**Očekivano:** Redirect na `/login` ili 401
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 2.2 Admin stranica bez autentikacije
**Koraci:**
1. Odjaviti se
2. U URL baru: `http://localhost:5000/admin.html`

**Očekivano:** Redirect na login ili poruka o autorizaciji
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 2.3 Create Post sa HTML sadržajem
**Koraci:**
1. Uloguj se kao admin
2. Idi na admin panel → Create Post
3. Title: `Test <script>alert('XSS')</script>`
4. Content: `<img src=x onerror=alert('XSS')>`
5. Sačuvaj

**Očekivano:** HTML je escape-ovan ili sanitizovan
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 2.4 Preview funkcija
**Koraci:**
1. Uloguj se kao admin
2. Kreiraj post sa XSS payload naslovom
3. Klikni Preview (ako postoji)

**Očekivano:** Payload se prikazuje kao tekst, ne izvršava se
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 3. Upload

### 3.1 Upload PHP fajla
**Koraci:**
1. Uloguj se kao admin
2. Otvori Gallery → Upload
3. Odaberi fajl sa `.php` ekstenzijom (može prazan fajl `test.php`)
4. Klikni Upload

**Očekivano:** "Dozvoljeni formati: png, jpg, jpeg, webp, gif"
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 3.2 Upload .exe fajla
**Koraci:**
1. Uloguj se kao admin
2. Gallery → Upload
3. Odaberi bilo koji `.exe` fajl
4. Klikni Upload

**Očekivano:** Odbijeno — nedozvoljen format
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 3.3 Preimenovani fajl
**Koraci:**
1. Kreiraj tekstualni fajl `malicious.txt` sa sadržajem `<?php system($_GET['cmd']); ?>`
2. Preimenuj u `malicious.jpg`
3. Uloguj se → Gallery → Upload
4. Upload-uj `malicious.jpg`

**Očekivano:** Validacija sadržaja (ne samo ekstenzije) treba odbiti
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 3.4 Prazan fajl
**Koraci:**
1. Gallery → Upload
2. Odaberi prazan fajl `empty.jpg` (0 bytes)
3. Klikni Upload

**Očekivano:** "Fajl je prazan" ili slična poruka
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 3.5 Fajl sa `../` u nazivu
**Koraci:**
1. Preimenovati fajl u `../../etc/passwd.jpg`
2. Upload-uj ga kroz Gallery

**Očekivano:** Ime fajla je sanitizovano ili upload odbijen
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 4. API rute

### 4.1 PUT bez auth
**Koraci:**
```bash
curl -X PUT http://localhost:5000/api/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Hacked"}'
```

**Očekivano:** 401 Unauthorized
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 4.2 DELETE bez auth
**Koraci:**
```bash
curl -X DELETE http://localhost:5000/api/posts/1
```

**Očekivano:** 401 Unauthorized
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 4.3 Create User bez auth
**Koraci:**
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "hacker", "email": "h@h.h", "password": "hack123", "role": "admin"}'
```

**Očekivano:** 401/404/405
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 4.4 Bulk Import Plan Aktivnosti bez auth
**Koraci:**
```bash
curl -X POST http://localhost:5000/api/plan-aktivnosti/import \
  -H "Content-Type: application/json" \
  -d '[]'
```

**Očekivano:** 401 Unauthorized
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 5. Error Handling

### 5.1 Stack trace curenje
**Koraci:**
1. Poslati zahtjev sa namjerno lošim JSON-om:
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{invalid json'
```

**Očekivano:** 400 Bad Request, bez stack trace-a
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 5.2 Nepostojeći ID sa ogromnim brojem
**Koraci:**
```bash
curl http://localhost:5000/api/posts/999999999999999
```

**Očekivano:** 404 Not Found, bez overflow greške
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 5.3 Division by zero u parametrima
**Koraci:**
```bash
curl "http://localhost:5000/api/posts/?per_page=1/0"
```

**Očekivano:** 400 ili 200 sa default vrijednosti, bez 500
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 6. Cookie i Sesija

### 6.1 Cookie atributi (Chrome DevTools)
**Koraci:**
1. Otvori DevTools → Application → Cookies
2. Uloguj se
3. Provjeri session cookie atribute:

| Atribut | Očekivano | Stvarno | Status |
|---------|-----------|---------|--------|
| HttpOnly | ✅ | ___ | ☐ PASS ☐ FAIL |
| Secure | ✅ (prod) / ❌ (dev) | ___ | ☐ PASS ☐ FAIL |
| SameSite | None (prod) / Lax (dev) | ___ | ☐ PASS ☐ FAIL |
| Path | `/` | ___ | ☐ PASS ☐ FAIL |

### 6.2 Sesija nakon zatvaranja browsera
**Koraci:**
1. Uloguj se
2. Zatvori browser potpuno
3. Otvori browser → idi na `/admin/dashboard`

**Očekivano:** Traži login (ako nema "remember me") ili automatski login (ako ima)
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 7. XSS (Cross-Site Scripting)

### 7.1 Reflected XSS kroz Search
**Koraci:**
1. Otvori: `http://localhost:5000/blog?search=<script>alert('XSS')</script>`

**Očekivano:** Parametar je escape-ovan, script se ne izvršava
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 7.2 Stored XSS u post naslovu
**Koraci:**
1. Uloguj se → Create Post
2. Title: `<script>alert('XSS')</script>`
3. Sačuvaj
4. Otvori blog stranicu kao neulogovani korisnik
5. Pogledaj naslov

**Očekivano:** Naslov se prikazuje kao tekst, ne izvršava se JS
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 7.3 SVG XSS
**Koraci:**
1. U neki unos polja (npr. opis eventa) unesi:
   `<svg onload="alert('XSS')">`
2. Sačuvaj
3. Otvori stranicu gdje se taj opis prikazuje

**Očekivano:** SVG se ne izvršava
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 8. CSRF

### 8.1 CSRF vanjski zahtjev
**Koraci:**
1. Kreiraj HTML fajl na drugom origin-u (npr. `file:///tmp/csrf_test.html`):
```html
<form method="POST" action="http://localhost:5000/api/posts/">
  <input name="title" value="CSRF Hacked">
  <input name="content" value="Hacked via CSRF">
  <input type="submit">
</form>
```
2. Otvori fajl u browseru dok si ulogovan u aplikaciju
3. Klikni Submit

**Očekivano:** 400 Bad Request — CSRF token missing or invalid
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## 9. Rate Limiting

### 9.1 Login brute force
**Koraci:**
1. Pokreni u terminalu:
```bash
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:5000/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"wrong"}'
done
```

**Očekivano:** Prvih 5: 401, ostali: 429
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

### 9.2 Password reset abuse
**Koraci:**
```bash
for i in {1..5}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:5000/api/password-reset-request \
    -H "Content-Type: application/json" \
    -d '{"email":"victim@test.com"}'
done
```

**Očekivano:** Nakon 3 zahtjeva: 429
**Stvarno:** ___
**Status:** ☐ PASS ☐ FAIL ☐ N/A

---

## Sažetak rezultata

| Kategorija | Testova | PASS | FAIL | N/A |
|------------|---------|------|------|-----|
| Autentikacija | 4 | ___ | ___ | ___ |
| Admin Panel | 4 | ___ | ___ | ___ |
| Upload | 5 | ___ | ___ | ___ |
| API rute | 4 | ___ | ___ | ___ |
| Error Handling | 3 | ___ | ___ | ___ |
| Cookie/Sesija | 2 | ___ | ___ | ___ |
| XSS | 3 | ___ | ___ | ___ |
| CSRF | 1 | ___ | ___ | ___ |
| Rate Limiting | 2 | ___ | ___ | ___ |
| **UKUPNO** | **28** | ___ | ___ | ___ |

---

## Najkritičniji nalazi

| # | Naziv | Ozbiljnost | Status |
|---|-------|------------|--------|
| 1 | ___ | Critical/High/Medium/Low | ☐ Otvoren ☐ Zatvoren |
| 2 | ___ | Critical/High/Medium/Low | ☐ Otvoren ☐ Zatvoren |
| 3 | ___ | Critical/High/Medium/Low | ☐ Otvoren ☐ Zatvoren |
