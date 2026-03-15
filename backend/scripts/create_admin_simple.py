"""
Multi-Admin User Creator for Render.com
========================================
Kreiraj više admin korisnika sa različitim lozinkama.
"""

from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User

# ============================================
# DODAJ/PROMENI ADMIN KORISNIKE OVDE
# ============================================
# Format: {"username": "password"}
ADMIN_USERS = {
    "radovan": "radovan-!sofija#22$jelena%25&",      # Radovan - glavni admin
    "aleksandar": "Aleksandar$2026!Ped#Majevica",    # Aleksandar admin
    "srecko": "Srecko#PedMajevica!2026$",            # Srećko admin
    "milojko": "Milojko&Majevica2026!Strong#",       # Milojko admin
}
# ============================================

def create_or_update_user(username, password):
    """
    Kreira ili ažurira jednog korisnika.

    Args:
        username (str): Korisničko ime
        password (str): Lozinka (biće hashirana)

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Proveri da li korisnik već postoji
        user = User.query.filter_by(username=username).first()

        if user:
            # Ažuriraj postojećeg
            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            return (True, f"✅ Korisnik '{username}' ažuriran (lozinka promenjena)")
        else:
            # Kreiraj novog
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(
                username=username,
                password_hash=password_hash,
                role='admin'
            )
            db.session.add(new_user)
            db.session.commit()
            return (True, f"✅ Korisnik '{username}' kreiran")

    except Exception as e:
        db.session.rollback()
        return (False, f"❌ Greška za '{username}': {e}")


def main():
    """Kreira/ažurira sve admin korisnike iz ADMIN_USERS liste."""
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("🔐 PED MAJEVICA - MULTI-ADMIN KREACIJA")
        print("=" * 60)
        print()

        if not ADMIN_USERS:
            print("⚠️  Nema definisanih korisnika u ADMIN_USERS!")
            print("📝 Dodaj korisnike u create_admin_simple.py fajl.")
            return

        print(f"📋 Obrađujem {len(ADMIN_USERS)} korisnika...\n")

        success_count = 0
        fail_count = 0

        for username, password in ADMIN_USERS.items():
            success, message = create_or_update_user(username, password)
            print(f"   {message}")

            if success:
                success_count += 1
            else:
                fail_count += 1

        print()
        print("=" * 60)
        print(f"📊 Rezultati: {success_count} uspešno, {fail_count} neuspešno")
        print("=" * 60)
        print()

        if success_count > 0:
            print("📋 ADMIN LOGIN KREDENCIJALI:")
            print("-" * 60)
            for username, password in ADMIN_USERS.items():
                print(f"   Username: {username:15} | Password: {password}")
            print("-" * 60)
            print()
            print("🔗 Login URL:")
            print("   Development: http://localhost:5000/pages/login.html")
            print("   Production:  https://pedmajevica.org/pages/login.html")
            print()


if __name__ == '__main__':
    main()
