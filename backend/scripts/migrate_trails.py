#!/usr/bin/env python3
"""Migrate hardcoded trails to database"""

from app import create_app, db
from app.models.trail import Trail

app = create_app()

TRAILS_DATA = [
    {
        'name': 'Velika staza - Orlovič (1180m)',
        'description': 'Dugačka i izazovna staza do vrha Orloviča sa predivnim pogledom na cijelu Majevicu.',
        'difficulty': 'Teška',
        'distance_km': 12.5,
        'duration_hours': 5.0,
        'elevation_gain_m': 780,
        'start_point': 'Planinarsko Društvo Majevica',
        'end_point': 'Vrh Orlovič (1180m)',
        'region': 'Majevica',
        'water_sources': True,
        'shelters': False,
        'scenic_views': True,
        'published': True
    },
    {
        'name': 'Mala staza - Porodična (450m)',
        'description': 'Lagana i kratka staza idealna za porodice sa djecom i početnike.',
        'difficulty': 'Lagana',
        'distance_km': 3.2,
        'duration_hours': 1.5,
        'elevation_gain_m': 150,
        'start_point': 'Planinarskuštvo Majevica',
        'end_point': 'Vidikovac (450m)',
        'region': 'Majevica',
        'water_sources': True,
        'shelters': True,
        'scenic_views': True,
        'published': True
    },
    {
        'name': 'Novakova pećina (720m)',
        'description': 'Staza srednje težine do čuvene Novakove pećine, prirodne atrakcije Majevice.',
        'difficulty': 'Srednja',
        'distance_km': 7.8,
        'duration_hours': 3.0,
        'elevation_gain_m': 420,
        'start_point': 'Planinarskuštvo Majevica',
        'end_point': 'Novakova pećina (720m)',
        'region': 'Majevica',
        'water_sources': False,
        'shelters': False,
        'scenic_views': True,
        'published': True
    }
]

with app.app_context():
    print("🏔️  Migriram staze u bazu...")

    for trail_data in TRAILS_DATA:
        existing = Trail.query.filter_by(name=trail_data['name']).first()

        if existing:
            print(f"  ⏭️  Skip: {trail_data['name']} (već postoji)")
        else:
            trail = Trail(**trail_data)
            db.session.add(trail)
            print(f"  ✅ Dodao: {trail_data['name']}")

    db.session.commit()
    print(f"\n✅ Migracija završena! Ukupno staza u bazi: {Trail.query.count()}")
