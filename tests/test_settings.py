from datetime import time

import pytest

from app.settings import SettingsError, load_settings


def test_defaults():
    s = load_settings({})
    assert s.database_url == "sqlite:///data/radar.db"
    assert s.host == "127.0.0.1"
    assert s.port == 8000
    assert s.scan_time == time(6, 0)
    assert s.scan_timezone == "Asia/Kolkata"
    assert s.llm_model is None
    assert s.github_token is None


def test_overrides():
    s = load_settings(
        {"HOST": "0.0.0.0", "PORT": "8123", "SCAN_TIME": "23:45", "LLM_MODEL": "some-model"}
    )
    assert s.host == "0.0.0.0"
    assert s.port == 8123
    assert s.scan_time == time(23, 45)
    assert s.llm_model == "some-model"


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("PORT", "abc"),
        ("PORT", "0"),
        ("PORT", "65536"),
        ("PORT", " 80"),
        ("PORT", "+80"),
        ("PORT", "8_0"),
        ("PORT", ""),
        ("SCAN_TIME", "6:00"),
        ("SCAN_TIME", "24:00"),
        ("SCAN_TIME", "06:60"),
        ("SCAN_TIME", "06:00:00"),
        ("SCAN_TIMEZONE", "Nowhere/Land"),
        ("SCAN_TIMEZONE", ""),
        ("HOST", ""),
        ("DATABASE_URL", ""),
    ],
)
def test_invalid_values_name_the_variable(name, value):
    with pytest.raises(SettingsError) as exc:
        load_settings({name: value})
    assert str(exc.value).startswith(f"{name}: expected ")
    assert f'got "{value}"' in str(exc.value)


def test_error_message_format():
    with pytest.raises(SettingsError, match=r'^PORT: expected .*, got "abc"$'):
        load_settings({"PORT": "abc"})


def test_empty_optional_values_are_unset():
    s = load_settings({"GITHUB_TOKEN": "", "LLM_MODEL": ""})
    assert s.github_token is None
    assert s.llm_model is None


def test_token_is_not_in_repr():
    s = load_settings({"GITHUB_TOKEN": "sample-token-value"})
    assert s.github_token == "sample-token-value"
    assert "sample-token-value" not in repr(s)


def test_token_is_not_in_errors():
    with pytest.raises(SettingsError) as exc:
        load_settings({"GITHUB_TOKEN": "sample-token-value", "PORT": "abc"})
    assert "sample-token-value" not in str(exc.value)
