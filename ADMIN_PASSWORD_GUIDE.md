# Admin Password Management Guide

## Overview

PED Majevica aplikacija ima **samo admin korisnike** (4 osobe) koji uređuju sadržaj preko admin panela. Obični korisnici se ne loguju na stranicu.

**Admin korisnici:**
- `radovan`
- `aleksandar`
- `srecko`
- `milojko`

## Setup Admin Passwords

### 1. Initial Setup (First Deployment)

Admin korisnici se automatski kreiraju prilikom pokretanja aplikacije **ako su postavljene environment varijable**.

**Environment varijable (Render.com / .env file):**
```
ADMIN_RADOVAN_PASSWORD=strong-password-here
ADMIN_ALEKSANDAR_PASSWORD=strong-password-here
ADMIN_SRECKO_PASSWORD=strong-password-here
ADMIN_MILOJKO_PASSWORD=strong-password-here
```

**Password requirements:**
- Minimum 8 karaktera (preporučeno 12+)
- Miješana slova (velika/mala), brojevi, simboli
- Različite lozinke za svakog admina

### 2. Reset Lost Password

Ako admin zaboravi lozinku, postoje **dva načina za reset**:

#### Option A: CLI Command (Recommended)

```bash
# SSH into server or use Render.com dashboard terminal
cd backend

# Interaktivni reset
flask reset-admin-password

# Ili direktno
flask reset-admin-password --username radovan --new-password nova-lozinka
```

**Interaktivni mod:**
1. Prikazuje sve admin korisnike
2. Pita za username
3. Nudi automatsku generaciju sigurne lozinke
4. Prikazuje novu lozinku (samo jednom!)

#### Option B: Password Reset Token (via Web)

1. Idite na `/pages/forgot-password.html`
2. Unesite admin email
3. **Token će biti logovan** (ne poslat emailom)
4. Kontaktirajte developera za token iz logova
5. Idite na `/pages/reset-password.html?token=TOKEN_HERE`

**Napomena:** Web password reset **ne šalje email** jer je aplikacija samo za admine. Token se loguje u server logove.

### 3. List Admin Users

```bash
flask list-admins
```

Prikazuje sve admin korisnike sa informacijama:
- Username i email
- Datum kreiranja
- Zadnja prijava
- Status (aktivan/neaktivan)

## Security Notes

### 1. Environment Variables
- **NEVER** hardcode passwords in code
- Use environment variables in production
- Rotate passwords periodically (every 6 months)

### 2. Access Control
- Only 4 admin accounts exist
- Each admin should have unique password
- Passwords should not be shared

### 3. Backup & Recovery
- Database is automatically backed up on Render.com
- Admin passwords can be reset via CLI
- Keep password recovery instructions accessible

## Troubleshooting

### Problem: Admin users not created
**Solution:**
1. Check environment variables are set
2. Restart application
3. Check logs for errors

### Problem: Cannot login to admin panel
**Solution:**
1. Reset password via CLI
2. Verify username is correct (lowercase)
3. Check if user is active (`is_active = True`)

### Problem: Password reset token not working
**Solution:**
1. Tokens expire after 1 hour
2. Use CLI command instead
3. Check server logs for token generation

### Problem: CLI command not available
**Solution:**
1. Ensure you're in `backend` directory
2. Flask app must be properly configured
3. Check `flask --help` for available commands

## Emergency Procedures

### Complete Password Loss
If all admin passwords are lost:

1. **Access server** via SSH/Render dashboard
2. **Reset each admin**:
   ```bash
   flask reset-admin-password --username radovan
   flask reset-admin-password --username aleksandar
   flask reset-admin-password --username srecko
   flask reset-admin-password --username milojko
   ```
3. **Distribute new passwords** securely

### Database Corruption
If admin users are deleted:

1. **Set environment variables** with new passwords
2. **Restart application** - auto-creates missing admins
3. **Or manually create** via CLI or database

---

## Quick Reference

| Task | Command |
|------|---------|
| Reset admin password | `flask reset-admin-password --username USERNAME` |
| List all admins | `flask list-admins` |
| Migrate blog posts | `flask migrate-json` |
| Database migrations | `flask db upgrade` |

---

*Last updated: April 2026*