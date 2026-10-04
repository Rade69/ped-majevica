"""Poslovna logika za uređivanje blokova sadržaja."""
import re

import nh3

from app.extensions import db
from app.models.content_block import ContentBlock, ContentRevision

# Stranice čiji se blokovi mogu uređivati (dodati ovdje za novu stranicu)
ALLOWED_PAGES = {"index", "galerija", "uclanite-se"}
KEY_RE = re.compile(r"^[a-z0-9_-]{1,64}$")
MAX_HTML_LENGTH = 20000
MAX_REVISIONS = 20

ALLOWED_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "span", "a",
    "ul", "ol", "li", "h2", "h3", "h4", "blockquote", "div", "img", "hr",
}
ALLOWED_ATTRIBUTES = {
    "*": {"class"},
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "width", "height", "loading"},
}
ALLOWED_URL_SCHEMES = {"http", "https", "mailto", "tel"}


class ContentError(ValueError):
    """Neispravan ulaz (stranica, ključ ili sadržaj)."""


def sanitize_html(html):
    """Ukloni sve osim dozvoljenih tagova/atributa (zaštita od XSS)."""
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
    ).strip()


def validate_target(page, key):
    if page not in ALLOWED_PAGES:
        raise ContentError("Nepoznata stranica")
    if not KEY_RE.match(key or ""):
        raise ContentError("Neispravan ključ bloka")


def get_page_blocks(page):
    """Vrati {key: html} samo za blokove koji imaju vlastiti sadržaj."""
    if page not in ALLOWED_PAGES:
        raise ContentError("Nepoznata stranica")
    rows = ContentBlock.query.filter(
        ContentBlock.page == page, ContentBlock.html.isnot(None)
    ).all()
    return {r.key: r.html for r in rows}


def _get_or_create(page, key):
    block = ContentBlock.query.filter_by(page=page, key=key).first()
    if block is None:
        block = ContentBlock(page=page, key=key)
        db.session.add(block)
        db.session.flush()
    return block


def _record(block, html, user_id):
    db.session.add(ContentRevision(block_id=block.id, html=html, created_by_id=user_id))
    db.session.flush()
    old = (
        ContentRevision.query.filter_by(block_id=block.id)
        .order_by(ContentRevision.id.desc())
        .offset(MAX_REVISIONS)
        .all()
    )
    for rev in old:
        db.session.delete(rev)


def save_block(page, key, html, user_id):
    validate_target(page, key)
    if not isinstance(html, str):
        raise ContentError("Sadržaj mora biti tekst")
    if len(html) > MAX_HTML_LENGTH:
        raise ContentError("Sadržaj je predugačak")
    clean = sanitize_html(html)
    block = _get_or_create(page, key)
    block.html = clean
    block.updated_by_id = user_id
    _record(block, clean, user_id)
    db.session.commit()
    return block


def reset_block(page, key, user_id):
    """Vrati blok na originalni sadržaj iz HTML fajla."""
    validate_target(page, key)
    block = _get_or_create(page, key)
    block.html = None
    block.updated_by_id = user_id
    _record(block, None, user_id)
    db.session.commit()
    return block


def get_history(page, key):
    validate_target(page, key)
    block = ContentBlock.query.filter_by(page=page, key=key).first()
    return list(block.revisions) if block else []


def restore_revision(page, key, revision_id, user_id):
    validate_target(page, key)
    block = ContentBlock.query.filter_by(page=page, key=key).first()
    rev = (
        ContentRevision.query.filter_by(id=revision_id, block_id=block.id).first()
        if block
        else None
    )
    if rev is None:
        raise ContentError("Verzija ne postoji")
    block.html = rev.html
    block.updated_by_id = user_id
    _record(block, rev.html, user_id)
    db.session.commit()
    return block
