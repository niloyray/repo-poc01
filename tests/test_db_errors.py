import pytest

from app.db import DatabaseConfigError, init_database


@pytest.mark.parametrize(
    "url",
    ["postgresql://u:p@localhost/db", "sqlite://", "sqlite:///:memory:", "not a url", "sqlite:///"],
)
def test_unsupported_url_names_database_url(url):
    with pytest.raises(DatabaseConfigError, match=r"^DATABASE_URL: "):
        init_database(url)


def test_uncreatable_path(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    with pytest.raises(DatabaseConfigError, match=r"^DATABASE_URL: "):
        init_database(f"sqlite:///{blocker / 'sub' / 'radar.db'}")


def test_directory_as_file(tmp_path):
    with pytest.raises(DatabaseConfigError, match=r"^DATABASE_URL: "):
        init_database(f"sqlite:///{tmp_path}")
