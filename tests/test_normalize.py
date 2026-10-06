from normalize.frequency import frequency_core
from normalize.units import doses_equal, parse_quantity, parse_titration_schedule, strengths_equal


def test_frequency_core_ndd1_variants_equal():
    assert frequency_core("1x per dag, 's ochtends nuchter") == frequency_core("1dd1")


def test_frequency_core_om_de_uur_equals_ddn():
    assert frequency_core("om de 8 uur") == frequency_core("3dd1")


def test_frequency_core_weekly_not_equal_to_daily():
    assert frequency_core("1x per week, elke maandag") != frequency_core("1dd1")


def test_frequency_core_modifier_ignored():
    assert frequency_core("'s avonds 1 tablet") == frequency_core("1dd1 's avonds")


def test_strengths_equal_mg_mcg():
    v1, u1 = parse_quantity("0,1 mg")
    v2, u2 = parse_quantity("100 microgram")
    assert strengths_equal(v1, u1, v2, u2)


def test_strengths_not_equal_when_different():
    v1, u1 = parse_quantity("40 mg")
    v2, u2 = parse_quantity("80 mg")
    assert not strengths_equal(v1, u1, v2, u2)


def test_doses_equal_plural_unit():
    v1, u1 = parse_quantity("1 tablet")
    v2, u2 = parse_quantity("1 tabletten")
    assert doses_equal(v1, u1, v2, u2)


def test_doses_not_equal_when_count_differs():
    v1, u1 = parse_quantity("1 tablet")
    v2, u2 = parse_quantity("2 tabletten")
    assert not doses_equal(v1, u1, v2, u2)


def test_titration_schedule_picks_current_week():
    text = "afbouwschema: 30mg week1, 20mg week2, 10mg week3 (nu week 3)"
    value, unit = parse_titration_schedule(text)
    assert value == 10.0
    assert unit == "mg"
