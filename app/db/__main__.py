"""Developer helper: ``python -m app.db upgrade`` / ``revision "message"``."""

import argparse
import sys

from alembic import command

from app.db.engine import DatabaseConfigError, prepare_engine
from app.db.migrate import init_database, make_config
from app.settings import SettingsError, get_settings


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.db")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("upgrade", help="apply all migrations to the database in DATABASE_URL")
    rev = sub.add_parser("revision", help="autogenerate a migration from app/db/schema.py")
    rev.add_argument("message")
    args = parser.parse_args(argv)
    try:
        url = get_settings().database_url
        init_database(url)  # autogenerate compares against a database at head
        if args.action == "revision":
            engine = prepare_engine(url)
            try:
                command.revision(make_config(engine), message=args.message, autogenerate=True)
            finally:
                engine.dispose()
    except (SettingsError, DatabaseConfigError) as exc:
        print(f"Invalid configuration: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
