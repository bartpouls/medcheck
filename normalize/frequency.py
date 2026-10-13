"""Frequentiecanonicalisatie.

Twee dingen expliciet uit elkaar gehouden, conform INTENDED_USE.md v1.0 §4:
- de **core** (doseerinstructie: hoe vaak/hoeveel) -- telt mee voor FREQUENCY_CHANGE.
- de **modifier** (gebruiksinstructie/innamemoment, bv. "'s avonds", "nuchter") --
  puur informatief, telt NOOIT mee bij het bepalen van een discrepantie.

Let op (workshopgoud, zie de workshopvoorbereiding (privé) en casus 022): een wekelijkse frequentie
("1x per week") wordt NOOIT gelijkgesteld aan een dagelijkse ("1dd1") — dat is precies
de overdrachtsfout die casus 022 opzettelijk test. Alleen expliciet als
dagfrequentie-varianten herkende notaties worden onderling gelijkgesteld.
"""

import re

_MODIFIER_PATTERNS = [
    r"'s\s*avonds",
    r"'s\s*(?:ochtends|morgens)",
    r"'s\s*middags",
    r"'s\s*nachts",
    r"nuchter",
]


def extract_modifier(text: str) -> str:
    found = []
    for pat in _MODIFIER_PATTERNS:
        m = re.search(pat, text)
        if m:
            found.append(re.sub(r"\s+", " ", m.group(0).strip().lower()))
    return " ".join(sorted(found))


def strip_modifiers(text: str) -> str:
    t = text
    for pat in _MODIFIER_PATTERNS:
        t = re.sub(pat, " ", t)
    t = re.sub(r"[,.]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _canonical_core(core: str) -> str:
    """Herkent de meest voorkomende dagfrequentie-notaties en zet ze om naar 'Ndd1'.
    Alles wat niet herkend wordt (incl. wekelijkse/zo-nodig-notaties) blijft letterlijk
    staan -- expliciet géén stille aanname over klinische gelijkwaardigheid."""
    t = core.strip().lower()
    if not t:
        return t

    m = re.match(r"^(\d+)\s*dd\s*1$", t)
    if m:
        return f"{m.group(1)}dd1"

    m = re.match(r"^(\d+)\s*x\s*(per\s*dag|daags)?$", t)
    if m:
        return f"{m.group(1)}dd1"

    m = re.match(r"^om de (\d+) uur$", t)
    if m:
        hours = int(m.group(1))
        if hours > 0 and 24 % hours == 0:
            return f"{24 // hours}dd1"
        return t

    if t in ("1 tablet", "1"):
        return "1dd1"

    return t


def frequency_core(frequency_text: str, dose_text: str = "") -> str:
    """De doseerinstructie-kern, modifiers eruit gefilterd. Dit is het enige dat
    diff.py gebruikt om FREQUENCY_CHANGE te bepalen."""
    freq = (frequency_text or "").strip().lower()
    core = strip_modifiers(freq)
    canonical_core = _canonical_core(core)

    if not canonical_core:
        # frequentie compleet leeg/alleen modifier -- val terug op "1 tablet" uit dosis
        # als enige aanwijzing voor eenmaal daags (bekend patroon in casus 015)
        dose_core = _canonical_core((dose_text or "").strip().lower())
        if dose_core == "1dd1":
            canonical_core = "1dd1"

    return canonical_core


def canonical_frequency(frequency_text: str, dose_text: str = "") -> str:
    """Volledige canonieke weergave (core + modifier) voor opslag/weergave in
    MedicationLine.frequency_canonical. Gebruik `frequency_core` voor vergelijking."""
    freq = (frequency_text or "").strip().lower()
    modifier = extract_modifier(freq)
    core = frequency_core(frequency_text, dose_text)
    if modifier:
        return f"{core} {modifier}".strip()
    return core
