# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""Shared AST-based import scanning helpers for architecture boundary tests.

These helpers are used across all three subprojects (management-api,
authorization-api, guardian-lib) to enforce hexagonal architecture boundaries.
"""

import ast
from pathlib import Path


def collect_imports_from_file(py_file: Path) -> list[tuple[Path, str]]:
    """Scan a single .py file and return (file, module-path) pairs.

    Handles both ``import X`` and ``from X import ...`` forms.  Returns the
    full dotted module path for each import (e.g., ``fastapi.routing`` from
    ``from fastapi.routing import APIRouter``).
    """
    results: list[tuple[Path, str]] = []
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except SyntaxError:  # pragma: no cover
        return results  # pragma: no cover
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((py_file, alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module:
            results.append((py_file, node.module))
    return results


def collect_imports(directory: Path) -> list[tuple[Path, str]]:
    """Scan all .py files under *directory* and return (file, module-path) pairs."""
    results: list[tuple[Path, str]] = []
    for py_file in sorted(directory.rglob("*.py")):
        results.extend(collect_imports_from_file(py_file))
    return results


def top_level(module: str) -> str:
    """Return the top-level package name from a dotted module path."""
    return module.split(".")[0]


def assert_file_does_not_import(
    py_file: Path,
    forbidden_top_level: str,
    *,
    root_dir: Path,
    layer_name: str = "",
) -> None:
    """Fail if *py_file* imports *forbidden_top_level*."""
    violations = [
        (py_file.relative_to(root_dir), module)
        for _, module in collect_imports_from_file(py_file)
        if top_level(module) == forbidden_top_level
    ]
    label = f" ({layer_name})" if layer_name else ""
    assert not violations, (
        f"Architecture violation{label}: forbidden import of '{forbidden_top_level}':\n"
        + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
    )


def assert_file_does_not_import_prefix(
    py_file: Path,
    forbidden_prefix: str,
    *,
    root_dir: Path,
    layer_name: str = "",
) -> None:
    """Fail if *py_file* imports a module starting with *forbidden_prefix*."""
    violations = [
        (py_file.relative_to(root_dir), module)
        for _, module in collect_imports_from_file(py_file)
        if module.startswith(forbidden_prefix)
    ]
    label = f" ({layer_name})" if layer_name else ""
    assert not violations, (
        f"Architecture violation{label}: forbidden import prefix '{forbidden_prefix}':\n"
        + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
    )


def assert_dir_does_not_import(
    directory: Path,
    forbidden_top_level: str,
    *,
    root_dir: Path,
    layer_name: str = "",
) -> None:
    """Fail if any .py file under *directory* imports *forbidden_top_level*."""
    violations = [
        (path.relative_to(root_dir), module)
        for path, module in collect_imports(directory)
        if top_level(module) == forbidden_top_level
    ]
    label = f" ({layer_name})" if layer_name else ""
    assert not violations, (
        f"Architecture violation{label}: forbidden import of '{forbidden_top_level}':\n"
        + "\n".join(f"  {path}  ->  {mod}" for path, mod in violations)
    )
