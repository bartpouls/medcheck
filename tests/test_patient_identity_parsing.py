"""Patiëntidentiteit uit CSV-brondata (parsing/common.py + parsing/csv_parser.py).
Kolommen zijn optioneel -- bestaande casus zonder deze kolommen (data/synthetic/casus/)
moeten `PatientIdentity()` (alles leeg) opleveren, geen foutmelding (zie identity.py:
"niet gevonden" is een waarschuwing, geen blokkade)."""

import csv

from parsing.common import extract_patient_identity
from parsing.csv_parser import parse_csv_identity

VALID_BSN = "111222333"


def test_extract_patient_identity_reads_bsn_naam_geboortedatum():
    records = [
        {
            "drug_name": "Emcor",
            "bsn": "111.222.333",
            "patient_naam": "Jansen, Piet",
            "geboortedatum": "1960-01-01",
        },
        {"drug_name": "Selokeen", "bsn": "111.222.333", "patient_naam": "Jansen, Piet", "geboortedatum": "1960-01-01"},
    ]
    identity = extract_patient_identity(records)
    assert identity.bsn == VALID_BSN
    assert identity.bsn_valid is True
    assert identity.name == "Jansen, Piet"
    assert identity.birth_date == "1960-01-01"


def test_extract_patient_identity_without_columns_is_empty_not_error():
    records = [{"drug_name": "Emcor", "sterkte": "5mg"}]
    identity = extract_patient_identity(records)
    assert identity.bsn == ""
    assert identity.bsn_valid is None
    assert identity.name == ""
    assert identity.birth_date == ""


def test_extract_patient_identity_flags_invalid_bsn_distinct_from_missing():
    records = [{"drug_name": "Emcor", "bsn": "123456780"}]
    identity = extract_patient_identity(records)
    assert identity.bsn == "123456780"
    assert identity.bsn_valid is False


def test_parse_csv_identity_end_to_end(tmp_path):
    path = tmp_path / "source_a.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["drug_name", "route", "dose_form", "frequency", "strength", "bsn", "geboortedatum"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "drug_name": "Emcor",
                "route": "oraal",
                "dose_form": "tablet",
                "frequency": "1dd1",
                "strength": "5mg",
                "bsn": VALID_BSN,
                "geboortedatum": "1960-01-01",
            }
        )

    identity = parse_csv_identity(path)
    assert identity.bsn == VALID_BSN
    assert identity.bsn_valid is True
    assert identity.birth_date == "1960-01-01"
