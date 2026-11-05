import sys

import uvicorn

from app.db import DatabaseConfigError, init_database
from app.settings import SettingsError, load_settings


def main() -> None:
    try:
        settings = load_settings()
        init_database(settings.database_url)
    except (SettingsError, DatabaseConfigError) as exc:
        print(f"Invalid configuration: {exc}", file=sys.stderr)
        sys.exit(2)
    uvicorn.run("app.main:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
