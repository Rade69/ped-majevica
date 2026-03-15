# 🧪 PED Majevica 1988 - Test Suite

Kompletan test suite za PED Majevica web aplikaciju.

## 📋 Sadržaj

- [Instalacija](#instalacija)
- [Pokretanje testova](#pokretanje-testova)
- [Struktura testova](#struktura-testova)
- [Coverage](#coverage)
- [CI/CD Integration](#cicd-integration)

## 📦 Instalacija

### 1. Kreiraj virtualno okruženje

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ili
venv\Scripts\activate  # Windows
```

### 2. Instaliraj dependency-je

```bash
# Production dependency-ji
pip install -r requirements.txt

# Test dependency-ji (uključuje production)
pip install -r requirements-dev.txt
```

## 🚀 Pokretanje Testova

### Osnovne komande

```bash
# Pokreni sve testove
./run_tests.sh

# Pokreni sve testove sa coverage report-om
./run_tests.sh coverage

# Pokreni testove sa verbose output-om
./run_tests.sh verbose

# Pokreni samo brze testove
./run_tests.sh quick
```

### Pokretanje specifičnih testova

```bash
# API testovi
./run_tests.sh api

# Frontend testovi
./run_tests.sh frontend

# Authentication testovi
./run_tests.sh auth

# Admin panel testovi
./run_tests.sh admin

# Production testovi
./run_tests.sh production
```

### Direktno sa pytest

```bash
# Svi testovi
pytest

# Specifičan fajl
pytest tests/test_routes.py -v

# Specifična kategorija
pytest -m api

# Sa coverage-om
pytest --cov=app --cov-report=html

# Parallel execution
pytest -n auto
```

## 📁 Struktura Testova

```
backend/tests/
├── conftest.py           # Zajednički fixture-ovi i konfiguracija
├── test_routes.py        # Frontend rute testovi
├── test_api.py           # API endpoint testovi
├── test_auth.py          # Login/Logout testovi (osnovni)
├── test_auth_extended.py # Prošireni auth testovi
├── test_admin.py         # Admin panel testovi
├── test_posts.py         # Posts CRUD testovi
└── test_production.py    # Production/Integration testovi
```

### Kategorije testova

| Fajl | Opis | Broj testova |
|------|------|--------------|
| `test_routes.py` | Frontend rute, navigacija, static files | ~25 |
| `test_api.py` | Gallery, Events, Trails, Posts API | ~40 |
| `test_auth.py` | Login, Logout, Session | ~10 |
| `test_auth_extended.py` | Rate limiting, Roles, Security | ~25 |
| `test_admin.py` | Admin dashboard, CRUD operacije | ~30 |
| `test_posts.py` | Posts specifični testovi | ~5 |
| `test_production.py` | Health checks, Performance, Security | ~30 |

**Ukupno: ~165 testova**

## 📊 Coverage

### Generisanje coverage report-a

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report
pytest --cov=app --cov-report=html

# Open HTML report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage ciljevi

| Tip | Minimum | Target |
|-----|---------|--------|
| Lines | 70% | 85% |
| Functions | 60% | 80% |
| Classes | 50% | 75% |

## 🔧 CI/CD Integration

### GitHub Actions

Kreiraj `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

### GitLab CI

Kreiraj `.gitlab-ci.yml`:

```yaml
stages:
  - test

test:
  stage: test
  image: python:3.10
  script:
    - cd backend
    - pip install -r requirements-dev.txt
    - pytest --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml
```

## 🏷️ Markeri

Koristi markere za kategorizaciju testova:

```python
@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.api
def test_api_endpoint():
    pass
```

### Pokretanje po markerima

```bash
# Samo brzi testovi
pytest -m "not slow"

# Samo integration testovi
pytest -m integration

# Samo API testovi
pytest -m api
```

## 🐛 Debugging

### Verbose output

```bash
pytest -v -s
```

### Stop on first failure

```bash
pytest -x
```

### Show local variables on failure

```bash
pytest -l
```

### Run specific test

```bash
pytest tests/test_api.py::TestGalleryAPI::test_get_gallery_list -v
```

## 📝 Best Practices

### 1. Nazivi testova

```python
# DOBRO
def test_login_with_valid_credentials():
def test_admin_cannot_access_without_auth():

# LOŠE
def test_login():
def test_admin():
```

### 2. Koristi fixture-ove

```python
# DOBRO
def test_create_post(client, sample_post):
    pass

# LOŠE
def test_create_post():
    app = create_app()
    client = app.test_client()
    # ... puno boilerplate koda
```

### 3. Assert poruke

```python
# DOBRO
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# DOBRO (sa pytest)
assert 200 == response.status_code
```

### 4. Test isolation

```python
# Svaki test treba da bude nezavisan
def test_create_user():
    # Kreiraj user za ovaj test
    
def test_delete_user():
    # Kreiraj drugog usera za ovaj test
```

## 🔍 Troubleshooting

### Problem: Testovi ne prolaze

```bash
# Proveri da li su dependency-ji instalirani
pip install -r requirements-dev.txt

# Proveri da li je baza čista
pytest --cache-clear

# Pokreni sa više informacija
pytest -vvv -s
```

### Problem: Coverage je nizak

```bash
# Proveri koje linije nisu pokrivene
pytest --cov=app --cov-report=term-missing

# Fokusiraj se na kritične delove
pytest tests/test_api.py --cov=app/routes
```

### Problem: Testovi su spori

```bash
# Pronađi najsporije testove
pytest --durations=10

# Preskoči spore testove
pytest -m "not slow"
```

## 📧 Kontakt

Za pitanja o testovima:
- Email: radovan1969@gmail.com
- GitHub Issues: [ped-majevica/issues](https://github.com/ped-majevica/issues)

---

**Napomena:** Testovi koriste SQLite in-memory bazu za brzinu. Za production testiranje koristi pravu bazu podataka.
