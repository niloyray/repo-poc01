import pytest

import app.__main__ as entry

ENV_NAMES = [
    "DATABASE_URL",
    "HOST",
    "PORT",
    "SCAN_TIME",
    "SCAN_TIMEZONE",
    "LLM_MODEL",
    "GITHUB_TOKEN",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def init_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(entry, "init_database", lambda url: calls.append(url))
    return calls


@pytest.fixture
def run_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(entry.uvicorn, "run", lambda *a, **kw: calls.append((a, kw)))
    return calls


def test_defaults(run_calls):
    entry.main()
    assert run_calls == [(("app.main:app",), {"host": "127.0.0.1", "port": 8000})]


def test_host_and_port_from_environment(monkeypatch, run_calls):
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8123")
    entry.main()
    assert run_calls == [(("app.main:app",), {"host": "0.0.0.0", "port": 8123})]


def test_bad_port_exits_with_message(monkeypatch, run_calls, capsys):
    monkeypatch.setenv("PORT", "abc")
    with pytest.raises(SystemExit) as exc:
        entry.main()
    assert exc.value.code == 2
    assert "PORT" in capsys.readouterr().err
    assert run_calls == []


def test_database_initialised_before_server_starts(monkeypatch):
    order = []
    monkeypatch.setattr(entry, "init_database", lambda url: order.append("db"))
    monkeypatch.setattr(entry.uvicorn, "run", lambda *a, **kw: order.append("run"))
    entry.main()
    assert order == ["db", "run"]


def test_database_error_exits_2_without_starting(monkeypatch, run_calls, capsys):
    def boom(url):
        raise entry.DatabaseConfigError("DATABASE_URL: nope")

    monkeypatch.setattr(entry, "init_database", boom)
    with pytest.raises(SystemExit) as exc:
        entry.main()
    assert exc.value.code == 2
    assert "DATABASE_URL: nope" in capsys.readouterr().err
    assert run_calls == []
