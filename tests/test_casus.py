"""Eén test per casus tegen expected_diff.json (CSV-pad).

Casus 001 is uitgesloten: `source_a.csv` en `expected_diff.json` zijn (onopgeslagen,
buiten deze sessie) overschreven met een ander, niet-compatibel schema (zie het
bouwrapport). Casus 024 is een bekende, gedocumenteerde ground-truth-inconsistentie
(amlodipine-sterktewijziging staat geclassificeerd als DOSE_CHANGE i.p.v.
STRENGTH_CHANGE, in tegenspraak met INTENDED_USE.md v0.3 en met de 8 andere
strength/dose-casus in deze set) -- xfail, geen stille aanpassing van de fixture.

Alleen `type`, `lines_a`, `lines_b` en `requires_escalation` worden geverifieerd.
`severity` is bewust niet getoetst: er is geen gedocumenteerde fijnmazige
laag/midden/hoog/kritiek-regel (zie triage/escalation.py), dus een exacte-match-test
zou de engine afrekenen op een norm die nergens is vastgelegd.
"""

import json
from pathlib import Path

import pytest

from compare import compare_files

CASUS_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic" / "casus"

EXCLUDED = {
    "001-merknaam-vs-stofnaam": "expected_diff.json/source_a.csv overschreven met ander schema, niet gebruikt",
}
KNOWN_GROUND_TRUTH_ISSUES = {
    "024-meervoudige-discrepanties-gemengd": (
        "amlodipine-sterktewijziging (5mg->10mg) is gelabeld als DOSE_CHANGE i.p.v. "
        "STRENGTH_CHANGE -- inconsistent met casus 013/014/017/019/020/021 en met "
        "INTENDED_USE.md v0.3. Nog niet medisch-inhoudelijk gereviewd (BACKLOG.md)."
    ),
}


def _casus_ids():
    return sorted(
        p.name for p in CASUS_DIR.iterdir()
        if p.is_dir() and (p / "expected_diff.json").exists() and p.name not in EXCLUDED
    )


def _as_comparable(entries):
    return sorted(
        (e["type"], tuple(sorted(e["lines_a"])), tuple(sorted(e["lines_b"])), e["requires_escalation"])
        for e in entries
    )


@pytest.mark.parametrize("casus_id", _casus_ids())
def test_casus_diff_matches_expected(casus_id):
    if casus_id in KNOWN_GROUND_TRUTH_ISSUES:
        pytest.xfail(KNOWN_GROUND_TRUTH_ISSUES[casus_id])

    casus_path = CASUS_DIR / casus_id
    expected = json.loads((casus_path / "expected_diff.json").read_text(encoding="utf-8"))
    result = compare_files(casus_path / "source_a.csv", casus_path / "source_b.csv")

    actual_entries = [d.model_dump() for d in result.discrepancies]
    assert _as_comparable(actual_entries) == _as_comparable(expected)
