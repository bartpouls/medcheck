"""Extractietest (geen ground truth) voor de twee praktijkcasus met echte HIX-/
CGM-Apotheek-PDF's (casus 026/027, testpatiënten). Dit toetst alleen of de nieuwe
parsers (parsing/hix.py, parsing/cgm_apotheek.py) feitelijk aansluiten bij wat er in
de bron-PDF staat -- géén oordeel over welke verschillen discrepanties zijn, dat is
de human check die Bart nog doet (zie notes.md in beide casusmappen). Zodra die klaar
is komt er een aparte test tegen expected_diff.json, net als tests/test_pdf_casus.py
en tests/test_prose_casus.py.

De bron-PDF's staan in data/local/ (echte systeemexports, nooit gecommit) en bestaan
dus alleen op Bart's machine -- deze module skipt in elke andere omgeving."""

from pathlib import Path

import pytest

from parsing.pdf_text import parse_pdf

CASUS_DIR = Path(__file__).resolve().parent.parent / "data" / "local" / "casus"

if not CASUS_DIR.exists():
    pytest.skip(
        "data/local/casus/ ontbreekt (echte systeemexports, nooit gecommit) -- alleen lokaal bij Bart",
        allow_module_level=True,
    )


def _substances(lines):
    return sorted(line.substance for line in lines)


def test_casus_026_hix_extraction():
    lines = parse_pdf(CASUS_DIR / "026-praktijkcasus-hix-cgm-testpat02" / "source_a.pdf", "a")
    assert _substances(lines) == ["amitriptyline"]
    assert lines[0].atc == "N06AA09"
    assert lines[0].strength_value == 10.0
    assert lines[0].strength_unit == "mg"


def test_casus_026_cgm_extraction():
    lines = parse_pdf(CASUS_DIR / "026-praktijkcasus-hix-cgm-testpat02" / "source_b.pdf", "b")
    assert _substances(lines) == ["amitriptyline", "paracetamol"]


def test_casus_027_hix_extraction():
    lines = parse_pdf(CASUS_DIR / "027-praktijkcasus-hix-cgm-testpat03" / "source_a.pdf", "a")
    assert _substances(lines) == sorted(
        ["acenocoumarol", "furosemide", "metoprolol", "enalapril", "paracetamol", "mirtazapine"]
    )
    enalapril = next(line for line in lines if line.substance == "enalapril")
    assert enalapril.stop_reason == "Tot nader order gestopt"


def test_casus_027_cgm_extraction():
    lines = parse_pdf(CASUS_DIR / "027-praktijkcasus-hix-cgm-testpat03" / "source_b.pdf", "b")
    assert _substances(lines) == sorted(
        ["semaglutide", "mirtazapine", "paracetamol", "metoprolol", "acenocoumarol"]
    )


def test_casus_028_asp_extraction():
    """ASP (Apotheek Woerden B.V.), casus 028 -- zie JOURNEY.md 2026-08-28 sessie 12.
    Toetst wat inmiddels bevestigd goed gaat (stofnaam/sterkte/vorm, "."-> expliciete
    "geen dosering geregistreerd", "maal"-synoniem). Toetst bewust NIET route/
    toelichting -- die kolommen lopen bij dit bronbestand door elkaar (Toelichting
    heeft geen herkend kolomlabel en "valt" in de Dosering-/TW-kolom, en de
    positionele ankerpositie van een tweewoordige koplabel als "Actuele Voorschrijver"
    ligt te ver naar rechts) -- bekend, nog open issue, geen stille aanname hier."""
    lines = parse_pdf(CASUS_DIR / "028-praktijkcasus-asp-testpat" / "source_a.pdf", "a")
    assert _substances(lines) == sorted(["irbesartan", "oxybutynine", "quetiapine", "oxazepam"])

    by_substance = {line.substance: line for line in lines}
    assert by_substance["irbesartan"].strength_value == 75.0
    assert by_substance["irbesartan"].strength_unit == "mg"
    assert by_substance["irbesartan"].frequency_canonical == "geen dosering geregistreerd"
    assert by_substance["oxybutynine"].frequency_canonical == "geen dosering geregistreerd"
    assert by_substance["quetiapine"].frequency_canonical == "geen dosering geregistreerd"
    assert by_substance["oxazepam"].frequency_canonical == "1 maal per dag"


@pytest.mark.parametrize(
    "casus_id",
    ["026-praktijkcasus-hix-cgm-testpat02", "027-praktijkcasus-hix-cgm-testpat03", "028-praktijkcasus-asp-testpat"],
)
def test_no_expected_diff_yet(casus_id):
    """Bewuste marker: zolang Bart's human check nog niet klaar is, hoort hier geen
    expected_diff.json te staan -- geen AI-oordeel over klinische relevantie
    (CLAUDE.md regel 2). Deze test faalt zodra dat bestand er wél is, als reminder om
    'm dan te vervangen door een echte assert-tegen-ground-truth-test."""
    assert not (CASUS_DIR / casus_id / "expected_diff.json").exists()
