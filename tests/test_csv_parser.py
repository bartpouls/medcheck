"""Test dat parse_csv/parse_csv_identity luid falen met een bruikbare foutmelding
i.p.v. stil 0 regels teruggeven (CLAUDE.md regel 4) -- zie ook parsing/pdf_text.py's
_diagnose_unreadable() voor hetzelfde patroon op het PDF-pad."""

import pytest

from parsing.csv_parser import UnreadableCsvError, parse_csv


def test_parse_csv_valid_header_still_works(tmp_path):
    path = tmp_path / "ok.csv"
    path.write_text(
        "middel,sterkte,vorm,dosering,frequentie\namoxicilline,500 mg,tablet,1 tablet,3dd1\n",
        encoding="utf-8",
    )
    lines = parse_csv(path, "a")
    assert len(lines) == 1
    assert lines[0].substance == "amoxicilline"


def test_parse_csv_raises_on_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(UnreadableCsvError, match="geen koprij"):
        parse_csv(path, "a")


def test_parse_csv_raises_when_no_header_recognized(tmp_path):
    path = tmp_path / "onbekend.csv"
    path.write_text("foo,bar,baz\n1,2,3\n", encoding="utf-8")
    with pytest.raises(UnreadableCsvError, match="Geen van de kolomkoppen"):
        parse_csv(path, "a")


def test_parse_csv_hints_at_semicolon_delimiter(tmp_path):
    path = tmp_path / "excel_nl.csv"
    path.write_text("middel;sterkte;vorm;dosering;frequentie\namoxicilline;500 mg;tablet;1 tablet;3dd1\n", encoding="utf-8")
    with pytest.raises(UnreadableCsvError, match="puntkomma-gescheiden"):
        parse_csv(path, "a")


def test_parse_csv_raises_constructive_message_on_non_utf8_encoding(tmp_path):
    path = tmp_path / "windows1252.csv"
    # "café" in cp1252 bevat een byte (0xE9) die geen geldige UTF-8-continuatie is.
    path.write_bytes("middel,sterkte\ncafé,500 mg\n".encode("cp1252"))
    with pytest.raises(UnreadableCsvError, match="UTF-8"):
        parse_csv(path, "a")
