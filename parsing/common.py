"""Gedeelde rij-naar-MedicationLine-logica voor CSV- en tekst-PDF-parser.

Beide bronformaten leveren uiteindelijk records met dezelfde canonieke veldnamen op
(zie HEADER_ALIASES); vanaf hier is de verwerking bestandstype-onafhankelijk, zoals
vastgelegd in MVP_OPZET.md.
"""

from models import MedicationLine, PatientIdentity
from normalize import units
from normalize.frequency import canonical_frequency
from locales.nl import brands as locale_nl
from locales.nl import patient_id as locale_nl_patient_id

# Twee headersets komen in de praktijk voor in data/casus/ (zie CASUS_FORMAAT_PROMPTS.md
# groep 1 en de canonieke generator-output) -- de parser is kolomvolgorde- en
# taal-onafhankelijk zolang de kolomnaam bekend is.
HEADER_ALIASES = {
    "middel": "substance",
    "drug_name": "substance",
    "sterkte": "strength",
    "strength": "strength",
    "vorm": "form",
    "dose_form": "form",
    "form": "form",
    "dosering": "dose",
    "dose": "dose",
    "frequentie": "frequency",
    "frequency": "frequency",
    "route": "route",
    "zo_nodig": "prn",
    "prn_flag": "prn",
    "prn": "prn",
    "gestart": "start_date",
    "start_date": "start_date",
    "gestopt": "stop_date",
    "stop_date": "stop_date",
    "reden_stop": "stop_reason",
    "stop_reason": "stop_reason",
    "bsn": "bsn",
    "patient_bsn": "bsn",
    "patient_naam": "patient_name",
    "naam_patient": "patient_name",
    "patient_name": "patient_name",
    "geboortedatum": "birth_date",
    "geboorte_datum": "birth_date",
    "birth_date": "birth_date",
    "dob": "birth_date",
}

_TRUE_VALUES = {"ja", "true", "1", "yes"}


def canonicalize_record(raw_record: dict) -> dict:
    """Zet een dict met willekeurige kolomnaamvolgorde/-taal om naar de canonieke
    veldnamen uit HEADER_ALIASES. Onbekende kolommen worden genegeerd (niet gegokt)."""
    out = {}
    for key, value in raw_record.items():
        if key is None:
            continue
        canon = HEADER_ALIASES.get(key.strip().lower())
        if canon:
            out[canon] = (value or "").strip() if isinstance(value, str) else value
    return out


def _parse_strength(strength_text: str) -> tuple:
    value, unit = units.parse_quantity(strength_text)
    if value is None and "nu week" in (strength_text or "").lower():
        value, unit = units.parse_titration_schedule(strength_text)
    return value, unit


def record_to_lines(record: dict, source: str) -> list[MedicationLine]:
    """Zet één canoniek record om in een of meer MedicationLine's. Meer dan één regel
    ontstaat alleen bij een bekend combinatiepreparaat (zie
    locales/nl/brands.py:COMBO_BRANDS) -- de ontleding is expliciet, geen gok."""
    raw_substance = record.get("substance", "")
    dose_text = record.get("dose", "") or ""
    frequency_text = record.get("frequency", "") or ""
    route = (record.get("route", "") or "").strip().lower()
    prn = (record.get("prn", "") or "").strip().lower() in _TRUE_VALUES
    stop_date = record.get("stop_date", "") or None
    stop_reason = record.get("stop_reason", "") or ""
    form = (record.get("form", "") or "").strip().lower()
    strength_text = record.get("strength", "") or ""
    freq_canon = canonical_frequency(frequency_text, dose_text)
    dose_value, dose_unit = units.parse_quantity(dose_text)
    if dose_unit:
        dose_unit = units.normalize_dose_unit(dose_unit)
    else:
        dose_unit = "stuk"

    components = locale_nl.combo_components(raw_substance)
    if components:
        lines = []
        for comp in components:
            lines.append(
                MedicationLine(
                    atc=comp["atc"],
                    substance=comp["substance"],
                    brand=raw_substance,
                    strength_value=comp["strength_value"],
                    strength_unit=comp["strength_unit"],
                    form=form,
                    dose_value=dose_value,
                    dose_unit=dose_unit,
                    frequency_canonical=freq_canon,
                    prn=prn,
                    route=route,
                    raw_text=f"{raw_substance} {strength_text}, {frequency_text}".strip(),
                    confidence=1.0,
                    source=source,
                    stop_date=stop_date,
                    stop_reason=stop_reason,
                )
            )
        return lines

    substance, atc = locale_nl.resolve_substance(raw_substance)
    strength_value, strength_unit = _parse_strength(strength_text)
    is_brand = substance.lower() != raw_substance.strip().lower()

    return [
        MedicationLine(
            atc=atc,
            substance=substance,
            brand=raw_substance if is_brand else "",
            strength_value=strength_value,
            strength_unit=strength_unit,
            form=form,
            dose_value=dose_value,
            dose_unit=dose_unit,
            frequency_canonical=freq_canon,
            prn=prn,
            route=route,
            raw_text=f"{raw_substance} {strength_text}, {frequency_text}".strip(),
            confidence=1.0,
            source=source,
            stop_date=stop_date,
            stop_reason=stop_reason,
        )
    ]


def records_to_lines(records: list, source: str) -> list[MedicationLine]:
    lines: list[MedicationLine] = []
    for raw_record in records:
        record = canonicalize_record(raw_record)
        lines.extend(record_to_lines(record, source))
    return lines


def extract_patient_identity(records: list) -> PatientIdentity:
    """Patiëntidentiteit is documentniveau, niet regelniveau -- bij CSV/tekst-PDF staat
    dit doorgaans op elke rij herhaald (of alleen de eerste). Pak de eerste niet-lege
    waarde per veld, negeer de rest. Ontbrekende kolommen leveren lege strings op
    (record.get() vindt niets); dat is bewust "niet gevonden", geen gok."""
    bsn = ""
    name = ""
    birth_date = ""
    for raw_record in records:
        record = canonicalize_record(raw_record)
        bsn = bsn or (record.get("bsn") or "")
        name = name or (record.get("patient_name") or "")
        birth_date = birth_date or (record.get("birth_date") or "")
        if bsn and name and birth_date:
            break

    normalized_bsn = locale_nl_patient_id.normalize_bsn(bsn) if bsn else ""
    bsn_valid = locale_nl_patient_id.is_valid_bsn(normalized_bsn) if normalized_bsn else None
    return PatientIdentity(
        bsn=normalized_bsn,
        bsn_valid=bsn_valid,
        name=name.strip(),
        birth_date=birth_date.strip(),
    )
