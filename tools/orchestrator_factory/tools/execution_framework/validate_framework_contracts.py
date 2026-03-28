from __future__ import annotations

import re
import sys
sys.dont_write_bytecode = True

from pathlib import Path
from typing import Any

from lib.common import discover_repo_root, read_json, stable_json_dumps


SEMVER_RE = re.compile(r"^\d+\.\d+(?:\.\d+)?$")


def _load_json(path: Path, errors: list[dict[str, str]]) -> dict[str, Any] | None:
    try:
        data = read_json(path)
    except Exception as exc:  # pragma: no cover - defensive guard
        errors.append({"code": "invalid_json", "path": str(path), "message": str(exc)})
        return None
    if not isinstance(data, dict):
        errors.append({"code": "invalid_shape", "path": str(path), "message": "JSON root must be an object"})
        return None
    return data


def _validate_schema_version(path: Path, payload: dict[str, Any], errors: list[dict[str, str]]) -> None:
    version = payload.get("schema_version")
    if version is None:
        return
    if not isinstance(version, str) or not SEMVER_RE.match(version.strip()):
        errors.append(
            {
                "code": "invalid_schema_version",
                "path": str(path),
                "message": "schema_version must match MAJOR.MINOR or MAJOR.MINOR.PATCH",
            }
        )


def _validate_schema_file(path: Path, payload: dict[str, Any], errors: list[dict[str, str]]) -> None:
    if not isinstance(payload.get("name"), str) or not payload["name"].strip():
        errors.append({"code": "schema_missing_name", "path": str(path), "message": "schema must define non-empty 'name'"})
    required = payload.get("required_fields")
    if not isinstance(required, dict):
        errors.append({"code": "schema_missing_required_fields", "path": str(path), "message": "schema must define object 'required_fields'"})
    optional = payload.get("optional_fields")
    if optional is not None and not isinstance(optional, dict):
        errors.append({"code": "schema_invalid_optional_fields", "path": str(path), "message": "'optional_fields' must be an object when present"})


def _validate_template_file(path: Path, payload: dict[str, Any], errors: list[dict[str, str]]) -> None:
    version = payload.get("schema_version")
    if not isinstance(version, str) or not version.strip():
        errors.append({"code": "template_missing_schema_version", "path": str(path), "message": "template json must include 'schema_version'"})


def _validate_template_schema_pairs(repo_root: Path, errors: list[dict[str, str]]) -> None:
    templates_root = repo_root / "templates/execution_framework"
    schemas_root = repo_root / "schemas/execution_framework"
    for template in sorted(templates_root.rglob("*.template.json")):
        base = template.name.replace(".template.json", "")
        schema = schemas_root / f"{base}.schema.json"
        if not schema.exists():
            errors.append(
                {
                    "code": "missing_schema_for_template",
                    "path": str(template),
                    "message": f"expected matching schema '{schema}'",
                }
            )


def validate(repo_root: Path) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    config_files = sorted((repo_root / "configs/execution_framework").glob("*.json"))
    schema_files = sorted((repo_root / "schemas/execution_framework").glob("*.json"))
    template_files = sorted((repo_root / "templates/execution_framework").rglob("*.template.json"))

    for path in config_files:
        payload = _load_json(path, errors)
        if payload is None:
            continue
        _validate_schema_version(path, payload, errors)

    for path in schema_files:
        payload = _load_json(path, errors)
        if payload is None:
            continue
        _validate_schema_file(path, payload, errors)

    for path in template_files:
        payload = _load_json(path, errors)
        if payload is None:
            continue
        _validate_template_file(path, payload, errors)
        _validate_schema_version(path, payload, errors)

    _validate_template_schema_pairs(repo_root, errors)

    return {
        "repo_root": str(repo_root),
        "checked": {
            "configs": len(config_files),
            "schemas": len(schema_files),
            "templates_json": len(template_files),
        },
        "errors": errors,
        "warnings": warnings,
        "ok": len(errors) == 0,
    }


def main() -> int:
    repo_root = discover_repo_root(Path(__file__).resolve())
    result = validate(repo_root)
    print(stable_json_dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
