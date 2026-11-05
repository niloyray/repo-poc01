"""Load the watched topics from the seed file into the ``topics`` table.

Insert-only: a name that is already in the table is never touched.
"""

import json
from pathlib import Path

from sqlalchemy.dialects.sqlite import insert

from app.db.engine import prepare_engine
from app.db.schema import topics

DEFAULT_SEED_PATH = Path(__file__).resolve().parent / "seed" / "topics.json"


class SeedError(RuntimeError):
    """The seed file cannot be loaded. The message names the file."""


def _label(index: int, name: object) -> str:
    if isinstance(name, str) and name.strip():
        return f'entry {index} ("{name.strip()}")'
    return f"entry {index} (no name)"


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        return None
    return [v.strip() for v in value if v.strip()]


def parse_seed(path: Path = DEFAULT_SEED_PATH) -> list[dict]:
    """Read and validate the whole file; raise one SeedError listing every problem."""
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SeedError(f"Seed file {path}: cannot read it: {exc}") from exc
    except ValueError as exc:
        raise SeedError(f"Seed file {path}: not valid JSON: {exc}") from exc

    entries = data.get("topics") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise SeedError(f'Seed file {path}: expected an object with a "topics" list')

    problems: list[str] = []
    result: list[dict] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            problems.append(f"entry {index} (no name): must be an object")
            continue
        label = _label(index, entry.get("name"))
        before = len(problems)
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            problems.append(f"{label}: name is missing or blank")
            name = ""
        name = name.strip()
        if name and name.casefold() in seen:
            problems.append(f"{label}: duplicate name")
        seen.add(name.casefold())

        description = entry.get("description", "")
        if not isinstance(description, str):
            problems.append(f"{label}: description must be a string")
        keywords = _string_list(entry.get("keywords"))
        if keywords is None:
            problems.append(f"{label}: keywords must be a list of strings")
        elif not keywords:
            problems.append(f"{label}: keywords must not be empty")
        exclusions = _string_list(entry.get("exclusion_keywords", []))
        if exclusions is None:
            problems.append(f"{label}: exclusion_keywords must be a list of strings")

        if len(problems) == before:
            result.append(
                {
                    "name": name,
                    "description": description,
                    "keywords": keywords,
                    "exclusion_keywords": exclusions,
                }
            )
    if problems:
        raise SeedError(f"Seed file {path}: " + "; ".join(problems))
    return result


def load_seed(database_url: str, seed_path: Path = DEFAULT_SEED_PATH) -> int:
    """Add the seed topics that are not yet in the table; return how many were added."""
    rows = parse_seed(seed_path)
    engine = prepare_engine(database_url)
    try:
        added = 0
        with engine.begin() as conn:
            for row in rows:
                stmt = insert(topics).values(**row).on_conflict_do_nothing(index_elements=["name"])
                added += conn.execute(stmt).rowcount
        return added
    finally:
        engine.dispose()
