"""Initial schema: sources, topics, items, item_topics, runs, digests.

Creates only the tables that are missing, so a hand-made partial file is
completed without touching existing rows.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def _tables():
    return {
        "sources": [
            sa.Column("id", sa.Integer, nullable=False),
            sa.Column("name", sa.Text, nullable=False),
            sa.Column("kind", sa.Text, nullable=False),
            sa.Column("address", sa.Text, nullable=False),
            sa.PrimaryKeyConstraint("id", name="pk_sources"),
        ],
        "topics": [
            sa.Column("id", sa.Integer, nullable=False),
            sa.Column("name", sa.Text, nullable=False),
            sa.PrimaryKeyConstraint("id", name="pk_topics"),
            sa.UniqueConstraint("name", name="uq_topics_name"),
        ],
        "items": [
            sa.Column("id", sa.Integer, nullable=False),
            sa.Column("title", sa.Text, nullable=False),
            sa.Column("canonical_url", sa.Text, nullable=False),
            sa.Column("source_id", sa.Integer, nullable=False),
            sa.Column("kind", sa.Text, nullable=False),
            sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("excerpt", sa.Text, nullable=True),
            sa.Column("score", sa.Float, nullable=True),
            sa.Column("score_reason", sa.Text, nullable=True),
            sa.Column("scoring_method", sa.Text, nullable=True),
            sa.Column("summary", sa.Text, nullable=True),
            sa.Column("outside_signals", sa.JSON, nullable=True),
            sa.ForeignKeyConstraint(
                ["source_id"], ["sources.id"], name="fk_items_source_id_sources"
            ),
            sa.PrimaryKeyConstraint("id", name="pk_items"),
            sa.UniqueConstraint("canonical_url", name="uq_items_canonical_url"),
        ],
        "item_topics": [
            sa.Column("item_id", sa.Integer, nullable=False),
            sa.Column("topic_id", sa.Integer, nullable=False),
            sa.ForeignKeyConstraint(["item_id"], ["items.id"], name="fk_item_topics_item_id_items"),
            sa.ForeignKeyConstraint(
                ["topic_id"], ["topics.id"], name="fk_item_topics_topic_id_topics"
            ),
            sa.PrimaryKeyConstraint("item_id", "topic_id", name="pk_item_topics"),
        ],
        "runs": [
            sa.Column("id", sa.Integer, nullable=False),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("outcome", sa.Text, nullable=True),
            sa.PrimaryKeyConstraint("id", name="pk_runs"),
        ],
        "digests": [
            sa.Column("id", sa.Integer, nullable=False),
            sa.Column("run_id", sa.Integer, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("content", sa.Text, nullable=False),
            sa.ForeignKeyConstraint(["run_id"], ["runs.id"], name="fk_digests_run_id_runs"),
            sa.PrimaryKeyConstraint("id", name="pk_digests"),
        ],
    }


def upgrade() -> None:
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    for name, columns in _tables().items():
        if name not in existing:
            op.create_table(name, *columns)


def downgrade() -> None:
    for name in ("digests", "runs", "item_topics", "items", "topics", "sources"):
        op.drop_table(name)
