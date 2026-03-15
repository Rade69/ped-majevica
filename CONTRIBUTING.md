# Contributing to PED Majevica 1988

Thank you for your interest in contributing to PED Majevica 1988!

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis (optional, for caching)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
flask db upgrade

# Start development server
flask run
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Project Structure

```
ped-majevica-main/
├── backend/           # Flask API
│   ├── app/
│   │   ├── models/   # Database models
│   │   ├── routes/   # API endpoints
│   │   ├── schemas/  # Marshmallow schemas
│   │   ├── services/ # Business logic
│   │   └── utils/    # Utilities
│   └── migrations/   # Alembic migrations
│
├── frontend/          # Static frontend
│   ├── js/          # JavaScript files
│   ├── css/         # Stylesheets
│   └── pages/       # HTML pages
│
└── docs/            # Documentation
```

## Coding Standards

### Python
- Follow PEP 8
- Use type hints where possible
- Write docstrings for all public functions
- Maximum line length: 100 characters

### JavaScript
- Use ES6+ features
- Use JSDoc comments
- Follow existing code style

### Git
- Create feature branches from `develop`
- Use meaningful commit messages
- Submit PRs to `develop` branch

## Testing

```bash
# Backend tests
cd backend
pytest -v

# Frontend linting
cd frontend
npm run lint
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Questions?

Contact: info@pedmajevica.org
