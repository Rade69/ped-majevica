# Analiza loših stvari u projektu PED Majevica 1988

**Datum:** 2026-04-11  
**Autor:** Pi Agent (analiza bazirana na pregledu koda)

## Uvod

Analiza je fokusirana isključivo na probleme, ranjivosti i loše prakse u projektu. Cilj je identifikovati šta treba popraviti da bi se poboljšala sigurnost, održivost i kvalitet koda.

---

## 🔴 KRITIČNI SIGURNOSNI PROPUSTI

### 1. Hardcodovane default lozinke za admin korisnike
**Lokacija:** `backend/app/services/user_service.py`  
**Problem:** Funkcija `init_admin()` koristi hardcodovane lozinke kao fallback kada environment varijable nisu postavljene. Ove lozinke su vidljive u kodu:
```python
ADMIN_USERS = {
    "radovan": os.getenv("ADMIN_RADOVAN_PASSWORD", "radovan-!sofija#22$jelena%25&"),
    "aleksandar": os.getenv("ADMIN_ALEKSANDAR_PASSWORD", "Aleksandar$2026!Ped#Majevica"),
    ...
}
```
**Rizik:** Ako se aplikacija pokrene bez environment varijabli (što se često dešava u razvoju), koriste se ove lozinke koje bi mogle biti poznate napadaču.

**Predlog popravke:**
- Ukloniti default vrijednosti - neka aplikacija failuje ako environment varijable nisu postavljene
- Ili koristiti `secrets.token_urlsafe()` za generisanje privremenih lozinki koje se loguju samo pri prvom pokretanju
- Dodati warning log kada se koriste default vrijednosti

### 2. Password reset token je samo user_id
**Lokacija:** `backend/app/routes/auth.py` - funkcija `password_reset_confirm()`  
**Problem:** Token za reset lozinke je samo `user_id` konvertovan u string. Ovo omogućava bilo kome da resetuje lozinku ako pogodi ili dobije user_id.
```python
try:
    user_id = int(token)  # Token je samo user_id!
    user = User.query.get(user_id)
```
**Rizik:** Ozbiljna ranjivost koja omogućava preuzimanje naloga.

**Predlog popravke:**
- Implementirati prave kriptografske tokene koristeći `itsdangerous.URLSafeTimedSerializer`
- Dodati expiry time (npr. 1 sat)
- Validirati token prije nego što se dozvoli reset lozinke

### 3. Password reset ne šalje email
**Lokacija:** `backend/app/routes/auth.py` - funkcija `password_reset_request()`  
**Problem:** Endpoint loguje zahtjev ali ne šalje stvarni email. Funkcionalnost resetovanja lozinke ne radi.
```python
# TODO: Implementirati slanje email-a
# Za sada samo logujemo
```
**Rizik:** Korisnici ne mogu resetovati lozinku, što vodi ka gubitku pristupa.

**Predlog popravke:**
- Integrisati email servis (SMTP ili SendGrid/Amazon SES)
- Kreirati email template sa sigurnim linkom
- Implementirati rate limiting da se spriječi zloupotreba

### 4. CSRF token ne rotira
**Lokacija:** `backend/app/utils/csrf.py`  
**Problem:** CSRF token se generiše pri prvom zahtjevu i ostaje isti tokom sesije. Nema rotacije nakon uspješne validacije.
**Rizik:** Ako token bude ukraden (npr. preko XSS), može se koristiti više puta.

**Predlog popravke:**
- Rotirati token nakon svake uspješne validacije
- Dodati expiry time za tokene
- Implementirati "double submit cookie" pattern kao dodatnu zaštitu

### 5. CORS dozvoljava nesigurne HTTP domene
**Lokacija:** `backend/app/__init__.py` - CORS konfiguracija  
**Problem:** U listi dozvoljenih origin-a postoje HTTP (ne HTTPS) domene:
```python
"origins": [
    "http://pedmajevica.org",  # Temporary: HTTP until SSL is active
    "http://www.pedmajevica.org",
    ...
]
```
**Rizik:** Man-in-the-middle napadi, cookie hijacking.

**Predlog popravke:**
- Ukloniti HTTP domene iz produkcijske konfiguracije
- Koristiti environment varijable za origins umjesto hardcodovanih vrijednosti
- Implementirati dinamičku provjeru origin-a za development

---

## 🟡 ARHITEKTURNI PROBLEMI

### 6. Auto-migracija direktno izvršava ALTER TABLE
**Lokacija:** `backend/app/__init__.py` - auto-migracija kod  
**Problem:** Aplikacija direktno izvršava SQL ALTER TABLE komande umjesto da koristi Alembic migracije:
```python
conn.execute(text(f"ALTER TABLE trail ADD COLUMN {col_name} {col_type}"))
```
**Rizik:** Može uzrokovati probleme u produkciji (locking, konflikti sa postojećim migracijama).

**Predlog popravke:**
- Ukloniti auto-migraciju
- Koristiti isključivo Flask-Migrate (Alembic) za sve promjene sheme
- Dodati skriptu za provjeru nedostajućih kolona u CI/CD

### 7. Model metode vrše direktne commit-e
**Lokacija:** `backend/app/models/user.py` - `update_last_login()`  
**Problem:** Metoda `update_last_login()` poziva `db.session.commit()` unutar modela:
```python
def update_last_login(self):
    self.last_login = datetime.utcnow()
    db.session.commit()  # PROBLEM: direktan commit
```
**Rizik:** Poremeti transakcije, može dovesti do neočekivanih commit-a.

**Predlog popravke:**
- Ukloniti `db.session.commit()` iz modela
- Metoda treba samo da ažurira atribut, a pozivatelj treba da commit-a
```python
def update_last_login(self):
    self.last_login = datetime.utcnow()
```

### 8. Redundancija session podataka
**Lokacija:** `backend/app/routes/auth.py` - `api_login()`  
**Problem:** Ručno postavljanje session podataka pored `login_user()`:
```python
session["user_id"] = user.id
session["username"] = username
session["role"] = user.role
session.permanent = True
login_user(user, remember=True)  # Ovo već postavlja session
```
**Rizik:** Neusklađenost podataka, potencijalni konflikti.

**Predlog popravke:**
- Ukloniti ručno postavljanje session varijabli
- Koristiti `current_user` objekt za pristup korisničkim podacima
- Ako su dodatni session podaci potrebni, koristiti Flask-Login extension metode

### 9. Cookie settings nisu environment-sensitive
**Lokacija:** `backend/app/config.py`  
**Problem:** `SESSION_COOKIE_SECURE = True` i `SESSION_COOKIE_SAMESITE = "None"` su postavljeni za sva okruženja:
```python
SESSION_COOKIE_SECURE = True  # Required for SameSite=None
SESSION_COOKIE_SAMESITE = "None"  # Allow cross-origin
```
**Rizik:** Lokalni razvoj neće raditi sa HTTP (jer Secure zahtijeva HTTPS).

**Predlog popravke:**
- Dinamički podesiti cookie settings na osnovu `FLASK_ENV`:
```python
SESSION_COOKIE_SECURE = ENV == "production"
SESSION_COOKIE_SAMESITE = "None" if ENV == "production" else "Lax"
```

### 10. Import unutar funkcije može uzrokovati circular imports
**Lokacija:** `backend/app/__init__.py` - `load_user()`  
**Problem:** Import servisa unutar funkcije:
```python
@login_manager.user_loader
def load_user(user_id):
    from app.services.user_service import get_user_by_id  # Import unutar funkcije
    return get_user_by_id(int(user_id))
```
**Rizik:** Circular imports, teško debugiranje.

**Predlog popravke:**
- Premjestiti import na vrh fajla
- Ili koristiti lazy loading pattern

---

## 🟠 FRONTEND PROBLEMI

### 11. API request ne šalje CSRF token
**Lokacija:** `frontend/js/api.js` - `request()` funkcija  
**Problem:** Za write operacije (POST, PUT, DELETE) se ne šalje CSRF token, dok backend zahtijeva CSRF validaciju.
```javascript
const res = await fetch(url, {
  credentials: "same-origin",
  headers: {
    "Content-Type": "application/json",
    // Nedostaje X-CSRF-Token header!
  },
});
```
**Rizik:** Cross-site request forgery napadi.

**Predlog popravke:**
- Dodati CSRF token u headers za sve state-changing metode:
```javascript
headers: {
  "Content-Type": "application/json",
  "X-CSRF-Token": getCsrfTokenFromCookieOrMetaTag(),
},
```

### 12. credentials: "same-origin" za cross-origin komunikaciju
**Lokacija:** `frontend/js/api.js` - `request()` funkcija  
**Problem:** Frontend je na Netlify (`ped-majevica.netlify.app`), backend na Render.com - različiti origini, ali `credentials: "same-origin"` ne šalje cookies.
**Rizik:** Autentifikacija ne radi u produkciji.

**Predlog popravke:**
- Promijeniti u `credentials: "include"`
- Osigurati da backend šalje pravilne CORS headers (`Access-Control-Allow-Credentials: true`)

### 13. Hardcodovani API endpointi
**Lokacija:** `frontend/js/api.js` i drugi JS fajlovi  
**Problem:** API endpointi su hardcodovani kao relativni paths (`"/api/posts/"`):
```javascript
return request("/api/posts/");
```
**Rizik:** Ne radi kada je frontend hostovan na drugom domenu ili subpath-u.

**Predlog popravke:**
- Dodati konfigurabilni base URL:
```javascript
const API_BASE_URL = window.API_BASE_URL || "/api";
return request(`${API_BASE_URL}/posts/`);
```
- Injektovati `API_BASE_URL` kroz globalnu varijablu ili meta tag.

### 14. Inline CSS u JavaScript-u
**Lokacija:** `frontend/js/api.js` - `showNotification()`  
**Problem:** CSS stilovi su inline u JavaScript-u:
```javascript
notification.style.cssText = `
  padding: 12px 16px;
  margin-bottom: 10px;
  ...
`;
```
**Rizik:** Teško održavanje, nije konzistentno sa Tailwind pristupom.

**Predlog popravke:**
- Koristiti CSS klase i Tailwind utility klase
- Dodati klase u `input.css` i koristiti `classList.add()`

---

## 🟢 CI/CD I DEVOPS PROBLEMI

### 15. CI/CD deployment koraci su placeholderi
**Lokacija:** `.github/workflows/ci.yml` - `deploy-staging` i `deploy-production`  
**Problem:** Deployment koraci samo print-uju poruku:
```yaml
run: |
  echo "Deploying to staging server..."
  # Add deployment commands here
```
**Rizik:** Nema automatskog deploymenta, ručni proces je podložan greškama.

**Predlog popravke:**
- Implementirati stvarni deployment za Render.com (koristeći Render API)
- Dodati deployment za frontend na Netlify
- Koristiti environment secrets za deploy ključeve

### 16. Frontend build artifacts se ne koriste
**Lokacija:** `.github/workflows/ci.yml` - `frontend-build` job  
**Problem:** Build generiše `output.min.css` ali CI upload-uje `frontend/dist` koji ne postoji:
```yaml
path: frontend/dist  # Ova direktorija ne postoji!
```
**Rizik:** Beskorisni artifacti, zbunjujuće.

**Predlog popravke:**
- Ili kreirati `dist` folder sa svim statičkim fajlovima
- Ili promijeniti path na stvarne build output fajlove

### 17. Nedostaje security scanning u CI
**Problem:** CI ima `security` job ali samo pokreće `safety check` i `npm audit` bez fail-a na kritičnim ranjivostima (`|| true`).
**Rizik:** Security issues se ne otkrivaju na vrijeme.

**Predlog popravke:**
- Postaviti `--exit-zero` samo za niskorizične ranjivosti
- Fail-ovati CI na high/critical ranjivostima
- Dodati SAST alate (semgrep, bandit za Python, ESLint za JS)

---

## 🔵 DOKUMENTACIJA I KONFIGURACIJA

### 18. Nedostaje produkcijska dokumentacija
**Problem:** Nema uputstva za:
- Kako generisati SECRET_KEY
- Kako postaviti Redis za caching
- Kako konfigurisati email servis
- Backup strategiju za bazu podataka

**Predlog popravke:**
- Kreirati `DEPLOYMENT.md` sa svim produkcijskim instrukcijama
- Dodati `docker-compose.yml` za lokalni razvoj sa svim servisima
- Dokumentovati monitoring i alerting

### 19. Environment varijable nisu dokumentovane
**Problem:** `.env.example` možda nije ažuran, nema opisa svake varijable.
**Predlog popravke:**
- Ažurirati `.env.example` sa svim potrebnim varijablama
- Dodati komentare za svaku varijablu
- Kreirati skriptu za validaciju environment varijabli

---

## 🟣 PERFORMANSE I SCALABILITY

### 20. Nema paginacije na svim listama
**Problem:** Iako TODO plan navodi da je paginacija implementirana, treba provjeriti da li svi endpointi vraćaju paginirane rezultate.
**Rizik:** Preveliki API response-i, spore stranice.

**Predlog popravke:**
- Implementirati paginaciju na svim listnim endpointima (`/api/posts`, `/api/events`, itd.)
- Dodati query parametre (`?page=1&per_page=20`)
- Vratiti metadata (`total`, `pages`, `next_page`)

### 21. Nema CDN za statičke fajlove
**Problem:** Slike i CSS su servirane sa istog servera kao i API.
**Rizik:** Slabe performanse, visoko opterećenje servera.

**Predlog popravke:**
- Konfigurisati CDN (Cloudflare, AWS CloudFront)
- Koristiti object storage (S3) za upload-ovane slike
- Implementirati image optimization pipeline

### 22. Redis cache nema fallback
**Lokacija:** `backend/app/utils/cache.py`  
**Problem:** Ako Redis nije dostupan, caching se jednostavno disable-uje.
```python
except Exception as e:
    logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
    redis_client = None
```
**Rizik:** Performanse naglo opadaju ako Redis padne.

**Predlog popravke:**
- Implementirati multi-layer caching (Redis → memory → database)
- Dodati health check za Redis
- Koristiti circuit breaker pattern

---

## 🟤 KOD KVALITET I ODRŽIVOST

### 23. Nedostaje konzistentno logovanje
**Problem:** Neki kritični događaji se ne loguju (kreiranje korisnika, brisanje podataka).
**Predlog popravke:**
- Implementirati strukturirano logovanje (JSON logs)
- Dodati audit log za administrativne akcije
- Konfigurisati log levels po environment-u

### 24. Nedostaje error handling na mnogim endpointima
**Problem:** Neki endpointi nemaju try-catch blokove za neočekivane greške.
**Predlog popravke:**
- Dodati globalni error handler u Flask aplikaciju
- Implementirati custom exception klase
- Vratiti konzistentne error response-ove

### 25. Testovi ne pokrivaju sve kritične funkcionalnosti
**Problem:** Testovi ne pokrivaju:
- Password reset flow
- Email verification
- Redis caching
- CSRF zaštitu

**Predlog popravke:**
- Povećati test coverage na 80%+
- Dodati integration testove za kompletne flow-ove
- Implementirati property-based testove

---

## 📋 PRIORITETI POPRAVKE

| Prioritet | Problem | Vrijeme popravke |
|-----------|---------|------------------|
| KRITIČNO | 1. Hardcodovane lozinke | 1 dan |
| KRITIČNO | 2. Password reset token | 2 dana |
| VISOKO | 3. CSRF token rotacija | 1 dan |
| VISOKO | 4. CORS HTTP domene | 1 dan |
| VISOKO | 5. Auto-migracija SQL | 2 dana |
| SREDNJE | 6. Frontend API problemi | 2 dana |
| SREDNJE | 7. CI/CD deployment | 3 dana |
| NISKO | 8. Dokumentacija | 1 tjedan |

---

## 🛠️ SLJEDEĆI KORACI

1. **Hitni popravci (ovaj tjedan):**
   - Popraviti hardcodovane lozinke
   - Implementirati prave password reset tokene
   - Rotirati CSRF tokene

2. **Kratkoročno (2 tjedna):**
   - Popraviti frontend API komunikaciju
   - Implementirati pravi deployment pipeline
   - Dodati security scanning u CI

3. **Srednjoročno (1 mjesec):**
   - Implementirati email servis
   - Dodati CDN i image optimization
   - Poboljšati test coverage

4. **Dugoročno (3 mjeseca):**
   - Implementirati monitoring i alerting
   - Dodati advanced caching strategije
   - Optimizovati performanse za visoki promet

---

## 💡 ZAKLJUČAK

Projekt ima solidnu osnovu ali ima kritične sigurnosne propuste koji moraju biti popravljeni prije produkcijskog deploymenta. Arhitekturni problemi će postati sve veći kako aplikacija raste. Fokus treba biti na:

1. **Sigurnost prvo** - popraviti sve kritične ranjivosti
2. **Automacija** - implementirati pravi CI/CD pipeline
3. **Monitoring** - dodati logovanje i alerting
4. **Dokumentacija** - olakšati održavanje i onboarding

Svi preporučeni popravci su iterativni i mogu se implementirati postepeno bez prekida rada aplikacije.