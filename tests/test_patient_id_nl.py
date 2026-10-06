"""BSN-elfproef (locales/nl/patient_id.py). "111222333" en "010000008" zijn publiek
bekende, veelgebruikte test-BSN's (o.a. in DigiD-testomgevingen) -- geen echte
patiëntdata, wél geldig volgens de 11-proef."""

from locales.nl.patient_id import is_valid_bsn, normalize_bsn


def test_valid_bsn_passes_elfproef():
    assert is_valid_bsn("111222333") is True


def test_single_digit_change_fails_elfproef():
    assert is_valid_bsn("111222334") is False


def test_eight_digit_bsn_is_left_padded():
    assert is_valid_bsn("10000008") is True


def test_all_zero_is_rejected_even_though_sum_is_divisible_by_11():
    assert is_valid_bsn("000000000") is False


def test_wrong_length_is_invalid():
    assert is_valid_bsn("12345") is False


def test_empty_is_invalid():
    assert is_valid_bsn("") is False


def test_normalize_strips_punctuation_and_spaces():
    assert normalize_bsn("111.222.333") == "111222333"
    assert normalize_bsn("1112 22 333") == "111222333"


def test_normalized_input_with_punctuation_still_validates():
    assert is_valid_bsn("111.222.333") is True
