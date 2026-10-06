"""Escalatie- en severity-bepaling, volgens de regels in CLAUDE.md ("Escalatieregels").

Severity is hier bewust minimaal en generiek gehouden: CLAUDE.md/RISK_ANALYSIS.md
documenteren risicoklassen en escalatietriggers, maar geen fijnmazige laag/midden/hoog/
kritiek-toewijzingsregel per situatie. Zelf een verfijnde severity-heuristiek verzinnen
zou precies het "AI verzint klinische heuristieken" risico zijn dat WORKSHOP_26AUG.md
expliciet waarschuwt te vermijden. `requires_escalation` volgt wél direct en volledig uit
de gedocumenteerde regels; `severity` is een grove, consistente indicatie -- geen
klinisch fijnafgestelde score. Zie het bouwrapport voor de volledige toelichting.
"""

from models import Discrepancy, MedicationLine
from reference import load_high_risk


def is_high_risk(line: MedicationLine) -> bool:
    data = load_high_risk()
    atc = line.atc or ""
    substance = line.substance.strip().lower()
    for risk_class in data["risk_classes"]:
        for prefix in risk_class.get("atc_prefixes", []):
            if atc.startswith(prefix):
                return True
        for code in risk_class.get("atc_codes", []):
            if atc == code:
                return True
        for example in risk_class.get("voorbeelden", []):
            if example.strip().lower() == substance:
                return True
    return False


def classify(
    disc_type: str,
    line_a: MedicationLine | None,
    line_b: MedicationLine | None,
) -> tuple[str, bool]:
    """Geeft (severity, requires_escalation) terug voor een discrepantie."""
    involved = [line for line in (line_a, line_b) if line is not None]
    risky = any(is_high_risk(line) for line in involved)

    if disc_type == "DUPLICATE_THERAPY":
        return "hoog", True

    if disc_type == "STOPPED":
        no_reason = not (line_a.stop_reason or "").strip() if line_a else True
        escalate = risky or no_reason
        if risky:
            severity = "hoog"
        elif no_reason:
            severity = "midden"
        else:
            severity = "laag"
        return severity, escalate

    # ADDED, DOSE_CHANGE, FREQUENCY_CHANGE, FORM_CHANGE, STRENGTH_CHANGE
    severity = "hoog" if risky else "midden"
    return severity, risky


def apply_triage(discrepancies: list[Discrepancy], lines_a: list, lines_b: list) -> list[Discrepancy]:
    result = []
    for disc in discrepancies:
        if disc.type == "DUPLICATE_THERAPY":
            severity, escalate = "hoog", True
        else:
            line_a = lines_a[disc.lines_a[0]] if disc.lines_a else None
            line_b = lines_b[disc.lines_b[0]] if disc.lines_b else None
            severity, escalate = classify(disc.type, line_a, line_b)
        result.append(disc.model_copy(update={"severity": severity, "requires_escalation": escalate}))
    return result
