#!/usr/bin/env python3
"""
Import podataka iz JSON fajlova u bazu
Učitava blog_posts.json i trails.json u database
"""

import json
import os
import sys

# Dodaj parent folder na path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.post import Post
from app.models.trail import Trail
from app.models.event import Event
from datetime import datetime

def import_posts():
    """Import blog posts from JSON"""
    print("\n📝 Import blog postova...")
    
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'blog_posts.json')
    
    if not os.path.exists(json_path):
        print(f"❌ Fajl ne postoji: {json_path}")
        return 0
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    posts_data = data.get('posts', [])
    
    if not posts_data:
        print("⚠️ Nema postova u JSON-u")
        return 0
    
    count = 0
    for post_data in posts_data:
        # Proveri da li post već postoji
        existing = Post.query.filter_by(slug=post_data.get('slug')).first()
        if existing:
            print(f"  ⏭️  Post već postoji: {post_data.get('title')}")
            continue
        
        try:
            post = Post(
                title=post_data.get('title', 'Bez naslova'),
                slug=post_data.get('slug', f"post-{count}"),
                content=post_data.get('content', ''),
                content_html=post_data.get('content_html'),
                content_text=post_data.get('content_text', ''),
                preview=post_data.get('preview'),
                category=post_data.get('category', 'ostalo'),
                word_count=post_data.get('word_count'),
                image_count=post_data.get('image_count', 0),
                images=post_data.get('images', []),
                published=post_data.get('published', True),
                likes_count=post_data.get('likes_count', 0),
                created_at=datetime.fromisoformat(post_data.get('created_at')) if post_data.get('created_at') else datetime.utcnow(),
                updated_at=datetime.fromisoformat(post_data.get('updated_at')) if post_data.get('updated_at') else datetime.utcnow(),
            )
            
            db.session.add(post)
            count += 1
            print(f"  ✅ Dodan: {post.title}")
            
        except Exception as e:
            print(f"  ❌ Greška pri importu posta {post_data.get('title')}: {e}")
    
    db.session.commit()
    print(f"✅ Ukupno dodano postova: {count}")
    return count


def import_trails():
    """Import trails from JSON"""
    print("\n🥾 Import staza...")
    
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'trails.json')
    
    if not os.path.exists(json_path):
        print(f"❌ Fajl ne postoji: {json_path}")
        return 0
    
    with open(json_path, 'r', encoding='utf-8') as f:
        trails_data = json.load(f)
    
    if not trails_data:
        print("⚠️ Nema staza u JSON-u")
        return 0
    
    count = 0
    for trail_data in trails_data:
        # Proveri da li staza već postoji (po imenu jer nema slug)
        existing = Trail.query.filter_by(name=trail_data.get('name')).first()
        if existing:
            print(f"  ⏭️  Staza već postoji: {trail_data.get('name')}")
            continue
        
        try:
            trail = Trail(
                name=trail_data.get('name', 'Bez naziva'),
                description=trail_data.get('description', ''),
                difficulty=trail_data.get('difficulty', 'srednji').lower(),
                distance_km=trail_data.get('distance_km'),
                duration_hours=trail_data.get('duration_hours'),
                elevation_gain_m=trail_data.get('elevation_gain_m'),
                start_point=trail_data.get('start_point'),
                end_point=trail_data.get('end_point'),
                region=trail_data.get('region'),
                images=trail_data.get('images', []),
                water_sources=trail_data.get('water_sources', False),
                shelters=trail_data.get('shelters', False),
                scenic_views=trail_data.get('scenic_views', False),
                features={},
                equipment={},
                warning=trail_data.get('warning'),
                contact=trail_data.get('contact'),
                published=trail_data.get('published', True),
            )
            
            db.session.add(trail)
            count += 1
            print(f"  ✅ Dodana: {trail.name}")
            
        except Exception as e:
            print(f"  ❌ Greška pri importu staze {trail_data.get('name')}: {e}")
    
    db.session.commit()
    print(f"✅ Ukupno dodano staza: {count}")
    return count


def main():
    print("=" * 60)
    print("📥 IMPORT PODATAKA IZ JSON U BAZU")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        posts_count = import_posts()
        trails_count = import_trails()
        
        print("\n" + "=" * 60)
        print("📊 REZIME")
        print("=" * 60)
        
        # Ukupan broj zapisa
        total_posts = Post.query.count()
        total_trails = Trail.query.count()
        total_events = Event.query.count()
        
        print(f"📝 Blog postova: {total_posts} (+{posts_count})")
        print(f"🥾 Staza: {total_trails} (+{trails_count})")
        print(f"📅 Događaja: {total_events}")
        
        print("\n✅ Import završen!")
        print("=" * 60)


if __name__ == '__main__':
    main()
