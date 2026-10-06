import csv
from pathlib import Path

from errors import DiagnosableError
from models import MedicationLine, PatientIdentity
from parsing.common import HEADER_ALIASES, extract_patient_identity, records_to_lines


class UnreadableCsvError(DiagnosableError, RuntimeError):
    """Kopregel leeg, of geen enkele kolomnaam herkend -- CLAUDE.md regel 4: luid
    falen i.p.v. stil 0 regels teruggeven. `canonicalize_record` negeert onbekende
    kolommen bewust wanneer ze NAAST bekende kolommen staan (parsing/common.py); dat
    is iets anders dan GEEN enkele kolom herkennen, wat op een verkeerd bestand/
    format wijst, niet op een paar extra kolommen."""


def _delimiter_hint(fieldnames: list[str]) -> str:
    """Herkent de meest voorkomende oorzaak van 'geen kolom herkend': een niet-komma-
    gescheiden bestand (bv. Excel-NL exporteert CSV standaard met ';', omdat ',' daar
    het decimaalteken is) dat als één lange kolomnaam binnenkomt."""
    if len(fieldnames) != 1:
        return ""
    candidate = fieldnames[0]
    for delim, label in ((";", "puntkomma"), ("\t", "tab")):
        parts = [p.strip().lower() for p in candidate.split(delim)]
        if any(p in HEADER_ALIASES for p in parts):
            return f" Ziet eruit als {label}-gescheiden (vaak Excel/NL-notatie) i.p.v. komma."
    return ""


def _read_records(path: Path) -> list[dict]:
    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            records = list(reader)
            fieldnames = list(reader.fieldnames or [])
    except UnicodeDecodeError as exc:
        raise UnreadableCsvError(
            f"{path.name} is niet leesbaar als UTF-8-tekst (byte {exc.start}: {exc.reason}).",
            "Waarschijnlijk een Excel-export in Windows-1252/Latin-1 -- sla het bestand "
            "opnieuw op als UTF-8 CSV en probeer opnieuw.",
        ) from exc

    if not fieldnames:
        raise UnreadableCsvError(f"{path.name} heeft geen koprij (leeg bestand?).")

    known = [h for h in fieldnames if h.strip().lower() in HEADER_ALIASES]
    if not known:
        detail_parts = [
            _delimiter_hint(fieldnames).strip(),
            f"Bekende koppen (NL/EN): {sorted(set(HEADER_ALIASES))}.",
        ]
        raise UnreadableCsvError(
            f"Geen van de kolomkoppen in {path.name} herkend: {fieldnames}.",
            " ".join(p for p in detail_parts if p),
        )
    return records


def parse_csv(path: Path, source: str) -> list[MedicationLine]:
    return records_to_lines(_read_records(path), source)


def parse_csv_identity(path: Path) -> PatientIdentity:
    return extract_patient_identity(_read_records(path))
