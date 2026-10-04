#!/usr/bin/env python3
"""
Pravi podskup Font Awesome (samo ikone koje sajt koristi) za samostalno posluzivanje.

Zasto: puni Font Awesome sa CDN-a je ~300 KB (3 fonta + CSS) i blokira prikaz stranice.
Podskup je nekoliko KB i dolazi sa nase adrese.

Koristenje (iz korijena projekta; potrebni paketi samo za ovaj alat: pip install fonttools brotli):
  1. Preuzmite Font Awesome Free 6.4.0 (all.min.css i webfonts/fa-solid-900.woff2,
     fa-regular-400.woff2, fa-brands-400.woff2) u neki folder IZVOR.
  2. python frontend/tools/build_fontawesome_subset.py IZVOR frontend/assets/vendor/fontawesome
Pokrenite ponovo kad se u stranicama/JS-u pojavi nova ikona (fa-...).
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BACKSLASH = chr(92)
UTILITY = re.compile(
    r'fa-(solid|regular|brands|spin|pulse|fw|ul|li|lg|xs|sm|\d+x|2xs|xl|2xl|beat|fade|flip|rotate|stack|border|pull|inverse|'
    r'swap|layers|bounce|shake)\b'
)


def used_icon_classes():
    files = (glob.glob(os.path.join(ROOT, 'pages', '*.html')) + glob.glob(os.path.join(ROOT, 'js', '*.js'))
             + glob.glob(os.path.join(ROOT, 'assets', 'js', '*.js')))
    used = set()
    for f in files:
        text = open(f, encoding='utf-8', errors='ignore').read()
        used |= set(re.findall(r'(?<![A-Za-z0-9_-])(fa-[a-z0-9-]+)\b', text))
    return used


def main(src, out):
    os.makedirs(os.path.join(out, 'webfonts'), exist_ok=True)
    used = used_icon_classes()
    css = open(os.path.join(src, 'all.min.css'), encoding='utf-8').read()

    # pravila ikona:  .fa-ime:before,.fa-alias:before{content:"\fxxx"}
    icon_rule = re.compile(r'((?:\.fa-[a-z0-9-]+:before,?)+)\{content:"([^"]*)"\}')
    kept, codepoints, found = [], set(), set()
    for m in icon_rule.finditer(css):
        classes = re.findall(r'\.(fa-[a-z0-9-]+):before', m.group(1))
        if any(c in used for c in classes):
            kept.append(m.group(0))
            found |= {c for c in classes if c in used}
            cp = m.group(2)
            if cp.startswith(BACKSLASH):
                codepoints.add(int(cp[1:], 16))
            elif len(cp) == 1:
                codepoints.add(ord(cp))
    rest = icon_rule.sub('', css)

    # @font-face: lokalni podskup (woff2), font-display: swap
    rest = re.sub(r'url\(\.\./webfonts/(fa-[a-z]+-\d+)\.woff2\) format\("woff2"\),url\(\.\./webfonts/[^)]+\) format\("truetype"\)',
                  r'url(/assets/vendor/fontawesome/webfonts/\1.woff2) format("woff2")', rest)
    rest = rest.replace('font-display:block', 'font-display:swap')
    header = ('/* Font Awesome Free 6.4.0 (https://fontawesome.com; ikone CC BY 4.0, fontovi SIL OFL 1.1, kod MIT).\n'
              '   Podskup: samo ikone koje sajt koristi (frontend/tools/build_fontawesome_subset.py). */\n')
    open(os.path.join(out, 'fa-subset.css'), 'w', encoding='utf-8').write(header + rest + '\n' + '\n'.join(kept) + '\n')

    unknown = sorted(c for c in used if c not in found and not UTILITY.match(c))
    print(f'ikona u koristenju: {len(found)}, znakova u fontu: {len(codepoints)}')
    if unknown:
        print('Klase koje nisu ikone ni pomocne (provjeriti):', unknown)

    unicodes = ','.join(f'U+{c:X}' for c in sorted(codepoints))
    for name in ('fa-solid-900', 'fa-regular-400', 'fa-brands-400'):
        target = os.path.join(out, 'webfonts', name + '.woff2')
        # TTF izvor je pouzdaniji za podskup (neki woff2 fajlovi nisu citljivi alatu)
        source = os.path.join(src, 'webfonts', name + ('.ttf' if os.path.exists(os.path.join(src, 'webfonts', name + '.ttf')) else '.woff2'))
        subprocess.run([sys.executable, '-m', 'fontTools.subset', source,
                        '--unicodes=' + unicodes, '--flavor=woff2', '--output-file=' + target,
                        '--layout-features=*', '--no-hinting'], check=True)
        print(f"{name}: {os.path.getsize(source) // 1024} KB -> "
              f"{os.path.getsize(target) // 1024} KB")
    print(f"CSS: {os.path.getsize(os.path.join(src, 'all.min.css')) // 1024} KB -> "
          f"{os.path.getsize(os.path.join(out, 'fa-subset.css')) // 1024} KB")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
