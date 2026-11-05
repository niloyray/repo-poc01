"""Application settings, read from environment variables.

This is the only module that reads the process environment. Other code
imports ``get_settings`` from here.
"""

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import time
from functools import cache
from zoneinfo import ZoneInfo

DEFAULT_DATABASE_URL = "sqlite:///data/radar.db"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_SCAN_TIME = "06:00"
DEFAULT_SCAN_TIMEZONE = "Asia/Kolkata"

_PORT_RE = re.compile(r"[0-9]{1,5}")
_SCAN_TIME_RE = re.compile(r"([01]\d|2[0-3]):([0-5]\d)")


class SettingsError(ValueError):
    """A setting has an invalid value. The message names the variable."""


@dataclass(frozen=True)
class Settings:
    database_url: str
    host: str
    port: int
    scan_time: time
    scan_timezone: str
    llm_model: str | None
    github_token: str | None = field(repr=False)


def _invalid(name: str, expected: str, value: str) -> SettingsError:
    return SettingsError(f'{name}: expected {expected}, got "{value}"')


def _text(env: Mapping[str, str], name: str, default: str, expected: str) -> str:
    value = env.get(name)
    if value is None:
        return default
    if value == "":
        raise _invalid(name, expected, value)
    return value


def _optional(env: Mapping[str, str], name: str) -> str | None:
    return env.get(name) or None


def _port(env: Mapping[str, str]) -> int:
    expected = "a whole number from 1 to 65535"
    raw = env.get("PORT")
    if raw is None:
        return DEFAULT_PORT
    if not _PORT_RE.fullmatch(raw) or not 1 <= int(raw) <= 65535:
        raise _invalid("PORT", expected, raw)
    return int(raw)


def _scan_time(env: Mapping[str, str]) -> time:
    raw = env.get("SCAN_TIME", DEFAULT_SCAN_TIME)
    match = _SCAN_TIME_RE.fullmatch(raw)
    if not match:
        raise _invalid("SCAN_TIME", "a 24-hour time as HH:MM", raw)
    return time(int(match.group(1)), int(match.group(2)))


def _timezone(env: Mapping[str, str]) -> str:
    raw = env.get("SCAN_TIMEZONE", DEFAULT_SCAN_TIMEZONE)
    try:
        ZoneInfo(raw)
    except (ValueError, OSError, KeyError):  # ZoneInfoNotFoundError is a KeyError
        raise _invalid(
            "SCAN_TIMEZONE", "an IANA time zone name such as Asia/Kolkata", raw
        ) from None
    return raw


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Parse and validate settings; raise SettingsError on the first bad value."""
    if env is None:
        env = os.environ
    return Settings(
        database_url=_text(env, "DATABASE_URL", DEFAULT_DATABASE_URL, "a non-empty database URL"),
        host=_text(env, "HOST", DEFAULT_HOST, "a non-empty host name or address"),
        port=_port(env),
        scan_time=_scan_time(env),
        scan_timezone=_timezone(env),
        llm_model=_optional(env, "LLM_MODEL"),
        github_token=_optional(env, "GITHUB_TOKEN"),
    )


@cache
def get_settings() -> Settings:
    """Settings for the running process, loaded once from the environment."""
    return load_settings()
