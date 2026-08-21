"""Alembic environment placeholder for future migrations.

The authoritative Step 5 schema is db/schema.sql; no migration is generated here.
"""
from alembic import context

config = context.config


def run_migrations_offline():
    context.configure(url=None, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    raise RuntimeError("No Alembic migrations are defined in Step 5; db/schema.sql is authoritative.")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
