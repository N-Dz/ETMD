import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import DublinCore
from serializers import to_json_dc, to_jsonld


def _make_model(**kwargs) -> DublinCore:
    return DublinCore(**kwargs)


def test_to_json_dc_excludes_none():
    model = _make_model(title="Test", creator=None)
    result = to_json_dc(model)
    assert "title" in result
    assert "creator" not in result


def test_to_json_dc_only_dc_keys():
    model = _make_model(title="T", creator="C", date="2024")
    result = to_json_dc(model)
    valid_keys = {
        "title", "creator", "subject", "description", "publisher",
        "contributor", "date", "type", "format", "identifier",
        "source", "language", "relation", "coverage", "rights",
    }
    assert set(result.keys()).issubset(valid_keys)


def test_to_jsonld_has_context_and_type():
    model = _make_model(title="Test")
    result = to_jsonld(model)
    assert result["@context"] == "http://purl.org/dc/elements/1.1/"
    assert result["@type"] == "Resource"


def test_to_jsonld_includes_dc_fields():
    model = _make_model(title="Test", publisher="MIT Press")
    result = to_jsonld(model)
    assert result["title"] == "Test"
    assert result["publisher"] == "MIT Press"


def test_to_jsonld_excludes_none():
    model = _make_model(title="Test", creator=None)
    result = to_jsonld(model)
    assert "creator" not in result
