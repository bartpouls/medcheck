"""Tests voor locales/nl/patient_portal_parser.py, gebaseerd op de letterlijke
tekstfragmenten die Bart deelde uit het ASP-patiëntportaaloverzicht (2026-08-28,
het privé-bouwlog sessie 14) -- geen patiëntgegevens, alleen medicatietekst."""

import pytest

from locales.nl.patient_portal_parser import (
    UnparsablePatientPortalError,
    _block_to_record,
    _dose_from_freqline,
    detect,
    parse_patient_portal,
)


def test_detect_true_on_uw_medicatie_met_secties():
    assert detect("Uw medicatie\nStart met deze medicatie\n...")
    assert detect("... Uw medicatie ... Doorgaan met deze medicatie ...")


def test_detect_false_without_sections():
    assert not detect("Uw medicatie")  # titel alleen, geen sectie-indeling
    assert not detect("iets heel anders")


def test_dose_from_freqline_telwoord_per_dag():
    assert _dose_from_freqline(
        "Drie keer per dag gedurende 60 doses. Innemen 1 tablet (50 mg per gift)"
    ) == ("3dd1", "1 tablet")


def test_dose_from_freqline_indien_nodig():
    assert _dose_from_freqline("Indien nodig. Innemen 1 stuk") == ("zo nodig", "1 stuk")


def test_dose_from_freqline_onherkend_telwoord_raist():
    with pytest.raises(UnparsablePatientPortalError):
        _dose_from_freqline("Zeven keer per dag. Innemen 1 tablet")


def test_dose_from_freqline_onherkende_vorm_raist():
    with pytest.raises(UnparsablePatientPortalError):
        _dose_from_freqline("iets heel anders")


def test_block_to_record_start_met_stopdatum():
    record = _block_to_record(
        "diclofenac 50mg tablet MSR",
        [
            "Gebruik stoppen op: 16 september 2026",
            "Drie keer per dag gedurende 60 doses. Innemen 1 tablet (50 mg per gift)",
        ],
    )
    assert record["middel"] == "diclofenac"
    assert record["sterkte"] == "50mg"
    assert record["vorm"] == "tablet msr"
    assert record["frequentie"] == "3dd1"
    assert record["dosering"] == "1 tablet"
    assert record["gestopt"] == "16 september 2026"
    assert record["zo_nodig"] == "nee"
    assert record["route"] == "oraal"


def test_block_to_record_doorgaan_prn_negeert_generiek_regel():
    record = _block_to_record(
        "DOMPERIDON 10mg tablet",
        ["Generiek medicijn: domperidon", "Indien nodig. Innemen 1 stuk"],
    )
    assert record["middel"] == "DOMPERIDON"
    assert record["frequentie"] == "zo nodig"
    assert record["dosering"] == "1 stuk"
    assert record["zo_nodig"] == "ja"


def test_block_to_record_stop_sectie_zonder_details():
    record = _block_to_record("famotidine 20mg tablet", [])
    assert record["middel"] == "famotidine"
    assert record["gestopt"] == ""
    assert record["reden_stop"] == ""
    assert record["dosering"] == ""


def test_parse_patient_portal_end_to_end_drie_secties():
    text = "\n".join(
        [
            "Uw medicatie",
            "Start met deze medicatie",
            "Ochtend Middag Avond Voor de",
            "nacht Zo nodig",
            "diclofenac 50mg tablet MSR",
            "Gebruik stoppen op: 16 september 2026",
            "Drie keer per dag gedurende 60 doses. Innemen 1 tablet (50 mg per gift)",
            "Doorgaan met deze medicatie (vervolg)",
            "Ochtend Middag Avond Voor de",
            "nacht Zo nodig",
            "DOMPERIDON 10mg tablet",
            "Generiek medicijn: domperidon",
            "Indien nodig. Innemen 1 stuk",
            "Stop deze medicatie",
            "famotidine 20mg tablet",
        ]
    )
    records = parse_patient_portal(text)
    assert [r["middel"] for r in records] == ["diclofenac", "DOMPERIDON", "famotidine"]
    assert records[0]["gestopt"] == "16 september 2026"
    assert records[1]["zo_nodig"] == "ja"
    assert records[2]["dosering"] == ""
