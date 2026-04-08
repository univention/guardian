# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""Architecture boundary tests enforcing hexagonal architecture.

Uses two complementary strategies:
- AST-based import scanning for external library checks (fastapi, sqlalchemy, etc.)
  because pytestarch only graphs project-internal modules.
- pytestarch rules for internal cross-package boundary checks (adapter isolation,
  domain-does-not-import-adapters/routes).

The authorization-api has a flatter structure than management-api:
- ports.py is a single file (not a directory)
- routes.py is a single file (not a directory)
- models/ contains domain, persistence, policy, and route models

Note: In this component ``ports``, ``business_logic``, ``routes``, and ``main`` are single-file modules
(not packages).  pytestarch's ``are_sub_modules_of`` only matches *children* of a package,
so we use ``have_name_matching`` when referencing single-file modules.
"""

from pathlib import Path
from typing import Any

import pytest
from guardian_pytest.architecture import (
    assert_file_does_not_import,
    assert_file_does_not_import_prefix,
    collect_imports,
)
from pytestarch import Rule, get_evaluable_architecture

ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT_DIR / "guardian_authorization_api"
MODELS_DIR = PACKAGE_DIR / "models"
ADAPTERS_DIR = PACKAGE_DIR / "adapters"

PKG = "guardian_authorization_api"


@pytest.fixture(scope="module")
def evaluable() -> Any:
    """Create an evaluable architecture representation for pytestarch rules."""
    return get_evaluable_architecture(str(PACKAGE_DIR), str(PACKAGE_DIR))


# ===================================================================
# Ports (ports.py) -- must not import adapters, routes, or frameworks
# ===================================================================


class TestPortsBoundaries:
    """Ports (ABCs) must depend only on stdlib, guardian-lib, and domain models."""

    PORTS_FILE = PACKAGE_DIR / "ports.py"

    @pytest.mark.parametrize(
        ("forbidden", "check_type"),
        [
            ("authlib", "top_level"),
            ("fastapi", "top_level"),
            ("httpx", "top_level"),
            ("jwt", "top_level"),
            ("opa_client", "top_level"),
            ("pydantic", "top_level"),
            ("requests", "top_level"),
            ("sqlalchemy", "top_level"),
            ("starlette", "top_level"),
            (f"{PKG}.adapters", "prefix"),
            (f"{PKG}.routes", "prefix"),
        ],
        ids=[
            "no-authlib",
            "no-fastapi",
            "no-httpx",
            "no-jwt",
            "no-opa-client",
            "no-pydantic",
            "no-requests",
            "no-sqlalchemy",
            "no-starlette",
            "no-adapter-imports",
            "no-routes-imports",
        ],
    )
    def test_ports_boundary(self, forbidden: str, check_type: str) -> None:
        if check_type == "top_level":
            assert_file_does_not_import(
                self.PORTS_FILE, forbidden, root_dir=ROOT_DIR, layer_name="ports"
            )
        else:
            assert_file_does_not_import_prefix(
                self.PORTS_FILE, forbidden, root_dir=ROOT_DIR, layer_name="ports"
            )


# ===================================================================
# Business logic -- must not import adapters, routes, or frameworks
# ===================================================================


class TestBusinessLogicBoundaries:
    """Business logic must depend only on ports and domain models."""

    BL_FILE = PACKAGE_DIR / "business_logic.py"

    @pytest.mark.parametrize(
        "forbidden",
        [
            "authlib",
            "fastapi",
            "httpx",
            "jwt",
            "opa_client",
            "requests",
            "sqlalchemy",
            "starlette",
        ],
    )
    def test_no_framework_import(self, forbidden: str) -> None:
        assert_file_does_not_import(
            self.BL_FILE, forbidden, root_dir=ROOT_DIR, layer_name="business_logic"
        )

    def test_no_adapter_imports(self) -> None:
        assert_file_does_not_import_prefix(
            self.BL_FILE,
            f"{PKG}.adapters",
            root_dir=ROOT_DIR,
            layer_name="business_logic",
        )

    def test_no_routes_imports(self) -> None:
        assert_file_does_not_import_prefix(
            self.BL_FILE,
            f"{PKG}.routes",
            root_dir=ROOT_DIR,
            layer_name="business_logic",
        )


# ===================================================================
# Models -- must not import adapters, routes, or business logic
# ===================================================================


class TestModelsDoNotImportImplementationLayers:
    """Domain/persistence/policy models must not import adapters, routes, or business logic."""

    def test_no_adapter_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(MODELS_DIR)
            if module.startswith(f"{PKG}.adapters")
        ]
        assert (
            not violations
        ), "Architecture violation (models): imports from adapters:\n" + "\n".join(
            f"  {path}  ->  {mod}" for path, mod in violations
        )

    def test_no_routes_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(MODELS_DIR)
            if module.startswith(f"{PKG}.routes")
        ]
        assert (
            not violations
        ), "Architecture violation (models): imports from routes:\n" + "\n".join(
            f"  {path}  ->  {mod}" for path, mod in violations
        )

    def test_no_business_logic_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(MODELS_DIR)
            if module.startswith(f"{PKG}.business_logic") or module == "business_logic"
        ]
        assert not violations, (
            "Architecture violation (models): imports from business_logic:\n"
            + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
        )


class TestModelsExternalImports:
    """Model files must not import web framework or external service libraries.

    models/routes.py is allowed to use pydantic (it defines API DTOs).
    """

    @pytest.mark.parametrize(
        "forbidden",
        ["fastapi", "opa_client", "requests", "starlette"],
    )
    def test_non_route_models_no_framework_libs(self, forbidden: str) -> None:
        """Non-routes model files must not import web/API framework libs."""
        for py_file in sorted(MODELS_DIR.rglob("*.py")):
            if py_file.name == "routes.py":
                continue
            assert_file_does_not_import(
                py_file, forbidden, root_dir=ROOT_DIR, layer_name="models"
            )

    def test_routes_model_no_fastapi(self) -> None:
        """Even the routes model should not import fastapi directly."""
        routes_file = MODELS_DIR / "routes.py"
        if routes_file.exists():
            assert_file_does_not_import(
                routes_file, "fastapi", root_dir=ROOT_DIR, layer_name="models/routes"
            )

    def test_routes_model_no_opa_client(self) -> None:
        routes_file = MODELS_DIR / "routes.py"
        if routes_file.exists():
            assert_file_does_not_import(
                routes_file,
                "opa_client",
                root_dir=ROOT_DIR,
                layer_name="models/routes",
            )


# ===================================================================
# Adapters -- must not import routes or business logic
# ===================================================================


class TestAdaptersBoundaries:
    """Adapters must not depend on routes or business logic."""

    def test_no_routes_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(ADAPTERS_DIR)
            if module.startswith(f"{PKG}.routes") or module == ".routes"
        ]
        assert (
            not violations
        ), "Architecture violation (adapters): imports from routes:\n" + "\n".join(
            f"  {path}  ->  {mod}" for path, mod in violations
        )

    def test_no_business_logic_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(ADAPTERS_DIR)
            if "business_logic" in module
        ]
        assert not violations, (
            "Architecture violation (adapters): imports from business_logic:\n"
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
            .have_name_matching(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
        )
        rule.assert_applies(evaluable)

    @pytest.mark.parametrize(
        "forbidden",
        [f"{PKG}.business_logic", f"{PKG}.main", f"{PKG}.routes"],
        ids=["no-business-logic", "no-main", "no-routes"],
    )
    def test_ports_do_not_import(self, evaluable: Any, forbidden: str) -> None:
        rule = (
            Rule()
            .modules_that()
            .have_name_matching(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .have_name_matching(forbidden)
        )
        rule.assert_applies(evaluable)


class TestPytestarchBusinessLogicBoundaries:
    """Business logic must not depend on implementation layers (pytestarch)."""

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

    def test_business_logic_does_not_import_routes(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .have_name_matching(f"{PKG}.business_logic")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.routes")
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


class TestPytestarchModelsBoundaries:
    """Models must not depend on implementation layers (pytestarch)."""

    def test_models_do_not_import_adapters(self, evaluable: Any) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.models")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
        )
        rule.assert_applies(evaluable)

    @pytest.mark.parametrize(
        "forbidden",
        [f"{PKG}.business_logic", f"{PKG}.main", f"{PKG}.ports", f"{PKG}.routes"],
        ids=["no-business-logic", "no-main", "no-ports", "no-routes"],
    )
    def test_models_do_not_import(self, evaluable: Any, forbidden: str) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.models")
            .should_not()
            .import_modules_that()
            .have_name_matching(forbidden)
        )
        rule.assert_applies(evaluable)


class TestPytestarchAdaptersBoundaries:
    """Adapters must not depend on routes, business logic, or main (pytestarch)."""

    @pytest.mark.parametrize(
        "forbidden",
        [f"{PKG}.business_logic", f"{PKG}.main", f"{PKG}.routes"],
        ids=["no-business-logic", "no-main", "no-routes"],
    )
    def test_adapters_do_not_import(self, evaluable: Any, forbidden: str) -> None:
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
            .should_not()
            .import_modules_that()
            .have_name_matching(forbidden)
        )
        rule.assert_applies(evaluable)
