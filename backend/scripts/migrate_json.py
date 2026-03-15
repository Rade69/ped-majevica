#!/usr/bin/env python3
"""Simple migration script to run via: flask shell < migrate_json.py"""

import json
from pathlib import Path
from datetime import datetime
from app import create_app, db
from app.models.post import Post

# Paths
BASE_DIR = Path(__file__).parent
JSON_PATH = BASE_DIR.parent / 'data' / 'blog_posts.json'

print("=" * 60)
print("  MIGRACIJA: JSON → BAZA PODATAKA")
print("=" * 60)
print()

# Load JSON
print(f"📚 Učitavam JSON fajl: {JSON_PATH}")
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

posts_data = data.get('posts', [])
print(f"📊 Pronađeno {len(posts_data)} članaka u JSON fajlu")

# Delete existing posts
existing_count = Post.query.count()
print(f"📊 Trenutno u bazi: {existing_count} članaka")

if existing_count > 0:
    print("🗑️  Brišem postojeće članke...")
    Post.query.delete()
    db.session.commit()

# Migrate posts
print("\n🚀 Započinjem migraciju...")
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

except Exception as e:
    db.session.rollback()
    print(f"\n❌ Greška pri commit-u: {e}")
