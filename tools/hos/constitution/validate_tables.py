#!/usr/bin/env python3
"""
HITECH OS — Constitution Tables Validator

Validates:
1) JSON Schema compliance for each table file
2) Invariants: unique columns, required fields in rows, no extra row keys, enum membership

Strict mode semantics (Activation Readiness):
- --strict FAILS if any table with authority_level in {warning,enforced} is NOT status=active.
This prevents "enforcement before constitution approval" while still allowing DRAFT validation.

Usage:
  python tools/hos/constitution/validate_tables.py --root .
  python tools/hos/constitution/validate_tables.py --root . --strict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import jsonschema
except Exception:
    print("ERROR: Missing dependency 'jsonschema'. Install with: pip install jsonschema", file=sys.stderr)
    raise

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")

def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)

def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def find_tables(root: Path) -> List[Path]:
    tables_dir = root / "docs" / "constitution" / "tables"
    if not tables_dir.exists():
        raise FileNotFoundError(f"Tables dir not found: {tables_dir}")
    return sorted([p for p in tables_dir.glob("TBL_*.json") if p.is_file()])

def validate_schema(table: Dict[str, Any], schema: Dict[str, Any], table_path: Path) -> List[str]:
    errors: List[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(table), key=str):
        loc = "/".join([str(x) for x in err.absolute_path]) or "(root)"
        errors.append(f"{table_path.name}: schema error at {loc}: {err.message}")
    return errors

def col_map(columns: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    m: Dict[str, Dict[str, Any]] = {}
    for c in columns:
        m[c["name"]] = c
    return m

def validate_invariants(table: Dict[str, Any], table_path: Path) -> List[str]:
    errors: List[str] = []

    tid = table.get("table_id", "")
    if not isinstance(tid, str) or not tid.startswith("TBL_"):
        errors.append(f"{table_path.name}: table_id must start with TBL_")

    ver = table.get("version", "")
    if not isinstance(ver, str) or not SEMVER_RE.match(ver):
        errors.append(f"{table_path.name}: version must be semver X.Y.Z")

    if table_path.stem != tid:
        errors.append(f"{table_path.name}: filename must match table_id (expected {tid}.json)")

    columns = table.get("columns", [])
    if not isinstance(columns, list) or not columns:
        errors.append(f"{table_path.name}: columns must be a non-empty array")
        return errors

    names = [c.get("name") for c in columns if isinstance(c, dict)]
    if len(names) != len(set(names)):
        errors.append(f"{table_path.name}: duplicate column names detected")

    cm = col_map(columns)

    enum_cols = {n: c for n, c in cm.items() if c.get("type") == "enum"}
    for n, c in enum_cols.items():
        vals = c.get("enum_values")
        if not isinstance(vals, list) or not vals:
            errors.append(f"{table_path.name}: enum column '{n}' missing enum_values")

    req_cols = {n for n, c in cm.items() if c.get("required") is True}
    defaults = table.get("row_defaults", {})
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        errors.append(f"{table_path.name}: row_defaults must be an object if provided")
        defaults = {}

    rows = table.get("rows", [])
    if not isinstance(rows, list):
        errors.append(f"{table_path.name}: rows must be an array")
        return errors

    declared_cols = set(cm.keys())

    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{table_path.name}: row[{i}] must be an object")
            continue

        merged = dict(defaults)
        merged.update(row)

        missing = [c for c in req_cols if c not in merged]
        if missing:
            errors.append(f"{table_path.name}: row[{i}] missing required columns: {', '.join(sorted(missing))}")

        extras = [k for k in merged.keys() if k not in declared_cols]
        if extras:
            errors.append(f"{table_path.name}: row[{i}] has undeclared columns: {', '.join(sorted(extras))}")

        for col, cdef in enum_cols.items():
            if col in merged:
                val = merged[col]
                allowed = cdef.get("enum_values", [])
                if allowed and val not in allowed:
                    errors.append(f"{table_path.name}: row[{i}] value '{val}' not allowed for enum '{col}'")

        for col, cdef in cm.items():
            if col not in merged:
                continue
            t = cdef.get("type")
            v = merged[col]
            if t == "string" and not isinstance(v, str):
                errors.append(f"{table_path.name}: row[{i}] column '{col}' must be string")
            elif t == "number" and not isinstance(v, (int, float)):
                errors.append(f"{table_path.name}: row[{i}] column '{col}' must be number")
            elif t == "boolean" and not isinstance(v, bool):
                errors.append(f"{table_path.name}: row[{i}] column '{col}' must be boolean")
            elif t == "enum" and not isinstance(v, str):
                errors.append(f"{table_path.name}: row[{i}] enum '{col}' must be string")

    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--strict", action="store_true", help="Activation readiness: warning/enforced tables must be ACTIVE")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    schema_path = root / "docs" / "constitution" / "tables" / "_schema" / "table_spec.schema.json"
    if not schema_path.exists():
        eprint(f"ERROR: schema not found: {schema_path}")
        return 2

    schema = load_json(schema_path)
    table_paths = find_tables(root)
    if not table_paths:
        eprint("ERROR: No tables found (TBL_*.json)")
        return 2

    all_errors: List[str] = []
    readiness_blockers: List[str] = []
    warnings_draft: List[str] = []
    has_warning = False

    for tp in table_paths:
        table = load_json(tp)

        all_errors.extend(validate_schema(table, schema, tp))
        all_errors.extend(validate_invariants(table, tp))

        auth = table.get("authority_level")
        status = table.get("status")
        if auth == "warning":
            has_warning = True
        if auth in ("warning", "enforced") and status != "active":
            warnings_draft.append(tp.name)
            if args.strict:
                readiness_blockers.append(tp.name)

    if all_errors:
        eprint("❌ Constitution tables validation FAILED:\n")
        for err in all_errors:
            eprint(" -", err)
        return 1

    if args.strict and readiness_blockers:
        eprint("❌ Strict mode (Activation Readiness): blocking-authority tables must be status=active.")
        eprint("   Promote these tables to status=active when the constitution is approved:")
        for t in readiness_blockers:
            eprint(" -", t)
        return 1

    print("✅ Constitution tables validation OK")
    if warnings_draft:
        print("ℹ️ Note: Some warning/enforced tables are still status=draft (expected while Constitution is DRAFT).")
        print("   Strict mode will fail until they are promoted to status=active.")
    elif has_warning:
        print("ℹ️ Note: warning-level tables exist; they are ready for CI-blocking once you wire enforcement.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
