"""End-to-end test van het ontslagbrief-sjabloonpad (locales/nl/prose_parser.py) tegen
Bart's eigen PDF's in casus 006-008 (Sint Barbara Ziekenhuis-sjabloon). Casus 009/010
hebben nog de oude, lege placeholder-PDF's staan en worden bewust overgeslagen --
Bart voegt hier later casus uit echte systemen met testpatiënten voor terug."""

import json
from pathlib import Path

import pytest

from compare import compare_files

CASUS_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic" / "casus"

PROSE_CASUS_IDS = [
    "006-dubbelmedicatie-atc4",
    "007-gestopt-zonder-reden",
    "008-geen-discrepantie-cardiovasculair",
]


def _as_comparable(entries):
    return sorted(
        (e["type"], tuple(sorted(e["lines_a"])), tuple(sorted(e["lines_b"])), e["requires_escalation"])
        for e in entries
    )


@pytest.mark.parametrize("casus_id", PROSE_CASUS_IDS)
def test_prose_casus_diff_matches_expected(casus_id):
    casus_path = CASUS_DIR / casus_id
    pdf_a, pdf_b = casus_path / "source_a.pdf", casus_path / "source_b.pdf"
    if not (pdf_a.exists() and pdf_b.exists()):
        pytest.skip(f"PDF-fixture ontbreekt voor {casus_id}")

    expected = json.loads((casus_path / "expected_diff.json").read_text(encoding="utf-8"))
    result = compare_files(pdf_a, pdf_b)

    actual_entries = [d.model_dump() for d in result.discrepancies]
    assert _as_comparable(actual_entries) == _as_comparable(expected)
