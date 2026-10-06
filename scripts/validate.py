"""Draait de synthetische casusset tegen de diff-engine en schrijft een rapport per
discrepantietype (gevonden / gemist / vals alarm). Zie VALIDATION.md voor de laatst
gemeten uitkomst en de aannames erachter (dit meet de diff-engine op schone CSV-input,
niet de AI-extractiestap -- zie VALIDATION.md).

Gebruik: python scripts/validate.py [--out pad/naar/rapport.md]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from compare import compare_files  # noqa: E402  (na sys.path-aanpassing)

CASUS_DIR = ROOT / "data" / "synthetic" / "casus"

EXCLUDED = {
    "001-merknaam-vs-stofnaam": "expected_diff.json gebruikt een ander schema (representation-diff), geen Discrepancy-vergelijking",
}
KNOWN_GROUND_TRUTH_ISSUES = {
    "024-meervoudige-discrepanties-gemengd": (
        "amlodipine-sterktewijziging is gelabeld als DOSE_CHANGE i.p.v. STRENGTH_CHANGE "
        "in de fixture zelf -- zie tests/test_casus.py"
    ),
}


def _entry_key(entry: dict) -> tuple:
    return (entry["type"], tuple(sorted(entry["lines_a"])), tuple(sorted(entry["lines_b"])), entry["requires_escalation"])


def _casus_ids() -> list[str]:
    return sorted(
        p.name for p in CASUS_DIR.iterdir()
        if p.is_dir() and (p / "expected_diff.json").exists() and p.name not in EXCLUDED
    )


def run() -> dict:
    """Geeft {type: Counter(gevonden=.., gemist=.., vals_alarm=..)} terug, plus per-casus detail."""
    per_type: dict[str, Counter] = {}
    per_casus: dict[str, dict] = {}

    for casus_id in _casus_ids():
        casus_path = CASUS_DIR / casus_id
        expected = json.loads((casus_path / "expected_diff.json").read_text(encoding="utf-8"))
        actual = [
            d.model_dump()
            for d in compare_files(casus_path / "source_a.csv", casus_path / "source_b.csv").discrepancies
        ]

        expected_keys = Counter(_entry_key(e) for e in expected)
        actual_keys = Counter(_entry_key(a) for a in actual)

        gevonden = expected_keys & actual_keys
        gemist = expected_keys - actual_keys
        vals_alarm = actual_keys - expected_keys

        for key, count in gevonden.items():
            per_type.setdefault(key[0], Counter())["gevonden"] += count
        for key, count in gemist.items():
            per_type.setdefault(key[0], Counter())["gemist"] += count
        for key, count in vals_alarm.items():
            per_type.setdefault(key[0], Counter())["vals_alarm"] += count

        per_casus[casus_id] = {
            "gevonden": sum(gevonden.values()),
            "gemist": sum(gemist.values()),
            "vals_alarm": sum(vals_alarm.values()),
            "bekend_probleem": KNOWN_GROUND_TRUTH_ISSUES.get(casus_id),
        }

    return {"per_type": per_type, "per_casus": per_casus}


def format_report(result: dict) -> str:
    lines = ["# Validatierapport\n", "Gegenereerd door `scripts/validate.py`. Zie VALIDATION.md voor duiding.\n"]

    lines.append("\n## Per discrepantietype\n")
    lines.append("| Type | Gevonden | Gemist | Vals alarm |")
    lines.append("|---|---|---|---|")
    for disc_type in sorted(result["per_type"]):
        c = result["per_type"][disc_type]
        lines.append(f"| {disc_type} | {c['gevonden']} | {c['gemist']} | {c['vals_alarm']} |")

    lines.append("\n## Per casus\n")
    lines.append("| Casus | Gevonden | Gemist | Vals alarm | Bekend probleem |")
    lines.append("|---|---|---|---|---|")
    for casus_id, c in result["per_casus"].items():
        probleem = c["bekend_probleem"] or ""
        lines.append(f"| {casus_id} | {c['gevonden']} | {c['gemist']} | {c['vals_alarm']} | {probleem} |")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "validate_report.md")
    args = parser.parse_args()

    result = run()
    report = format_report(result)
    args.out.write_text(report, encoding="utf-8")
    print(report)
    print(f"Rapport geschreven naar {args.out}")


if __name__ == "__main__":
    main()
