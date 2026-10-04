# Izmjene na sajtu bez asistenta

Priručnik za vlasnika sajta. Sajt: https://pedmajevica.org. Kod: https://github.com/Rade69/ped-majevica.

## 1. Šta se mijenja gdje

| Šta želite promijeniti | Gdje |
|---|---|
| Tekstove, brojke, naslove, adresu, telefon, e-mail | Admin panel → tab **Sadržaj** (bez koda) |
| Članke, staze, kalendar, galeriju | Admin panel → ostali tabovi |
| Izgled (boje, razmaci, veličine) | `frontend/tailwind.config.js` (boje) i klase u `frontend/pages/*.html` |
| Slike | `frontend/assets/images/` |
| Početna stranica | `frontend/pages/index.html` |
| Galerija / Učlanite se / Login / Admin | `frontend/pages/galerija.html`, `uclanite-se.html`, `login.html`, `admin.html` |
| Ponašanje (blog, staze, kalendar) | `frontend/js/*.js` |

Nikad ne mijenjajte: `backend/.env` na serveru (lozinke), niti fajlove u `backend/migrations/`.

## 2. Sitna izmjena koda (korak po korak)

1. Otvorite https://github.com/Rade69/ped-majevica, nađite fajl (npr. `frontend/pages/index.html`) i kliknite olovku (**Edit this file**).
2. Promijenite tekst. Mijenjajte samo ono što razumijete; ne brišite oznake `<` i `>` ni atribute `data-cms=...`.
3. Dolje kliknite **Commit changes** i izaberite **Create a new branch** (npr. `moja-izmjena`) pa **Propose changes** i **Create pull request**.
4. Sačekajte oko 3 minute da zelena kvačica pokaže da su testovi prošli (kartica **Checks** na pull requestu). Ako je crveno, **ne objavljujte**.
5. Kliknite **Merge pull request**.
6. **Objava je automatska.** Poslije spajanja GitHub ponovo pokrene testove (kartica **Actions**), i ako prođu, sam objavi izmjenu na server i provjeri da sajt radi. Traje oko 4–5 minuta. Zeleno = objavljeno, crveno = nije objavljeno (sajt ostaje na staroj verziji).
7. Otvorite sajt i uradite **Ctrl+F5**.

Direktna izmjena na grani `main` (bez pull requesta) također se automatski objavljuje poslije uspješnih testova. Zato koristite pull request za sve što niste sigurni da je ispravno: testovi tada prođu prije nego što išta stigne na sajt.

Ručna objava (ako je automatika u kvaru): `ssh root@169.58.208.91 "bash /var/www/ped-majevica/deployment/scripts/deploy.sh"`. Na kraju treba da piše `OK: deploy gotov`. Ako aplikacija poslije objave ne odgovara, skripta sama vraća staru verziju.

## 3. Prije veće izmjene

- Napravite **snimak** u Contabo panelu (Serveri → vaš server → Snimci → Napravi snimak). Besplatan je jedan, i briše se nakon 30 dana.
- Baza se sama kopira nedjeljom u 03:30; ručno: `ssh root@169.58.208.91 "bash /var/www/ped-majevica/deployment/scripts/backup-db.sh"`.

## 4. Ako nešto pođe po zlu

| Problem | Šta uraditi |
|---|---|
| Izmjena izgleda loše | Na GitHub-u otvorite pull request, kliknite **Revert**, spojite, pa ponovo pokrenite deploy komandu |
| Stranica ne radi | `ssh root@169.58.208.91 "systemctl restart pedmajevica"` pa provjerite sajt |
| Ništa ne pomaže | Contabo panel → Snimci → vratite snimak (**gubi se sve poslije njega**, uključujući nove članke) |
| Ne možete na SSH | Contabo panel → VNC konzola (prijava lozinkom servera iz KeePassXC) |

## 5. Ako asistent nije dostupan

Projekat je običan Flask (Python) sajt s običnim JavaScript-om i Tailwind CSS-om. Sva uputstva su u repou: `AGENTS.md` (pravila projekta), `docs/DEPLOY.md` (server i objava). Svaki programer, ili drugi AI alat, može preuzeti posao bez ičije pomoći. Dajte im pristup repozitoriju i ovom priručniku.
