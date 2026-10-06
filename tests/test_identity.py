"""Patiëntidentiteitscontrole (identity.py). Dekt de volgorde uit het gesprek met
Bart (2026-08-26): BSN primair, naam+geboortedatum als fallback zodra BSN ontbreekt of
ongeldig is, nooit blokkerend -- alleen `matched` en de waarschuwingscodes wijzigen."""

from identity import check_identity
from models import PatientIdentity

VALID_BSN_A = "111222333"
VALID_BSN_B = "010000008"


def _identity(**kwargs) -> PatientIdentity:
    return PatientIdentity(**kwargs)


def test_matching_valid_bsn_is_confirmed_without_warnings():
    a = _identity(bsn=VALID_BSN_A, bsn_valid=True)
    b = _identity(bsn=VALID_BSN_A, bsn_valid=True)
    result = check_identity(a, b)
    assert result.matched is True
    assert result.method == "bsn"
    assert result.warnings == []


def test_mismatching_valid_bsn_is_not_confirmed():
    a = _identity(bsn=VALID_BSN_A, bsn_valid=True)
    b = _identity(bsn=VALID_BSN_B, bsn_valid=True)
    result = check_identity(a, b)
    assert result.matched is False
    assert result.method == "bsn"
    assert [w.code for w in result.warnings] == ["BSN_MISMATCH"]


def test_missing_bsn_falls_back_to_name_and_dob_match():
    a = _identity(bsn="", bsn_valid=None, name="Jansen, Piet", birth_date="1960-01-01")
    b = _identity(bsn=VALID_BSN_B, bsn_valid=True, name="Jansen, Piet", birth_date="1960-01-01")
    result = check_identity(a, b)
    assert result.matched is True
    assert result.method == "naam_geboortedatum"
    assert [w.code for w in result.warnings] == ["BSN_ONTBREEKT"]
    assert result.warnings[0].source == "a"


def test_invalid_bsn_is_a_distinct_warning_from_missing_bsn():
    a = _identity(bsn="123456782", bsn_valid=False, name="Jansen, Piet", birth_date="1960-01-01")
    b = _identity(bsn="", bsn_valid=None, name="Jansen, Piet", birth_date="1960-01-01")
    result = check_identity(a, b)
    codes = {w.code for w in result.warnings}
    assert codes == {"BSN_ONGELDIG", "BSN_ONTBREEKT"}
    assert result.matched is True
    assert result.method == "naam_geboortedatum"


def test_name_dob_mismatch_is_not_confirmed_but_never_raises():
    a = _identity(bsn=VALID_BSN_A, bsn_valid=True, name="Jansen, Piet", birth_date="1960-01-01")
    b = _identity(bsn="", bsn_valid=None, name="De Vries, Anne", birth_date="1975-05-05")
    result = check_identity(a, b)
    assert result.matched is False
    assert result.method == "naam_geboortedatum"
    codes = [w.code for w in result.warnings]
    assert codes == ["BSN_ONTBREEKT", "NAAM_GEBOORTEDATUM_MISMATCH"]


def test_no_identifiers_at_all_is_not_confirmed_but_never_raises():
    a = _identity()
    b = _identity()
    result = check_identity(a, b)
    assert result.matched is False
    assert result.method == "geen"
    codes = [w.code for w in result.warnings]
    assert codes.count("BSN_ONTBREEKT") == 2
    assert "GEEN_IDENTIFICATIE_MOGELIJK" in codes


def test_name_match_is_case_and_whitespace_insensitive():
    a = _identity(name="  Piet Jansen  ", birth_date="1960-01-01")
    b = _identity(name="piet jansen", birth_date="1960-01-01")
    result = check_identity(a, b)
    assert result.matched is True
    assert result.method == "naam_geboortedatum"
