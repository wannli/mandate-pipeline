# Tests for IGov utilities

from mandate_pipeline.igov import (
    default_session_label,
    normalize_decision_number,
    decision_in_series,
)


def test_default_session_label():
    assert default_session_label(80) == "80th session of the General Assembly"
    assert default_session_label(81) == "81st session of the General Assembly"
    assert default_session_label(82) == "82nd session of the General Assembly"
    assert default_session_label(83) == "83rd session of the General Assembly"
    assert default_session_label(84) == "84th session of the General Assembly"
    assert default_session_label(11) == "11th session of the General Assembly"


def test_normalize_decision_number():
    assert normalize_decision_number("80/401") == 401
    assert normalize_decision_number("80/408 A and B") == 408
    assert normalize_decision_number("80/") is None
    assert normalize_decision_number("") is None


def test_decision_in_series():
    series = [401, 501]
    assert decision_in_series(401, series)
    assert decision_in_series(499, series)
    assert not decision_in_series(500, series)
    assert decision_in_series(501, series)
