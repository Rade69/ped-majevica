#!/usr/bin/env python3
"""
Create or Update Admin User
============================
Script za kreiranje ili ažuriranje admin korisnika.

Usage:
    python create_admin.py

Environment Variables (opciono):
    ADMIN_USERNAME - Default: admin
    ADMIN_PASSWORD - Default: admin123
"""

import os
import sys
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User


def create_or_update_admin(username='admin', password='admin123'):
    """
    Kreira novog admin korisnika ili ažurira postojećeg.

    Args:
        username (str): Admin username
        password (str): Admin password (biće hashovan)

    Returns:
        bool: True ako je uspešno, False ako ne
    """
    app = create_app()

    with app.app_context():
        try:
            # Proveri da li korisnik već postoji
            user = User.query.filter_by(username=username).first()

            if user:
                # Ažuriraj postojećeg korisnika
                print(f"⚠️  Korisnik '{username}' već postoji. Ažuriram lozinku...")
                user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                db.session.commit()
                print(f"✅ Lozinka za korisnika '{username}' je uspešno ažurirana!")
            else:
                # Kreiraj novog korisnika
                print(f"📝 Kreiram novog admin korisnika '{username}'...")
                password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = User(
                    username=username,
                    password_hash=password_hash,
                    role='admin'
                )
                db.session.add(new_user)
                db.session.commit()
                print(f"✅ Admin korisnik '{username}' je uspešno kreiran!")

            print(f"\n📋 Login kredencijali:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"\n🔗 Login URL:")
            print(f"   Development: http://localhost:5000/pages/login.html")
            print(f"   Production:  https://pedmajevica.org/pages/login.html")

            return True

        except Exception as e:
            print(f"❌ Greška: {e}")
            db.session.rollback()
            return False


def interactive_mode():
    """Interaktivni mod za unos korisničkog imena i lozinke."""
    print("=" * 60)
    print("🔐 PED MAJEVICA - ADMIN USER KREACIJA")
    print("=" * 60)
    print()

    # Unos korisničkog imena
    username = input("Unesite admin korisničko ime [admin]: ").strip()
    if not username:
        username = 'admin'

    # Unos lozinke
    password = input("Unesite admin lozinku [admin123]: ").strip()
    if not password:
        password = 'admin123'

    print()
    print(f"Kreiram korisnika: {username}")
    print()

    return create_or_update_admin(username, password)


def main():
    """Main funkcija - pokreće interaktivni mod ili koristi env varijable."""
    # Proveri da li su env varijable postavljene
    env_username = os.getenv('ADMIN_USERNAME')
    env_password = os.getenv('ADMIN_PASSWORD')

    if env_username and env_password:
        # Koristi env varijable (za automatizaciju/CI/CD)
        print(f"Koristim env varijable za kreaciju korisnika '{env_username}'...")
        return create_or_update_admin(env_username, env_password)
    else:
        # Interaktivni mod
        return interactive_mode()


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operacija otkazana.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Neočekivana greška: {e}")
        sys.exit(1)
