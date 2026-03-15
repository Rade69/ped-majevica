"""Flask CLI commands"""

import json
import click
from pathlib import Path
from datetime import datetime
from flask.cli import with_appcontext

from app.extensions import db
from app.models.post import Post


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
