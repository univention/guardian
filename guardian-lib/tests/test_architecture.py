# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""Architecture boundary tests enforcing hexagonal architecture.

Uses two complementary strategies:
- AST-based import scanning for external library checks (sqlalchemy, etc.)
  because pytestarch only graphs project-internal modules.
- pytestarch rules for internal cross-package boundary checks (adapter isolation,
  ports-do-not-import-adapters).

guardian-lib is a shared library with a small surface:
- ports.py: Abstract port interfaces (ABCs)
- adapters/: Concrete adapter implementations (authentication, settings)
- models/: Data models (authentication)

As a shared library, guardian-lib must not import from service-specific packages
(guardian_management_api, guardian_authorization_api).
"""

from pathlib import Path
from typing import Any

import pytest
from guardian_pytest.architecture import (
    assert_dir_does_not_import,
    assert_file_does_not_import,
    assert_file_does_not_import_prefix,
    collect_imports,
    top_level,
)
from pytestarch import Rule, get_evaluable_architecture

ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT_DIR / "guardian_lib"
ADAPTERS_DIR = PACKAGE_DIR / "adapters"
MODELS_DIR = PACKAGE_DIR / "models"

PKG = "guardian_lib"


@pytest.fixture(scope="module")
def evaluable() -> Any:
    """Create an evaluable architecture representation for pytestarch rules."""
    return get_evaluable_architecture(str(PACKAGE_DIR), str(PACKAGE_DIR))


# ===================================================================
# Ports (ports.py) -- must not import adapters or service-specific code
# ===================================================================


class TestPortsBoundaries:
    """Ports (ABCs) must not import from adapters, frameworks, or service-specific packages."""

    PORTS_FILE = PACKAGE_DIR / "ports.py"

    @pytest.mark.parametrize(
        "forbidden",
        ["authlib", "fastapi", "httpx", "jwt", "requests", "sqlalchemy", "starlette"],
    )
    def test_no_framework_import(self, forbidden: str) -> None:
        assert_file_does_not_import(
            self.PORTS_FILE, forbidden, root_dir=ROOT_DIR, layer_name="ports"
        )

    def test_no_adapter_imports(self) -> None:
        assert_file_does_not_import_prefix(
            self.PORTS_FILE,
            f"{PKG}.adapters",
            root_dir=ROOT_DIR,
            layer_name="ports",
        )

    def test_no_management_api_imports(self) -> None:
        assert_file_does_not_import(
            self.PORTS_FILE,
            "guardian_management_api",
            root_dir=ROOT_DIR,
            layer_name="ports",
        )

    def test_no_authorization_api_imports(self) -> None:
        assert_file_does_not_import(
            self.PORTS_FILE,
            "guardian_authorization_api",
            root_dir=ROOT_DIR,
            layer_name="ports",
        )


# ===================================================================
# Models -- must not import adapters, frameworks, or service-specific code
# ===================================================================


class TestModelsBoundaries:
    """Models must not import from adapters, frameworks, or service-specific packages."""

    @pytest.mark.parametrize(
        "forbidden",
        ["authlib", "fastapi", "httpx", "jwt", "requests", "sqlalchemy", "starlette"],
    )
    def test_no_framework_import(self, forbidden: str) -> None:
        assert_dir_does_not_import(
            MODELS_DIR, forbidden, root_dir=ROOT_DIR, layer_name="models"
        )

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

    def test_no_management_api_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(MODELS_DIR)
            if top_level(module) == "guardian_management_api"
        ]
        assert not violations, (
            "Architecture violation (models): imports from management-api:\n"
            + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
        )

    def test_no_authorization_api_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(MODELS_DIR)
            if top_level(module) == "guardian_authorization_api"
        ]
        assert not violations, (
            "Architecture violation (models): imports from authorization-api:\n"
            + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
        )


# ===================================================================
# Adapters -- must not import service-specific code
# ===================================================================


class TestAdaptersBoundaries:
    """Adapters must not import service-specific packages."""

    def test_no_management_api_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(ADAPTERS_DIR)
            if top_level(module) == "guardian_management_api"
        ]
        assert not violations, (
            "Architecture violation (adapters): imports from management-api:\n"
            + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
        )

    def test_no_authorization_api_imports(self) -> None:
        violations = [
            (path.relative_to(ROOT_DIR), module)
            for path, module in collect_imports(ADAPTERS_DIR)
            if top_level(module) == "guardian_authorization_api"
        ]
        assert not violations, (
            "Architecture violation (adapters): imports from authorization-api:\n"
            + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
        )


# ===================================================================
# Pytestarch rules -- internal cross-package boundary checks
# ===================================================================


class TestPytestarchBoundaries:
    """Cross-package import boundaries enforced via pytestarch."""

    def test_ports_do_not_import_adapters(self, evaluable: Any) -> None:
        """Ports must not import from adapter modules."""
        rule = (
            Rule()
            .modules_that()
            .have_name_matching(f"{PKG}.ports")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
        )
        rule.assert_applies(evaluable)

    def test_models_do_not_import_adapters(self, evaluable: Any) -> None:
        """Models must not import from adapter modules."""
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.models")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
        )
        rule.assert_applies(evaluable)

    def test_models_do_not_import_ports(self, evaluable: Any) -> None:
        """Models must not import from ports (dependency goes ports -> models, not reverse)."""
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.models")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.ports")
        )
        rule.assert_applies(evaluable)

    def test_adapters_do_not_import_logging(self, evaluable: Any) -> None:
        """Adapters must not import the guardian_lib.logging utility module
        (logging belongs in composition/infrastructure, not adapters).
        """
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of(f"{PKG}.adapters")
            .should_not()
            .import_modules_that()
            .have_name_matching(f"{PKG}.logging")
        )
        rule.assert_applies(evaluable)
