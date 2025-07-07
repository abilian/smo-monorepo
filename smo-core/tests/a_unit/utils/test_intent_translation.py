# tests/utils/test_intent_translation.py
import pytest

from smo_core.utils.intent_translation import (
    translate_cpu,
    translate_memory,
    translate_storage,
)


def test_translate_cpu():
    """Test CPU translation."""

    assert translate_cpu("light") == 0.5
    assert translate_cpu("medium") == 4


def test_translate_memory():
    """Test memory translation."""

    assert translate_memory("small") == "1GiB"
    assert translate_memory("large") == "8GiB"


def test_translate_storage():
    """Test storage translation."""

    assert translate_storage("small") == "10GB"
    assert translate_storage("medium") == "20GB"


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("light", 0.5),
        ("small", 1),
        ("medium", 4),
        ("large", 8),
    ],
)
def test_translate_cpu2(input_val, expected):
    assert translate_cpu(input_val) == expected


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("light", "500MiB"),
        ("small", "1GiB"),
        ("medium", "2GiB"),
        ("large", "8GiB"),
    ],
)
def test_translate_memory2(input_val, expected):
    assert translate_memory(input_val) == expected


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("small", "10GB"),
        ("medium", "20GB"),
        ("large", "40GB"),
    ],
)
def test_translate_storage2(input_val, expected):
    assert translate_storage(input_val) == expected


def test_translate_cpu_invalid():
    with pytest.raises(KeyError):
        translate_cpu("extra_large")
