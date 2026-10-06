"""Sjabloon-specifieke parser voor een patiëntvriendelijk "Uw medicatie"-overzicht:
secties "Start met deze medicatie" / "Doorgaan met deze medicatie" / "Stop deze
medicatie", met een Ochtend/Middag/Avond/Voor de nacht/Zo nodig-tijdvakraster ernaast.
Voorbeeld: ASP (Apotheek Service Punt) van een ziekenhuis, 2026-08-28 -- zie
data/local/casus/029-praktijkcasus-asp-patientportaal/notes.md voor de bronfragmenten
(veilig gedeeld: getypte/geschermafbeelde medicatietekst, geen patiëntgegevens).

Zelfde aanpak als locales/nl/prose_parser.py: vaste zinsconstructies per sectie, geen
vrije tekst -- een regel die niet in het bekende patroon past faalt hard (CLAUDE.md
regel 4), wordt niet gegokt. Bewust een EIGEN kopregex i.p.v. pdf_parser.py's
_MIDDEL_CEL_RE hergebruikt/verruimd: dit format zet sterkte vóór de vorm
("diclofenac 50mg tablet MSR"), _MIDDEL_CEL_RE verwacht vorm vóór sterkte
("IRBESARTAN TABLET 75MG") -- twee woordordes in één regex vergroot het risico op een
foute match in allebei; een aparte regex per sjabloon is veiliger.

Het Ochtend/Middag/Avond/Voor de nacht/Zo nodig-vinkjesraster wordt NIET zelf gelezen:
de doseerzin ernaast ("Drie keer per dag ...", "Indien nodig ...") bevat dezelfde
informatie al in tekstvorm en is betrouwbaarder dan vinkjes/checkmark-glyphs uit een
PDF halen (die extractie is broos, niet CLAUDE.md-regel-4-proof).

Bewuste aanname, Bart's akkoord nodig (zie JOURNEY.md 2026-08-28 sessie 14): een regel
onder "Stop deze medicatie" heeft in dit format geen datum/reden. Wordt hier WEL
opgenomen (niet stilzwijgend weggelaten) met lege stop_date/stop_reason -- de
bestaande triage-regel "STOPPED zonder geregistreerde reden" escaleert 'm dan vanzelf.
Stilzwijgend uitsluiten van de lijst zou de veiligere keuze precies omdraaien.

Nog NIET bevestigd tegen de echte PDF-bytes -- alleen tegen letterlijk overgetypte/
geschermafbeelde tekstfragmenten. Met name paginabreuk-gedrag ("Doorgaan met deze
medicatie (vervolg)" suggereert dat een sectie over meerdere pagina's kan lopen) is
ongeverifieerd. Loud-fail bij onbekende regelvormen is hier extra belangrijk zolang
dat zo is.
"""

import re

from models import MedicationLine
from parsing.common import records_to_lines
from locales.nl.vocab import ROUTE_BY_VORM, VORM_PATTERNS

_STERKTE_RE = r"[\d,.]+\s*(?:MG/ML|MG|MCG|G|ML)"
_VORM_ALT = "|".join(VORM_PATTERNS)

_KOP_RE = re.compile(
    rf"^(?P<middel>[A-Za-zÀ-ÿ]+)\s+(?P<sterkte>{_STERKTE_RE})\s+(?P<vorm>{_VORM_ALT})$",
    re.IGNORECASE,
)
_STOP_OP_RE = re.compile(r"^Gebruik stoppen op:\s*(?P<datum>.+?)\.?$", re.IGNORECASE)
_GENERIEK_RE = re.compile(r"^Generiek medicijn:\s*.+$", re.IGNORECASE)

_GETAL_WOORDEN = {"een": "1", "twee": "2", "drie": "3", "vier": "4", "vijf": "5", "zes": "6"}

_FREQ_DOSE_RE = re.compile(
    r"^(?P<telwoord>\w+)\s+keer per dag(?:\s+gedurende\s+\d+\s+doses)?\.\s*"
    r"Innemen\s+(?P<aantal>\d+)\s+(?P<eenheid>[A-Za-z]+)(?:\s*\([^)]*\))?\.?$",
    re.IGNORECASE,
)
_PRN_DOSE_RE = re.compile(
    r"^Indien nodig\.\s*Innemen\s+(?P<aantal>\d+)\s+(?P<eenheid>[A-Za-z]+)\.?$",
    re.IGNORECASE,
)

_SECTION_HEADER_RE = re.compile(
    r"^(?P<naam>Start met deze medicatie|Doorgaan met deze medicatie(?:\s*\(vervolg\))?|"
    r"Stop deze medicatie)\s*$",
    re.IGNORECASE,
)


class UnparsablePatientPortalError(RuntimeError):
    """Het patiëntportaal-sjabloon ('Uw medicatie') is herkend, maar een regel past
    niet in een van de bekende patronen -- hard falen (CLAUDE.md regel 4), niet
    gokken."""


def detect(full_text: str) -> bool:
    lowered = (full_text or "").lower()
    return "uw medicatie" in lowered and any(
        marker in lowered
        for marker in ("start met deze medicatie", "doorgaan met deze medicatie", "stop deze medicatie")
    )


def _dose_from_freqline(line: str) -> tuple[str, str]:
    m = _FREQ_DOSE_RE.match(line)
    if m:
        telwoord = m.group("telwoord").lower()
        getal = _GETAL_WOORDEN.get(telwoord)
        if not getal:
            raise UnparsablePatientPortalError(
                f"Onherkend telwoord in doseerzin: '{line}'. Bekende telwoorden: "
                f"{sorted(_GETAL_WOORDEN)} (locales/nl/patient_portal_parser.py)."
            )
        return f"{getal}dd1", f"{m.group('aantal')} {m.group('eenheid').lower()}"

    m = _PRN_DOSE_RE.match(line)
    if m:
        return "zo nodig", f"{m.group('aantal')} {m.group('eenheid').lower()}"

    raise UnparsablePatientPortalError(
        f"Onherkende doseerzin: '{line}'. Herkent alleen '<telwoord> keer per dag "
        "[gedurende N doses]. Innemen <aantal> <eenheid>[(...)]' of 'Indien nodig. "
        "Innemen <aantal> <eenheid>'."
    )


def _block_to_record(kop_line: str, detail_lines: list[str]) -> dict:
    kop_match = _KOP_RE.match(kop_line.strip())
    if not kop_match:
        raise UnparsablePatientPortalError(
            f"Onherkende medicatiekop: '{kop_line.strip()}'. Verwacht "
            "'<stofnaam> <sterkte> <vorm>' (locales/nl/patient_portal_parser.py)."
        )
    middel = kop_match.group("middel")
    sterkte = re.sub(r"\s+", "", kop_match.group("sterkte"))
    vorm = re.sub(r"\s+", " ", kop_match.group("vorm").strip().lower())

    stop_date = ""
    dosering = ""
    frequentie = ""
    prn = "nee"

    for raw_line in detail_lines:
        line = raw_line.strip()
        if not line or _GENERIEK_RE.match(line):
            continue
        stop_match = _STOP_OP_RE.match(line)
        if stop_match:
            stop_date = stop_match.group("datum").strip()
            continue
        frequentie, dosering = _dose_from_freqline(line)
        if frequentie == "zo nodig":
            prn = "ja"

    route = ROUTE_BY_VORM.get(vorm, "")

    return {
        "middel": middel,
        "sterkte": sterkte,
        "vorm": vorm,
        "dosering": dosering,
        "frequentie": frequentie,
        "route": route,
        "zo_nodig": prn,
        "gestart": "",
        "gestopt": stop_date,
        "reden_stop": "",
    }


def parse_patient_portal(full_text: str) -> list[dict]:
    """Segmenteert de tekst na 'Uw medicatie' in medicatieblokken (kopregel + 0..N
    detailregels, een blok eindigt bij de volgende kopregel, sectiekop, of einde
    tekst). Sectiekoppen zelf leveren geen record op, ze worden alleen gebruikt om
    zeker te zijn dat we ná de titel zitten -- de sectie-naam wordt momenteel niet
    los vastgelegd op de record (geen apart datamodelveld voor "start/doorgaan/stop"
    los van gestopt/gestart, zie moduledocstring)."""
    if not detect(full_text):
        raise UnparsablePatientPortalError(
            "Geen 'Uw medicatie'-sectie met Start/Doorgaan/Stop-indeling gevonden."
        )

    lines = [ln.strip() for ln in full_text.splitlines()]
    start_idx = next((i for i, ln in enumerate(lines) if ln.strip().lower() == "uw medicatie"), None)
    if start_idx is None:
        raise UnparsablePatientPortalError("'Uw medicatie' niet als eigen regel gevonden.")

    records: list[dict] = []
    current_kop: str | None = None
    current_details: list[str] = []

    def _flush():
        if current_kop is not None:
            records.append(_block_to_record(current_kop, current_details))

    for line in lines[start_idx + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if _SECTION_HEADER_RE.match(stripped):
            _flush()
            current_kop, current_details = None, []
            continue
        if _KOP_RE.match(stripped):
            _flush()
            current_kop, current_details = stripped, []
            continue
        if current_kop is None:
            # Nog geen kopregel gezien binnen deze sectie -- vermoedelijk het
            # tijdvakraster ("Ochtend Middag Avond...") of een lege restregel, geen
            # medicatiedetail. Bewust overgeslagen, niet als fout (nog geen enkel
            # medicijn in dit blok om aan toe te wijzen).
            continue
        current_details.append(stripped)
    _flush()

    return records


def parse_patient_portal_pdf_text(text: str, source: str) -> list[MedicationLine]:
    records = parse_patient_portal(text)
    return records_to_lines(records, source)
