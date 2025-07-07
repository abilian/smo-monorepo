# tests/utils/test_intent_translation.py
import pytest

from smo_core.utils.intent_translation import (
    tranlsate_cpu,
    tranlsate_memory,
    tranlsate_storage,
)


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("light", 0.5),
        ("small", 1),
        ("medium", 4),
        ("large", 8),
    ],
)
def test_translate_cpu(input_val, expected):
    assert tranlsate_cpu(input_val) == expected


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("light", "500MiB"),
        ("small", "1GiB"),
        ("medium", "2GiB"),
        ("large", "8GiB"),
    ],
)
def test_translate_memory(input_val, expected):
    assert tranlsate_memory(input_val) == expected


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("small", "10GB"),
        ("medium", "20GB"),
        ("large", "40GB"),
    ],
)
def test_translate_storage(input_val, expected):
    assert tranlsate_storage(input_val) == expected


def test_translate_cpu_invalid():
    with pytest.raises(KeyError):
        tranlsate_cpu("extra_large")
