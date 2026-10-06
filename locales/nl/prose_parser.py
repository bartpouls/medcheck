"""Sjabloon-specifieke parser voor het 'Sint Barbara Ziekenhuis'-ontslagbriefformaat
(casus 006-010): vaste briefopbouw, vaste zinsconstructie per middel ("Patiënt gebruikt
<middel> <sterkte>, <frequentie in woorden> <aantal> <vorm>."), consistent over meerdere
casus. Dat maakt dit -- ondanks dat het geen tabel is -- net zo deterministisch
parseerbaar als een label:value-medicatieoverzicht uit een systeem: één vast sjabloon,
geen vrije clinicus-tekst.

Expliciet GEEN generieke ontslagbrief-/NLP-parser: een zin die niet in het bekende
patroon past levert een harde fout op (CLAUDE.md regel 4), geen gok. Nieuwe
briefsjablonen (ander ziekenhuis, andere zinsbouw) hebben een eigen parser nodig --
uitbreiden is een bewuste, aparte stap, geen automatische generalisatie.

Bekende encoding-eigenaardigheid in de huidige casus-PDF's: 'ë' komt uit pdfplumber
als U+FFFD ('�') -- vermoedelijk een fontencoding-probleem in de bron-PDF's zelf. De
regex hieronder is daar bewust ongevoelig voor (matcht beide varianten); dit is aparte
feedback voor wie deze PDF's genereert, geen parserfout.
"""

import re

from models import MedicationLine
from parsing.common import records_to_lines

_E_TREMA = "[ë�]"

_SECTION_RE = re.compile(
    # Case-gevoelig en regelgebonden (^...$ per regel): de brieftekst noemt "medicatie
    # bij ontslag" ook los in een inleidende zin ("...over de actuele medicatie bij
    # ontslag."). Alleen de kop op een eigen regel, met hoofdletter, is de echte sectiestart.
    r"^Medicatie bij ontslag\s*\n(.*?)\nMet vriendelijke groet",
    re.MULTILINE | re.DOTALL,
)
_EMPTY_RE = re.compile(r"geen (?:vaste )?medicijnen|geen medicatie", re.IGNORECASE)

_CONNECTORS = [
    rf"Pati{_E_TREMA}nt gebruikt",
    rf"Tevens gebruikt pati{_E_TREMA}nt",
    rf"Ook gebruikt pati{_E_TREMA}nt",
    rf"Daarnaast gebruikt pati{_E_TREMA}nt",
]
_CONNECTOR_SPLIT_RE = re.compile("(?:" + "|".join(_CONNECTORS) + r")\s+", re.IGNORECASE)

_FREQ_WORDS = {"eenmaal": "1", "tweemaal": "2", "driemaal": "3", "viermaal": "4"}

_CLAUSE_RE = re.compile(
    r"^(?P<middel>[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-]*)\s+"
    r"(?P<sterkte_waarde>[\d,]+)\s*(?P<sterkte_eenheid>mg|microgram|mcg|g|ml)\s*,\s*"
    r"(?P<freq_woord>eenmaal|tweemaal|driemaal|viermaal)\s+(?P<freq_eenheid>daags|per week|per dag)"
    r"(?:\s+(?P<aantal>\d+)\s+(?P<vorm>tablet(?:ten)?|capsule(?:s)?|ml|pleister(?:s)?))?"
    r"(?:\s+(?P<modifier>'s\s*avonds|'s\s*ochtends|'s\s*middags|'s\s*nachts|nuchter))?"
    r"\s*\.?\s*$",
    re.IGNORECASE,
)


class UnparsableProseError(RuntimeError):
    """Het ontslagbriefsjabloon is herkend, maar een zin binnen de medicatiesectie
    past niet in het bekende patroon -- hard falen (CLAUDE.md regel 4), niet gokken."""


def _clause_to_record(clause: str) -> dict:
    match = _CLAUSE_RE.match(clause.strip())
    if not match:
        raise UnparsableProseError(
            f"Onherkende zinsvorm in de medicatiesectie: '{clause.strip()}'. Dit "
            "sjabloon herkent alleen 'gebruikt <middel> <sterkte>, <frequentie> "
            "<aantal> <vorm>' -- pas de parser aan (locales/nl/prose_parser.py) of gebruik "
            "een ander pad voor deze brief."
        )
    fields = match.groupdict()
    freq_number = _FREQ_WORDS[fields["freq_woord"].lower()]
    if fields["freq_eenheid"].lower() == "per week":
        frequency = f"{freq_number}x per week"
    else:
        frequency = f"{freq_number}dd1"
    modifier = (fields["modifier"] or "").strip()
    if modifier:
        frequency = f"{frequency} {modifier}"

    dose = f"{fields['aantal']} {fields['vorm']}" if fields["aantal"] else ""

    return {
        "middel": fields["middel"],
        "sterkte": f"{fields['sterkte_waarde']} {fields['sterkte_eenheid']}",
        "vorm": (fields["vorm"] or "").rstrip("s") if fields["vorm"] else "",
        "dosering": dose,
        "frequentie": frequency,
        "route": "oraal",
        "zo_nodig": "nee",
        "gestart": "",
        "gestopt": "",
        "reden_stop": "",
    }


def parse_ontslagbrief(text: str) -> list:
    section_match = _SECTION_RE.search(text)
    if not section_match:
        raise UnparsableProseError(
            "Geen 'Medicatie bij ontslag'-sectie gevonden -- dit is niet het "
            "verwachte Sint Barbara-ontslagbriefsjabloon."
        )
    section = re.sub(r"\s+", " ", section_match.group(1)).strip()

    if _EMPTY_RE.search(section):
        return []

    clauses = [c.strip() for c in _CONNECTOR_SPLIT_RE.split(section) if c.strip()]
    return [_clause_to_record(clause) for clause in clauses]


def parse_prose_pdf_text(text: str, source: str) -> list[MedicationLine]:
    records = parse_ontslagbrief(text)
    return records_to_lines(records, source)
