import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from extractors import url_extractor


def _mock_response(html: str):
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


OG_HTML = """
<html><head>
  <meta property="og:title" content="My Article" />
  <meta property="og:description" content="An interesting article." />
  <meta property="og:type" content="article" />
  <meta name="author" content="Jane Doe" />
  <meta name="keywords" content="science, nature" />
</head><body></body></html>
"""

TITLE_ONLY_HTML = """
<html><head><title>Fallback Title</title></head><body></body></html>
"""


def test_extracts_open_graph_tags():
    with patch("extractors.url_extractor.requests.get", return_value=_mock_response(OG_HTML)):
        result = url_extractor.extract("https://example.com")
    assert result["title"] == "My Article"
    assert result["description"] == "An interesting article."


def test_extracts_meta_name_tags():
    with patch("extractors.url_extractor.requests.get", return_value=_mock_response(OG_HTML)):
        result = url_extractor.extract("https://example.com")
    assert result["author"] == "Jane Doe"
    assert result["keywords"] == "science, nature"


def test_fallback_to_title_tag():
    with patch("extractors.url_extractor.requests.get", return_value=_mock_response(TITLE_ONLY_HTML)):
        result = url_extractor.extract("https://example.com")
    assert result["title"] == "Fallback Title"


def test_source_url_always_present():
    with patch("extractors.url_extractor.requests.get", return_value=_mock_response(TITLE_ONLY_HTML)):
        result = url_extractor.extract("https://example.com/page")
    assert result["source_url"] == "https://example.com/page"


def test_empty_content_values_excluded():
    html = '<html><head><meta name="author" content="" /></head></html>'
    with patch("extractors.url_extractor.requests.get", return_value=_mock_response(html)):
        result = url_extractor.extract("https://example.com")
    assert "author" not in result
