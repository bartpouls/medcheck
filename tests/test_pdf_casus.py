"""End-to-end test van het tekst-PDF-pad (parse_pdf -> compare_files) tegen drie
gegenereerde tabel-achtige PDF-fixtures (zie scripts/make_pdf_fixture.py). Los van
tests/test_casus.py, dat alleen het CSV-pad dekt.

Deze drie casus zijn gekozen omdat casus 006-010 al Bart's eigen, lopende
PDF-experiment bevatten (ontslagbrief-stijl, vrije tekst -- niet bruikbaar voor dit
pad, zie het privé-bouwlog 2026-08-26); 002/013/017 hadden nog geen PDF en dekken drie
verschillende paden: combipreparaat-ontleding, frequentiewijziging, dosiswijziging."""

import json
from pathlib import Path

import pytest

from compare import compare_files

CASUS_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic" / "casus"

PDF_CASUS_IDS = [
    "002-combinatiepreparaat",
    "013-frequentiewijziging",
    "017-insulineschema-meervoudig",
]


def _as_comparable(entries):
    return sorted(
        (e["type"], tuple(sorted(e["lines_a"])), tuple(sorted(e["lines_b"])), e["requires_escalation"])
        for e in entries
    )


@pytest.mark.parametrize("casus_id", PDF_CASUS_IDS)
def test_pdf_casus_diff_matches_expected(casus_id):
    casus_path = CASUS_DIR / casus_id
    pdf_a, pdf_b = casus_path / "source_a.pdf", casus_path / "source_b.pdf"
    if not (pdf_a.exists() and pdf_b.exists()):
        pytest.skip(f"PDF-fixture ontbreekt voor {casus_id} -- genereer met scripts/make_pdf_fixture.py")

    expected = json.loads((casus_path / "expected_diff.json").read_text(encoding="utf-8"))
    result = compare_files(pdf_a, pdf_b)

    actual_entries = [d.model_dump() for d in result.discrepancies]
    assert _as_comparable(actual_entries) == _as_comparable(expected)
