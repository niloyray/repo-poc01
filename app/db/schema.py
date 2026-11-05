"""The database schema: one MetaData with the six tables."""

import sqlalchemy as sa

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)

sources = sa.Table(
    "sources",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.Text, nullable=False),
    sa.Column("kind", sa.Text, nullable=False),
    sa.Column("address", sa.Text, nullable=False),
)

topics = sa.Table(
    "topics",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.Text, nullable=False, unique=True),
)

items = sa.Table(
    "items",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("title", sa.Text, nullable=False),
    sa.Column("canonical_url", sa.Text, nullable=False, unique=True),
    sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id"), nullable=False),
    sa.Column("kind", sa.Text, nullable=False),
    sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("excerpt", sa.Text, nullable=True),
    sa.Column("score", sa.Float, nullable=True),
    sa.Column("score_reason", sa.Text, nullable=True),
    sa.Column("scoring_method", sa.Text, nullable=True),
    sa.Column("summary", sa.Text, nullable=True),
    sa.Column("outside_signals", sa.JSON, nullable=True),
)

item_topics = sa.Table(
    "item_topics",
    metadata,
    sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id"), primary_key=True),
    sa.Column("topic_id", sa.Integer, sa.ForeignKey("topics.id"), primary_key=True),
)

runs = sa.Table(
    "runs",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("outcome", sa.Text, nullable=True),
)

digests = sa.Table(
    "digests",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("run_id", sa.Integer, sa.ForeignKey("runs.id"), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("content", sa.Text, nullable=False),
)
