# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""Architecture boundary tests enforcing hexagonal architecture.

Uses two complementary strategies:
- AST-based import scanning for external library checks (fastapi, sqlalchemy, etc.)
  because pytestarch only graphs project-internal modules.
- pytestarch rules for internal cross-package boundary checks (adapter isolation,
  domain-does-not-import-adapters/routers).

Known boundary violations (tracked as technical debt):

- ``business_logic.py`` imports ``fastapi.Request`` directly.
- ``business_logic.py`` imports ``adapters.namespace.FastAPINamespaceAPIAdapter``
  (concrete adapter type instead of abstract port).
- ``ports/context.py`` and ``ports/namespace.py`` import from ``models.routers.*``
  (API-layer DTOs in port definitions).
- ``models/sql_persistence.py`` imports ``sqlalchemy`` and ``port_loader``
  (persistence infrastructure in the models package).

These are marked with ``pytest.mark.xfail(strict=True)`` so they document the debt without blocking CI.
"""

from pathlib import Path
from typing import Any

import pytest
from guardian_pytest.architecture import (
    assert_dir_does_not_import,
    assert_file_does_not_import,
    collect_imports,
    collect_imports_from_file,
    top_level,
)
from pytestarch import Rule, get_evaluable_architecture

ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT_DIR / "guardian_management_api"
DOMAIN_MODELS_DIR = PACKAGE_DIR / "models"
PORTS_DIR = PACKAGE_DIR / "ports"

PKG = "guardian_management_api"


@pytest.fixture(scope="module")
def evaluable() -> Any:
    """Create an evaluable architecture representation for pytestarch rules."""
    return get_evaluable_architecture(str(PACKAGE_DIR), str(PACKAGE_DIR))


# ---------------------------------------------------------------------------
# Domain model file collection (excluding routers/ and sql_persistence.py)
# ---------------------------------------------------------------------------

_DOMAIN_MODELS_EXCLUSIONS: set[str] = {
    "routers",
    "sql_persistence.py",
}

_DOMAIN_MODEL_FILES = [
    f
    for f in sorted(DOMAIN_MODELS_DIR.glob("*.py"))
    if f.name not in _DOMAIN_MODELS_EXCLUSIONS
    and not any(
        f.is_relative_to(DOMAIN_MODELS_DIR / excl) for excl in _DOMAIN_MODELS_EXCLUSIONS
    )
]


def _get_domain_model_imports() -> list[tuple[Path, str]]:
    """Collect imports from domain model files (excluding routers/ and sql_persistence)."""
    results: list[tuple[Path, str]] = []
    for py_file in _DOMAIN_MODEL_FILES:
        results.extend(collect_imports_from_file(py_file))
    return results


def _assert_domain_does_not_import(forbidden_module: str) -> None:
    """Fail if any domain model file imports *forbidden_module* (top-level name)."""
    violations = [
        (path.relative_to(ROOT_DIR), module)
        for path, module in _get_domain_model_imports()
        if top_level(module) == forbidden_module
    ]
    assert (
        not violations
    ), f"Domain models import forbidden module '{forbidden_module}':\n" + "\n".join(
        f"  {path}" for path, _ in violations
    )


# ===================================================================
# Domain models layer -- pure dataclasses, no framework imports
# ===================================================================


class TestDomainModelsDoNotImportFrameworks:
    """Domain model dataclasses must be framework-free."""

    @pytest.mark.parametrize(
        "forbidden",
        [
            "authlib",
            "fastapi",
            "httpx",
            "jwt",
            "port_loader",
            "pydantic",
            "sqlalchemy",
            "starlette",
        ],
    )
    def test_no_framework_import(self, forbidden: str) -> None:
        _assert_domain_does_not_import(forbidden)


# ===================================================================
# Ports layer -- must not import adapters, routers, or frameworks
# ===================================================================


class TestPortsDoNotImportFrameworks:
    """Ports (ABCs) must depend only on stdlib, guardian-lib, and domain models."""

    @pytest.mark.parametrize(
        "forbidden",
        ["authlib", "fastapi", "httpx", "jwt", "pydantic", "sqlalchemy", "starlette"],
    )
    def test_no_framework_import(self, forbidden: str) -> None:
        assert_dir_does_not_import(
            PORTS_DIR, forbidden, root_dir=ROOT_DIR, layer_name="ports"
        )


# ===================================================================
# Business logic -- must not import SQL models, frameworks, or adapters
# ===================================================================


class TestBusinessLogicBoundaries:
    """Business logic must depend only on ports and domain/router models."""

    BL_FILE = PACKAGE_DIR / "business_logic.py"

    @pytest.mark.xfail(
        reason="Known debt: business_logic.py imports fastapi.Request",
        strict=True,
    )
    def test_no_fastapi(self) -> None:
        """Business logic must not import FastAPI."""
        assert_file_does_not_import(
            self.BL_FILE, "fastapi", root_dir=ROOT_DIR, layer_name="business_logic"
        )

    @pytest.mark.parametrize(
        "forbidden",
        ["authlib", "httpx", "jwt", "sqlalchemy", "starlette"],
    )
    def test_no_framework_import(self, forbidden: str) -> None:
        """Business logic must not import framework/infrastructure libraries."""
        assert_file_does_not_import(
            self.BL_FILE, forbidden, root_dir=ROOT_DIR, layer_name="business_logic"
        )

    def test_no_sql_persistence_models(self) -> None:
        """Business logic must not import SQL persistence models."""
        imports = [mod for _, mod in collect_imports_from_file(self.BL_FILE)]
        violations = [m for m in imports if "sql_persistence" in m]
        assert (
            not violations
        ), f"business_logic.py imports SQL persistence models: {violations}"


# ===================================================================
# SQL persistence models -- known boundary violation
# ===================================================================


class TestSQLModelsIsolation:
    """SQL persistence models must not import ports, adapters, routers, or business logic.

    Note: sql_persistence.py importing sqlalchemy and port_loader is a known
    boundary violation -- these table definitions conceptually belong in the
    adapters layer.
    """

    _sql_imports: list[str]

    @classmethod
    def setup_class(cls) -> None:
        sql_file = DOMAIN_MODELS_DIR / "sql_persistence.py"
        cls._sql_imports = [mod for _, mod in collect_imports_from_file(sql_file)]

    @pytest.mark.xfail(
        reason="Known debt: models/sql_persistence.py imports sqlalchemy",
        strict=True,
    )
    def test_no_sqlalchemy(self) -> None:
        """sql_persistence.py must not import sqlalchemy."""
        violations = [m for m in self._sql_imports if top_level(m) == "sqlalchemy"]
        assert not violations, f"sql_persistence.py imports sqlalchemy: {violations}"

    @pytest.mark.xfail(
        reason="Known debt: models/sql_persistence.py imports port_loader",
        strict=True,
    )
    def test_no_port_loader(self) -> None:
        """sql_persistence.py must not import port_loader."""
        violations = [m for m in self._sql_imports if top_level(m) == "port_loader"]
        assert not violations, f"sql_persistence.py imports port_loader: {violations}"

    def test_no_port_imports(self) -> None:
        """sql_persistence.py must not import from ports/."""
        violations = [
            m for m in self._sql_imports if ".ports" in m or m.endswith("ports")
        ]
        assert not violations, f"sql_persistence.py imports from ports: {violations}"

    def test_no_adapter_imports(self) -> None:
        """sql_persistence.py must not import from adapters/."""
        violations = [
            m for m in self._sql_imports if ".adapters" in m or m.endswith("adapters")
        ]
        assert not violations, f"sql_persistence.py imports from adapters: {violations}"

    def test_no_router_imports(self) -> None:
        """sql_persistence.py must not import from routers/."""
        violations = [
            m for m in self._sql_imports if ".routers" in m or m.endswith("routers")
        ]
        assert not violations, f"sql_persistence.py imports from routers: {violations}"

    def test_no_business_logic_imports(self) -> None:
        """sql_persistence.py must not import business_logic."""
        violations = [m for m in self._sql_imports if "business_logic" in m]
        assert (
            not violations
        ), f"sql_persistence.py imports business_logic: {violations}"


# ===================================================================
# Router models (Pydantic) -- must not import SQL models or adapters
# ===================================================================


class TestRouterModelsIsolation:
    """Router Pydantic models must not import SQL models, adapters, or infra libs."""

    ROUTER_MODELS_DIR = DOMAIN_MODELS_DIR / "routers"

    @pytest.mark.parametrize(
        "forbidden",
        ["authlib", "httpx", "jwt", "sqlalchemy", "starlette"],
    )
    def test_no_infra_lib(self, forbidden: str) -> None:
        assert_dir_does_not_import(
            self.ROUTER_MODELS_DIR,
            forbidden,
            root_dir=ROOT_DIR,
            layer_name="router models",
        )

    def test_no_adapter_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(self.ROUTER_MODELS_DIR)
            if module.startswith(f"{PKG}.adapters")
        ]
        assert not violations, (
            "Architecture violation (router models): imports from adapters:\n"
            + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
        )


# ===================================================================
# Pytestarch rules -- internal cross-package boundary checks
# ===================================================================


class TestPytestarchPortsBoundaries:
    """Ports must not depend on implementation layers (pytestarch)."""

    def test_ports_do_not_import_adapters(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
        )
        rule.assert_applies(evaluable)

    def test_ports_do_not_import_routers(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.routers")
        )
        rule.assert_applies(evaluable)

    def test_ports_do_not_import_business_logic(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.business_logic")
        )
        rule.assert_applies(evaluable)

    def test_ports_do_not_import_main(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.main")
        )
        rule.assert_applies(evaluable)

    @pytest.mark.xfail(
        reason=(
            "Known violation: ports/context.py and ports/namespace.py import "
            "Pydantic router models (ContextEditRequest, NamespaceEditRequest, "
            "GetByAppRequest, NamespacesGetRequest) for use as type hints in "
            "abstract method signatures.  Port ABCs should reference domain "
            "types only; the Pydantic models should be replaced with domain "
            "equivalents or generic TypeVars."
        ),
        strict=True,
    )
    def test_ports_do_not_import_router_models(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.models.routers")
        )
        rule.assert_applies(evaluable)


class TestPytestarchBusinessLogicBoundaries:
    """Business logic must not depend on implementation layers (pytestarch)."""

    @pytest.mark.xfail(
        reason=(
            "Known debt: business_logic.py imports adapters.namespace.FastAPINamespaceAPIAdapter"
        ),
        strict=True,
    )
    def test_business_logic_does_not_import_adapters(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .have_name_matching(f"{PKG}.business_logic")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
        )
        rule.assert_applies(evaluable)

    def test_business_logic_does_not_import_routers(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .have_name_matching(f"{PKG}.business_logic")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.routers")
        )
        rule.assert_applies(evaluable)

    def test_business_logic_does_not_import_main(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .have_name_matching(f"{PKG}.business_logic")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.main")
        )
        rule.assert_applies(evaluable)


class TestPytestarchDomainModelsBoundaries:
    """Domain models must not depend on adapters, routers, ports, or business logic (pytestarch)."""

    @pytest.mark.parametrize(
        ("forbidden_module", "match_method"),
        [
            (f"{PKG}.adapters", "are_sub_modules_of"),
            (f"{PKG}.business_logic", "have_name_matching"),
            (f"{PKG}.main", "have_name_matching"),
            (f"{PKG}.ports", "are_sub_modules_of"),
            (f"{PKG}.routers", "are_sub_modules_of"),
        ],
        ids=["no-adapters", "no-business-logic", "no-main", "no-ports", "no-routers"],
    )
    def test_domain_models_do_not_import(
        self, evaluable: Any, forbidden_module: str, match_method: str
    ) -> None:
        rule_builder = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.models")
            .should_not()
            .import_modules_that()
        )
        rule = getattr(rule_builder, match_method)(forbidden_module)
        rule.assert_applies(evaluable)


class TestPytestarchAdaptersBoundaries:
    """Adapters must not depend on routers, business logic, or main (pytestarch)."""

    @pytest.mark.parametrize(
        ("forbidden_module", "match_method"),
        [
            (f"{PKG}.business_logic", "have_name_matching"),
            (f"{PKG}.main", "have_name_matching"),
            (f"{PKG}.routers", "are_sub_modules_of"),
        ],
        ids=["no-business-logic", "no-main", "no-routers"],
    )
    def test_adapters_do_not_import(
        self, evaluable: Any, forbidden_module: str, match_method: str
    ) -> None:
        rule_builder = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
            .should_not()
            .import_modules_that()
        )
        rule = getattr(rule_builder, match_method)(forbidden_module)
        rule.assert_applies(evaluable)


class TestPytestarchRoutersBoundaries:
    """Routers must not depend on SQL persistence models or main (pytestarch)."""

    def test_routers_do_not_import_sql_persistence(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.routers")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.models.sql_persistence")
        )
        rule.assert_applies(evaluable)

    def test_routers_do_not_import_main(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.routers")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.main")
        )
        rule.assert_applies(evaluable)
