# ⚡ Quick Reference - VPS Commands

Brze komande za svakodnevne operacije na VPS-u.

---

## 🔗 Konekcija

```bash
# SSH na VPS
ssh root@TVOJ_VPS_IP

# Ili sa domenom (nakon DNS setup-a)
ssh root@pedmajevica.org
```

---

## 📊 Status Provjera

```bash
# Flask aplikacija
sudo systemctl status pedmajevica

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql

# Firewall
sudo ufw status
```

---

## 🔄 Restart Servisa

```bash
# Flask app
sudo systemctl restart pedmajevica

# Nginx
sudo systemctl restart nginx

# PostgreSQL
sudo systemctl restart postgresql

# SVE
sudo systemctl restart pedmajevica nginx
```

---

## 📝 Logovi

```bash
# Flask error log
sudo tail -f /var/log/pedmajevica/error.log

# Flask access log
sudo tail -f /var/log/pedmajevica/access.log

# Nginx error log
sudo tail -f /var/log/nginx/pedmajevica-error.log

# Nginx access log
sudo tail -f /var/log/nginx/pedmajevica-access.log

# Systemd logs (zadnjih 50 linija)
sudo journalctl -u pedmajevica -n 50

# Live systemd logs
sudo journalctl -u pedmajevica -f
```

---

## 🚀 Deployment (Update Sajta)

```bash
cd /var/www/pedmajevica
sudo bash /root/deploy.sh
```

**Ili manuelno:**
```bash
cd /var/www/pedmajevica
git pull origin master
source venv/bin/activate
cd backend
pip install -r requirements.txt --upgrade
flask db upgrade
cd ..
npm run build
sudo systemctl restart pedmajevica
```

---

## 💾 Backup

```bash
# Manuelni backup
sudo bash /root/backup.sh

# Proveri backups
ls -lh /var/backups/pedmajevica/

# Restore backup
sudo -u postgres psql -d ped_majevica < /var/backups/pedmajevica/db_YYYY-MM-DD_HH-MM-SS.sql
```

---

## 🗄️ Database

```bash
# Konektuj se na PostgreSQL
sudo -u postgres psql -d ped_majevica

# Osnovne komande (unutar psql):
\dt              # List tables
\d users         # Describe users table
SELECT * FROM users;
\q               # Quit
```

---

## 🔒 SSL

```bash
# Proveri SSL certifikat
sudo certbot certificates

# Manuelni renewal
sudo certbot renew

# Test renewal (dry-run)
sudo certbot renew --dry-run
```

---

## 🔧 Permissions Fix

```bash
# Ako ima problema sa permissions
sudo chown -R www-data:www-data /var/www/pedmajevica
sudo chmod -R 755 /var/www/pedmajevica
sudo chmod 660 /var/www/pedmajevica/backend/.env
```

---

## 📈 Resource Usage

```bash
# CPU i RAM (interactive)
htop

# Disk space
df -h

# Folder sizes
du -sh /var/www/pedmajevica/*

# Memory usage
free -h

# Network connections
sudo netstat -tulpn | grep -E '(80|443|5432)'
```

---

## 🧹 Cleanup

```bash
# Ukloni stare logove (starije od 30 dana)
find /var/log/pedmajevica/ -name "*.log" -mtime +30 -delete

# Ukloni stare backups (starije od 30 dana)
find /var/backups/pedmajevica/ -name "*.sql.gz" -mtime +30 -delete

# APT cleanup
sudo apt autoremove
sudo apt autoclean
```

---

## 🔐 Security

```bash
# Proveri firewall rules
sudo ufw status verbose

# Proveri fail2ban
sudo fail2ban-client status
sudo fail2ban-client status sshd

# Proveri SSH logove
sudo tail -f /var/log/auth.log
```

---

## ⚙️ Config Files Lokacije

```
/var/www/pedmajevica/backend/.env           → Flask env variables
/etc/systemd/system/pedmajevica.service     → Systemd service
/etc/nginx/sites-available/pedmajevica      → Nginx config
/var/www/pedmajevica/backend/wsgi.py        → Flask entry point
```

---

## 🆘 Emergency Restart

```bash
# Ako sve ode u kvasac
sudo systemctl stop pedmajevica
sudo systemctl stop nginx
sudo systemctl start postgresql
sudo systemctl start pedmajevica
sudo systemctl start nginx

# Proveri da radi
curl -I https://pedmajevica.org
```

---

## 📞 Korisne Komande

```bash
# Koji proces koristi port 80?
sudo lsof -i :80

# Koliko Flask app koristi RAM-a?
ps aux | grep gunicorn

# Poslednji reboot
uptime

# System info
hostnamectl
```

---

Made with ❤️ for PED Majevica 1988 🏔️
