"""Flask CLI commands"""

import json
import click
from pathlib import Path
from datetime import datetime
from flask.cli import with_appcontext

from app.extensions import db, bcrypt
from app.models.post import Post
from app.models.user import User


@click.command('migrate-json')
@with_appcontext
def migrate_json_command():
    """Migrate blog posts from JSON file to database"""

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    JSON_PATH = BASE_DIR.parent / 'data' / 'blog_posts.json'

    click.echo("=" * 60)
    click.echo("  MIGRACIJA: JSON → BAZA PODATAKA")
    click.echo("=" * 60)
    click.echo()

    if not JSON_PATH.exists():
        click.echo(f"❌ JSON fajl ne postoji: {JSON_PATH}")
        return

    # Load JSON
    click.echo(f"📚 Učitavam JSON fajl: {JSON_PATH}")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    posts_data = data.get('posts', [])
    click.echo(f"📊 Pronađeno {len(posts_data)} članaka u JSON fajlu")

    if not posts_data:
        click.echo("⚠️  Nema članaka za migraciju")
        return

    # Check existing posts
    existing_count = Post.query.count()
    click.echo(f"📊 Trenutno u bazi: {existing_count} članaka")

    if existing_count > 0:
        if not click.confirm(f"\n⚠️  Baza već ima {existing_count} članaka. Obrisati i ponovo importovati?"):
            click.echo("❌ Migracija otkazana")
            return

        # Delete all posts
        click.echo("🗑️  Brišem postojeće članke...")
        Post.query.delete()
        db.session.commit()

    # Migrate posts
    click.echo("\n🚀 Započinjem migraciju...")
    migrated = 0
    failed = 0

    for idx, post_data in enumerate(posts_data, 1):
        try:
            # Parse date
            date_str = post_data.get('date', '')
            try:
                created_at = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                created_at = datetime.utcnow()

            # Create Post object
            post = Post(
                title=post_data.get('title', 'Bez naslova'),
                slug=post_data.get('slug', f'post-{post_data.get("id", idx)}'),
                content=post_data.get('content_markdown', post_data.get('content_text', '')),
                content_html=post_data.get('content_html'),
                content_text=post_data.get('content_text'),
                preview=post_data.get('preview'),
                category=post_data.get('category', 'ostalo'),
                word_count=post_data.get('word_count'),
                image_count=post_data.get('image_count', 0),
                images=post_data.get('images', []),
                created_at=created_at,
                published=True,
                likes_count=0,
            )

            db.session.add(post)
            migrated += 1

            click.echo(f"  ✅ [{idx}/{len(posts_data)}] {post.title[:50]}...")

        except Exception as e:
            failed += 1
            click.echo(f"  ❌ [{idx}/{len(posts_data)}] Greška: {e}")
            continue

    # Commit all changes
    try:
        db.session.commit()
        click.echo(f"\n✅ Migracija uspješna!")
        click.echo(f"   - Migrirano: {migrated} članaka")
        click.echo(f"   - Neuspješno: {failed} članaka")
        click.echo(f"   - Ukupno u bazi: {Post.query.count()} članaka")

    except Exception as e:
        db.session.rollback()
        click.echo(f"\n❌ Greška pri commit-u: {e}")


@click.command('reset-admin-password')
@click.option('--username', '-u', help='Admin username to reset password')
@click.option('--new-password', '-p', help='New password (leave empty for random)')
@with_appcontext
def reset_admin_password_command(username, new_password):
    """Reset admin password (alternative to email reset)"""
    
    click.echo("=" * 60)
    click.echo("  RESET ADMIN PASSWORD")
    click.echo("=" * 60)
    click.echo()
    
    # List all admin users
    admin_users = User.query.filter_by(role='admin').all()
    
    if not admin_users:
        click.echo("❌ Nema admin korisnika u bazi")
        click.echo("   Pokrenite aplikaciju da se automatski kreiraju admin korisnici")
        click.echo("   (zahtijeva ADMIN_*_PASSWORD environment varijable)")
        return
    
    click.echo("🔐 Dostupni admin korisnici:")
    for i, user in enumerate(admin_users, 1):
        click.echo(f"   {i}. {user.username} ({user.email or 'nema email'})")
    
    # If username not provided, ask interactively
    if not username:
        username = click.prompt("\n📝 Unesite username admina za reset lozinke")
    
    user = User.query.filter_by(username=username, role='admin').first()
    
    if not user:
        click.echo(f"\n❌ Admin sa username '{username}' nije pronađen")
        click.echo("   Dostupni admini:")
        for u in admin_users:
            click.echo(f"   - {u.username}")
        return
    
    click.echo(f"\n✅ Pronađen admin: {user.username} ({user.email or 'nema email'})")
    
    # If new password not provided, generate random or ask
    if not new_password:
        if click.confirm("\n🎲 Želite li automatski generisanu sigurnu lozinku?"):
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
            new_password = ''.join(secrets.choice(alphabet) for _ in range(16))
            click.echo(f"\n🔐 Generisana lozinka: {new_password}")
            click.echo("   ZAPIŠITE OVU LOZINKU! Neće biti prikazana ponovo.")
        else:
            new_password = click.prompt("\n🔐 Unesite novu lozinku", hide_input=True)
            confirm_password = click.prompt("🔐 Potvrdite lozinku", hide_input=True)
            
            if new_password != confirm_password:
                click.echo("\n❌ Lozinke se ne poklapaju")
                return
    
    # Validate password strength
    if len(new_password) < 8:
        if not click.confirm("\n⚠️  Lozinka ima manje od 8 karaktera. Sigurno želite nastaviti?"):
            return
    
    # Update password
    try:
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        click.echo(f"\n✅ Lozinka za {user.username} uspješno promijenjena!")
        click.echo(f"   Username: {user.username}")
        if user.email:
            click.echo(f"   Email: {user.email}")
        click.echo()
        
        # Show login instructions
        click.echo("📋 Instrukcije za prijavu:")
        click.echo("   1. Idite na /pages/login.html")
        click.echo(f"   2. Unesite username: {user.username}")
        click.echo(f"   3. Unesite lozinku: [lozinka koju ste postavili]")
        click.echo()
        click.echo("⚠️  Ako ste generisali lozinku, zapišite je na sigurno!")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"\n❌ Greška pri promjeni lozinke: {e}")


@click.command('list-admins')
@with_appcontext
def list_admins_command():
    """List all admin users"""
    
    click.echo("=" * 60)
    click.echo("  ADMIN KORISNICI")
    click.echo("=" * 60)
    click.echo()
    
    admin_users = User.query.filter_by(role='admin').order_by(User.username).all()
    
    if not admin_users:
        click.echo("❌ Nema admin korisnika u bazi")
        click.echo("   Pokrenite aplikaciju da se automatski kreiraju admin korisnici")
        return
    
    click.echo(f"📊 Ukupno admin korisnika: {len(admin_users)}")
    click.echo()
    
    for user in admin_users:
        click.echo(f"👤 {user.username}")
        if user.email:
            click.echo(f"   📧 Email: {user.email}")
        click.echo(f"   🆔 ID: {user.id}")
        click.echo(f"   📅 Kreiran: {user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'nepoznato'}")
        click.echo(f"   🔐 Zadnja prijava: {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'nikad'}")
        click.echo(f"   ✅ Aktivan: {'DA' if user.is_active else 'NE'}")
        click.echo()


@click.command('init-admin')
@with_appcontext
def init_admin_command():
    """Inicijalizuj admin korisnike iz ADMIN_*_PASSWORD env varijabli."""
    from app.services.user_service import init_admin

    click.echo("🔐 Inicijalizacija admin korisnika...")
    init_admin()
    click.echo("✅ Admin inicijalizacija završena")
