"""NL-landmodule: merknaam -> stofnaam, stofnaam -> ATC, combinatiepreparaten.

CLAUDE.md: normalisatie-backbone is ATC (internationaal); alles wat NL-specifiek is
(merknamen, combipreparaat-samenstelling) hoort hier en nergens anders.
"""

import reference

# Combinatiepreparaten: merken die uit meerdere stofnamen bestaan. Klein, handmatig
# bijgehouden -- alleen de merken die in de huidige casusset voorkomen. Uitbreiden
# zodra een nieuwe casus/praktijkgeval een ander combipreparaat vereist.
COMBO_BRANDS = {
    "exforge": [
        {"substance": "amlodipine", "atc": "C08CA01", "strength_value": 5.0, "strength_unit": "mg"},
        {"substance": "valsartan", "atc": "C09CA03", "strength_value": 80.0, "strength_unit": "mg"},
    ],
}


def resolve_substance(name: str) -> tuple:
    """Geeft (stofnaam, atc) terug voor een merknaam of stofnaam. Onbekende termen
    komen terug als (oorspronkelijke_naam_lowercase, None) -- CLAUDE.md regel 4: nooit
    stilzwijgend gokken, onbekend blijft zichtbaar onbekend."""
    key = name.strip().lower()
    substance_map = reference.substance_to_atc()
    if key in substance_map:
        return key, substance_map[key]
    brand_map = reference.brand_to_substance()
    if key in brand_map:
        substance = brand_map[key]
        return substance, substance_map.get(substance.lower())
    return key, None


def combo_components(name: str):
    """Geeft de samenstellende stoffen van een combinatiepreparaat terug, of None
    als de naam geen bekend combipreparaat is."""
    return COMBO_BRANDS.get(name.strip().lower())
