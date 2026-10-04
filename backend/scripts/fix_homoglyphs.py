#!/usr/bin/env python3
"""
Ispravka latinicnih slova umetnutih u cirilicne rijeci u clancima.

Uzrok: u izvornom tekstu su neka slova bila "blizanci" latinicnih (npr. latinicno "o" i "c"
umjesto cirilicnog "о" i "с"). Takva rijec ne radi u pretrazi i pogresno se preslovi.

Podrazumijevano je samo PRIKAZ sta bi se promijenilo. Promjena u bazi tek s --apply.
Koristi se:  python scripts/fix_homoglyphs.py            (prikaz)
             python scripts/fix_homoglyphs.py --apply    (primijeni)
Prije --apply napravite backup baze (deployment/scripts/backup-db.sh).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Samo slova koja su vizuelno ista kao cirilicna i NE koriste se kao engleska slova u ovim tekstovima.
# 'x' i 'y' namjerno nisu ovdje (cesto su engleske rijeci: mix, System): prijavljuju se za rucni pregled.
LOOKALIKE = {
    'A': 'А', 'B': 'В', 'C': 'С', 'E': 'Е', 'H': 'Н', 'K': 'К', 'M': 'М', 'O': 'О', 'P': 'Р', 'T': 'Т',
    'a': 'а', 'c': 'с', 'e': 'е', 'o': 'о', 'p': 'р',
}
# Rucno provjerene ispravke (slovo bez cirilicnog blizanca u rijeci)
MANUAL = {'ocuм': 'осим'}
CYR = re.compile('[Ѐ-ӿ]')
LAT = re.compile('[A-Za-z]')
TOKEN = re.compile('[A-Za-zЀ-ӿ]+')
TAG = re.compile(r'(<[^>]+>)')
FIELDS = ("title", "content", "content_html", "content_text", "preview")


def fix_segment(text, report):
    """Ispravi tekst koji nije HTML oznaka. Vraca novi tekst; report dobija (staro, novo) ili (staro, None) za rucni pregled."""
    tokens = list(TOKEN.finditer(text))
    if not tokens:
        return text
    has_cyr = [bool(CYR.search(t.group())) for t in tokens]
    out, last = [], 0
    for i, t in enumerate(tokens):
        word = t.group()
        latin = LAT.findall(word)
        if not latin:
            continue
        all_look = all(c in LOOKALIKE for c in latin)
        convert = False
        if word in MANUAL:
            report.append((word, MANUAL[word]))
            out.append(text[last:t.start()])
            out.append(MANUAL[word])
            last = t.end()
            continue
        if has_cyr[i]:
            # rijec mijesa cirilicu i latinicu
            if all_look:
                convert = True
            else:
                report.append((word, None))  # sadrzi slovo bez cirilicnog blizanca: rucno
                continue
        elif all_look and len(word) <= 4 and not word.isupper():  # skracenice (C, BC, KK) ostaju
            # kratka latinicna rijec okruzena cirilicnim rijecima (npr. "He" umjesto "Не")
            near = (i > 0 and has_cyr[i - 1]) or (i + 1 < len(tokens) and has_cyr[i + 1])
            convert = near
        if convert:
            fixed = ''.join(LOOKALIKE.get(c, c) for c in word)
            report.append((word, fixed))
            out.append(text[last:t.start()])
            out.append(fixed)
            last = t.end()
    out.append(text[last:])
    return ''.join(out)


def fix_field(value, is_html, report):
    if not value:
        return value
    if not is_html:
        return fix_segment(value, report)
    return ''.join(part if TAG.fullmatch(part) else fix_segment(part, report) for part in TAG.split(value))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    from app import create_app
    from app.extensions import db
    from app.models.post import Post

    app = create_app()
    with app.app_context():
        changed_posts = manual = 0
        for post in Post.query.order_by(Post.id).all():
            post_report, updates = [], {}
            for field in FIELDS:
                rep = []
                old = getattr(post, field)
                new = fix_field(old, field == 'content_html', rep)
                if new != old:
                    updates[field] = new
                post_report.extend(rep)
            fixes = [(a, b) for a, b in post_report if b]
            leftovers = [a for a, b in post_report if not b]
            if not fixes and not leftovers:
                continue
            title = post.title[:50]
            print(f"#{post.id} {title!r}: {len(fixes)} ispravki" + (f", {len(set(leftovers))} za rucni pregled" if leftovers else ""))
            seen = set()
            for a, b in fixes:
                if (a, b) not in seen:
                    seen.add((a, b))
                    print(f"     {a}  ->  {b}")
            for a in sorted(set(leftovers)):
                print(f"     RUCNO: {a}")
            manual += len(set(leftovers))
            if updates:
                changed_posts += 1
                if args.apply:
                    for field, value in updates.items():
                        setattr(post, field, value)
        if args.apply:
            db.session.commit()
            print(f"\nPrimijenjeno na {changed_posts} clanaka.")
        else:
            print(f"\nPRIKAZ (nista nije promijenjeno): {changed_posts} clanaka bi se promijenilo; za rucni pregled: {manual} rijeci.")


if __name__ == '__main__':
    main()
