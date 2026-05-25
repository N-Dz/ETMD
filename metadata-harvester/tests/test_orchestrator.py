import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from unittest.mock import patch, MagicMock


def _mock_gemini_response(text: str):
    mock_resp = MagicMock()
    mock_resp.text = text
    return mock_resp


# Patch Gemini at import time to avoid needing a real API key in tests
with patch("google.generativeai.configure"), \
     patch("google.generativeai.GenerativeModel"):
    import orchestrator


def test_classify_doi():
    orchestrator._model.generate_content.return_value = _mock_gemini_response("doi")
    assert orchestrator.classify("10.1038/nature12373") == "doi"


def test_classify_url():
    orchestrator._model.generate_content.return_value = _mock_gemini_response("url")
    assert orchestrator.classify("https://en.wikipedia.org/wiki/Python") == "url"


def test_classify_pdf():
    orchestrator._model.generate_content.return_value = _mock_gemini_response("pdf")
    assert orchestrator.classify("thesis.pdf") == "pdf"


def test_classify_defaults_to_url_on_unknown_response():
    orchestrator._model.generate_content.return_value = _mock_gemini_response("not sure")
    assert orchestrator.classify("something") == "url"


def test_enrich_parses_json_response():
    dc = {"title": "Test", "creator": "Jane", "date": "2024"}
    orchestrator._model.generate_content.return_value = _mock_gemini_response(json.dumps(dc))
    result = orchestrator.enrich({"raw_title": "Test"})
    assert result["title"] == "Test"
    assert result["creator"] == "Jane"


def test_enrich_strips_markdown_fences():
    dc = {"title": "Fenced", "creator": "Bob"}
    fenced = f"```json\n{json.dumps(dc)}\n```"
    orchestrator._model.generate_content.return_value = _mock_gemini_response(fenced)
    result = orchestrator.enrich({"x": "y"})
    assert result["title"] == "Fenced"
