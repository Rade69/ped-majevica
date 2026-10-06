"""Provjera i čuvanje GPX fajla staze."""
import re
import xml.etree.ElementTree as ET

from app.extensions import db

MAX_GPX_BYTES = 5 * 1024 * 1024  # 5 MB (tipična staza je nekoliko stotina KB)
_FORBIDDEN = re.compile(rb"<!\s*(DOCTYPE|ENTITY)", re.IGNORECASE)  # zaštita od XML bombi


class GpxError(ValueError):
    """Neispravan GPX fajl."""


def validate_gpx(data: bytes) -> dict:
    """Provjeri da je fajl pravi GPX; vrati kratak sažetak (broj tačaka)."""
    if not data:
        raise GpxError("Fajl je prazan.")
    if len(data) > MAX_GPX_BYTES:
        raise GpxError("Fajl je prevelik (najviše 5 MB).")
    if _FORBIDDEN.search(data):
        raise GpxError("Fajl nije ispravan GPX (nedozvoljen sadržaj).")
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        raise GpxError("Fajl nije ispravan GPX (XML se ne može pročitati).")

    def local(tag):  # ime elementa bez prostora imena
        return tag.rsplit("}", 1)[-1]

    if local(root.tag) != "gpx":
        raise GpxError("Fajl nije GPX (očekuje se element <gpx>).")
    points = sum(1 for el in root.iter() if local(el.tag) in ("trkpt", "rtept", "wpt"))
    if points == 0:
        raise GpxError("GPX ne sadrži nijednu tačku staze.")
    return {"points": points}


def safe_filename(trail_name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (trail_name or "staza").lower()
                  .translate(str.maketrans("čćđšž", "ccdsz"))).strip("-")
    return f"{base or 'staza'}.gpx"


def save_gpx(trail, data: bytes) -> dict:
    summary = validate_gpx(data)
    trail.gpx_data = data
    trail.gpx_filename = safe_filename(trail.name)
    trail.has_gpx = True
    db.session.commit()
    return {**summary, "filename": trail.gpx_filename, "size": len(data)}


def remove_gpx(trail) -> None:
    trail.gpx_data = None
    trail.gpx_filename = None
    trail.has_gpx = False
    db.session.commit()
