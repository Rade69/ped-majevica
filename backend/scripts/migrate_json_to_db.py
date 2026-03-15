#!/usr/bin/env python3
"""
Migration script: JSON blog posts → Database

Prebacuje sve blog članke iz blog_posts.json u SQLite/PostgreSQL bazu podataka.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.extensions import db
from app.models.post import Post


def parse_date(date_str):
    """Parse date string from JSON to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return datetime.utcnow()


def migrate_json_to_database():
    """Main migration function"""

    # Paths
    BASE_DIR = Path(__file__).parent
    JSON_PATH = BASE_DIR.parent / 'data' / 'blog_posts.json'

    if not JSON_PATH.exists():
        print(f"❌ JSON fajl ne postoji: {JSON_PATH}")
        return False

    # Load JSON
    print(f"📚 Učitavam JSON fajl: {JSON_PATH}")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    posts_data = data.get('posts', [])
    print(f"📊 Pronađeno {len(posts_data)} članaka u JSON fajlu")

    if not posts_data:
        print("⚠️  Nema članaka za migraciju")
        return True

    # Create Flask app and context
    app = create_app()

    with app.app_context():
        # Check existing posts
        existing_count = Post.query.count()
        print(f"📊 Trenutno u bazi: {existing_count} članaka")

        if existing_count > 0:
            response = input(f"\n⚠️  Baza već ima {existing_count} članaka. Obrisati i ponovo importovati? (y/N): ")
            if response.lower() != 'y':
                print("❌ Migracija otkazana")
                return False

            # Delete all posts
            print("🗑️  Brišem postojeće članke...")
            Post.query.delete()
            db.session.commit()

        # Migrate posts
        print("\n🚀 Započinjem migraciju...")
        migrated = 0
        failed = 0

        for idx, post_data in enumerate(posts_data, 1):
            try:
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
                    created_at=parse_date(post_data.get('date')),
                    published=True,
                    likes_count=0,
                )

                db.session.add(post)
                migrated += 1

                print(f"  ✅ [{idx}/{len(posts_data)}] {post.title[:50]}...")

            except Exception as e:
                failed += 1
                print(f"  ❌ [{idx}/{len(posts_data)}] Greška: {e}")
                continue

        # Commit all changes
        try:
            db.session.commit()
            print(f"\n✅ Migracija uspješna!")
            print(f"   - Migrirano: {migrated} članaka")
            print(f"   - Neuspješno: {failed} članaka")
            print(f"   - Ukupno u bazi: {Post.query.count()} članaka")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Greška pri commit-u: {e}")
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("  MIGRACIJA: JSON → BAZA PODATAKA")
    print("=" * 60)
    print()

    success = migrate_json_to_database()

    if success:
        print("\n🎉 Migracija završena uspješno!")
        sys.exit(0)
    else:
        print("\n❌ Migracija nije uspjela")
        sys.exit(1)
