"""Testovi za scripts/fix_homoglyphs.py (ispravka latinicnih slova u cirilici)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "fix_homoglyphs", Path(__file__).resolve().parents[1] / "scripts" / "fix_homoglyphs.py"
)
fh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fh)


def fix(text, html=False):
    report = []
    return fh.fix_field(text, html, report), report


def test_latin_k_inside_cyrillic_word_is_fixed():
    assert fix("планини Kоњух")[0] == "планини Коњух"


def test_short_latin_word_between_cyrillic_words_is_fixed():
    assert fix("He оставља трагове")[0] == "Не оставља трагове"


def test_known_manual_case():
    assert fix("ocuм трагова")[0] == "осим трагова"


def test_english_letters_x_and_y_are_not_touched():
    out, report = fix("Сyстем и миx")
    assert out == "Сyстем и миx"  # ostaje za rucni pregled
    assert ("миx", None) in report


def test_pure_latin_text_and_abbreviations_untouched():
    assert fix("Plain English text")[0] == "Plain English text"
    assert fix("витамин C и BC")[0] == "витамин C и BC"


def test_html_markup_is_not_changed():
    html = '<p class="Kontakt"><a href="https://example.com/Koh">Kоњух</a></p>'
    out, _ = fix(html, html=True)
    assert out == '<p class="Kontakt"><a href="https://example.com/Koh">Коњух</a></p>'


def test_html_tags_in_any_field_are_never_converted():
    # <p> ispred cirilice se ne smije pretvoriti u cirilicno "р" (polje 'content' moze sadrzavati HTML)
    html = "<p><strong>Ујед змије</strong></p><p>Знаци</p>"
    out, report = fix(html, html=False)
    assert out == html
    assert report == []
