# Deploy na VPS (Contabo, Ubuntu)

Server: 169.58.208.91. Aplikacija: `/var/www/ped-majevica`, servis `pedmajevica` (gunicorn na 127.0.0.1:8000), nginx ispred, PostgreSQL lokalno.

## Prvi put (kao root na serveru)
```bash
curl -fsSLO https://raw.githubusercontent.com/Rade69/ped-majevica/main/deployment/scripts/server-setup.sh
sudo bash server-setup.sh      # paketi, korisnik, baza, .env (sa generisanim lozinkama), venv, nginx, ufw
sudo bash /var/www/ped-majevica/deployment/scripts/deploy.sh   # migracije, CSS build, start
```
Admin lozinke se prikazuju samo jednom na kraju `server-setup.sh` (cuvaju se i u `backend/.env`, chmod 600).
Prvi admini se kreiraju sa: `cd /var/www/ped-majevica/backend && sudo -u pedmajevica env FLASK_APP=wsgi.py venv/bin/flask init-admin`.

## Pocetni sadrzaj (jednom, nakon prvog deploya)
Provjereno na praznoj PostgreSQL bazi: 25 clanaka, 3 staze, 5 dogadjaja; sve stranice vracaju 200.
```bash
cd /var/www/ped-majevica/backend
sudo -u pedmajevica env FLASK_APP=wsgi.py PYTHONPATH=. venv/bin/python scripts/import_blog_posts.py     # 25 clanaka (preskace duplikate)
sudo -u pedmajevica env FLASK_APP=wsgi.py PYTHONPATH=. venv/bin/python scripts/seed_trails_events.py     # 3 staze + 5 PRIMJERA dogadjaja (zamijeniti kroz admin)
```
Plan aktivnosti na javnoj stranici dolazi iz `frontend/assets/data/plan_aktivnosti.json` (ide s kodom); DB tabela se puni iz admina.

## HTTPS (kad domena pokazuje na 169.58.208.91)
```bash
sudo certbot --nginx -d pedmajevica.org -d www.pedmajevica.org
```
Bez HTTPS-a login ne radi: produkcijski cookie-ji su `Secure`.

## Automatski deploy
Push na `main` pokrece CI (testovi); ako prodju, posao `deploy` u `.github/workflows/ci.yml` se SSH-om spaja na server i pokrece `deploy.sh`.
SSH kljuc za to (`github-actions-deploy-ped-majevica` u `/root/.ssh/authorized_keys`) je ogranicen sa `restrict,command=...` i smije pokrenuti iskljucivo `deploy.sh`.
Tajne u GitHub-u: `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`. Za iskljucivanje: obrisati taj red iz `authorized_keys` i obje tajne.

## Update
```bash
sudo bash /var/www/ped-majevica/deployment/scripts/deploy.sh
```
`.env`, baza i `backend/uploads` se ne diraju. Logovi: `journalctl -u pedmajevica -n 50`, `/var/log/pedmajevica/`, `/var/log/nginx/pedmajevica-error.log`.

## Poruke iz kontakt forme
Poruke se uvijek cuvaju u bazi i vide se u admin panelu, tab **Poruke** (znacka pokazuje broj neprocitanih).
Obavjestenje na e-mail radi tek kad se podesi slanje posta. Najlakse: na serveru pokrenuti
`sudo bash /var/www/ped-majevica/deployment/scripts/setup-mail.sh` (trazi Gmail adresu i lozinku za aplikacije, lozinka se unosi skriveno,
upisuje u `.env`, restartuje aplikaciju i salje probni e-mail). Rucno, u `/var/www/ped-majevica/backend/.env`:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=adresa@gmail.com
MAIL_PASSWORD=<lozinka za aplikacije>      # Google nalog -> Sigurnost -> Potvrda u 2 koraka -> Lozinke za aplikacije
MAIL_DEFAULT_SENDER=adresa@gmail.com
CONTACT_NOTIFY_EMAIL=pedmajevica88@gmail.com   # neobavezno; ovo je podrazumijevano
```
Zatim `systemctl restart pedmajevica`. Odgovor posjetiocu ide direktno (Reply-To je njegov e-mail).

## Brzina (Lighthouse, mobilni, spora mreza)
Performanse 99, pristupacnost 96, najbolje prakse 100, SEO 100. Fontovi (Montserrat, Playfair), ikone (podskup Font Awesome),
AOS i PDF biblioteke se posluzuju sa nase adrese (`frontend/assets/fonts`, `frontend/assets/vendor`). Nginx komprimuje CSS/JS/JSON i koristi HTTP/2.
Nova ikona (`fa-...`) u stranici ili JS-u: ponovo napraviti podskup alatom `frontend/tools/build_fontawesome_subset.py` (uputa u samom fajlu).

## Sigurnosne napomene
- Izmjena clanaka, staza, dogadjaja, galerije, plana i poruka dozvoljena je samo ulogama admin/editor (testovi: `backend/tests/test_authorization.py`).
- Testovi i produkcija koriste iste verzije biblioteka (`requirements-dev.txt` uvlaci `requirements.txt`), Python 3.12.
- SSH: samo kljucem; kolacic sesije je `Secure`, `HttpOnly`. HSTS i Permissions-Policy postavlja nginx.
- Poznato i odlozeno: `SameSite=None` kolacic (nepotrebno poslije prelaska na isti origin) i CSP zaglavlje (stranica koristi inline skripte); oba traze dogovor/ vece izmjene.

## Backup baze
Automatski, nedjeljom u 03:30 (systemd timer `pedmajevica-backup.timer`); cuva se zadnjih 8 kopija u `/var/backups/pedmajevica/`.
Rucno: `sudo bash /var/www/ped-majevica/deployment/scripts/backup-db.sh`. Provjera rasporeda: `systemctl list-timers pedmajevica-backup.timer`.
Vracanje (u praznu bazu): `gunzip -c FAJL.sql.gz | sudo -u postgres psql ped_majevica`.
Napomena: kopije su na istom serveru; za zastitu od gubitka servera povremeno ih preuzmite na svoj racunar (`scp root@169.58.208.91:/var/backups/pedmajevica/*.gz .`).
