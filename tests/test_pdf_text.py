"""Test de tabel-/tekst-naar-record-logica van parsing/pdf_text.py los van echte
PDF-bestanden (geen PDF-schrijver beschikbaar zonder nieuwe dependency, zie
MVP_OPZET.md). Dit isoleert de canonicalisatielogica van pdfplumber's I/O -- de
werkelijke `parse_pdf`-functie is alleen te toetsen op een echte tekst-PDF, die nog
niet bestaat (zie bouwrapport)."""

from parsing.pdf_text import _diagnose_unreadable, _rows_from_table, _rows_from_text


def test_rows_from_table_uses_header_aliases():
    table = [
        ["middel", "sterkte", "vorm", "dosering", "frequentie", "route", "zo_nodig", "gestart", "gestopt", "reden_stop"],
        ["amoxicilline", "500 mg", "tablet", "1 tablet", "3dd1", "oraal", "nee", "2026-01-01", "", ""],
    ]
    records = _rows_from_table(table)
    assert records == [
        {
            "middel": "amoxicilline", "sterkte": "500 mg", "vorm": "tablet", "dosering": "1 tablet",
            "frequentie": "3dd1", "route": "oraal", "zo_nodig": "nee", "gestart": "2026-01-01",
            "gestopt": "", "reden_stop": "",
        }
    ]


def test_rows_from_table_rejects_unknown_header():
    table = [["foo", "bar"], ["1", "2"]]
    assert _rows_from_table(table) == []


def test_rows_from_text_parses_csv_like_lines():
    text = "middel,sterkte,vorm,dosering,frequentie,route,zo_nodig,gestart,gestopt,reden_stop\namoxicilline,500 mg,tablet,1 tablet,3dd1,oraal,nee,2026-01-01,,"
    records = _rows_from_text(text)
    assert len(records) == 1
    assert records[0]["middel"] == "amoxicilline"


def test_diagnose_unreadable_flags_scanned_pdf_when_no_text_and_large_image():
    # Casus 029-vorm: vrijwel geen tekst, één afbeelding die de pagina domineert.
    message = _diagnose_unreadable("", [(0, 88.0)])
    assert "gescande/foto-PDF" in message
    assert "vision-extractie" in message
    assert "88%" in message


def test_diagnose_unreadable_flags_unsupported_format_when_text_present():
    message = _diagnose_unreadable("Wel tekst maar geen bekend format" * 3, [(102, 0.0)])
    assert "wel selecteerbare tekst gevonden" in message
    assert "diagnose_pdf_layout.py" in message


def test_diagnose_unreadable_treats_small_image_alongside_text_as_unsupported_format():
    # Tekst + een klein logo/afbeelding is geen scan -- moet niet als scan geflagd worden.
    message = _diagnose_unreadable("Ruim voldoende tekst " * 10, [(210, 15.0)])
    assert "wel selecteerbare tekst gevonden" in message
