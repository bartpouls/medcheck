"""Matching tussen lijst A en lijst B.

Matching-key bevat bewust GEEN sterkte/dosis/frequentie/vorm -- alleen stof en route.
Dat zijn precies de velden die engine/diff.py ná het matchen per gematcht paar
vergelijkt om STRENGTH_CHANGE/DOSE_CHANGE/FREQUENCY_CHANGE/FORM_CHANGE te bepalen
(zie MVP_OPZET.md, sectie 6) -- vorm zat er eerder wél in, maar dat maakte een
vormwijziging (casus 005) onherkenbaar als gematcht paar; zie het bouwrapport.
Fallback op stofnaam zit al in locales/nl/brands.py (merknaam wordt vóór matching
naar stofnaam vertaald)."""

from collections import defaultdict

from models import MedicationLine

MatchPair = tuple


def match_key(line: MedicationLine) -> tuple:
    # Vorm zit hier bewust NIET in: een vormwijziging (casus 005, tablet -> drank) moet
    # als gematcht paar met FORM_CHANGE herkend worden, niet als STOPPED+ADDED.
    return (line.substance.strip().lower(), line.route.strip().lower())


def match_lines(lines_a: list[MedicationLine], lines_b: list[MedicationLine]) -> list[MatchPair]:
    a_by_key: dict = defaultdict(list)
    for i, line in enumerate(lines_a):
        a_by_key[match_key(line)].append(i)
    b_by_key: dict = defaultdict(list)
    for i, line in enumerate(lines_b):
        b_by_key[match_key(line)].append(i)

    pairs: list[MatchPair] = []
    for key in set(a_by_key) | set(b_by_key):
        a_idxs = a_by_key.get(key, [])
        b_idxs = b_by_key.get(key, [])
        for i in range(max(len(a_idxs), len(b_idxs))):
            a_idx = a_idxs[i] if i < len(a_idxs) else None
            b_idx = b_idxs[i] if i < len(b_idxs) else None
            pairs.append((a_idx, b_idx))

    pairs.sort(key=lambda p: (p[0] if p[0] is not None else 10**6, p[1] if p[1] is not None else 10**6))
    return pairs
