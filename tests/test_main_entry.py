import pytest

import app.__main__ as entry

ENV_NAMES = ["DATABASE_URL", "HOST", "PORT", "SCAN_TIME", "SCAN_TIMEZONE", "LLM_MODEL", "GITHUB_TOKEN"]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


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
