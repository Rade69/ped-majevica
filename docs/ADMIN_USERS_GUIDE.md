# 🔐 Admin Users Guide - PED Majevica

## 📋 Kako Dodati/Promeniti Admin Korisnike

### Korak 1: Otvori Fajl

Otvori `backend/create_admin_simple.py` u editoru.

### Korak 2: Pronađi ADMIN_USERS Sekciju

```python
# ============================================
# DODAJ/PROMENI ADMIN KORISNIKE OVDE
# ============================================
# Format: {"username": "password"}
ADMIN_USERS = {
    "admin": "PedMajevica2026!",           # Glavni admin
    # "radovan": "RadovanLozinka123!",     # Primer: dodaj nove admine
    # "marko": "MarkoLozinka456!",         # Primer: još jedan admin
    # "ivana": "IvanaLozinka789!",         # Primer: još jedan admin
}
# ============================================
```

### Korak 3: Dodaj Nove Admine

Ukloni `#` (uncomment) i dodaj svoje korisnike:

```python
ADMIN_USERS = {
    "admin": "PedMajevica2026!",           # Glavni admin
    "radovan": "RadovanLozinka123!",       # Dodao sam Radovana
    "marko": "MarkoLozinka456!",           # Dodao sam Marka
}
```

**Ili dodaj potpuno nove:**

```python
ADMIN_USERS = {
    "admin": "MojaNovaSifra2026!",
    "nikola": "NikolaSifra789!",
    "ana": "AnaSigurnaSifra123!",
}
```

---

## 🔄 Deployment Proces

### 1. Commituj Promene

```bash
git add backend/create_admin_simple.py
git commit -m "Update admin users"
git push origin main
```

### 2. Deploy na Render

1. Idi na **Render Dashboard**: https://dashboard.render.com/
2. Otvori **Web Service**: `ped-majevica`
3. Klikni **"Manual Deploy"** → **"Deploy latest commit"**
4. Sačekaj 1-2 minuta

### 3. Proveri Logove

U **Render Dashboard** → **Logs**, trebao bi da vidiš:

```
🔐 Creating/updating admin user...
============================================================
🔐 PED MAJEVICA - MULTI-ADMIN KREACIJA
============================================================

📋 Obrađujem 3 korisnika...

   ✅ Korisnik 'admin' kreiran
   ✅ Korisnik 'radovan' kreiran
   ✅ Korisnik 'marko' kreiran

============================================================
📊 Rezultati: 3 uspešno, 0 neuspešno
============================================================

📋 ADMIN LOGIN KREDENCIJALI:
------------------------------------------------------------
   Username: admin          | Password: MojaNovaSifra2026!
   Username: radovan        | Password: RadovanLozinka123!
   Username: marko          | Password: MarkoLozinka456!
------------------------------------------------------------
```

---

## 🔑 Sigurnost Lozinki

### ✅ Dobra Lozinka:

- Minimum 12 karaktera
- Kombinacija velikih i malih slova
- Brojevi
- Specijalni karakteri (!@#$%^&*)

**Primeri:**
- `PedMajevica2026!`
- `RadovanSigurno123!`
- `MarkoAdmin$2026`

### ❌ Loša Lozinka:

- `admin` (prekratka)
- `12345678` (samo brojevi)
- `password` (očigledna)
- `admin123` (česta)

---

## 📝 Promena Postojeće Lozinke

### Opcija 1: Ažuriraj `create_admin_simple.py`

```python
ADMIN_USERS = {
    "admin": "NovaSifra2026!",  # Promenio sam lozinku
}
```

Commituj i deployuj ponovo - **lozinka će biti ažurirana**!

### Opcija 2: Kroz Admin Panel (Kada Bude Implementiran)

U budućnosti ćeš moći da menjaš lozinke direktno kroz admin panel.

---

## 🗑️ Brisanje Admin Korisnika

**Trenutno:** Ukloni korisnika iz `ADMIN_USERS` liste i deployuj. Korisnik **neće biti obrisan** iz baze, samo neće biti ažuriran.

**Za potpuno brisanje:** Moraš dodati u bazu i ručno obrisati (za sada nije implementirano).

---

## 🔗 Login URL

**Development:**
```
http://localhost:5000/pages/login.html
```

**Production:**
```
https://pedmajevica.org/pages/login.html
```

---

## 🛠️ Troubleshooting

### Problem: Korisnik ne može da se uloguje

**Proveri:**
1. Da li si deployovao najnoviju verziju?
2. Da li si proverio logove u Render Dashboard-u?
3. Da li si koristio tačnu lozinku (case-sensitive)?

**Rešenje:**
- Ažuriraj lozinku u `create_admin_simple.py`
- Commituj i deployuj ponovo
- Proveri logove da vidiš da li je korisnik kreiran

### Problem: "Greška pri kreiranju korisnika"

**Mogući uzroci:**
- Database connection problema
- Duplikat username (već postoji)

**Rešenje:**
- Proveri Render logove za detalje
- Promeni username na jedinstveno ime

---

## 📚 Primer: Dodavanje Novog Admina

### 1. Otvori `backend/create_admin_simple.py`

### 2. Dodaj novog korisnika:

**Pre:**
```python
ADMIN_USERS = {
    "admin": "PedMajevica2026!",
}
```

**Posle:**
```python
ADMIN_USERS = {
    "admin": "PedMajevica2026!",
    "nikola": "NikolaSifra123!",  # Novi admin
}
```

### 3. Commit i Deploy:

```bash
git add backend/create_admin_simple.py
git commit -m "Add admin user: nikola"
git push origin main
```

### 4. Render - Manual Deploy

Klikni "Deploy latest commit" u Render Dashboard-u.

### 5. Testiraj Login

Idi na `https://pedmajevica.org/pages/login.html`:
- Username: `nikola`
- Password: `NikolaSifra123!`

---

## 🔐 Najbolje Prakse

1. **Nikad ne commituj lozinke u production kod**
   - Koristi environment varijable (buduća implementacija)

2. **Koristi jake lozinke**
   - Minimum 12 karaktera
   - Mix karaktera

3. **Promeni default lozinke odmah**
   - Zameni `PedMajevica2026!` sa svojom

4. **Čuvaj kredencijale na sigurnom mestu**
   - Password manager (LastPass, 1Password, Bitwarden)

5. **Redovno menjaj lozinke**
   - Na svakih 3-6 meseci

---

## 📞 Pomoć

Ako naiđeš na probleme:
1. Proveri Render logove
2. Proveri da li je fajl commitovan
3. Proveri da li je deployment uspeo
4. Otvori GitHub issue sa detaljima

---

**Datum kreiranja**: 12. Januar 2026
**Autor**: Claude Sonnet 4.5
**Projekat**: PED Majevica 1988
