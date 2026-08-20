#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
from pathlib import Path

GOVERNED_GUARDRAILS = (
    "uq_pricelist_single_default_per_business",
    "uq_taxrate_single_default_per_business",
    "uq_cashsession_single_open_per_terminal",
)
REQUIRED_TRIGGERS = {
    "trg_purchase_order_line_ai",
    "trg_purchase_order_line_au",
    "trg_purchase_order_line_ad",
    "trg_purchase_order_totals_guard",
    "trg_goods_receipt_line_ai",
    "trg_goods_receipt_line_au",
    "trg_goods_receipt_line_ad",
    "trg_goods_receipt_totals_guard",
}


def normalize_default(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"0", "false"}:
        return "false"
    if text in {"1", "true"}:
        return "true"
    return text


def snapshot(path: Path) -> dict[str, object]:
    conn = sqlite3.connect(path)
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            if row[0] != "_prisma_migrations"
        ]
        columns: dict[str, list[tuple[object, ...]]] = {}
        foreign_keys: dict[str, list[tuple[object, ...]]] = {}
        index_signatures: dict[str, set[tuple[bool, tuple[str, ...]]]] = {}
        for table in tables:
            columns[table] = sorted(
                (
                    row[1],
                    str(row[2]).upper(),
                    int(row[3]),
                    normalize_default(row[4]),
                    int(row[5]),
                )
                for row in conn.execute(f'PRAGMA table_info("{table}")')
            )
            foreign_keys[table] = sorted(
                (row[2], row[3], row[4], row[5], row[6])
                for row in conn.execute(f'PRAGMA foreign_key_list("{table}")')
            )
            signatures: set[tuple[bool, tuple[str, ...]]] = set()
            for index_row in conn.execute(f'PRAGMA index_list("{table}")'):
                name = str(index_row[1])
                unique = bool(index_row[2])
                index_columns = tuple(
                    str(row[2]) for row in conn.execute(f'PRAGMA index_info("{name}")')
                )
                signatures.add((unique, index_columns))
            index_signatures[table] = signatures

        guardrails: dict[str, str | None] = {}
        for name in GOVERNED_GUARDRAILS:
            row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='index' AND name=?", (name,)
            ).fetchone()
            guardrails[name] = str(row[0]) if row and row[0] else None

        return {
            "tables": tables,
            "columns": columns,
            "foreignKeys": foreign_keys,
            "indexSignatures": index_signatures,
            "foreignKeyCheck": [list(row) for row in conn.execute("PRAGMA foreign_key_check")],
            "guardrails": guardrails,
            "triggers": [
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name"
                )
            ],
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--canonical-ddl", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    database = Path(args.database).resolve()
    canonical_ddl = Path(args.canonical_ddl).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not database.is_file():
        raise SystemExit(f"database not found: {database}")
    if not canonical_ddl.is_file():
        raise SystemExit(f"canonical DDL not found: {canonical_ddl}")

    with tempfile.TemporaryDirectory(prefix="pc-wave2-schema-") as tmp:
        target_db = Path(tmp) / "canonical-target.db"
        conn = sqlite3.connect(target_db)
        try:
            conn.executescript(canonical_ddl.read_text(encoding="utf-8"))
        finally:
            conn.close()

        actual = snapshot(database)
        target = snapshot(target_db)

    missing_target_indexes: dict[str, list[dict[str, object]]] = {}
    for table in target["tables"]:
        missing = target["indexSignatures"][table] - actual["indexSignatures"].get(table, set())
        if missing:
            missing_target_indexes[table] = [
                {"unique": unique, "columns": list(columns)}
                for unique, columns in sorted(missing)
            ]

    missing_guardrails = [
        name
        for name, sql in actual["guardrails"].items()
        if not sql or " WHERE " not in sql.upper()
    ]
    missing_triggers = sorted(REQUIRED_TRIGGERS - set(actual["triggers"]))

    report = {
        "verifier": "PC_WAVE2_GOVERNED_SCHEMA_PARITY_V1",
        "database": str(database),
        "canonicalDdl": str(canonical_ddl),
        "comparison": (
            "canonical schema semantics must be present; index names and column order are ignored; "
            "governed partial-unique guardrails and accounting triggers must remain"
        ),
        "tablesEqual": actual["tables"] == target["tables"],
        "columnsEquivalent": actual["columns"] == target["columns"],
        "foreignKeysEqual": actual["foreignKeys"] == target["foreignKeys"],
        "missingTargetIndexSignatures": missing_target_indexes,
        "governedPartialUniqueGuardrails": actual["guardrails"],
        "missingGovernedGuardrails": missing_guardrails,
        "missingRequiredTriggers": missing_triggers,
        "foreignKeyViolations": actual["foreignKeyCheck"],
    }
    report["pass"] = all(
        [
            report["tablesEqual"],
            report["columnsEquivalent"],
            report["foreignKeysEqual"],
            not missing_target_indexes,
            not missing_guardrails,
            not missing_triggers,
            not report["foreignKeyViolations"],
        ]
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
