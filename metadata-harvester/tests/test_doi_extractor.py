import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from extractors import doi_extractor


CROSSREF_RESPONSE = {
    "message": {
        "title": ["Nature of Things"],
        "author": [{"given": "Jane", "family": "Doe"}, {"given": "John", "family": "Smith"}],
        "publisher": "Nature Publishing",
        "container-title": ["Nature"],
        "issued": {"date-parts": [[2023, 6, 15]]},
        "abstract": "An abstract.",
        "language": "en",
        "URL": "https://doi.org/10.1038/test",
        "ISSN": ["0028-0836"],
        "subject": ["Biology", "Chemistry"],
        "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}],
    }
}


def _mock_get(response_json):
    mock_resp = MagicMock()
    mock_resp.json.return_value = response_json
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_extract_title_and_authors():
    with patch("extractors.doi_extractor.requests.get", return_value=_mock_get(CROSSREF_RESPONSE)):
        result = doi_extractor.extract("10.1038/test")
    assert result["title"] == "Nature of Things"
    assert "Jane Doe" in result["author"]
    assert "John Smith" in result["author"]


def test_extract_publisher_and_date():
    with patch("extractors.doi_extractor.requests.get", return_value=_mock_get(CROSSREF_RESPONSE)):
        result = doi_extractor.extract("10.1038/test")
    assert result["publisher"] == "Nature Publishing"
    assert result["issued"] == "2023-6-15"


def test_extract_language_and_subject():
    with patch("extractors.doi_extractor.requests.get", return_value=_mock_get(CROSSREF_RESPONSE)):
        result = doi_extractor.extract("10.1038/test")
    assert result["language"] == "en"
    assert "Biology" in result["subject"]


def test_extract_strips_doi_prefix():
    with patch("extractors.doi_extractor.requests.get", return_value=_mock_get(CROSSREF_RESPONSE)) as mock_get:
        doi_extractor.extract("https://doi.org/10.1038/test")
    called_url = mock_get.call_args[0][0]
    assert "https://doi.org/" not in called_url.replace("api.crossref.org", "")


def test_extract_empty_message_returns_doi_only():
    with patch("extractors.doi_extractor.requests.get", return_value=_mock_get({"message": {}})):
        result = doi_extractor.extract("10.1038/test")
    assert result == {"doi": "10.1038/test"}
