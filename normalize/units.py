"""Eenheidsnormalisatie: parsen van sterkte/dosis-tekst en vergelijken over eenheden heen."""

import re
from typing import Optional

_UNIT_WORD_ALIASES = {
    "microgram": "mcg",
    "µg": "mcg",
    "ug": "mcg",
    "mcg": "mcg",
    "milligram": "mg",
    "mg": "mg",
    "gram": "g",
    "g": "g",
    "milliliter": "ml",
    "ml": "ml",
    "eenheden": "IE",
    "eenheid": "IE",
    "ie": "IE",
    "e": "IE",
}

_MASS_TO_MG = {"mcg": 0.001, "mg": 1.0, "g": 1000.0}

_DOSE_UNIT_ALIASES = {
    "tablet": "tablet",
    "tabletten": "tablet",
    "capsule": "capsule",
    "capsules": "capsule",
    "ml": "ml",
    "eenheid": "eenheid",
    "eenheden": "eenheid",
    "pleister": "pleister",
    "pleisters": "pleister",
    "stuk": "stuk",
}

_LEADING_NUMBER = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*(.*)$")


def _normalize_unit_word(word: str) -> str:
    key = word.lower().strip()
    return _UNIT_WORD_ALIASES.get(key, key)


def normalize_unit_text(text: str) -> str:
    """Normaliseert los-tekstuele eenheidsnotatie (bv. samengestelde sterktes als
    '160/4,5 microgram') zonder een enkele numerieke waarde te vereisen."""
    if not text:
        return ""
    t = text.strip().lower()
    for word, canon in _UNIT_WORD_ALIASES.items():
        t = re.sub(rf"\b{re.escape(word)}\b", canon.lower(), t)
    return t


def parse_quantity(text: Optional[str] = None) -> tuple:
    """Splitst tekst als '5 mg' / '0,25 mg' / '2 tabletten' in (waarde, eenheid).
    Bij een samengestelde/niet-numerieke tekst (bv. '5/80 mg', 'volgens doseerschema')
    wordt (None, genormaliseerde_tekst) teruggegeven."""
    if not text:
        return None, ""
    match = _LEADING_NUMBER.match(text.strip())
    if not match:
        return None, normalize_unit_text(text)
    value_str, rest = match.groups()
    if "/" in rest or "/" in text:
        return None, normalize_unit_text(text)
    try:
        value = float(value_str.replace(",", "."))
    except ValueError:
        return None, normalize_unit_text(text)
    unit = _normalize_unit_word(rest.strip())
    return value, unit


_WEEK_DOSE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(mg|mcg|g)\s*week\s*(\d+)", re.I)
_CURRENT_WEEK = re.compile(r"nu\s*week\s*(\d+)", re.I)


def parse_titration_schedule(text: str) -> tuple:
    """Deterministische tekstextractie (geen klinische aanname): een afbouw-/
    titratieschema dat expliciet '(nu week N)' vermeldt naast een lijst
    'Xmg weekN' -- pakt de dosis bij de aangegeven huidige week. Levert (None, tekst)
    als het patroon niet exact aanwezig is; geen gok bij afwijkende schrijfwijzen."""
    current = _CURRENT_WEEK.search(text)
    if not current:
        return None, normalize_unit_text(text)
    week_no = current.group(1)
    for value_str, unit, week in _WEEK_DOSE.findall(text):
        if week == week_no:
            return float(value_str.replace(",", ".")), _normalize_unit_word(unit)
    return None, normalize_unit_text(text)


def normalize_dose_unit(unit: str) -> str:
    return _DOSE_UNIT_ALIASES.get(unit.lower().strip(), unit.lower().strip())


def strengths_equal(value_a, unit_a: str, value_b, unit_b: str, raw_a: str = "", raw_b: str = "") -> bool:
    if value_a is not None and value_b is not None:
        if unit_a in _MASS_TO_MG and unit_b in _MASS_TO_MG:
            return abs(value_a * _MASS_TO_MG[unit_a] - value_b * _MASS_TO_MG[unit_b]) < 1e-6
        return unit_a == unit_b and abs(value_a - value_b) < 1e-9
    # geen van beide (of een van beide) numeriek te parsen -- val terug op
    # genormaliseerde tekstvergelijking (bv. samengestelde sterktes)
    return normalize_unit_text(raw_a) == normalize_unit_text(raw_b)


def doses_equal(value_a, unit_a: str, value_b, unit_b: str) -> bool:
    if value_a is None or value_b is None:
        return value_a == value_b
    norm_a, norm_b = normalize_dose_unit(unit_a), normalize_dose_unit(unit_b)
    # "stuk" is het systeembrede, vorm-agnostische standaardaantal (models.py:
    # MedicationLine.dose_unit default, parsing/common.py's fallback zonder
    # herkende eenheid) -- het staat voor "aantal van de vorm", dus vergelijkbaar
    # met elke specifieke telbare eenheid (tablet, capsule, ...), niet alleen met
    # zichzelf. Voorkomt een valse DOSE_CHANGE wanneer één bron "1 stuk" zegt en de
    # andere "1 tablet" voor dezelfde, ongewijzigde dosis (zie casus 027).
    if "stuk" in (norm_a, norm_b):
        return abs(value_a - value_b) < 1e-9
    return norm_a == norm_b and abs(value_a - value_b) < 1e-9
