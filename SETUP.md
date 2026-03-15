# 🚀 Setup Instructions - PED Majevica 1988

## Prerequisites

Before you begin, ensure you have installed:

| Tool       | Version | Download                                      |
| ---------- | ------- | --------------------------------------------- |
| Python     | 3.11+   | [python.org](https://www.python.org/)         |
| Node.js    | 20+     | [nodejs.org](https://nodejs.org/)             |
| PostgreSQL | 15+     | [postgresql.org](https://www.postgresql.org/) |
| Git        | Latest  | [git-scm.com](https://git-scm.com/)           |

### Optional
- **Redis** - For caching (recommended for production)
- **Docker** - For containerized deployment

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/ped-majevica-main.git
cd ped-majevica-main
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:

```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_APP=run.py

# Database
DATABASE_URL=postgresql://user:password@localhost/pedmajevica

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Email (optional, for verification)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 4. Database Setup

```bash
# Initialize database
flask db init

# Run migrations
flask db migrate -m "Initial migration"
flask db upgrade

# (Optional) Seed with sample data
flask seed
```

### 5. Create Admin User

```bash
# Create admin via command
flask create-admin --username admin --email admin@example.com --password your-password
```

### 6. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

---

## Running the Application

### Development

**Backend:**
```bash
cd backend
flask run
# Runs on http://localhost:5000
```

**Frontend (with hot reload):**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Production

**Using Gunicorn:**
```bash
cd backend
gunicorn -c deployment/configs/gunicorn.conf.py run:app
```

**Using Docker:**
```bash
docker-compose up -d
```

---

## Common Issues

### Database Connection Error

Make sure PostgreSQL is running:
```bash
# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

### Port Already in Use

Find and kill the process:
```bash
lsof -i :5000
kill -9 <PID>
```

### Module Not Found

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### CSS/JS Not Loading

Clear browser cache or run:
```bash
npm run build
```

---

## Testing

```bash
# Backend tests
cd backend
pytest -v --cov

# Frontend linting
cd frontend
npm run lint
```

---

## Project Structure

```
ped-majevica-main/
├── backend/              # Flask API
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routes/      # API endpoints
│   │   ├── schemas/     # Marshmallow schemas
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── migrations/      # Alembic migrations
│   └── tests/           # Unit & integration tests
│
├── frontend/             # Static frontend
│   ├── js/             # JavaScript modules
│   ├── css/            # Stylesheets
│   └── pages/          # HTML pages
│
├── deployment/          # Deployment configs
└── docs/               # Documentation
```

---

## Next Steps

1. ✅ Set up the development environment
2. 🔲 Review API documentation at `/api/docs`
3. 🔲 Configure email settings
4. 🔲 Set up production deployment
5. 🔲 Enable Redis caching

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Last updated: Mart 2026*
