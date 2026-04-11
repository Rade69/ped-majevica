# AGENTS.md — PED Majevica 1988

**Čitaj zajedno s globalnim `~/.claude/AGENTS.md`.**
Ovaj dokument je specifičan za projekat **PED Majevica 1988** — web aplikacija planinarskog društva.

---

## 1. Stack

| Komponenta | Detalj |
|------------|--------|
| Backend | Python 3.x, Flask 3.0+ |
| ORM | Flask-SQLAlchemy + Flask-Migrate (Alembic) |
| Auth | Flask-Login + Flask-Bcrypt |
| Serijalizacija | Marshmallow schemas |
| Rate limiting | Flask-Limiter |
| CORS | Flask-CORS |
| Frontend | Vanilla JS, Tailwind CSS |
| DB (dev) | SQLite — `backend/instance/ped.db` |
| DB (prod) | PostgreSQL (Render.com) |
| Server | Gunicorn (produkcija) |

---

## 2. Arhitektura

### Backend — Application Factory + Blueprints

```
backend/
├── app/
│   ├── __init__.py      # create_app() factory
│   ├── config.py        # Config klasa (env varijable)
│   ├── extensions.py    # db, login_manager, bcrypt, migrate...
│   ├── models/          # SQLAlchemy modeli
│   ├── routes/          # Flask Blueprinti
│   ├── schemas/         # Marshmallow schemas (serijalizacija)
│   ├── services/        # Business logika
│   └── utils/           # Helperi (csrf, cache, decorators...)
├── migrations/          # Alembic migracije
├── scripts/             # Admin/import skripte
└── run.py               # Dev server
```

### Modeli

| Model | Fajl |
|-------|------|
| User (auth, RBAC) | `models/user.py` |
| Post (blog) | `models/post.py` |
| Event | `models/event.py` |
| Trail | `models/trail.py` |
| Gallery | `models/gallery.py` |
| Like | `models/like.py` |
| PlanAktivnosti | `models/plan_aktivnosti.py` |

### Blueprinti (routes/)

`admin`, `api`, `auth`, `events`, `frontend`, `gallery`, `posts`, `trails`, `plan_aktivnosti`

### Frontend

```
frontend/
├── js/          # Vanilla JS moduli
├── pages/       # HTML stranice
└── assets/      # Slike, fontovi
```

---

## 3. Pravila za backend

### Migracije — uvijek koristiti Flask-Migrate
```bash
# Nova migracija nakon promjene modela
flask db migrate -m "opis promjene"
flask db upgrade
```
**Nikad direktno mijenjati SQLite fajl ili pisati vlastite ALTER TABLE.**

### Schemas — uvijek za API response
```python
# ✅ Serijalizovati kroz Marshmallow schema
from app.schemas.post import PostSchema
return PostSchema().dump(post)

# ❌ Direktno vraćati model objekt ili vlastiti dict
return {"id": post.id, "title": post.title}  # Ne!
```

### RBAC — koristiti postojeće dekoratore
```python
from app.utils.decorators import admin_required, member_required

@bp.route('/admin/something')
@admin_required
def admin_view():
    ...
```

### Env varijable — nikad hardkodovati
Sve osjetljive vrijednosti idu u `.env`:
- `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`
- `.env` je u `.gitignore` — ne commitovati

---

## 4. Pravila za frontend

- Vanilla JS — **bez React, Vue ili sličnih frameworka**
- Tailwind CSS za stilove — ne pisati custom CSS gdje Tailwind može
- Modularni JS fajlovi u `frontend/js/` — jedan fajl po funkcionalnosti
- API pozivi idu kroz `frontend/js/api.js`

---

## 5. Zabrane specifične za ovaj projekat

| Zabrana | Razlog |
|---------|--------|
| Direktno mijenjati DB shemu bez migracije | Lomi produkcijsku bazu |
| Dodavati npm pakete bez dogovora | Frontend je namjerno vanilla |
| Pisati raw SQL bez SQLAlchemy ORM | Nije konzistentno s ostatkom koda |
| Commitovati `.env` ili `instance/ped.db` | Sigurnosni rizik |
| Mijenjati `config.py` produkcijske vrijednosti | Utječe na Render.com deploy |

---

## 6. Pokretanje lokalno

```bash
cd backend
source .venv/bin/activate   # ili: python -m venv .venv && pip install -r requirements.txt
flask db upgrade             # primijeni migracije
python run.py                # dev server na http://localhost:5000
```

---

*Ovaj fajl kreira i održava Claude Sonnet kao nadzorni agent.*
