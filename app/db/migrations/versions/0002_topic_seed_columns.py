"""Topics get a description, keywords and exclusion keywords.

Adds only the columns that are missing, so existing rows are kept.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def _columns():
    return {
        "description": sa.Column("description", sa.Text, nullable=False, server_default=""),
        "keywords": sa.Column("keywords", sa.JSON, nullable=False, server_default="[]"),
        "exclusion_keywords": sa.Column(
            "exclusion_keywords", sa.JSON, nullable=False, server_default="[]"
        ),
    }


def upgrade() -> None:
    existing = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("topics")}
    missing = [c for name, c in _columns().items() if name not in existing]
    if not missing:
        return
    with op.batch_alter_table("topics") as batch:
        for column in missing:
            batch.add_column(column)


def downgrade() -> None:
    existing = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("topics")}
    present = [name for name in _columns() if name in existing]
    if not present:
        return
    with op.batch_alter_table("topics") as batch:
        for name in present:
            batch.drop_column(name)
