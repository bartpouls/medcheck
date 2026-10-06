import pytest

from locales.nl.prose_parser import UnparsableProseError, parse_ontslagbrief

_LETTERHEAD = (
    "Sint Barbara Ziekenhuis\nAfdeling Interne Geneeskunde\nOntslagbrief\n"
    "Patiënt: Testpatiënt 999\nGeboortedatum: 01-01-1955\nDatum brief: 01-01-2026\n"
    "Betreft: ontslag na opname op de afdeling Interne Geneeskunde. Onderstaand de "
    "gegevens over de actuele medicatie bij ontslag.\n"
)
_FOOTER = "\nMet vriendelijke groet,\nBehandelend arts, Sint Barbara Ziekenhuis\n"


def test_single_medication_parsed():
    text = _LETTERHEAD + "Medicatie bij ontslag\nPatiënt gebruikt ibuprofen 400 mg, driemaal daags 1 tablet.\n" + _FOOTER
    records = parse_ontslagbrief(text)
    assert len(records) == 1
    assert records[0]["middel"] == "ibuprofen"
    assert records[0]["frequentie"] == "3dd1"


def test_multiple_medications_with_connectors():
    text = (
        _LETTERHEAD
        + "Medicatie bij ontslag\nPatiënt gebruikt bisoprolol 5 mg, eenmaal daags 1 tablet. Tevens gebruikt "
        "patiënt atorvastatine 40 mg, eenmaal daags 1 tablet 's avonds. Ook gebruikt patiënt metformine "
        "850 mg, tweemaal daags 1 tablet.\n" + _FOOTER
    )
    records = parse_ontslagbrief(text)
    assert [r["middel"] for r in records] == ["bisoprolol", "atorvastatine", "metformine"]
    assert records[2]["frequentie"] == "2dd1"


def test_weekly_frequency_not_converted_to_daily():
    text = _LETTERHEAD + "Medicatie bij ontslag\nPatiënt gebruikt methotrexaat 10 mg, eenmaal per week.\n" + _FOOTER
    records = parse_ontslagbrief(text)
    assert records[0]["frequentie"] == "1x per week"


def test_empty_medication_list():
    text = _LETTERHEAD + "Medicatie bij ontslag\nEr zijn op dit moment geen vaste medicijnen genoteerd.\n" + _FOOTER
    assert parse_ontslagbrief(text) == []


def test_unknown_sentence_raises_loudly():
    text = _LETTERHEAD + "Medicatie bij ontslag\nPatiënt gebruikt iets vaags zonder duidelijke dosering.\n" + _FOOTER
    with pytest.raises(UnparsableProseError):
        parse_ontslagbrief(text)


def test_missing_section_raises_loudly():
    with pytest.raises(UnparsableProseError):
        parse_ontslagbrief(_LETTERHEAD + _FOOTER)


def test_inline_mention_before_heading_does_not_confuse_section_extraction():
    # "...over de actuele medicatie bij ontslag." staat vóór de echte kop -- de sectie
    # mag pas bij de kop op eigen regel beginnen (zie prose_nl.py::_SECTION_RE).
    text = _LETTERHEAD + "Medicatie bij ontslag\nPatiënt gebruikt ibuprofen 400 mg, driemaal daags 1 tablet.\n" + _FOOTER
    records = parse_ontslagbrief(text)
    assert len(records) == 1
