#!/usr/bin/env python3
"""Migrate hardcoded events to database"""

from app import create_app, db
from app.models.event import Event
from datetime import date

app = create_app()

EVENTS_DATA = [
    {
        'title': 'Godišnji izlet na Orlovič',
        'description': 'Tradicionalni godišnji izlet od 1988. godine. Uspon na vrh Orloviča sa zajedničkim ručkom i druženje.',
        'event_date': date(2026, 5, 25),
        'start_time': '07:00',
        'end_time': '18:00',
        'max_participants': 15,
        'activity_type': 'Izlet',
        'difficulty': 'Teška',
        'location': 'Orlovič (1180m)',
        'published': True
    },
    {
        'title': 'Radionica navigacije',
        'description': 'Osnove korištenja kompasa, GPS uređaja i čitanja topografskih karata.',
        'event_date': date(2026, 6, 1),
        'start_time': '10:00',
        'end_time': '16:00',
        'max_participants': 20,
        'activity_type': 'Radionica',
        'difficulty': 'Lagana',
        'location': 'Planinarsko Društvo',
        'published': True
    },
    {
        'title': 'Porodični izlet - 35. godišnjica',
        'description': 'Obilježavanje 35. godišnjice društva sa porodičnim izletom prilagođenim svim uzrastima.',
        'event_date': date(2026, 6, 15),
        'start_time': '09:00',
        'end_time': '17:00',
        'max_participants': 30,
        'activity_type': 'Proslava',
        'difficulty': 'Lagana',
        'location': 'Mala staza',
        'published': True
    }
]

with app.app_context():
    print("📅 Migriram akcije u bazu...")

    for event_data in EVENTS_DATA:
        existing = Event.query.filter_by(title=event_data['title']).first()

        if existing:
            print(f"  ⏭️  Skip: {event_data['title']} (već postoji)")
        else:
            event = Event(**event_data)
            db.session.add(event)
            print(f"  ✅ Dodao: {event_data['title']}")

    db.session.commit()
    print(f"\n✅ Migracija završena! Ukupno akcija u bazi: {Event.query.count()}")
