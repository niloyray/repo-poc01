"""Alembic environment. Configured in code: no alembic.ini, no logging changes."""

from alembic import context

from app.db.schema import metadata

config = context.config
engine = config.attributes["engine"]

with engine.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=metadata,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()
