# 🔄 Git Repository - Uputstvo

Git repository je kreiran i spreman za push na GitHub/GitLab!

---

## ✅ ŠTA JE URADENO

- [x] Git repository inicijalizovan
- [x] .gitignore konfigurisan
- [x] Prvi commit napravljen
- [x] 176 fajlova commit-ovano
- [x] Git user konfigurisan (Radovan Stojanović)

---

## 📊 GIT STATUS

```
Branch: master
Commit: da833c1
Files: 176
Status: Clean (ništa za commit)
```

---

## 🚀 PUSH NA GITHUB

### 1. Kreiraj Repository na GitHub-u

**Opcija A: Preko Web Browser-a**

1. Otvori https://github.com/new
2. Repository name: `ped-majevica`
3. Description: "PED Majevica 1988 - Planinarsko Društvo Web Application"
4. **Public** ili **Private** (preporuka: Private za production)
5. **NE klikći** "Add README" ili ".gitignore"
6. Klikni "Create repository"

**Opcija B: Preko GitHub CLI**

```bash
# Instaliraj GitHub CLI (ako nemaš)
sudo dnf install gh

# Login
gh auth login

# Kreiraj repository
gh repo create ped-majevica --private --source=. --remote=origin
```

### 2. Push-uj na GitHub

Nakon što kreiraš repository, GitHub će ti pokazati komande.

**Komande za push:**

```bash
cd /home/radovan/Downloads/ped-majevica-main

# Dodaj remote (zamjeni <TVOJ_USERNAME> sa tvojim GitHub username-om)
git remote add origin https://github.com/<TVOJ_USERNAME>/ped-majevica.git

# Ili preko SSH (preporuka!)
git remote add origin git@github.com:<TVOJ_USERNAME>/ped-majevica.git

# Promjeni master u main (opciono, ali preporučeno)
git branch -M main

# Push-uj na GitHub
git push -u origin main
```

### 3. Verifikuj Push

Otvori svoj browser i idi na:
```
https://github.com/<TVOJ_USERNAME>/ped-majevica
```

Trebaš vidjeti sve fajlove!

---

## 🔐 SSH KLJUČEVI ZA GITHUB (Preporuka)

### 1. Generiši SSH Key (ako nemaš)

```bash
ssh-keygen -t ed25519 -C "radovan1969@gmail.com"
# Ili za starije sisteme:
# ssh-keygen -t rsa -b 4096 -C "radovan1969@gmail.com"
```

### 2. Dodaj SSH Key na GitHub

1. Kopiraj javni ključ:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Ili: cat ~/.ssh/id_rsa.pub
   ```

2. Otvori https://github.com/settings/keys

3. Klikni "New SSH key"

4. Zalijepi ključ i sačuvaj

### 3. Testiraj Konekciju

```bash
ssh -T git@github.com
# Trebaš vidjeti: "Hi username! You've successfully authenticated"
```

---

## 🔄 PUSH NA GITLAB

### 1. Kreiraj Repository na GitLab-u

1. Otvori https://gitlab.com/projects/new
2. Project name: `ped-majevica`
3. Visibility: **Private**
4. Kreiraj

### 2. Push-uj na GitLab

```bash
cd /home/radovan/Downloads/ped-majevica-main

# Dodaj remote
git remote add origin https://gitlab.com/<TVOJ_USERNAME>/ped-majevica.git

# Ili preko SSH
git remote add origin git@gitlab.com:<TVOJ_USERNAME>/ped-majevica.git

# Promjeni branch
git branch -M main

# Push
git push -u origin main
```

---

## 📝 GIT WORKFLOW

### Svaki put kad praviš izmjene:

```bash
# 1. Provjeri šta je izmijenjeno
git status

# 2. Dodaj fajlove
git add .
# Ili specifične fajlove:
# git add backend/app/routes/frontend.py

# 3. Commit-uj
git commit -m "Opis izmjena (šta si radio/la)"

# 4. Push-uj na GitHub
git push origin main
```

### Primjeri Dobrih Commit Poruka:

```bash
# Dobro:
git commit -m "Dodana galerija slika"
git commit -m "Popravljen login bug"
git commit -m "Ažurirana dokumentacija za deploy"

# Loše:
git commit -m "fix"
git commit -m "update"
git commit -m "asdfasdf"
```

---

## 🛡️ .GITIGNORE - Šta Se NE Commit-uje

Ovi fajlovi su automatski ignorisani:

```
✅ .env (environment varijable - sadrže lozinke!)
✅ venv/ (Python virtual environment)
✅ node_modules/ (Node.js dependencies)
✅ instance/*.db (SQLite baze)
✅ .pytest_cache/ (Test cache)
✅ uploads/ (User upload-ovane slike)
✅ *.log (Log fajlovi)
✅ .vscode/, .idea/ (IDE postavke)
```

**NIKAD ne commit-uj:**
- ❌ .env fajlove (sadrže lozinke!)
- ❌ Baze podataka sa stvarnim podacima
- ❌ Upload-ovane slike od korisnika
- ❌ Log fajlove sa osjetljivim informacijama

---

## 📊 GIT ALIJASI (Opciono - Ubrzava Rad)

```bash
# Dodaj korisne alijase
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.la "log --oneline --all"

# Sada možeš koristiti:
git st      # Umjesto git status
git co        # Umjesto git checkout
git br        # Umjesto git branch
git ci        # Umjesto git commit
git la        # Pregled svih commit-ova
```

---

## 🔄 DEPLOY SA GITHUB-A (CI/CD)

### GitHub Actions (Opciono)

Kreiraj `.github/workflows/deploy.yml` za automatski deploy:

```yaml
name: Deploy to VPS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_IP }}
          username: pedadmin
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /var/www/ped-majevica
            git pull origin main
            cd backend
            source venv/bin/activate
            pip install -r requirements.txt
            flask db upgrade
            sudo systemctl restart pedmajevica
```

---

## 📞 KORISNI LINKOVI

- GitHub Docs: https://docs.github.com/
- Git Book: https://git-scm.com/book/en/v2
- GitHub CLI: https://cli.github.com/
- Learn Git Branching: https://learngitbranching.js.org/

---

## 🎯 SLJEDECI KORACI

1. **Kreiraj repository na GitHub-u** (5 min)
2. **Dodaj remote i push-uj** (2 min)
3. **Verifikuj na GitHub-u** (1 min)
4. **Opcionalno:** Konfiguriši CI/CD za auto-deploy

---

**Git Repository Status:** ✅ SPREMAN ZA PUSH  
**Commit-ova:** 1  
**Fajlova:** 176  
**Vrijeme do GitHub-a:** ~10 minuta
