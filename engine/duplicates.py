"""Duplicaatdetectie: twee verschillende stoffen in lijst B die tot dezelfde
therapeutische klasse behoren (data/reference/duplicate_classes.json). Vervangt de
losse ADDED-melding voor de nieuw bijgekomen regel(s) door één DUPLICATE_THERAPY-melding
(zie casus 006, 023).

Een kale ATC-4-prefixvergelijking bleek niet te werken: ibuprofen/diclofenac delen
alleen ATC-4, oxazepam/temazepam delen zelfs geen ATC-4, terwijl amoxicilline/
flucloxacilline en insuline aspart/glargine wél ATC-4 delen maar geen duplicaat zijn.
Zie duplicate_classes.json._meta voor de volledige toelichting en het bouwrapport."""

from collections import defaultdict

from models import Discrepancy, MedicationLine
from reference import load_duplicate_classes


def _class_key_for_line(line: MedicationLine) -> set:
    keys = set()
    atc = line.atc or ""
    substance = line.substance.strip().lower()
    for duplicate_class in load_duplicate_classes()["classes"]:
        categorie = duplicate_class["categorie"]
        prefix = duplicate_class.get("atc_prefix")
        substances = {s.lower() for s in duplicate_class.get("substances", [])}
        if (prefix and atc.startswith(prefix)) or substance in substances:
            keys.add(categorie)
    return keys


def find_duplicate_groups(lines_b: list[MedicationLine]) -> list[list[int]]:
    class_groups: dict = defaultdict(list)
    for i, line in enumerate(lines_b):
        for categorie in _class_key_for_line(line):
            class_groups[categorie].append(i)

    result = []
    for indices in class_groups.values():
        substances = {lines_b[i].substance for i in indices}
        if len(substances) >= 2:
            result.append(sorted(indices))
    return result


def apply_duplicate_overlay(
    discrepancies: list[Discrepancy],
    pairs: list,
    lines_a: list[MedicationLine],
    lines_b: list[MedicationLine],
) -> list[Discrepancy]:
    groups = find_duplicate_groups(lines_b)
    if not groups:
        return discrepancies

    b_to_a = {b_idx: a_idx for a_idx, b_idx in pairs if a_idx is not None and b_idx is not None}
    covered_b_indices: set = set()
    duplicate_discrepancies = []

    for group in groups:
        lines_a_idx = sorted({b_to_a[b_idx] for b_idx in group if b_idx in b_to_a})
        substances = ", ".join(sorted({lines_b[i].substance for i in group}))
        duplicate_discrepancies.append(
            Discrepancy(
                type="DUPLICATE_THERAPY",
                lines_a=lines_a_idx,
                lines_b=group,
                severity="hoog",
                requires_escalation=True,
                reason=f"Meerdere middelen uit dezelfde therapeutische klasse tegelijk in lijst B: {substances}.",
            )
        )
        covered_b_indices.update(group)

    filtered = [
        d for d in discrepancies
        if not (d.type == "ADDED" and d.lines_b and d.lines_b[0] in covered_b_indices)
    ]
    return filtered + duplicate_discrepancies
