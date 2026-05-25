import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from normalizer import normalize
from models import DublinCore


def test_normalize_valid_fields():
    result = normalize({"title": "Test Paper", "creator": "Jane Doe", "date": "2024"})
    assert isinstance(result, DublinCore)
    assert result.title == "Test Paper"
    assert result.creator == "Jane Doe"
    assert result.date == "2024"


def test_normalize_ignores_unknown_keys():
    result = normalize({"title": "Hello", "unknown_field": "should be dropped"})
    assert result.title == "Hello"
    assert not hasattr(result, "unknown_field")


def test_normalize_none_values_stay_none():
    result = normalize({"title": "Hello", "creator": None})
    assert result.creator is None


def test_normalize_converts_non_string_to_str():
    result = normalize({"date": 2024, "title": "Paper"})
    assert result.date == "2024"
    assert isinstance(result.date, str)


def test_normalize_empty_dict():
    result = normalize({})
    assert isinstance(result, DublinCore)
    assert result.title is None
