# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
from dataclasses import asdict
from logging.config import fileConfig

from alembic import context
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_management_api.adapter_registry import (
    configure_registry,
)
from guardian_management_api.adapters.sql_persistence import SQLAlchemyMixin
from guardian_management_api.models.sql_persistence import (
    Base,
    SQLPersistenceAdapterSettings,
)
from port_loader import AsyncAdapterSettingsProvider
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    configure_registry(ADAPTER_REGISTRY)
    settings_port: AsyncAdapterSettingsProvider = await ADAPTER_REGISTRY.request_port(
        AsyncAdapterSettingsProvider
    )
    settings = await settings_port.get_adapter_settings(SQLPersistenceAdapterSettings)
    db_string = SQLAlchemyMixin.create_db_string(**asdict(settings))
    # get the alembic section of the config file
    ini_section = config.get_section(config.config_ini_section, {})
    ini_section["sqlalchemy.url"] = db_string
    connectable = async_engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
