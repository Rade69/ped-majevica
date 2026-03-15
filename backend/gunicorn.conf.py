# ========================================
# Gunicorn Configuration for PED Majevica
# ========================================
# Production WSGI Server Settings
#
# Usage:
#   gunicorn -c gunicorn.conf.py wsgi:app
#
# ========================================

# -----------------------------
# Server Binding
# -----------------------------
bind = "127.0.0.1:8000"  # Bind to localhost only (Nginx will proxy)

# -----------------------------
# Workers
# -----------------------------
# Formula: workers = (2 x CPU) + 1
# For CPX11 (2 vCPU): 2-3 workers
# For CPX21 (4 vCPU): 5-7 workers
workers = 2
worker_class = "sync"
threads = 2

# -----------------------------
# Timeouts
# -----------------------------
timeout = 120          # Maximum request timeout (seconds)
keepalive = 5          # Keep-alive connections (seconds)
graceful_timeout = 30  # Graceful shutdown timeout

# -----------------------------
# Logging
# -----------------------------
# Log files location (create directory first!)
# mkdir -p /var/log/pedmajevica
errorlog = "/var/log/pedmajevica/gunicorn-error.log"
accesslog = "/var/log/pedmajevica/gunicorn-access.log"
loglevel = "info"
capture_output = True

# Log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# -----------------------------
# Process Naming
# -----------------------------
proc_name = "pedmajevica"
pythonpath = "/var/www/ped-majevica/backend"

# -----------------------------
# Security
# -----------------------------
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# -----------------------------
# Server Mechanics
# -----------------------------
daemon = False  # Run in foreground (systemd will manage)
pidfile = "/var/log/pedmajevica/gunicorn.pid"
umask = 0o002  # File permissions

# Run as specific user/group (set in systemd instead)
# user = "pedadmin"
# group = "pedadmin"

# -----------------------------
# SSL (Optional - Nginx handles SSL)
# -----------------------------
# keyfile = None
# certfile = None

# -----------------------------
# Server Hooks (Optional)
# -----------------------------
def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 50)
    print("PED Majevica 1988 - Starting Gunicorn")
    print("=" * 50)

def on_reload(server):
    """Called to recycle workers during SIGHUP."""
    print("PED Majevica: Reloading...")

def worker_int(worker):
    """Called when a worker receives SIGINT/SIGTERM."""
    print(f"PED Majevica: Worker {worker.pid} received interrupt signal")

def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    print(f"PED Majevica: Worker {worker.pid} received abort signal")

# -----------------------------
# Preload (Optional - saves memory)
# -----------------------------
# preload_app = True

# -----------------------------
# For use with systemd (recommended)
# -----------------------------
# Set in systemd service file instead:
# User=pedadmin
# Group=pedadmin
# WorkingDirectory=/var/www/ped-majevica/backend
# Environment=PATH=/var/www/ped-majevica/backend/venv/bin
