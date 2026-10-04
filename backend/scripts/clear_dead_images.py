#!/usr/bin/env python3
"""
Ukloni iz clanaka adrese slika koje vise ne postoje (stari WordPress: /wp-content/uploads/...).

Zasto: browser za svaku takvu sliku salje zahtjev koji zavrsi sa 404 (greske u konzoli, sporije ucitavanje),
a posjetilac svakako vidi zamjensku ikonu. Adrese ostaju sacuvane u backend/data/*.json,
pa se mogu vratiti ponovnim uvozom ako slike jednom pronadjemo.

Svaka adresa se PROVJERI (HEAD zahtjev); uklanja se samo ona koja vraca 404/410.
Podrazumijevano je samo prikaz; promjena u bazi tek s --apply (prije toga backup baze).
"""
import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DEAD_STATUSES = (404, 410)


def is_dead(url):
    if not url.startswith(("http://", "https://")):
        return False  # lokalne putanje ne diramo
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ped-majevica-maintenance"})
        with urllib.request.urlopen(req, timeout=15):
            return False
    except urllib.error.HTTPError as e:
        return e.code in DEAD_STATUSES
    except Exception:
        return False  # mreza/DNS greska: ne brisati


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    from app import create_app
    from app.extensions import db
    from app.models.post import Post

    app = create_app()
    with app.app_context():
        removed_total = changed = 0
        for post in Post.query.order_by(Post.id).all():
            images = list(post.images or [])
            alive = [u for u in images if not is_dead(u)]
            dead = len(images) - len(alive)
            if not dead:
                continue
            removed_total += dead
            changed += 1
            print(f"#{post.id} {post.title[:45]!r}: {dead} od {len(images)} slika ne postoji")
            if args.apply:
                post.images = alive
                post.image_count = len(alive)
        if args.apply:
            db.session.commit()
            print(f"\nUklonjeno {removed_total} mrtvih adresa iz {changed} clanaka.")
        else:
            print(f"\nPRIKAZ (nista nije promijenjeno): {removed_total} mrtvih adresa u {changed} clanaka.")


if __name__ == "__main__":
    main()
