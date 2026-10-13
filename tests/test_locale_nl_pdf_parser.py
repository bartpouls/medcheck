"""Test de vocab-gedreven segmentatie-/uitlijningslogica van locales/nl/pdf_parser.py
(voorheen parsing/generic_nl.py, verplaatst bij de i18n-herstructurering) los van
echte PDF's (zelfde aanpak als de eerdere tests/test_hix.py en
tests/test_cgm_apotheek.py, die deze test vervangt nu beide vendor-specifieke
parsers zijn samengevoegd tot één generieke parser -- zie het privé-bouwlog 2026-08-26
sessie 9)."""

import pytest

from locales.nl.pdf_parser import (
    UnparsableGenericError,
    _align_columns_by_shape,
    _cells_to_record,
    _column,
    _contains_section_marker,
    _find_labels_in_text,
    _header_row_field_map,
    _parse_dosering_cell,
    _parse_middel_cell,
    _parse_table,
    _split_stopdatum,
    detect,
)


def test_detect_true_on_section_marker():
    assert detect("... Artsenverklaring / Ärtzliches Attest ...")
    assert detect("HUIDIGE MEDICATIE (op ATC code) Startdatum ...")


def test_detect_false_without_marker():
    assert not detect("iets heel anders")


def test_find_labels_in_text_order_of_appearance():
    text = "HUIDIGE MEDICATIE (op ATC code) Startdatum Stopdatum Dosering TW Actuele voorschrijver"
    assert _find_labels_in_text(text) == ["start_date", "stop_date", "dose", "route", "prescriber"]


def test_find_labels_in_text_word_boundary_no_false_positive():
    # "tw" mag niet toevallig binnenin een ander woord matchen
    assert "route" not in _find_labels_in_text("toelichting actuele voorschrijver")


# -- celwaarde-segmentatie (gedeeld tussen HIX- en CGM-achtige bronnen) --------------


def test_parse_middel_cell_strips_salt_and_reads_form_strength():
    assert _parse_middel_cell("Amitriptyline hcl tablet 10mg") == {
        "middel": "Amitriptyline", "vorm": "tablet", "sterkte": "10mg",
    }


def test_parse_middel_cell_mga_vorm_with_modifier():
    result = _parse_middel_cell("METOPROLOL TABLET MGA 25MG (SUCCINAAT)")
    assert result == {"middel": "METOPROLOL", "vorm": "tablet mga", "sterkte": "25MG"}


def test_parse_middel_cell_injectiepen_with_trailing_annotation():
    result = _parse_middel_cell("SEMAGLUTIDE INJ PEN 0,5MG=1DO (4DO/PEN)+TB")
    assert result["vorm"] == "inj pen"
    assert result["sterkte"] == "0,5MG=1DO"


def test_parse_middel_cell_unknown_shape_raises():
    with pytest.raises(UnparsableGenericError):
        _parse_middel_cell("iets heel anders zonder sterkte")


def test_parse_dosering_cell_moves_time_modifier_to_frequency():
    result = _parse_dosering_cell("1 x per dag 2 tabletten 's morgens 's avonds")
    assert result["dosering"] == "2 tabletten"
    assert "'s morgens" in result["frequentie"] and "'s avonds" in result["frequentie"]


def test_parse_dosering_cell_empty_marker_is_explicit_not_a_guess():
    # ASP, casus 028: "." in de Dosering-kolom betekent "niet ingevuld" -- moet een
    # expliciete waarde opleveren, niet stilzwijgend als kopregel-restant overgeslagen
    # worden (SAFETY.md automation bias) en niet hard falen (het is een herkende,
    # gedocumenteerde waarde, geen onbekend patroon).
    assert _parse_dosering_cell(".") == {"frequentie": "geen dosering geregistreerd", "dosering": ""}


def test_parse_dosering_cell_maal_synoniem_voor_x():
    result = _parse_dosering_cell("1 maal per dag 1 tablet")
    assert result == {"frequentie": "1 maal per dag", "dosering": "1 tablet"}


def test_split_stopdatum_variants():
    assert _split_stopdatum("- -") == ("", "")
    assert _split_stopdatum("13-5-2020") == ("13-5-2020", "")
    assert _split_stopdatum("Tot nader\norder gestopt") == ("", "Tot nader order gestopt")


def test_cells_to_record_infers_route_from_vorm():
    record = _cells_to_record({"substance": "Acenocoumarol tablet 1mg", "dose": "1 x per dag 1 stuk"})
    assert record["route"] == "oraal"


# -- kolomuitlijning: samengevoegde koprij (HIX-achtig) ------------------------------


def test_align_columns_by_shape_skips_unrecognized_middle_columns():
    # bootst HIX na: koplabels start/stop/dose/route gevonden, maar de databodyrij
    # heeft twee extra, niet-herkende kolommen ertussen (kloktijden, toelichting) en
    # een koploze eerste kolom (het middel zelf).
    field_order = ["start_date", "stop_date", "dose", "route", "prescriber"]
    sample_row = [
        "Acenocoumarol tablet 1mg", "1-12-2023", "- -", "1 x per dag 1 stuk",
        "07:00", "", "oraal", "Recourt, H.",
    ]
    field_to_col = _align_columns_by_shape(field_order, sample_row)
    assert field_to_col == {"substance": 0, "start_date": 1, "stop_date": 2, "dose": 3, "route": 6}


def test_align_columns_by_shape_free_text_stop_reason():
    field_order = ["start_date", "stop_date", "dose"]
    sample_row = ["Enalapril tablet 5mg", "13-5-2020", "Tot nader order gestopt", "1 x per dag 1 stuk"]
    field_to_col = _align_columns_by_shape(field_order, sample_row)
    assert field_to_col["stop_date"] == 2


def test_header_row_field_map_direct_per_cell_labels():
    header = ["Sterkte", "Vorm", "Dosering"]
    assert _header_row_field_map(header) == {"strength": 0, "form": 1, "dose": 2}


def test_contains_section_marker_distinguishes_similar_headers():
    # "RECENT BEEINDIGDE MEDICATIE" deelt kolomlabels met "HUIDIGE MEDICATIE" maar
    # bevat geen enkele sectiemarker-frase -- moet dus NIET als kop herkend worden.
    assert not _contains_section_marker(
        "RECENT BEEINDIGDE MEDICATIE (afgelopen 30 d.) Startdatum Stopdatum Dosering"
    )
    assert _contains_section_marker("HUIDIGE MEDICATIE (op ATC code) Startdatum Stopdatum")


# -- volledige tabel, samengevoegde koprij (end-to-end op letterlijke tabelstructuur) -


def test_parse_table_merged_header_end_to_end():
    table = [
        ["Afgegeven door:"],
        [
            "HUIDIGE MEDICATIE (op ATC code) Startdatum Stopdatum Dosering Tijden "
            "Toelichting/Indicatie TW Actuele voorschrijver",
            None, None, None, None, None, None, None,
        ],
        ["Acenocoumarol tablet 1mg", "1-12-2023", "- -", "1 x per dag 1 stuk", "07:00", "", "oraal", "Recourt, H."],
        ["Enalapril tablet 5mg", "13-5-2020", "Tot nader\norder gestopt", "1 x per dag 1 stuk", "07:00", "", "oraal", "Werf, M."],
        ["RECENT BEEINDIGDE MEDICATIE (afgelopen 30 d.) Startdatum Stopdatum Dosering", None, None, None, None, None, None, None],
    ]
    records = _parse_table(table)
    assert [r["middel"] for r in records] == ["Acenocoumarol", "Enalapril"]
    assert records[0]["gestart"] == "1-12-2023"
    assert records[1]["reden_stop"] == "Tot nader order gestopt"


def test_parse_table_no_header_returns_empty():
    assert _parse_table([["foo", "bar"], ["1", "2"]]) == []


def test_parse_table_title_row_separate_from_label_row():
    # ASP (openbare apotheek, casus 028): sectietitel staat als eigen rij BOVEN de
    # koprij met per-kolom kopcellen, niet samengevoegd zoals bij HIX. Kolomvolgorde
    # en -namen nagebootst op basis van de chat-upload; dosering hier met een
    # herkenbaar "N x per dag"-patroon (de "." /"1 maal per dag"-varianten uit de
    # echte ASP-casus zijn een apart, nog open punt -- zie
    # data/local/casus/028-praktijkcasus-asp-testpat/notes.md).
    table = [
        ["Medicatie (Voorschriften/ Afleveringen)", None, None, None, None, None, None],
        ["Geneesmiddel (op ATC code)", "Datum", "Einddatum", "Dosering", "Toelichting", "TW", "Actuele Voorschrijver"],
        ["IRBESARTAN TABLET 75MG", "", "", "1 x per dag 1 tablet", "", "ORAAL", "()"],
        ["Gestopte en gewijzigde medicatie", None, None, None, None, None, None],
        ["Geneesmiddel (op ATC code)", "Datum", "Einddatum", "Dosering", "Toelichting", "TW", "Actuele Voorschrijver"],
    ]
    records = _parse_table(table)
    assert [r["middel"] for r in records] == ["IRBESARTAN"]
    assert records[0]["route"] == "oraal"


def test_column_buckets_by_dynamic_anchors():
    anchors = [("substance", 253.5), ("dose", 450.3)]
    assert _column(60.3, anchors) is None  # vóór het eerste anker (bv. merknaam-kolom): genegeerd
    assert _column(253.5, anchors) == "substance"
    assert _column(450.3, anchors) == "dose"
