#!/usr/bin/env python3
"""
HITECH OS — Render Constitution Tables (JSON -> Markdown)

- Reads canonical JSON tables in docs/constitution/tables/TBL_*.json
- Writes per-table markdown to docs/constitution/tables/rendered/<TABLE_ID>.md
- Writes combined docs/constitution/TABLES_RENDERED.md
- Writes docs/constitution/tables/_schema/TABLES_SHA256.json for drift detection

No external dependencies.
"""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

def load_json(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def dump_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_bytes(p: Path) -> bytes:
    return p.read_bytes()

def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", "<br>")

def render_table_md(table: Dict[str, Any]) -> str:
    tid = table["table_id"]
    ver = table.get("version", "")
    status = table.get("status", "")
    auth = table.get("authority_level", "")
    scope = table.get("scope", "")

    cols = table["columns"]
    col_names = [c["name"] for c in cols]
    rows = table.get("rows", [])
    defaults = table.get("row_defaults", {}) if isinstance(table.get("row_defaults", {}), dict) else {}

    header = f"""## {tid}

- **Version:** {ver}
- **Status:** {status}
- **Authority:** {auth}
- **Scope:** {scope}

"""
    # Markdown table
    md = header
    md += "| " + " | ".join(col_names) + " |\n"
    md += "| " + " | ".join(["---"] * len(col_names)) + " |\n"

    for r in rows:
        merged = dict(defaults)
        merged.update(r)
        values = []
        for c in col_names:
            v = merged.get(c, "")
            if isinstance(v, bool):
                v = "true" if v else "false"
            elif isinstance(v, (int, float)):
                v = str(v)
            elif isinstance(v, list):
                v = ", ".join([str(x) for x in v])
            else:
                v = str(v)
            values.append(md_escape(v))
        md += "| " + " | ".join(values) + " |\n"

    md += "\n"
    return md

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    tables_dir = root / "docs" / "constitution" / "tables"
    rendered_dir = tables_dir / "rendered"
    combined_out = root / "docs" / "constitution" / "TABLES_RENDERED.md"
    sha_out = tables_dir / "_schema" / "TABLES_SHA256.json"

    if not tables_dir.exists():
        raise FileNotFoundError(f"Tables dir not found: {tables_dir}")

    table_files = sorted([p for p in tables_dir.glob("TBL_*.json") if p.is_file()])
    if not table_files:
        raise FileNotFoundError("No TBL_*.json files found")

    combined = "# Rendered Constitution Tables\n\nGenerated from canonical JSON tables.\n\n"
    shas: Dict[str, str] = {}

    rendered_dir.mkdir(parents=True, exist_ok=True)

    for p in table_files:
        b = read_bytes(p)
        shas[p.name] = sha256_bytes(b)

        table = load_json(p)
        md = render_table_md(table)

        per_out = rendered_dir / f"{table['table_id']}.md"
        per_out.write_text(md, encoding="utf-8")

        combined += md

    combined_out.write_text(combined, encoding="utf-8")
    dump_json(sha_out, {"generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z", "sha256": shas})

    print("✅ Rendered tables:", len(table_files))
    print(" - per-table:", rendered_dir)
    print(" - combined:", combined_out)
    print(" - shas:", sha_out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
