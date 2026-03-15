"""
Migracija: Dodavanje polja za modal staze
- features (JSON) - lista karakteristika
- equipment (JSON) - lista potrebne opreme
- warning (TEXT) - upozorenje
- contact (VARCHAR) - kontakt telefon

Pokreni sa: python -c "from migrations.add_trail_modal_fields import upgrade; upgrade()"
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def upgrade():
    app = create_app()
    with app.app_context():
        # Dodaj nova polja u trail tabelu
        with db.engine.connect() as conn:
            # Provjeri da li kolone već postoje
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'trail' AND column_name IN ('features', 'equipment', 'warning', 'contact')
            """))
            existing_columns = [row[0] for row in result]

            if 'features' not in existing_columns:
                conn.execute(text("ALTER TABLE trail ADD COLUMN features JSON"))
                print("✅ Dodana kolona: features")
            else:
                print("ℹ️ Kolona features već postoji")

            if 'equipment' not in existing_columns:
                conn.execute(text("ALTER TABLE trail ADD COLUMN equipment JSON"))
                print("✅ Dodana kolona: equipment")
            else:
                print("ℹ️ Kolona equipment već postoji")

            if 'warning' not in existing_columns:
                conn.execute(text("ALTER TABLE trail ADD COLUMN warning TEXT"))
                print("✅ Dodana kolona: warning")
            else:
                print("ℹ️ Kolona warning već postoji")

            if 'contact' not in existing_columns:
                conn.execute(text("ALTER TABLE trail ADD COLUMN contact VARCHAR(100)"))
                print("✅ Dodana kolona: contact")
            else:
                print("ℹ️ Kolona contact već postoji")

            conn.commit()

        print("\n✅ Migracija završena!")

def downgrade():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE trail DROP COLUMN IF EXISTS features"))
            conn.execute(text("ALTER TABLE trail DROP COLUMN IF EXISTS equipment"))
            conn.execute(text("ALTER TABLE trail DROP COLUMN IF EXISTS warning"))
            conn.execute(text("ALTER TABLE trail DROP COLUMN IF EXISTS contact"))
            conn.commit()
        print("✅ Kolone uklonjene")

if __name__ == "__main__":
    upgrade()
