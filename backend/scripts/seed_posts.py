#!/usr/bin/env python3
"""
Seed blog posts into database
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.post import Post
from datetime import datetime


def seed_posts():
    posts_data = [
        {
            "title": "Dobrodošli u PED Majevica 1988",
            "slug": "dobrodosli-u-ped-majevica",
            "content": "Planinsko ekološko društvo **Majevica** osnovano je 1988. godine sa ciljem promovisanja planinarenja, očuvanja prirode i okupljanja ljubitelja ljepota Majevice.\n\nKroz više od tri decenije postojanja, organizovali smo stotine pohoda, edukativnih programa i akcija čišćenja planinskih staza.\n\nNaša misija je jednostavna: _čuvati prirodu za buduće generacije, dok uživamo u ljepotama koje nam Majevica pruža._",
            "content_html": "<p>Planinsko ekološko društvo <strong>Majevica</strong> osnovano je 1988. godine sa ciljem promovisanja planinarenja, očuvanja prirode i okupljanja ljubitelja ljepota Majevice.</p><p>Kroz više od tri decenije postojanja, organizovali smo stotine pohoda, edukativnih programa i akcija čišćenja planinskih staza.</p><p>Naša misija je jednostavna: <em>čuvati prirodu za buduće generacije, dok uživamo u ljepotama koje nam Majevica pruža.</em></p>",
            "content_text": "Planinsko ekološko društvo Majevica osnovano je 1988. godine sa ciljem promovisanja planinarenja, očuvanja prirode i okupljanja ljubitelja ljepota Majevice.",
            "preview": "Saznajte više o našem društvu, misiji i viziji očuvanja prirode Majevice.",
            "category": "ostalo",
            "published": True,
        },
        {
            "title": "Top 5 staza na Majevici za početnike",
            "slug": "top-5-staza-majevica-pocetnici",
            "content": "Majevica nudi predivne staze za sve nivoe planinara. Evo naših preporuka za **početnike**:\n\n1. **Novakova pećina** — lagana šetnja od 5km kroz mješovitu šumu\n2. **Staza zdravlja** — uređena staza oko Lopara, idealna za porodice\n3. **Herojeva staza (donji dio)** — prvi dio staze do vidikovca\n4. **Manastir Tavna** — kulturno-istorijska šetnja\n5. **Šuplja stijena** — kratka ali spektakularna staza sa pogledom\n\nSvaka od ovih staza ima **označene puteve**, a na većini se nalaze i planinarski domovi gdje možete odmoriti.",
            "content_html": "<p>Majevica nudi predivne staze za sve nivoe planinara.</p><ol><li><strong>Novakova pećina</strong> — lagana šetnja od 5km</li><li><strong>Staza zdravlja</strong> — uređena staza oko Lopara</li><li><strong>Herojeva staza</strong> — do vidikovca</li><li><strong>Manastir Tavna</strong> — kulturno-istorijska šetnja</li><li><strong>Šuplja stijena</strong> — kratka ali spektakularna</li></ol>",
            "content_text": "Majevica nudi predivne staze za sve nivoe planinara. Evo naših preporuka za početnike.",
            "preview": "Otkrijte najljepše i najlakše staze na Majevici za one koji tek počinju sa planinarenjem.",
            "category": "staze",
            "published": True,
        },
        {
            "title": "Priprema za planinski pohod — vodič za početnike",
            "slug": "priprema-planinski-pohod-vodic",
            "content": "Priprema je ključ uspješnog i sigurnog planinarenja. Evo šta trebate znati:\n\n## Oprema\n- **Planinarske cipele** — obavezno, sa dobrim đonom\n- **Slojevita odjeća** — vremenske promjene na planini su brze\n- **Voda i hrana** — minimum 2 litre vode po osobi\n- **Zaštita od sunca** — kapa, naočale, krema\n- **Plan i mapa** — uvijek imajte plan rute\n\n## Kondicija\nPočnite sa laganim šetnjama i postepeno povećavajte intenzitet. Za većinu naših staza dovoljna je osnovna kondicija.\n\n## Pravila\n- Poštujte _Leave No Trace_ principe\n- Obavijestite nekoga o vašoj ruti\n- Ne idite sami na nepoznate staze",
            "content_html": "<p>Priprema je ključ uspješnog i sigurnog planinarenja.</p><h2>Oprema</h2><ul><li>Planinarske cipele</li><li>Slojevita odjeća</li><li>Voda i hrana</li><li>Zaštita od sunca</li><li>Plan i mapa</li></ul>",
            "content_text": "Priprema je ključ uspješnog i sigurnog planinarenja. Evo šta trebate znati o opremi, kondiciji i pravilima.",
            "preview": "Kompletan vodič za pripremu vašeg prvog planinarskog pohoda na Majevici.",
            "category": "savjeti",
            "published": True,
        },
    ]

    print("\n📝 Dodavanje blog postova...")
    count = 0
    for post_data in posts_data:
        existing = Post.query.filter_by(slug=post_data["slug"]).first()
        if existing:
            print(f"   ⏭️  Post već postoji: {post_data['title']}")
            continue

        post = Post(
            title=post_data["title"],
            slug=post_data["slug"],
            content=post_data["content"],
            content_html=post_data.get("content_html"),
            content_text=post_data.get("content_text", ""),
            preview=post_data.get("preview"),
            category=post_data.get("category", "ostalo"),
            published=post_data.get("published", True),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(post)
        count += 1
        print(f"   ✅ Dodan post: {post_data['title']}")

    db.session.commit()
    print(f"✅ Uspješno dodano {count} postova!\n")


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_posts()
        total = Post.query.count()
        print(f"📊 Ukupno postova u bazi: {total}")


if __name__ == "__main__":
    main()
