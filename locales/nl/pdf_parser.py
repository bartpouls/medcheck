"""Generieke parser voor Nederlandse medicatieoverzicht-PDF's -- gedreven door de
landelijke synoniemenlijst in locales/nl/vocab.py, niet door één letterlijk
documentsjabloon per leverancier. Vervangt de eerdere, bijna-identieke `parsing/hix.py`
en `parsing/cgm_apotheek.py` (zie JOURNEY.md 2026-08-26 sessie 9 voor de aanleiding: die
twee bleken op de gedeelde NHG/KNMP-begrippenset achter Nictiz' AMO/MP9-informatiestandaard
te herleiden, wat generalisatie zonder gokken mogelijk maakt).

Twee structurele extractiewegen, allebei vocab-gedreven, geen van beide vendor-specifiek:

1. **Tabelpad** (`_parse_table`): pdfplumber's `extract_tables()` levert cellen.
   De koprij wordt herkend aan de combinatie van (a) een letterlijke sectiemarker
   ("huidige medicatie" e.d.) EN (b) minstens twee herkende kolomlabels in diezelfde
   rijtekst -- dat onderscheidt een echte medicatiekop van een gelijkende rij elders
   in hetzelfde PDF-object (bv. "RECENT BEËINDIGDE MEDICATIE" deelt kolomlabels maar
   niet de sectiemarker-frase, zie HIX-voorbeeld). Twee subvarianten van de koprij zelf:
   per-kolom kopcellen (kolomindex volgt direct uit de kopcel zelf), of alle
   kopwoorden samengevoegd in één cel (zoals HIX) -- in dat laatste geval is er geen
   directe kolomindex per label, dus wordt elk veld (in leesvolgorde, stofnaam
   voorop) gekoppeld aan de eerstvolgende kolom in de eerste databodyrij die qua
   *celinhoud* bij dat veld past (`_align_columns_by_shape`); tussenliggende,
   niet-herkende kolommen (kloktijden, toelichting, voorschrijver) worden overgeslagen.
   Derde variant (zoals ASP, casus 028): sectiemarker en kolomlabels op twee aparte
   rijen (titelrij, dan een eigen koprij met per-kolom kopcellen) -- de sectiemarker
   mag daarom ook in de rij vlak BOVEN de koprij staan, niet alleen in de koprij zelf.

2. **Positioneel pad** (`_parse_positional`): geen pdfplumber-tabel (zoals CGM
   Apotheek, geen zichtbare cellijnen). Koplabels worden gezocht in de losse woorden
   van de pagina; hun x-positie bepaalt de kolomgrenzen dynamisch (niet hardgecodeerd
   per leverancier -- elke kolom zonder herkend label, zoals een merknaam-kolom, valt
   buiten de gevonden kolomgrenzen en wordt genegeerd). Rijen worden daarna
   gegroepeerd via de verticale afstand tussen tekstregels.

In beide paden geldt: een koprij zonder minstens twee herkende labels betekent "dit is
niet de medicatietabel" (geen match, geen gok). Bij het lezen van databodyrijen wordt
een rij die niet in het verwachte "<stof> [zout] <vorm> <sterkte> [restant]" resp.
"<N> x per dag <dosis>"-patroon past, ALLEEN overgeslagen zolang er nog geen enkele
geldige rij gevonden is (dan is het vermoedelijk kopregel-restant, bv. een tweede/derde
regel van een meertalige koptekst) -- zodra er wél al een geldige rij is gevonden,
betekent een niet-passende rij het natuurlijke einde van de sectie. Dit is een bewuste,
gedocumenteerde grens van CLAUDE.md regel 4: geen letterlijke eindmarker per bron nodig
(dat zou weer vendor-specifiek zijn), maar wel het risico dat een echt kapotte
medicatieregel binnen de sectie stilzwijgend als "einde sectie" gelezen wordt i.p.v. als
fout gemeld. Zie JOURNEY.md 2026-08-26 sessie 9 voor de afweging.
"""

import re

from models import MedicationLine
from normalize.frequency import extract_modifier, strip_modifiers
from locales.nl.vocab import (
    COLUMN_LABELS,
    EMPTY_DOSE_MARKERS,
    FREQUENCY_TIMES_WOORDEN,
    ROUTE_BY_VORM,
    SALT_WOORDEN,
    SECTION_MARKERS,
    VORM_PATTERNS,
)
from parsing.common import records_to_lines

_VORM_ALT = "|".join(VORM_PATTERNS)
_STERKTE_RE = r"[\d,.]+(?:MG/ML|MG|MCG|G|ML)(?:=\d+[A-Z]+)?"

# Eén zoutwoord (bv. "hcl", "succinaat" -- zie SALT_WOORDEN in nl_medication_vocab.py)
# tussen stofnaam en vorm is toegestaan, gedreven door dezelfde gesloten lijst -- niet
# elk willekeurig extra woord.
_SALT_ALT = "|".join(re.escape(w) for w in SALT_WOORDEN)
_TIMES_ALT = "|".join(re.escape(w) for w in FREQUENCY_TIMES_WOORDEN)

_MIDDEL_CEL_RE = re.compile(
    rf"^(?P<middel>[A-Za-zÀ-ÿ]+)(?:\s+(?:{_SALT_ALT}))?\s+"
    rf"(?P<vorm>{_VORM_ALT})\s+"
    rf"(?P<sterkte>{_STERKTE_RE})"
    rf"(?:\s+(?P<modifier>.+))?$",
    re.IGNORECASE,
)
_DOSERING_RE = re.compile(rf"^(?P<freq>\d+\s*(?:{_TIMES_ALT})\s*per\s*dag)\s+(?P<dose>.+)$", re.IGNORECASE)
_DATE_RE = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")
_EMPTY_DOSE_TEXT = "geen dosering geregistreerd"

_LINE_TOLERANCE = 3.0  # pt; woorden binnen deze marge op dezelfde tekstregel
_ROW_GAP_THRESHOLD = 14.0  # pt; grotere sprong dan dit tussen regels = nieuwe rij


class UnparsableGenericError(RuntimeError):
    """Geen herkenbare medicatiesectie/-kolomkop gevonden, of een celwaarde past niet
    in het verwachte patroon -- hard falen (CLAUDE.md regel 4), niet gokken."""


def detect(full_text: str) -> bool:
    lowered = (full_text or "").lower()
    return any(marker in lowered for marker in SECTION_MARKERS)


def _contains_section_marker(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in SECTION_MARKERS)


def _find_labels_in_text(text: str) -> list[str]:
    """Zoekt bekende kolomlabels (op woordgrens) in tekst, geeft veldnamen terug in
    volgorde van voorkomen -- die volgorde bepaalt bij een samengevoegde koprij welke
    positie in de databodyrij bij welk veld hoort."""
    lowered = text.lower()
    hits = []
    for field, synonyms in COLUMN_LABELS.items():
        best_pos = None
        for syn in synonyms:
            m = re.search(rf"\b{re.escape(syn)}\b", lowered)
            if m and (best_pos is None or m.start() < best_pos):
                best_pos = m.start()
        if best_pos is not None:
            hits.append((best_pos, field))
    hits.sort(key=lambda pair: pair[0])
    return [field for _, field in hits]


def _parse_middel_cell(text: str) -> dict:
    line = (text or "").strip().splitlines()[0].strip() if text else ""
    match = _MIDDEL_CEL_RE.match(line)
    if not match:
        raise UnparsableGenericError(
            f"Onherkende stofnaam-cel: '{line}'. Herkent alleen '<stof> [zout] <vorm> "
            "<sterkte> [restant]' met vorm/zout uit locales/nl/vocab.py."
        )
    fields = match.groupdict()
    vorm = re.sub(r"\s+", " ", fields["vorm"].strip().lower())
    return {"middel": fields["middel"], "vorm": vorm, "sterkte": fields["sterkte"].strip()}


def _is_empty_dose(line: str) -> bool:
    return line in EMPTY_DOSE_MARKERS


def _parse_dosering_cell(text: str) -> dict:
    """Splitst frequentie + dosis; een innamemoment-modifier zonder scheidingsteken
    ("2 tabletten 's morgens") hoort bij de frequentie (wanneer), niet bij de dosis
    (hoeveel) -- zie parsing/cgm_apotheek.py's oorspronkelijke onderbouwing.

    Een letterlijke lege-dosering-marker (EMPTY_DOSE_MARKERS, bv. ".") is een
    expliciete, gedocumenteerde waarde -- geen onherkend patroon dat moet falen, en
    zeker geen stille drop (CLAUDE.md regel 4 / SAFETY.md automation bias)."""
    line = (text or "").strip().splitlines()[0].strip() if text else ""
    if _is_empty_dose(line):
        return {"frequentie": _EMPTY_DOSE_TEXT, "dosering": ""}
    match = _DOSERING_RE.match(line)
    if not match:
        raise UnparsableGenericError(
            f"Onherkende dosering-cel: '{line}'. Herkent alleen '<N> x per dag <dosis>'."
        )
    freq = match.group("freq")
    dose = match.group("dose").strip()
    modifier = extract_modifier(dose)
    if modifier:
        dose = strip_modifiers(dose)
        freq = f"{freq} {modifier}"
    return {"frequentie": freq, "dosering": dose}


def _split_stopdatum(text: str) -> tuple:
    cell = re.sub(r"\s+", " ", (text or "").strip())
    if not cell or cell in ("- -", "--"):
        return "", ""
    if _DATE_RE.match(cell):
        return cell, ""
    return "", cell


def _cells_to_record(cells: dict) -> dict:
    """cells: veldnaam -> celtekst, voor precies één medicatierij. Vult ontbrekende
    velden aan (route uit vorm, dosering/frequentie uit één gecombineerde cel indien
    geen aparte kolommen gevonden zijn)."""
    if "strength" in cells or "form" in cells:
        middel = (cells.get("substance") or "").strip().splitlines()[0].strip()
        vorm = (cells.get("form") or "").strip().lower()
        sterkte = (cells.get("strength") or "").strip()
        if not middel or not vorm or not sterkte:
            raise UnparsableGenericError(f"Onvolledige medicatierij (aparte kolommen): {cells!r}")
    else:
        parsed = _parse_middel_cell(cells.get("substance", ""))
        middel, vorm, sterkte = parsed["middel"], parsed["vorm"], parsed["sterkte"]

    if "frequency" in cells and "dose" in cells:
        frequentie = (cells.get("frequency") or "").strip()
        dosering = (cells.get("dose") or "").strip()
        if not frequentie or not dosering:
            raise UnparsableGenericError(f"Onvolledige medicatierij (dosering/frequentie): {cells!r}")
    else:
        dosering_bron = cells.get("dose") or cells.get("frequency") or ""
        parsed_dosering = _parse_dosering_cell(dosering_bron)
        frequentie, dosering = parsed_dosering["frequentie"], parsed_dosering["dosering"]

    route = (cells.get("route") or "").strip().lower() or ROUTE_BY_VORM.get(vorm, "")
    gestopt, reden_stop = _split_stopdatum(cells.get("stop_date", ""))
    if cells.get("stop_reason"):
        reden_stop = cells["stop_reason"].strip()

    return {
        "middel": middel,
        "sterkte": sterkte,
        "vorm": vorm,
        "dosering": dosering,
        "frequentie": frequentie,
        "route": route,
        "zo_nodig": "ja" if cells.get("prn") else "nee",
        "gestart": (cells.get("start_date") or "").strip(),
        "gestopt": gestopt,
        "reden_stop": reden_stop,
    }


# Alleen deze velden worden daadwerkelijk gebruikt door _cells_to_record -- een
# herkend label voor iets anders (bv. "voorschrijver") wordt genegeerd bij het
# uitlijnen van kolommen, zodat het geen kolom "opeet" die eigenlijk voor een wél
# gebruikt veld bedoeld is.
_USED_FIELDS = {"substance", "strength", "form", "dose", "frequency", "route", "prn", "start_date", "stop_date", "stop_reason"}
_ROUTE_WOORDEN = set(ROUTE_BY_VORM.values())


def _looks_like_middel_cell(text: str) -> bool:
    first_line = (text or "").strip().splitlines()[0].strip() if text else ""
    return bool(_MIDDEL_CEL_RE.match(first_line))


def _looks_like_dosering_cell(text: str) -> bool:
    first_line = (text or "").strip().splitlines()[0].strip() if text else ""
    return _is_empty_dose(first_line) or bool(_DOSERING_RE.match(first_line))


def _looks_like_route(text: str) -> bool:
    return (text or "").strip().lower() in _ROUTE_WOORDEN


def _looks_like_date(text: str) -> bool:
    cell = re.sub(r"\s+", " ", (text or "").strip())
    return bool(_DATE_RE.match(cell)) or cell in ("- -", "--")


# Shape-check per veld voor de "samengevoegde koprij"-uitlijning hieronder: True zodra
# een celwaarde plausibel bij dit veld hoort. stop_date is bewust permissief (accepteert
# ook vrije tekst als "Tot nader order gestopt", zie parsing/hix.py's oorspronkelijke
# onderbouwing) -- dat mag omdat de uitlijning start_date altijd eerst consumeert, dus
# de kolom die overblijft voor stop_date staat al vast vóórdat deze check draait.
_SHAPE_CHECKS = {
    "substance": _looks_like_middel_cell,
    "start_date": _looks_like_date,
    "stop_date": lambda text: True,
    "dose": _looks_like_dosering_cell,
    "frequency": _looks_like_dosering_cell,
    "route": _looks_like_route,
}


def _align_columns_by_shape(field_order: list, sample_row: list) -> dict:
    """Voor een 'samengevoegde koprij' (alle koplabels in één cel, zoals HIX) is er
    geen directe kolomindex per label. In plaats van de tekstvolgorde blindelings op
    kolomindexen te plakken (breekt zodra er tussenliggende, niet-herkende kolommen
    zijn zoals HIX's 'Tijden'/'Toelichting'), wordt elk veld -- 'substance' voorop,
    daarna de herkende labels in leesvolgorde -- gekoppeld aan de eerstvolgende kolom
    in `sample_row` die qua celinhoud bij dat veld past (zie _SHAPE_CHECKS). Kolommen
    die bij geen van de gezochte velden passen (bv. kloktijden, toelichting,
    voorschrijver) worden stilzwijgend overgeslagen -- niet gebruikt, niet fout."""
    fields = [f for f in field_order if f in _USED_FIELDS and f != "substance"]
    if "substance" not in fields:
        fields = ["substance", *fields]

    field_to_col: dict = {}
    col_index = 0
    for field in fields:
        check = _SHAPE_CHECKS.get(field, lambda text: True)
        while col_index < len(sample_row) and not check(sample_row[col_index]):
            col_index += 1
        if col_index < len(sample_row):
            field_to_col[field] = col_index
            col_index += 1
    return field_to_col


def _header_row_field_map(header_row: list) -> dict:
    """Header met per-kolom kopcellen (elke cel z'n eigen label): kolomindex direct
    uit de celpositie zelf, geen uitlijning nodig. Geeft, net als
    `_align_columns_by_shape`, veldnaam -> kolomindex terug (niet andersom) -- zie
    `_parse_table`, die beide paden via dezelfde inversie naar col->field omzet."""
    field_to_col = {}
    for i, cell in enumerate(header_row):
        labels = _find_labels_in_text(cell or "")
        if labels and labels[0] not in field_to_col:
            field_to_col[labels[0]] = i
    return field_to_col


def _parse_table(table: list) -> list[dict]:
    header_idx, header_row_text, header_row = None, None, None
    prev_row_text = None
    for i, row in enumerate(table):
        row_text = " ".join((c or "") for c in row)
        has_marker = _contains_section_marker(row_text) or (
            prev_row_text is not None and _contains_section_marker(prev_row_text)
        )
        if has_marker and len(_find_labels_in_text(row_text)) >= 2:
            header_idx, header_row_text, header_row = i, row_text, row
            break
        prev_row_text = row_text
    if header_idx is None:
        return []

    data_rows = table[header_idx + 1 :]
    if not data_rows:
        return []

    non_empty_cells = sum(1 for c in header_row if (c or "").strip())
    if non_empty_cells > 1:
        field_to_col = _header_row_field_map(header_row)
    else:
        field_order = _find_labels_in_text(header_row_text)
        field_to_col = _align_columns_by_shape(field_order, data_rows[0])
    if not field_to_col:
        raise UnparsableGenericError(
            f"Koprij herkend maar geen enkel kolomveld kon aan een databodykolom "
            f"gekoppeld worden: '{header_row_text}'."
        )
    col_to_field = {col: field for field, col in field_to_col.items()}

    records: list[dict] = []
    for row in data_rows:
        if not row or not (row[0] or "").strip():
            if records:
                break
            continue
        cells = {field: (row[col] if col < len(row) else "") for col, field in col_to_field.items()}
        try:
            records.append(_cells_to_record(cells))
        except UnparsableGenericError:
            if records:
                break
            continue
    return records


def _column(x0: float, anchors: list) -> str | None:
    field = None
    for anchor_field, anchor_x0 in anchors:
        if x0 >= anchor_x0 - _LINE_TOLERANCE:
            field = anchor_field
        else:
            break
    return field


def _group_lines(words: list) -> list:
    lines: list = []
    for word in sorted(words, key=lambda w: w["top"]):
        if lines and abs(word["top"] - lines[-1]["top"]) <= _LINE_TOLERANCE:
            lines[-1]["words"].append(word)
        else:
            lines.append({"top": word["top"], "words": [word]})
    return lines


def _group_rows(lines: list) -> list:
    rows: list = []
    prev_top = None
    for line in lines:
        if prev_top is None or (line["top"] - prev_top) > _ROW_GAP_THRESHOLD:
            rows.append([])
        rows[-1].append(line)
        prev_top = line["top"]
    return rows


def _find_word_label_anchors(words: list) -> list:
    """Zoekt, per kolomlabel, het eerste (bovenste) woord dat er (op woordgrens)
    exact mee overeenkomt -- alleen enkelwoordige labelherkenning; meerwoordlabels in
    COLUMN_LABELS worden hier genegeerd (positioneel pad heeft ze vooralsnog niet
    nodig, zie casus 026/027). Geeft (veldnaam, x0)-paren terug, gesorteerd op x0."""
    single_word_labels: dict[str, str] = {}
    for field, synonyms in COLUMN_LABELS.items():
        for syn in synonyms:
            if " " not in syn:
                single_word_labels.setdefault(syn, field)

    hits: dict[str, tuple] = {}
    for word in sorted(words, key=lambda w: w["top"]):
        cleaned = word["text"].strip(",.():").lower()
        field = single_word_labels.get(cleaned)
        if field and field not in hits:
            hits[field] = (word["top"], word["x0"])
    if not hits:
        return [], None
    header_top = max(top for top, _x0 in hits.values())
    anchors = sorted(((field, x0) for field, (_top, x0) in hits.items()), key=lambda pair: pair[1])
    return anchors, header_top


def _parse_positional(words: list) -> list[dict]:
    anchors, header_top = _find_word_label_anchors(words)
    if len(anchors) < 2:
        return []

    data_words = [w for w in words if w["top"] > header_top + _LINE_TOLERANCE]
    lines = _group_lines(data_words)
    rows = _group_rows(lines)

    records: list[dict] = []
    for row_lines in rows:
        cols: dict[str, list[str]] = {}
        for line in row_lines:
            for word in sorted(line["words"], key=lambda w: w["x0"]):
                field = _column(word["x0"], anchors)
                if field:
                    cols.setdefault(field, []).append(word["text"])
        cells = {field: " ".join(parts).strip() for field, parts in cols.items()}
        if not cells:
            if records:
                break
            continue
        try:
            records.append(_cells_to_record(cells))
        except UnparsableGenericError:
            if records:
                break
            continue
    return records


def parse_generic(tables: list, words: list, full_text: str, source: str) -> list[MedicationLine]:
    if not detect(full_text):
        raise UnparsableGenericError(
            "Geen bekende medicatieoverzicht-sectiemarker gevonden "
            "(zie locales/nl/vocab.py:SECTION_MARKERS)."
        )

    for table in tables:
        records = _parse_table(table)
        if records:
            return records_to_lines(records, source)

    records = _parse_positional(words)
    if records:
        return records_to_lines(records, source)

    raise UnparsableGenericError(
        "Sectiemarker gevonden, maar geen kolomkop met minstens twee herkende labels "
        "(zie locales/nl/vocab.py:COLUMN_LABELS) in tabellen of losse tekst."
    )
