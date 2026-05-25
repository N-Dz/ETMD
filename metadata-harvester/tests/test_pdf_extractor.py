import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from extractors import pdf_extractor


def _mock_doc(metadata: dict):
    mock_doc = MagicMock()
    mock_doc.metadata = metadata
    mock_doc.close = MagicMock()
    return mock_doc


def test_returns_non_empty_metadata():
    meta = {"title": "Test PDF", "author": "Jane Doe", "creationDate": "2024-01-01", "producer": ""}
    with patch("extractors.pdf_extractor.fitz.open", return_value=_mock_doc(meta)):
        result = pdf_extractor.extract(b"fake-bytes")
    assert result["title"] == "Test PDF"
    assert result["author"] == "Jane Doe"


def test_excludes_empty_values():
    meta = {"title": "Test", "producer": "", "creator": None}
    with patch("extractors.pdf_extractor.fitz.open", return_value=_mock_doc(meta)):
        result = pdf_extractor.extract(b"fake-bytes")
    assert "producer" not in result
    assert "creator" not in result


def test_empty_metadata_returns_empty_dict():
    with patch("extractors.pdf_extractor.fitz.open", return_value=_mock_doc({})):
        result = pdf_extractor.extract(b"fake-bytes")
    assert result == {}


def test_doc_is_closed_after_extract():
    mock_doc = _mock_doc({"title": "T"})
    with patch("extractors.pdf_extractor.fitz.open", return_value=mock_doc):
        pdf_extractor.extract(b"fake-bytes")
    mock_doc.close.assert_called_once()
