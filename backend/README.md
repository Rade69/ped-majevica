# 🔧 Backend - Flask API

Flask backend za PED Majevica web aplikaciju.

---

## 🚀 Quick Start

### **Development (lokalno)**

```bash
# 1. Kreiraj virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ili
venv\Scripts\activate  # Windows

# 2. Instaliraj dependencies
pip install -r requirements.txt

# 3. Kopiraj environment varijable
cp .env.example .env

# 4. Inicijalizuj bazu (SQLite)
flask db upgrade

# 5. Importuj test podatke (opciono)
python migrate_json_to_db.py

# 6. Pokreni development server
python run.py
```

Backend će biti dostupan na: `http://127.0.0.1:5000`

---

## 🗄️ Database

### **Development: SQLite**
- Automatski se kreira u `instance/ped.db`
- Ne treba instalacija
- Odlično za development

### **Production: PostgreSQL**
- Postavlja se automatski na Render.com
- Definiše se preko `DATABASE_URL` environment varijable

---

## 🔑 Environment Variables

Kopiraj `.env.example` u `.env` i ažuriraj vrednosti:

```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key-min-32-characters
DATABASE_URL=sqlite:///instance/ped.db  # ili PostgreSQL URL
LOG_LEVEL=INFO
```

---

## 📊 Database Migrations

```bash
# Kreiranje nove migracije
flask db migrate -m "Description of changes"

# Primena migracija
flask db upgrade

# Rollback na prethodnu verziju
flask db downgrade
```

---

## 🧪 Testing

```bash
# Pokreni sve testove
pytest

# Test sa coverage
pytest --cov=app tests/
```

---

## 🏗️ Struktura Projekta

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Konfiguracija
│   ├── extensions.py        # Flask extensions
│   ├── commands.py          # CLI komande
│   ├── models/              # Database modeli
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── trail.py
│   │   └── event.py
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── posts.py
│   │   ├── trails.py
│   │   └── events.py
│   └── services/            # Business logic
│       ├── user_service.py
│       └── post_service.py
├── migrations/              # Database migrations
├── instance/                # SQLite database (gitignored)
├── run.py                   # Development entry point
├── wsgi.py                  # Production entry point
├── requirements.txt         # Python dependencies
└── .env.example             # Environment template
```

---

## 🔐 Admin Panel

Default admin nalog se kreira automatski:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **VAŽNO:** Promeni password u produkciji!

---

## 📦 Production Deployment

Vidi [DEPLOYMENT.md](../DEPLOYMENT.md) u root direktorijumu.

**TL;DR:**
```bash
# Production se koristi sa Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
```

---

## 🛠️ Tech Stack

- **Flask 3.0** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Flask-Migrate** - Database migrations
- **Flask-Bcrypt** - Password hashing
- **Gunicorn** - WSGI server (production)
- **PostgreSQL** - Database (production)
- **SQLite** - Database (development)

---

## 📝 API Endpoints

### **Authentication**
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### **Posts (Članci)**
- `GET /api/posts` - List all posts
- `GET /api/posts/<id>` - Get single post
- `POST /api/posts` - Create post (admin)
- `PUT /api/posts/<id>` - Update post (admin)
- `DELETE /api/posts/<id>` - Delete post (admin)

### **Trails (Staze)**
- `GET /api/trails` - List all trails
- `POST /api/trails` - Create trail (admin)
- `PUT /api/trails/<id>` - Update trail (admin)
- `DELETE /api/trails/<id>` - Delete trail (admin)

### **Events (Događaji)**
- `GET /api/events` - List all events
- `POST /api/events` - Create event (admin)
- `PUT /api/events/<id>` - Update event (admin)
- `DELETE /api/events/<id>` - Delete event (admin)

---

Made with ❤️ for PED Majevica 1988 🏔️
