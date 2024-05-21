# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import sqlite3
from functools import wraps
from typing import Optional, Tuple, Type, TypeVar

from sqlalchemy import Engine, event, select
from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_dbapi
from sqlalchemy.dialects.sqlite.aiosqlite import AsyncAdapt_aiosqlite_connection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql.functions import count

from ..errors import ObjectExistsError, ParentNotFoundError, PersistenceError
from ..models.sql_persistence import DBApp, DBNamespace

POSTGRES_ER_FOREIGN_KEY_VIOLATION = "23503"
POSTGRES_ER_UNIQUE_VIOLATION = "23505"


def error_guard(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as exc:
            raise PersistenceError("An unidentified error occurred.") from exc

    return wrapper


ORMObj = TypeVar("ORMObj")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    This event listener activates the foreign key constraint evaluation on sqlite databases

    https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support
    """
    if isinstance(dbapi_connection, AsyncAdapt_aiosqlite_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class SQLAlchemyMixin:
    def __init__(self):
        self._sql_engine = None
        self._session = None
        self._db_string = ""
        self._dialect = ""

    @staticmethod
    def create_db_string(
        dialect: str, host: str, port: str, db_name: str, username: str, password: str
    ) -> str:
        if dialect == "sqlite":
            return (
                f"sqlite+aiosqlite:///{db_name}" if db_name else "sqlite+aiosqlite://"
            )
        elif dialect == "postgresql":
            if not (host and db_name and username and password):
                raise ValueError(
                    "The dialect postgresql requires a host, db_name, username and password to connect."
                )
            dialect = "postgresql+asyncpg"
        else:
            raise ValueError(f"The dialect {dialect} is not supported.")
        credentials = f"{username}:{password}@" if username and password else ""
        port = f":{port}" if port else ""
        db_name = f"/{db_name}" if db_name else ""
        return f"{dialect}://{credentials}{host}{port}{db_name}"

    @staticmethod
    def session_wrapper(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if kwargs.get("session") is None:
                async with args[0].session() as session:
                    kwargs["session"] = session
                    return await func(*args, **kwargs)
            else:
                return await func(*args, **kwargs)

        return wrapper

    @property
    def sql_engine(self) -> AsyncEngine:  # pragma: no cover
        if self._sql_engine is None:
            self._sql_engine = create_async_engine(self._db_string)
        return self._sql_engine

    @property
    def session(self):  # pragma: no cover
        if self._session is None:
            self._session = async_sessionmaker(self.sql_engine, expire_on_commit=False)
        return self._session

    @error_guard
    async def _get_single_object(
        self,
        orm_cls: Type[ORMObj],
        name: str,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
    ) -> Optional[ORMObj]:
        stmt = select(orm_cls).where(getattr(orm_cls, "name") == name)
        if app_name and namespace_name:
            stmt = (
                stmt.join(DBNamespace)
                .join(DBApp)
                .where(
                    getattr(orm_cls, "namespace_id") == DBNamespace.id,
                    DBNamespace.app_id == DBApp.id,
                    DBApp.name == app_name,
                    DBNamespace.name == namespace_name,
                )
            )
        elif app_name:
            stmt = stmt.join(DBApp).where(
                DBApp.name == app_name, getattr(orm_cls, "app_id") == DBApp.id
            )
        async with self.session() as session:
            return (await session.execute(stmt)).scalar()

    @error_guard
    async def _get_num_objects(self, orm_cls: Type[ORMObj]):
        """
        Returns the total number of objects in the database.
        """
        async with self.session() as session:
            return await session.scalar(select(count(getattr(orm_cls, "id"))))

    def _configure_stmt_for_namespace(
        self,
        stmt,
        orm_cls: Type[ORMObj],
        app_name: Optional[str],
        namespace_name: Optional[str],
    ):
        if app_name and namespace_name:
            stmt = (
                stmt.join(DBNamespace)
                .join(DBApp)
                .where(
                    getattr(orm_cls, "namespace_id") == DBNamespace.id,
                    DBNamespace.app_id == DBApp.id,
                    DBApp.name == app_name,
                    DBNamespace.name == namespace_name,
                )
            )
        elif app_name and issubclass(orm_cls, DBNamespace):
            stmt = stmt.join(DBApp).where(
                DBApp.name == app_name, getattr(orm_cls, "app_id") == DBApp.id
            )
        elif app_name:
            stmt = (
                stmt.join(
                    DBNamespace, getattr(orm_cls, "namespace_id") == DBNamespace.id
                )
                .join(DBApp, DBNamespace.app_id == DBApp.id)
                .where(DBApp.name == app_name)
            )
        return stmt

    @error_guard
    async def _get_many_objects(
        self,
        orm_cls: Type[ORMObj],
        offset: int,
        limit: Optional[int],
        order_by: str = "name",
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
    ) -> Tuple[list[ORMObj], int]:
        async with self.session() as session:
            select_stmt = (
                select(orm_cls).offset(offset).order_by(getattr(orm_cls, order_by))
            )
            count_stmt = select(count(getattr(orm_cls, "id")))
            if limit:
                select_stmt = select_stmt.limit(limit)
            select_stmt = self._configure_stmt_for_namespace(
                select_stmt, orm_cls, app_name, namespace_name
            )
            count_stmt = self._configure_stmt_for_namespace(
                count_stmt, orm_cls, app_name, namespace_name
            )
            return list(
                (await session.scalars(select_stmt)).unique().all()
            ), await session.scalar(count_stmt)

    @error_guard
    @session_wrapper
    async def _create_object(self, obj: ORMObj, session: AsyncSession) -> ORMObj:
        try:
            async with session.begin():
                session.add(obj)
        except (
            IntegrityError
        ) as exc:  # This needs separate handling for each underlying dialect.
            # See univention/components/authorization-engine/guardian#98
            if (
                isinstance(exc.orig, sqlite3.IntegrityError)
                and exc.orig.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
            ) or (
                isinstance(exc.orig, AsyncAdapt_asyncpg_dbapi.IntegrityError)
                and exc.orig.pgcode == POSTGRES_ER_UNIQUE_VIOLATION  # type: ignore
            ):
                raise ObjectExistsError(
                    "An object with the given identifiers already exists."
                )
            elif (
                isinstance(exc.orig, sqlite3.IntegrityError)
                and exc.orig.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY"
            ) or (
                isinstance(exc.orig, AsyncAdapt_asyncpg_dbapi.IntegrityError)
                and exc.orig.pgcode == POSTGRES_ER_FOREIGN_KEY_VIOLATION  # type: ignore
            ):
                raise ParentNotFoundError(
                    "The app/namespace of the object to be created does not exist."
                )
            else:
                raise exc  # pragma: no cover
        await session.refresh(obj)
        return obj

    @error_guard
    async def _update_object(self, orm_obj: ORMObj, /, **new_values) -> ORMObj:
        async with self.session() as session:
            for key, value in new_values.items():
                setattr(orm_obj, key, value)
            async with session.begin():
                session.add(orm_obj)
        return orm_obj

    @error_guard
    @session_wrapper
    async def _delete_obj(self, obj: ORMObj, session: AsyncSession) -> None:
        async with session.begin():
            session.add(obj)
            await session.delete(obj)
        return None
