# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass, field
from typing import Optional

from port_loader.models import SETTINGS_NAME_METADATA
from sqlalchemy import (
    JSON,
    Column,
    Enum,
    ForeignKey,
    LargeBinary,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from guardian_management_api.constants import STRING_MAX_LENGTH
from guardian_management_api.models.capability import CapabilityConditionRelation
from guardian_management_api.models.condition import ConditionParameterType

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
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH), unique=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(STRING_MAX_LENGTH))
    namespaces: Mapped[list["DBNamespace"]] = relationship(back_populates="app")


class DBNamespace(Base):
    __tablename__ = "namespace"

    id: Mapped[int] = mapped_column(primary_key=True)
    app_id: Mapped[int] = mapped_column(ForeignKey(DBApp.id))
    app: Mapped[DBApp] = relationship(back_populates="namespaces", lazy="joined")
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH))
    display_name: Mapped[Optional[str]] = mapped_column(String(STRING_MAX_LENGTH))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("app_id", "name"),
    )


class DBPermission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH))
    display_name: Mapped[Optional[str]] = mapped_column(String(STRING_MAX_LENGTH))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )


class DBRole(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH))
    display_name: Mapped[Optional[str]] = mapped_column(String(STRING_MAX_LENGTH))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )


class DBContext(Base):
    __tablename__ = "context"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH))
    display_name: Mapped[Optional[str]] = mapped_column(String(STRING_MAX_LENGTH))

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )


class DBConditionParameter(Base):
    __tablename__ = "condition_parameter"

    id: Mapped[int] = mapped_column(primary_key=True)
    condition_id: Mapped[int] = mapped_column(ForeignKey("condition.id"))
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH))
    value_type: Mapped[ConditionParameterType] = mapped_column(
        Enum(ConditionParameterType, native_enum=False)
    )
    position: Mapped[int] = mapped_column(nullable=False)


class DBCondition(Base):
    __tablename__ = "condition"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH))
    display_name: Mapped[Optional[str]] = mapped_column(String(STRING_MAX_LENGTH))
    documentation: Mapped[Optional[str]] = mapped_column(Text())
    parameters: Mapped[list[DBConditionParameter]] = relationship(
        lazy="joined",
        cascade="all, delete-orphan",
        order_by=DBConditionParameter.position,
    )
    code: Mapped[bytes] = mapped_column(LargeBinary())

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )


capability_permission_table = Table(
    "capability_permission",
    Base.metadata,
    Column(
        "capability_id",
        ForeignKey("capability.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class DBCapabilityCondition(Base):
    __tablename__ = "capability_condition"
    id: Mapped[int] = mapped_column(primary_key=True)
    capability_id: Mapped[int] = mapped_column(
        ForeignKey("capability.id", ondelete="CASCADE")
    )
    capability: Mapped["DBCapability"] = relationship(
        lazy="joined", back_populates="conditions"
    )
    condition_id: Mapped[int] = mapped_column(
        ForeignKey(DBCondition.id, ondelete="CASCADE")
    )
    condition: Mapped[DBCondition] = relationship(lazy="joined")
    kwargs = mapped_column(JSON())


class DBCapability(Base):
    __tablename__ = "capability"
    id: Mapped[int] = mapped_column(primary_key=True)
    namespace_id: Mapped[int] = mapped_column(ForeignKey(DBNamespace.id))
    namespace: Mapped[DBNamespace] = relationship(lazy="joined")
    name: Mapped[str] = mapped_column(String(STRING_MAX_LENGTH))
    display_name: Mapped[Optional[str]] = mapped_column(String(STRING_MAX_LENGTH))
    role_id: Mapped[int] = mapped_column(ForeignKey(DBRole.id))
    role: Mapped[DBRole] = relationship(lazy="joined")
    permissions: Mapped[set[DBPermission]] = relationship(
        secondary=capability_permission_table,
        lazy="joined",
    )
    relation: Mapped[CapabilityConditionRelation] = mapped_column(
        Enum(CapabilityConditionRelation, native_enum=False)
    )
    conditions: Mapped[set[DBCapabilityCondition]] = relationship(
        lazy="joined", back_populates="capability", cascade="all, delete"
    )

    __table_args__ = (  # type: ignore[var-annotated]
        UniqueConstraint("namespace_id", "name"),
    )
