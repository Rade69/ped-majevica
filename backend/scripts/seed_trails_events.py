#!/usr/bin/env python3
"""
Seed script to populate trails and events in PostgreSQL database
Run this directly on Render or locally with DATABASE_URL set
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.trail import Trail
from app.models.event import Event


def seed_trails():
    """Add sample trails to database"""
    trails_data = [
        {
            "name": "Velika Staza-Tavna",
            "description": "Kao skroman doprinos širenju zdravog načina života i druženja sa prirodom uredili smo pješačke staze  koje se protežu obroncima Majevice.Obilaskom naših staza bićete u prilici da vidite  i upoznate značajne prirodne potencijale našeg kraja Novakovu pećinu, Šuplju stijenu ,Orlović, vodopad Skakavac kao i istorijski znamenitosti Manastir Tavnu, kuću u kojoj je rođen Filip Višnjić",
            "difficulty": "Srednja",
            "distance_km": 16.29,
            "duration_hours": 6.44,
            "elevation_gain_m": 676,
            "start_point": "Lopare",
            "end_point": "Orlović (524nm)",
            "region": "Majevica",
            "water_sources": True,
            "shelters": True,
            "scenic_views": True,
            "published": True,
            "images": ["/assets/images/trails/velika-staza-tavna.webp"]
        },
        {
            "name": "Herojeva staza",
            "description": "Kraća ali zahtjevnija staza do najvišeg vrha Majevice - Zmajevca (916m). Idealna za iskusne planinare koji žele brzi uspon sa nagradnim pogledom.",
            "difficulty": "Teška",
            "distance_km": 8.3,
            "duration_hours": 3.5,
            "elevation_gain_m": 780,
            "start_point": "Brusnica",
            "end_point": "Vrh Zmajevca (916m)",
            "region": "Majevica",
            "water_sources": False,
            "shelters": False,
            "scenic_views": True,
            "published": True,
            "images": ["/assets/images/trails/herojeva-staza.webp"]
        },
        {
            "name": "Novakova pećina",
            "description": "Lagana šetnja kroz šume Majevice, idealna za porodice sa djecom. Prolazi pored potoka i kroz livade sa divljim cvijećem.",
            "difficulty": "Lagana",
            "distance_km": 5.2,
            "duration_hours": 2.0,
            "elevation_gain_m": 180,
            "start_point": "Lopare",
            "end_point": "Planinarski Dom",
            "region": "Majevica",
            "water_sources": True,
            "shelters": True,
            "scenic_views": False,
            "published": True,
            "images": ["/assets/images/trails/novakova-pecina.webp"]
        },

    ]

    print("\n📍 Dodavanje staza u bazu...")
    for trail_data in trails_data:
        # Check if trail already exists
        existing = Trail.query.filter_by(name=trail_data['name']).first()
        if existing:
            print(f"   ⏭️  Staza '{trail_data['name']}' već postoji")
            continue

        trail = Trail(**trail_data)
        db.session.add(trail)
        print(f"   ✅ Dodana staza: {trail_data['name']}")

    db.session.commit()
    print(f"✅ Uspješno dodano {len(trails_data)} staza!\n")


def seed_events():
    """Add sample events to database"""
    today = date.today()

    events_data = [
        {
            "title": "Proljetni Pohod na Majevicu",
            "description": "Tradicionalni proljetni pohod na Majevicu za sve uzraste. Pohod uključuje uspon na vrh Stolice sa ručkom u planinskom domu.",
            "event_date": today + timedelta(days=30),
            "start_time": "08:00",
            "end_time": "16:00",
            "activity_type": "Planinarenje",
            "difficulty": "Srednja",
            "location": "Start: Lopare, Cilj: Vrh Stolice",
            "max_participants": 50,
            "published": True
        },
        {
            "title": "Noćni Pohod - Posmatranje Zvijezda",
            "description": "Poseban noćni pohod sa astronomom. Uspon do vrha Zmajevca gdje ćemo posmatrati zvijezdano nebo daleko od svjetlosnog zagađenja.",
            "event_date": today + timedelta(days=45),
            "start_time": "20:00",
            "end_time": "02:00",
            "activity_type": "Poseban događaj",
            "difficulty": "Srednja",
            "location": "Vrh Zmajevca (916m)",
            "max_participants": 30,
            "published": True
        },
        {
            "title": "Jesenji Maraton Majevice",
            "description": "Trail running maraton kroz najljepše staze Majevice. Tri kategorije: 10km, 21km, i 42km. Registracija obavezna.",
            "event_date": today + timedelta(days=90),
            "start_time": "07:00",
            "end_time": "14:00",
            "activity_type": "Trail Running",
            "difficulty": "Teška",
            "location": "Start/Cilj: Lopare",
            "max_participants": 150,
            "published": True
        },
        {
            "title": "Porodična Šetnja - Upoznajmo Majevicu",
            "description": "Lagana porodična šetnja kroz šume Majevice sa edukativnim sadržajem o biljnom i životinjskom svijetu. Idealno za djecu.",
            "event_date": today + timedelta(days=15),
            "start_time": "10:00",
            "end_time": "14:00",
            "activity_type": "Planinarenje",
            "difficulty": "Lagana",
            "location": "Lopare - Planinarski Dom",
            "max_participants": 40,
            "published": True
        },
        {
            "title": "Fotografski Izlet - Magija Majevice",
            "description": "Poseban fotografski izlet sa profesionalnim fotografom. Učenje landscape fotografije u praksi.",
            "event_date": today + timedelta(days=60),
            "start_time": "05:00",
            "end_time": "12:00",
            "activity_type": "Poseban događaj",
            "difficulty": "Lagana",
            "location": "Različite lokacije na Majevici",
            "max_participants": 15,
            "published": True
        }
    ]

    print("📅 Dodavanje događaja u bazu...")
    for event_data in events_data:
        # Check if event already exists
        existing = Event.query.filter_by(title=event_data['title']).first()
        if existing:
            print(f"   ⏭️  Događaj '{event_data['title']}' već postoji")
            continue

        event = Event(**event_data)
        db.session.add(event)
        print(f"   ✅ Dodan događaj: {event_data['title']} ({event_data['event_date']})")

    db.session.commit()
    print(f"✅ Uspješno dodano {len(events_data)} događaja!\n")


def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("🌲 PED MAJEVICA - SEED TRAILS & EVENTS 🌲")
    print("="*60)

    app = create_app()

    with app.app_context():
        try:
            # Ensure tables exist
            db.create_all()

            # Seed data
            seed_trails()
            seed_events()

            # Show final counts
            trail_count = Trail.query.count()
            event_count = Event.query.count()

            print("="*60)
            print(f"✅ ZAVRŠENO!")
            print(f"📊 Ukupno staza u bazi: {trail_count}")
            print(f"📊 Ukupno događaja u bazi: {event_count}")
            print("="*60 + "\n")

        except Exception as e:
            print(f"\n❌ GREŠKA: {e}")
            db.session.rollback()
            sys.exit(1)


if __name__ == "__main__":
    main()
