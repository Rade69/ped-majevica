# 🔒 Security & Stability Test Plan — PED Majevica 1988

**Datum:** 2026-04-11
**Verzija:** 1.0
**Status:** Aktivan

---

## 1. Pregled

Ovaj dokument definiše kompletan test paket za sigurnosno i stabilizaciono testiranje
aplikacije PED Majevica 1988. Svi testovi se pokreću **lokalno** i **ponovljivo**.

### Ciljevi
- Otkriti sigurnosne ranjivosti (auth bypass, XSS, injection, upload abuse)
- Otkriti stabilnosne probleme (500 greške, duple operacije, crash na loš unos)
- Verificirati da zaštite rade (CSRF, rate limiting, RBAC, validacija)
- Omogućiti re-test nakon popravki

### Pokretanje svih testova
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/test_security_*.py -v --tb=short
```

### Pokretanje pojedinačne kategorije
```bash
pytest tests/test_security_auth_bypass.py -v
pytest tests/test_security_xss.py -v
pytest tests/test_security_upload.py -v
# ... itd.
```

---

## 2. Kategorije testova

### 2.1 Auth Bypass (`test_security_auth_bypass.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | Pristup admin rutama bez sesije | 302 redirect ili 401 |
| 2 | POST na admin akcije bez auth | 401 |
| 3 | PUT/DELETE na resurse bez auth | 401 |
| 4 | Pristup `/api/debug/*` bez auth | 403/401 |
| 5 | Manipulacija session cookie-a | 401 |
| 6 | Pristup nakon logout-a | 401/302 |
| 7 | RBAC — regular user na admin rute | 403 |
| 8 | RBAC — editor na delete operacije | Zavisi od config |

### 2.2 Input Validation (`test_security_input_validation.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | Prazan title u postu | 400 |
| 2 | Predugačak string (10K+ chars) | 400 ili uspješno (ograničeno) |
| 3 | Negativni brojevi gdje ne smiju biti | 400 |
| 4 | Ogromni brojevi (10^15) | 400 ili normalizovano |
| 5 | Null/None vrijednosti | 400 |
| 6 | Pogrešan tip podatka (string umjesto int) | 400 |
| 7 | Unicode i emoji input | Prihvaćeno ili 400 |
| 8 | Leading/trailing whitespace | Trimovano ili prihvaćeno |
| 9 | Dupli submit iste forme | Jedan zapis ili idempotentno |
| 10 | SQL injection stringovi | 400 ili sigurno handle-ovano |

### 2.3 XSS (`test_security_xss.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | `<script>alert(1)</script>` u naslovu | Escape-ovano ili odbijeno |
| 2 | `<img src=x onerror=alert(1)>` u opisu | Escape-ovano ili odbijeno |
| 3 | SVG payload sa JS-om | Odbijeno ili escape-ovano |
| 4 | Event handler atributi | Escape-ovano |
| 5 | Stored XSS — unos kroz API, čitanje kroz API | Podatak escape-ovan |
| 6 | Reflected XSS kroz search parametar | Parametar escape-ovan |
| 7 | XSS u category polju | Escape-ovano ili validirano |

### 2.4 Upload Security (`test_security_upload.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | Dozvoljen format (jpg, png, webp) | 201 |
| 2 | Zabranjen format (.php, .exe, .sh) | 400 |
| 3 | Lažna ekstenzija (txt renamed na jpg) | 400 |
| 4 | Double extension (file.php.jpg) | 400 |
| 5 | Prevelik fajl (>10MB) | 400/413 |
| 6 | Prazan fajl (0 bytes) | 400 |
| 7 | Fajl sa `../` u nazivu | Odbijeno |
| 8 | Fajl sa specijalnim znakovima | Sanitizovano ili odbijeno |
| 9 | GIF bomb (mali fajl, ogromna slika) | Odbijeno ili ograničeno |

### 2.5 Error Handling (`test_security_error_handling.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | Nepostojeći ID (999999) | 404, bez stack trace-a |
| 2 | Invalid JSON body | 400, bez stack trace-a |
| 3 | Pogrešan Content-Type | 400/415 |
| 4 | Maliciozni query parametri | 400/404 |
| 5 | Division by zero u inputu | 500 generic error |
| 6 | Ogroman URL path | 404/414 |

### 2.6 IDOR (`test_security_idor.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | Pristup tuđem postu preko ID | Dozvoljeno (javni postovi) |
| 2 | Brisanje tuđeg posta | 403 |
| 3 | Editovanje tuđeg posta | 403 |
| 4 | Pristup gallery image drugog usera | Dozvoljeno (javne slike) |

### 2.7 Abuse (`test_security_abuse.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | Brzi login pokušaji (rate limit) | 429 nakon 5 |
| 2 | Brzi POST zahtjevi | 429 ili usporeno |
| 3 | Više pretraga zaredom | Stabilno |
| 4 | Ponovljeni zahtjevi na isti resurs | Stabilno |

### 2.8 Session/Cookies (`test_security_session.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | Session cookie ima HttpOnly | True |
| 2 | Session cookie ima SameSite | Lax/None (zavisno od env) |
| 3 | Logout invalidira sesiju | Da |
| 4 | Pristup zaštićenoj ruti nakon logout | 401/302 |

### 2.9 Endpoint Exposure (`test_security_endpoint_exposure.py`)
| # | Test | Očekivano |
|---|------|-----------|
| 1 | `/api/debug/auth` dostupan javno | 403/404 |
| 2 | `/api/csrf-token` otkriva previše | Samo token |
| 3 | Password hash u API response | Ne smije biti |
| 4 | Interni pathovi u error response | Ne smiju biti |
| 5 | Konfiguracioni detalji u response | Ne smiju biti |

---

## 3. Nivoi ozbiljnosti

| Nivo | Opis | Primjer |
|------|------|---------|
| **Critical** | Omogućava neovlašteni pristup, izvršavanje koda, brisanje podataka | Auth bypass, RCE, SQL injection |
| **High** | Omogućava izmjenu tuđih podataka, XSS, upload opasnog sadržaja | Stored XSS, IDOR write |
| **Medium** | Curenje informacija, nedostajuće zaštite | Debug endpoint dostupan, stack trace |
| **Low** | UX problem, manji stabilnosni issue | Dupli submit, loša poruka greške |

---

## 4. Re-test procedura

Nakon svake popravke:
```bash
# Pokreni specifični test koji je fail-ovao
pytest tests/test_security_<kategorija>.py::<TestKlasa>::<test_ime> -v

# Pokreni sve security testove
pytest tests/test_security_*.py -v

# Pokreni kompletnu suite (uključujući postojeće testove)
pytest tests/ -v
```

Test se smatra **popravljenim** kada:
1. Test koji je fail-ovao sada prolazi (PASS)
2. Nijedan drugi test nije break-ovan
3. Ručna provjera potvrđuje ispravku

---

## 5. Arhitektura testova

```
backend/tests/
├── conftest.py                           # Shared fixtures
├── test_security_auth_bypass.py          # Auth bypass testovi
├── test_security_input_validation.py     # Input validacija
├── test_security_xss.py                  # XSS testovi
├── test_security_upload.py               # Upload sigurnost
├── test_security_error_handling.py       # Error handling
├── test_security_idor.py                 # IDOR testovi
├── test_security_abuse.py                # Abuse scenariji
├── test_security_session.py              # Session/cookies
├── test_security_endpoint_exposure.py    # Izloženi endpointi
└── SECURITY_FINDINGS.md                  # Izvještaj o nalazima
```

---

## 6. Ograničenja

- Ne testira se produkcija — sve lokalno
- Ne rade se destructive operacije nad pravom bazom
- Rate limit testovi koriste blage vrijednosti (nema pravog DoS-a)
- Testovi ne mijenjaju poslovnu logiku
