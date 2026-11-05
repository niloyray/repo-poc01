from importlib.metadata import version

from fastapi.testclient import TestClient

from app import __version__
from app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__


def test_version_matches_metadata():
    assert client.get("/health").json()["version"] == version("ai-radar")


def test_post_not_allowed():
    assert client.post("/health").status_code == 405


def test_unknown_path():
    assert client.get("/unknown").status_code == 404
