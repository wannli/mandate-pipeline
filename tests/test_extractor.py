import pytest
from pathlib import Path
from mandate_pipeline.extractor import extract_operative_paragraphs, extract_title

def test_extract_operative_paragraphs_basic():
    text = """
    The General Assembly,

    1. Decides to do something;

    2. Requests the Secretary-General to report back;

    3. Also decides to adjourn.
    """

    paragraphs = extract_operative_paragraphs(text)

    assert len(paragraphs) == 3
    assert paragraphs[1] == "Decides to do something;"
    assert paragraphs[2] == "Requests the Secretary-General to report back;"
    assert paragraphs[3] == "Also decides to adjourn."

def test_extract_operative_paragraphs_messy_whitespace():
    text = """
      1.   First paragraph
    with multiple lines.

    2. Second paragraph.
    """

    paragraphs = extract_operative_paragraphs(text)

    assert len(paragraphs) == 2
    assert paragraphs[1] == "First paragraph with multiple lines."
    assert paragraphs[2] == "Second paragraph."

def test_extract_operative_paragraphs_no_matches():
    text = "This text has no numbered paragraphs."
    paragraphs = extract_operative_paragraphs(text)
    assert paragraphs == {}

def test_extract_operative_paragraphs_real_data():
    text = """
    Resolution adopted by the General Assembly

    1. Adopts the rules;
    2. Decides to meet again.
    """
    paragraphs = extract_operative_paragraphs(text)
    assert 1 in paragraphs
    assert 2 in paragraphs

def test_extract_title_resolution():
    text = """
    United Nations
    General Assembly
    Distr.: General
    20 September 2024

    Resolution adopted by the General Assembly on 10 September 2024
    [without reference to a Main Committee (A/80/L.1)]

    80/1. The Title of the Resolution

    The General Assembly,
    Recalling its resolution...
    """
    title = extract_title(text)
    assert title == "80/1. The Title of the Resolution"

def test_extract_title_proposal():
    text = """
    United Nations
    General Assembly
    Distr.: Limited

    Draft resolution
    A/80/L.1

    The Situation in Testland

    The General Assembly,
    ...
    """
    title = extract_title(text)
    assert title == "The Situation in Testland"

def test_extract_title_multiline():
    text = """
    Resolution adopted by the General Assembly

    80/1. The Title of the Resolution
    continues on the next line

    The General Assembly,
    """
    title = extract_title(text)
    assert title == "80/1. The Title of the Resolution continues on the next line"

def test_extract_title_ignores_headers():
    text = """
    Agenda item 5
    A/RES/80/1
    Original: English

    Resolution adopted by the General Assembly

    80/1. The Actual Title

    The General Assembly
    """
    title = extract_title(text)
    assert title == "80/1. The Actual Title"
