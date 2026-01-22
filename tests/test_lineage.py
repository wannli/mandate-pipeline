# Tests for lineage analysis and UN Digital Library integration

import pytest

from mandate_pipeline.lineage import (
    fetch_undl_metadata,
    _parse_undl_marc_xml,
    link_documents,
    is_resolution,
    is_proposal,
)


# Sample MARC XML response for testing
SAMPLE_MARC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <datafield tag="191" ind1=" " ind2=" ">
      <subfield code="a">A/RES/80/142</subfield>
      <subfield code="b">A/</subfield>
      <subfield code="c">80</subfield>
    </datafield>
    <datafield tag="993" ind1="2" ind2=" ">
      <subfield code="a">A/C.2/80/L.35/Rev.1</subfield>
    </datafield>
    <datafield tag="993" ind1="4" ind2=" ">
      <subfield code="a">A/80/PV.64</subfield>
    </datafield>
    <datafield tag="993" ind1="2" ind2=" ">
      <subfield code="a">A/80/555</subfield>
    </datafield>
  </record>
</collection>
"""

SAMPLE_MARC_XML_NO_DRAFT = """<?xml version="1.0" encoding="UTF-8"?>
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <datafield tag="191" ind1=" " ind2=" ">
      <subfield code="a">A/RES/80/166</subfield>
    </datafield>
    <datafield tag="993" ind1="4" ind2=" ">
      <subfield code="a">A/80/PV.70</subfield>
    </datafield>
  </record>
</collection>
"""

SAMPLE_MARC_XML_MULTIPLE_DRAFTS = """<?xml version="1.0" encoding="UTF-8"?>
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <datafield tag="191" ind1=" " ind2=" ">
      <subfield code="a">A/RES/80/100</subfield>
    </datafield>
    <datafield tag="993" ind1="2" ind2=" ">
      <subfield code="a">A/80/L.50</subfield>
    </datafield>
    <datafield tag="993" ind1="2" ind2=" ">
      <subfield code="a">A/80/L.51</subfield>
    </datafield>
  </record>
</collection>
"""


class TestParseUndlMarcXml:
    """Tests for MARC XML parsing."""

    def test_parse_resolution_with_draft(self):
        """Parse resolution metadata with draft symbol in tag 993."""
        result = _parse_undl_marc_xml(SAMPLE_MARC_XML, "A/RES/80/142")

        assert result is not None
        assert result["symbol"] == "A/RES/80/142"
        assert "A/C.2/80/L.35/Rev.1" in result["related_symbols"]
        assert "A/80/PV.64" in result["related_symbols"]
        assert result["draft_symbols"] == ["A/C.2/80/L.35/Rev.1"]
        assert result["base_proposal"] == "A/C.2/80/L.35/Rev.1"

    def test_parse_resolution_no_draft(self):
        """Parse resolution without draft symbol."""
        result = _parse_undl_marc_xml(SAMPLE_MARC_XML_NO_DRAFT, "A/RES/80/166")

        assert result is not None
        assert result["symbol"] == "A/RES/80/166"
        assert result["draft_symbols"] == []
        assert result["base_proposal"] is None

    def test_parse_resolution_multiple_drafts(self):
        """Parse resolution with multiple draft symbols."""
        result = _parse_undl_marc_xml(SAMPLE_MARC_XML_MULTIPLE_DRAFTS, "A/RES/80/100")

        assert result is not None
        assert len(result["draft_symbols"]) == 2
        assert "A/80/L.50" in result["draft_symbols"]
        assert "A/80/L.51" in result["draft_symbols"]
        assert result["base_proposal"] == "A/80/L.50"

    def test_parse_symbol_not_found(self):
        """Return None when target symbol not in XML."""
        result = _parse_undl_marc_xml(SAMPLE_MARC_XML, "A/RES/99/999")

        assert result is None

    def test_parse_invalid_xml(self):
        """Return None for malformed XML."""
        result = _parse_undl_marc_xml("<invalid>not xml", "A/RES/80/142")

        assert result is None

    def test_parse_empty_xml(self):
        """Return None for empty collection."""
        empty_xml = """<?xml version="1.0"?>
        <collection xmlns="http://www.loc.gov/MARC21/slim">
        </collection>
        """
        result = _parse_undl_marc_xml(empty_xml, "A/RES/80/142")

        assert result is None

    def test_parse_case_insensitive_symbol_match(self):
        """Match symbol case-insensitively."""
        result = _parse_undl_marc_xml(SAMPLE_MARC_XML, "a/res/80/142")

        assert result is not None
        assert result["symbol"] == "a/res/80/142"


class TestFetchUndlMetadata:
    """Tests for UN Digital Library API fetching."""

    def test_fetch_success(self, mocker):
        """Fetch metadata successfully from UNDL."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_MARC_XML
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("mandate_pipeline.lineage.requests.get", return_value=mock_response)

        result = fetch_undl_metadata("A/RES/80/142")

        assert result is not None
        assert result["base_proposal"] == "A/C.2/80/L.35/Rev.1"

    def test_fetch_network_error(self, mocker):
        """Return None on network error."""
        import requests

        mocker.patch(
            "mandate_pipeline.lineage.requests.get",
            side_effect=requests.RequestException("Connection failed"),
        )

        result = fetch_undl_metadata("A/RES/80/142")

        assert result is None

    def test_fetch_http_error(self, mocker):
        """Return None on HTTP error status."""
        import requests

        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        mocker.patch("mandate_pipeline.lineage.requests.get", return_value=mock_response)

        result = fetch_undl_metadata("A/RES/80/142")

        assert result is None

    def test_fetch_timeout(self, mocker):
        """Return None on timeout."""
        import requests

        mocker.patch(
            "mandate_pipeline.lineage.requests.get",
            side_effect=requests.Timeout("Request timed out"),
        )

        result = fetch_undl_metadata("A/RES/80/142")

        assert result is None


class TestLinkDocumentsWithUndl:
    """Tests for link_documents with UNDL metadata integration."""

    def test_link_via_undl_metadata(self, mocker):
        """Link resolution to proposal via UNDL metadata (Pass 0)."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_MARC_XML
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("mandate_pipeline.lineage.requests.get", return_value=mock_response)

        documents = [
            {"symbol": "A/RES/80/142", "title": "Test Resolution"},
            {"symbol": "A/C.2/80/L.35/Rev.1", "title": "Test Draft"},
        ]

        link_documents(documents, use_undl_metadata=True)

        resolution = documents[0]
        proposal = documents[1]

        assert resolution["link_method"] == "undl_metadata"
        assert resolution["link_confidence"] == 1.0
        assert resolution["base_proposal_symbol"] == "A/C.2/80/L.35/Rev.1"
        assert "A/C.2/80/L.35/Rev.1" in resolution["linked_proposal_symbols"]

        assert proposal["linked_resolution_symbol"] == "A/RES/80/142"
        assert proposal["link_method"] == "undl_metadata"

    def test_link_fallback_to_symbol_reference(self, mocker):
        """Fall back to symbol reference when UNDL has no draft."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_MARC_XML_NO_DRAFT
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("mandate_pipeline.lineage.requests.get", return_value=mock_response)

        documents = [
            {
                "symbol": "A/RES/80/166",
                "title": "Test Resolution",
                "symbol_references": ["A/80/L.99"],
            },
            {"symbol": "A/80/L.99", "title": "Test Draft"},
        ]

        link_documents(documents, use_undl_metadata=True)

        resolution = documents[0]

        # Should fall back to Pass 1 (symbol_reference)
        assert resolution["link_method"] == "symbol_reference"
        assert resolution["base_proposal_symbol"] == "A/80/L.99"

    def test_link_undl_disabled(self, mocker):
        """Skip UNDL lookup when disabled."""
        mock_get = mocker.patch("mandate_pipeline.lineage.requests.get")

        documents = [
            {
                "symbol": "A/RES/80/142",
                "title": "Test Resolution",
                "symbol_references": ["A/80/L.50"],
            },
            {"symbol": "A/80/L.50", "title": "Test Draft"},
        ]

        link_documents(documents, use_undl_metadata=False)

        # Should not have called the API
        mock_get.assert_not_called()

        # Should use symbol_reference method
        resolution = documents[0]
        assert resolution["link_method"] == "symbol_reference"

    def test_link_undl_draft_not_in_local_collection(self, mocker):
        """Store base_proposal even when draft not in local collection."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_MARC_XML
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("mandate_pipeline.lineage.requests.get", return_value=mock_response)

        # Only resolution, no local copy of the draft
        documents = [
            {"symbol": "A/RES/80/142", "title": "Test Resolution"},
        ]

        link_documents(documents, use_undl_metadata=True)

        resolution = documents[0]

        # Should still record the base_proposal from UNDL
        assert resolution["base_proposal_symbol"] == "A/C.2/80/L.35/Rev.1"
        assert resolution["link_method"] == "undl_metadata"
        # But linked_proposal_symbols should be empty (not in local collection)
        assert resolution["linked_proposal_symbols"] == []

    def test_link_skip_already_linked(self, mocker):
        """Skip UNDL lookup for already-linked documents."""
        mock_get = mocker.patch("mandate_pipeline.lineage.requests.get")

        documents = [
            {
                "symbol": "A/RES/80/142",
                "title": "Test Resolution",
                "linked_proposal_symbols": ["A/80/L.1"],  # Already linked
            },
        ]

        link_documents(documents, use_undl_metadata=True)

        # Should not call API for already-linked resolution
        mock_get.assert_not_called()


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_is_resolution(self):
        """Identify resolution symbols."""
        assert is_resolution("A/RES/80/142") is True
        assert is_resolution("A/RES/79/1") is True
        assert is_resolution("A/80/L.1") is False
        assert is_resolution("A/C.1/80/L.5") is False

    def test_is_proposal(self):
        """Identify proposal/draft symbols."""
        assert is_proposal("A/80/L.1") is True
        assert is_proposal("A/C.1/80/L.5") is True
        assert is_proposal("A/C.2/80/L.35/Rev.1") is True
        assert is_proposal("A/RES/80/142") is False
        assert is_proposal("A/80/100") is False
