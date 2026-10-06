"""Laadt de referentiebestanden uit data/reference/ (172 middelen, risicoklassen).

Beide bestanden zijn expliciet gelabeld 'CONCEPT -- ongeverifieerd door mens' in hun
eigen _meta.waarschuwing (zie data/reference/README.md). Dat blijft zo totdat Bart's
eigen steekproef is afgerond; deze module verandert daar niets aan, ze laadt alleen.
"""

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REFERENCE_DIR = ROOT / "data" / "reference"


@lru_cache(maxsize=1)
def load_atc_subset() -> dict:
    with open(REFERENCE_DIR / "atc_subset.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_high_risk() -> dict:
    with open(REFERENCE_DIR / "high_risk.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_duplicate_classes() -> dict:
    with open(REFERENCE_DIR / "duplicate_classes.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def substance_to_atc() -> dict:
    return {m["substance"].lower(): m["atc"] for m in load_atc_subset()["middelen"]}


@lru_cache(maxsize=1)
def brand_to_substance() -> dict:
    mapping = {}
    for m in load_atc_subset()["middelen"]:
        for brand in m.get("brands_nl", []):
            mapping[brand.lower()] = m["substance"]
    return mapping
