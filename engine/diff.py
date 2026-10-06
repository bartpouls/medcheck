"""Diff-regels per Discrepancy.type. Geen AI (ADR-001) -- puur deterministische
veldvergelijking op gematchte paren uit matching.py.

Bij een gematcht paar wordt per veld gecontroleerd; wijzigen meerdere velden tegelijk
(zie casus 024), dan levert dat meerdere aparte Discrepancy's op dezelfde
lines_a/lines_b -- geen samengevoegde blob (zie MVP_OPZET.md sectie 6)."""

from models import Discrepancy, MedicationLine
from normalize.frequency import frequency_core
from normalize.units import doses_equal, strengths_equal


def _placeholder_discrepancy(disc_type: str, lines_a: list[int], lines_b: list[int], reason: str) -> Discrepancy:
    # severity/requires_escalation worden pas door triage.escalation.apply_triage ingevuld;
    # hier een neutrale placeholder zodat het model geldig blijft vóór die stap.
    return Discrepancy(
        type=disc_type,
        lines_a=lines_a,
        lines_b=lines_b,
        severity="laag",
        requires_escalation=False,
        reason=reason,
    )


def _compare_matched_pair(idx_a: int, idx_b: int, line_a: MedicationLine, line_b: MedicationLine) -> list[Discrepancy]:
    discrepancies = []
    same_form = line_a.form.strip().lower() == line_b.form.strip().lower()

    # Sterkte/dosis zijn alleen vergelijkbaar binnen dezelfde vorm (mg per tablet is
    # geen zinvolle vergelijking met mg/ml drank). Bij een vormwijziging (casus 005)
    # levert dat uitsluitend FORM_CHANGE op, geen valse STRENGTH_CHANGE/DOSE_CHANGE
    # erbovenop -- zie het bouwrapport.
    if same_form and not strengths_equal(
        line_a.strength_value, line_a.strength_unit, line_b.strength_value, line_b.strength_unit,
        raw_a=line_a.strength_unit, raw_b=line_b.strength_unit,
    ):
        discrepancies.append(
            _placeholder_discrepancy(
                "STRENGTH_CHANGE", [idx_a], [idx_b],
                f"{line_a.substance}: sterkte gewijzigd ({line_a.strength_value}{line_a.strength_unit} -> "
                f"{line_b.strength_value}{line_b.strength_unit}).",
            )
        )

    if same_form and not doses_equal(line_a.dose_value, line_a.dose_unit, line_b.dose_value, line_b.dose_unit):
        discrepancies.append(
            _placeholder_discrepancy(
                "DOSE_CHANGE", [idx_a], [idx_b],
                f"{line_a.substance}: dosering gewijzigd ({line_a.dose_value} {line_a.dose_unit} -> "
                f"{line_b.dose_value} {line_b.dose_unit}).",
            )
        )

    freq_a = frequency_core(line_a.frequency_canonical)
    freq_b = frequency_core(line_b.frequency_canonical)
    if freq_a != freq_b:
        discrepancies.append(
            _placeholder_discrepancy(
                "FREQUENCY_CHANGE", [idx_a], [idx_b],
                f"{line_a.substance}: frequentie gewijzigd ({line_a.frequency_canonical} -> "
                f"{line_b.frequency_canonical}).",
            )
        )

    if not same_form:
        discrepancies.append(
            _placeholder_discrepancy(
                "FORM_CHANGE", [idx_a], [idx_b],
                f"{line_a.substance}: toedieningsvorm gewijzigd ({line_a.form} -> {line_b.form}).",
            )
        )

    return discrepancies


def diff(lines_a: list[MedicationLine], lines_b: list[MedicationLine], pairs: list) -> list[Discrepancy]:
    discrepancies: list[Discrepancy] = []
    for idx_a, idx_b in pairs:
        if idx_a is not None and idx_b is not None:
            discrepancies.extend(_compare_matched_pair(idx_a, idx_b, lines_a[idx_a], lines_b[idx_b]))
        elif idx_a is not None:
            line = lines_a[idx_a]
            discrepancies.append(
                _placeholder_discrepancy(
                    "STOPPED", [idx_a], [],
                    f"{line.substance} komt niet meer voor in lijst B.",
                )
            )
        elif idx_b is not None:
            line = lines_b[idx_b]
            discrepancies.append(
                _placeholder_discrepancy(
                    "ADDED", [], [idx_b],
                    f"{line.substance} nieuw gestart, komt niet voor in lijst A.",
                )
            )
    return discrepancies
