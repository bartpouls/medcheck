"""Structurele diagnose van een medicatieoverzicht-PDF -- ZONDER de inhoud te tonen.

Bedoeld om een echt bronbestand (dus met echte patiëntdata) te debuggen zonder het
bestand, een screenshot, of de ruwe tekst ervan te hoeven delen (CLAUDE.md regel 1):
dit script print alleen structurele feiten (aantal tabellen/rijen/cellen, WELKE
kolomlabels/sectiemarkers herkend worden -- interne veldnamen als "substance"/"dose",
nooit de brontekst zelf). Geef alleen de output van dit script door, nooit het
bestand.

Gebruik: python scripts/diagnose_pdf_layout.py <pad-naar-pdf>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pdfplumber

from locales.nl.patient_portal_parser import detect as patient_portal_detect
from locales.nl.pdf_parser import (
    _contains_section_marker,
    _find_labels_in_text,
    _find_word_label_anchors,
    detect,
)
from locales.nl.prose_parser import _SECTION_RE


def _row_summary(row: list) -> str:
    row_text = " ".join((c or "") for c in row)
    labels = _find_labels_in_text(row_text)
    marker = _contains_section_marker(row_text)
    return f"{len(row)} cel(len), sectiemarker={marker}, herkende labels={labels}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = Path(sys.argv[1])

    full_text_parts = []
    all_words = []
    with pdfplumber.open(path) as pdf:
        for page_i, page in enumerate(pdf.pages):
            print(f"=== pagina {page_i} ===")
            tables = page.extract_tables() or []
            print(f"{len(tables)} tabel(len) gevonden door pdfplumber")
            for t_i, table in enumerate(tables):
                print(f"  tabel {t_i}: {len(table)} rij(en)")
                for r_i, row in enumerate(table):
                    print(f"    rij {r_i}: {_row_summary(row)}")
            page_text = page.extract_text() or ""
            full_text_parts.append(page_text)
            all_words.extend(page.extract_words())
            print(f"{len(page_text)} teken(s) doorzoekbare tekst op deze pagina")
            print(f"{len(page.images)} ingesloten afbeelding(en) op deze pagina")
            for img_i, img in enumerate(page.images):
                width, height = round(img["width"], 1), round(img["height"], 1)
                dekking = round(100 * width * height / (page.width * page.height))
                print(f"  afbeelding {img_i}: {width}x{height}pt, dekt ~{dekking}% van de pagina")

    full_text = "\n".join(full_text_parts)

    print("\n=== samenvatting (pad 1: generieke tabel, pad 2: patiëntportaal, pad 5: Sint Barbara) ===")
    print(f"pad 1 detect() -- generieke parser triggert op sectiemarker: {detect(full_text)}")

    anchors, header_top = _find_word_label_anchors(all_words)
    anchor_fields = [field for field, _x0 in anchors]
    print(f"pad 1 positioneel: {len(anchors)} kolomanker(s) gevonden -- velden: {anchor_fields}")

    lowered = full_text.lower()
    print(f"pad 2 detect() -- patiëntportaalparser triggert: {patient_portal_detect(full_text)}")
    print(f"  bevat 'uw medicatie': {'uw medicatie' in lowered}")
    print(f"  bevat 'start met deze medicatie': {'start met deze medicatie' in lowered}")
    print(f"  bevat 'doorgaan met deze medicatie': {'doorgaan met deze medicatie' in lowered}")
    print(f"  bevat 'stop deze medicatie': {'stop deze medicatie' in lowered}")

    prose_match = bool(_SECTION_RE.search(full_text))
    print(f"pad 5 Sint Barbara-briefsjabloon ('Medicatie bij ontslag'-sectie): {prose_match}")


if __name__ == "__main__":
    main()
