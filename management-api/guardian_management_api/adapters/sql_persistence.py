# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import sqlite3
from functools import wraps
from typing import Optional, Type, TypeVar

from sqlalchemy import Engine, event, select
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
        elif True:  # Remove with univention/components/authorization-engine/guardian#98
            raise ValueError(
                f"The dialect {dialect} is not supported. "
                f"Support for mysql and postgresql will be added soon!"
            )
        elif dialect == "postgresql":
            if not (host and db_name and username and password):
                raise ValueError(
                    "The dialect postgresql requires a host, db_name, username and password to connect."
                )
            dialect = "postgresql+asyncpg"
        elif dialect == "mysql":
            if not (host and db_name and username and password):
                raise ValueError(
                    "The dialect mysql requires a host, db_name, username and password to connect."
                )
            dialect = "mysql+aiomysql"
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
        async with self.session() as session:
            return await session.scalar(select(count(getattr(orm_cls, "id"))))

    @error_guard
    async def _get_many_objects(
        self,
        orm_cls: Type[ORMObj],
        offset: int,
        limit: Optional[int],
        order_by: str = "name",
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
    ) -> list[ORMObj]:
        async with self.session() as session:
            stmt = select(orm_cls).offset(offset).order_by(getattr(orm_cls, order_by))
            if limit:
                stmt = stmt.limit(limit)
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
            return list((await session.scalars(stmt)).all())

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
            # print(exc.orig.__dict__)
            if (
                isinstance(exc.orig, sqlite3.IntegrityError)
                and exc.orig.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
            ):
                raise ObjectExistsError(
                    "An object with the given identifiers already exists."
                )
            elif (
                isinstance(exc.orig, sqlite3.IntegrityError)
                and exc.orig.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY"
            ):
                raise ParentNotFoundError(
                    "The app/namespace of the object to be created does not exist."
                )
            else:
                raise exc  # pragma: no cover
        return await self._get_single_object(type(obj), name=obj.name)  # type: ignore[attr-defined]

    @error_guard
    async def _update_object(self, orm_obj: ORMObj, /, **new_values) -> ORMObj:
        async with self.session() as session:
            for key, value in new_values.items():
                setattr(orm_obj, key, value)
            async with session.begin():
                session.add(orm_obj)
        return orm_obj
