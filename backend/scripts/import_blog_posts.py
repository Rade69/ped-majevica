#!/usr/bin/env python3
"""
Import blog posts from blog_posts_categorized.json into database
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app import create_app
from app.extensions import db
from app.models.post import Post
from datetime import datetime


def main():
    app = create_app()
    with app.app_context():
        db.create_all()

        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "blog_posts_categorized.json",
        )

        if not os.path.exists(json_path):
            print(f"❌ Fajl ne postoji: {json_path}")
            sys.exit(1)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        posts_data = data.get("posts", [])
        print(f"📝 Pronađeno {len(posts_data)} postova u JSON-u")

        added = 0
        skipped = 0
        errors = 0

        for post_data in posts_data:
            # Use id as external_id to detect duplicates
            external_id = post_data.get("id")

            # Try to find existing post by slug or external id in title
            existing = Post.query.filter_by(slug=post_data.get("slug", "")).first()
            if existing:
                skipped += 1
                continue

            try:
                # Parse date
                created_at = None
                date_str = post_data.get("date", "")
                if date_str:
                    try:
                        created_at = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        created_at = datetime.utcnow()
                else:
                    created_at = datetime.utcnow()

                # Build images list from the images array
                images = post_data.get("images", [])

                post = Post(
                    title=post_data.get("title", "Bez naslova"),
                    slug=post_data.get("slug", f"post-{external_id}"),
                    content=post_data.get("content_markdown", "") or post_data.get("content_text", ""),
                    content_html=post_data.get("content_html", ""),
                    content_text=post_data.get("content_text", ""),
                    preview=post_data.get("preview", ""),
                    category=post_data.get("category", "ostalo"),
                    images=images,
                    published=True,
                    created_at=created_at,
                    updated_at=datetime.utcnow(),
                )

                db.session.add(post)
                added += 1
                print(f"   ✅ [{post.category}] {post.title[:60]}...")

            except Exception as e:
                errors += 1
                print(f"   ❌ Greška: {post_data.get('title', '?')}: {e}")

        db.session.commit()

        print(f"\n{'='*60}")
        print(f"✅ Dodano: {added}")
        print(f"⏭️  Preskočeno (već postoji): {skipped}")
        print(f"❌ Greške: {errors}")
        total = Post.query.count()
        print(f"📊 Ukupno postova u bazi: {total}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
