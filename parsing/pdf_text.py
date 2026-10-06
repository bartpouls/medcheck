"""Tekst-PDF-parser: alleen voor PDF's met selecteerbare tekst. Geen AI, geen vision --
puur deterministische tekst-onttrekking via pdfplumber. Vijf paden, geprobeerd in
volgorde (breedste vocab-gedreven herkenning eerst, smallere heuristieken als val-terug):

1. Generiek, vocab-gedreven medicatieoverzicht (NHG/KNMP-begrippenset, EPD-/
   apotheeksysteemexports als HIX/CGM Apotheek/ASP) -> locales/nl/pdf_parser.py.
2. Patiëntvriendelijk "Uw medicatie"-overzicht (Start/Doorgaan/Stop-secties, ASP
   patiëntportaal) -> locales/nl/patient_portal_parser.py.
3. Generieke tabel-lay-out met een bekende canonieke kolomkop (HEADER_ALIASES,
   bv. gegenereerde testfixtures) -> parsing/common.py.
4. Generieke kommagescheiden tekstregels met zo'n kop -> parsing/common.py.
5. Eén bekend, vast briefsjabloon (Sint Barbara Ziekenhuis-ontslagbrief, casus 006-010)
   -> locales/nl/prose_parser.py.

Pad 1 was tot 2026-08-26 twee losse, bijna-identieke sjabloonparsers (parsing/hix.py,
parsing/cgm_apotheek.py); die bleken beide op dezelfde landelijke veldterminologie te
herleiden en zijn vervangen door één vocab-gedreven parser (zie JOURNEY.md 2026-08-26
sessie 9 en locales/nl/pdf_parser.py's eigen moduledocstring voor de grenzen daarvan).
Pad 2 en pad 5 blijven wel sjabloonspecifiek: vrije tekst/vaste secties laten zich niet
op kolomlabels herkennen, zie de eigen moduledocstrings van
locales/nl/patient_portal_parser.py resp. locales/nl/prose_parser.py. Alle drie zijn
Nederlandse landmodules (`locales/nl/`); dit bestand zelf (`parsing/pdf_text.py`) hoort
bij de taal-agnostische kern en roept de locale-parsers alleen aan, geen NL-specifieke
logica hierin.

Gescande/foto-PDF's (geen selecteerbare tekst) vallen hier nog steeds buiten -- dat
blijft fase 2 (vision-extractie), zie MVP_OPZET.md.
"""

from pathlib import Path

import pdfplumber

from errors import DiagnosableError
from locales.nl.patient_portal_parser import UnparsablePatientPortalError, parse_patient_portal_pdf_text
from locales.nl.pdf_parser import UnparsableGenericError, parse_generic
from locales.nl.prose_parser import UnparsableProseError, parse_prose_pdf_text
from models import MedicationLine, PatientIdentity
from parsing.common import HEADER_ALIASES, extract_patient_identity, records_to_lines


class UnreadablePdfError(DiagnosableError, RuntimeError):
    """Geen bruikbare tabel/tekst/bekend briefsjabloon gevonden -- CLAUDE.md regel 4:
    geen stille fixes, hard falen in plaats van gokken of leeg resultaat teruggeven."""


def _rows_from_table(table: list) -> list:
    if not table or len(table) < 2:
        return []
    header = [(cell or "").strip().lower() for cell in table[0]]
    if not any(h in HEADER_ALIASES for h in header):
        return []
    records = []
    for row in table[1:]:
        record = {header[i]: (row[i] or "").strip() if i < len(row) else "" for i in range(len(header))}
        records.append(record)
    return records


def _rows_from_text(text: str) -> list:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    if len(lines) < 2:
        return []
    header = [h.strip().lower() for h in lines[0].split(",")]
    if not any(h in HEADER_ALIASES for h in header):
        return []
    records = []
    for line in lines[1:]:
        cells = [c.strip() for c in line.split(",")]
        record = {header[i]: (cells[i] if i < len(cells) else "") for i in range(len(header))}
        records.append(record)
    return records


def _max_image_coverage_pct(page) -> float:
    """Grootste percentage van de pagina dat één ingesloten afbeelding beslaat --
    zelfde berekening als scripts/diagnose_pdf_layout.py, hier hergebruikt om
    scan-/foto-PDF's automatisch te herkennen i.p.v. alleen via het losse script."""
    if not page.width or not page.height:
        return 0.0
    coverages = (100 * img["width"] * img["height"] / (page.width * page.height) for img in page.images)
    return max(coverages, default=0.0)


def _diagnose_unreadable(full_text: str, page_stats: list[tuple[int, float]]) -> str:
    """Onderscheidt de twee hoofdoorzaken van UnreadablePdfError, zodat de melding
    zegt WAAROM het niet werkte i.p.v. alleen DAT het niet werkte (CLAUDE.md regel 4:
    luid falen, geen gok -- en de vlag zelf zo informatief mogelijk). Drempels (50
    tekens, 50% dekking) zijn een vuistregel, geijkt op casus 029 (0 tekens, ~88%
    dekking, zie docs/JOURNEY.md 2026-08-28 sessie 16) en bewust ruim genomen."""
    total_chars = len(full_text.strip())
    max_coverage = max((cov for _chars, cov in page_stats), default=0.0)
    if total_chars < 50 and max_coverage >= 50:
        return (
            f"Vermoedelijk een gescande/foto-PDF: slechts {total_chars} teken(s) "
            f"selecteerbare tekst gevonden, terwijl een ingesloten afbeelding tot "
            f"~{round(max_coverage)}% van een pagina beslaat. Controleer met Ctrl+A of "
            "tekst te selecteren is. Tekst-extractie werkt hier niet -- dat vraagt "
            "vision-extractie (fase 2, nog niet gebouwd). Zie docs/BACKLOG.md "
            "'Nieuwe bronsystemen' (casus 029)."
        )
    return (
        f"Er is wel selecteerbare tekst gevonden ({total_chars} teken(s)), maar geen "
        "van de ondersteunde formaten herkende de indeling -- waarschijnlijk een nog "
        "niet ondersteund bronsysteem. Draai voor een structurele diagnose (geen "
        "patiëntdata in de output) `python scripts/diagnose_pdf_layout.py <bestand>` "
        "en zie docs/BACKLOG.md 'Nieuwe bronsystemen'."
    )


def parse_pdf(path: Path, source: str) -> list[MedicationLine]:
    all_tables = []
    all_records = []
    all_words = []
    full_text_parts = []
    page_stats: list[tuple[int, float]] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables() or []
            all_tables.extend(page_tables)
            for table in page_tables:
                all_records.extend(_rows_from_table(table))
            page_text = page.extract_text()
            full_text_parts.append(page_text or "")
            page_stats.append((len(page_text or ""), _max_image_coverage_pct(page)))
            if not all_records:
                all_records.extend(_rows_from_text(page_text))
            all_words.extend(page.extract_words())

    full_text = "\n".join(full_text_parts)

    try:
        return parse_generic(all_tables, all_words, full_text, source)
    except UnparsableGenericError:
        pass

    try:
        return parse_patient_portal_pdf_text(full_text, source)
    except UnparsablePatientPortalError:
        pass

    if all_records:
        return records_to_lines(all_records, source)

    try:
        return parse_prose_pdf_text(full_text, source)
    except UnparsableProseError as exc:
        # Bewust GEEN losse deelparser-reden hier (bv. de Sint Barbara-specifieke
        # tekst) als hoofdmelding -- dat zou suggereren dat de applicatie één
        # bepaald format "verwacht", terwijl vijf paden geprobeerd zijn en geen
        # ervan matchte. De laatst geprobeerde deelreden blijft wel beschikbaar via
        # de exception chain (`from exc`) voor wie in de logs/stacktrace duikt.
        raise UnreadablePdfError(
            f"Geen van de ondersteunde medicatieoverzicht-formaten herkend in "
            f"{path.name} (kolomtabel, patiëntportaaloverzicht, of briefsjabloon).",
            _diagnose_unreadable(full_text, page_stats),
        ) from exc


def parse_pdf_identity(path: Path) -> PatientIdentity:
    """Patiëntidentiteit uit het tekst-PDF-pad. Alleen de generieke tabel/tekst-paden
    (2 en 3, zie moduledocstring) leveren hiervoor bruikbare records op -- de
    vocab-gedreven parser (pad 1) en het briefsjabloon (pad 4) herkennen kolomkoppen
    niet op dezelfde manier en hebben nog geen eigen identiteitsextractie (openstaand,
    zie docs/BACKLOG.md). Dat leidt niet tot een fout: identity.py behandelt "geen
    identiteit gevonden" als een niet-blokkerende waarschuwing, niet als een gok
    (CLAUDE.md regel 4 geldt voor de medicatie-extractie zelf, die blijft ongewijzigd)."""
    all_records = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                all_records.extend(_rows_from_table(table))
            if not all_records:
                all_records.extend(_rows_from_text(page.extract_text()))
    return extract_patient_identity(all_records)
