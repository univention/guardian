from dataclasses import dataclass, field
from typing import Optional

from guardian_lib.models.settings import SETTINGS_NAME_METADATA
from sqlalchemy import ForeignKey, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

SQL_DIALECT = "sql_persistence_adapter.dialect"
SQL_HOST = "sql_persistence_adapter.host"
SQL_PORT = "sql_persistence_adapter.port"
SQL_DB_NAME = "sql_persistence_adapter.db_name"
SQL_USERNAME = "sql_persistence_adapter.username"
SQL_PASSWORD = "sql_persistence_adapter.password"  # nosec B105


@dataclass(frozen=True)
class SQLPersistenceAdapterSettings:
    dialect: str = field(metadata={SETTINGS_NAME_METADATA: SQL_DIALECT})
    host: str = field(default="", metadata={SETTINGS_NAME_METADATA: SQL_HOST})
    port: str = field(default="", metadata={SETTINGS_NAME_METADATA: SQL_PORT})
    db_name: str = field(default="", metadata={SETTINGS_NAME_METADATA: SQL_DB_NAME})
    username: str = field(default="", metadata={SETTINGS_NAME_METADATA: SQL_USERNAME})
    password: str = field(default="", metadata={SETTINGS_NAME_METADATA: SQL_PASSWORD})


class Base(DeclarativeBase):
    pass


class DBApp(Base):
    __tablename__ = "app"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(256))
    namespaces: Mapped[list["DBNamespace"]] = relationship(back_populates="app")


class DBNamespace(Base):
    __tablename__ = "namespace"

    id: Mapped[int] = mapped_column(primary_key=True)
    app_id: Mapped[int] = mapped_column(ForeignKey(DBApp.id))
    app: Mapped[DBApp] = relationship(back_populates="namespaces", lazy="joined")
    name: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[Optional[str]] = mapped_column(String(256))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("app_id", "name"),
    )


class DBPermission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[Optional[str]] = mapped_column(String(256))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )


class DBRole(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[Optional[str]] = mapped_column(String(256))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )


class DBContext(Base):
    __tablename__ = "context"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[Optional[str]] = mapped_column(String(256))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )


class DBCondition(Base):
    __tablename__ = "condition"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[Optional[str]] = mapped_column(String(256))
    documentation: Mapped[Optional[str]] = mapped_column(Text())
    parameters: Mapped[str] = mapped_column(Text)
    code: Mapped[bytes] = mapped_column(LargeBinary())

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )
