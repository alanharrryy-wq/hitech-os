from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from code_atlas.coverage.atlas_audit import CoverageAuditConfig, run_audit
from code_atlas.coverage.important_gate import evaluate_gate
from code_atlas.db_glass.reality_check import run_reality_check
from code_atlas.manifest.todo_el_show_plus import run_todo_plus


def make_fixture(root: Path) -> None:
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    atlas = {"important_entrypoints": ["src/app.py"], "nodes": [{"path": "src/app.py"}]}
    (root / "atlas.json").write_text(json.dumps(atlas), encoding="utf-8")
    prisma_dir = root / "prisma"
    prisma_dir.mkdir()
    (prisma_dir / "schema.prisma").write_text('''datasource db {\n provider = "sqlite"\n url = env("DATABASE_URL")\n}\nmodel User {\n id Int @id\n name String\n posts Post[]\n}\nmodel Post {\n id Int @id\n user_id Int\n title String\n}\n''', encoding="utf-8")
    db = root / "app.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT)")
    conn.execute("INSERT INTO users(name) VALUES ('Ana')")
    conn.commit(); conn.close()


def main() -> int:
    out = ROOT / "reports" / "selftest_atlas_plus"
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        fixture = Path(td) / "fixture"
        fixture.mkdir()
        make_fixture(fixture)
        coverage = run_audit(CoverageAuditConfig(project_root=fixture, atlas_paths=(fixture / "atlas.json",), output_dir=out))
        assert coverage["validation"] == "PASS", coverage
        gate = evaluate_gate(coverage)
        assert gate["status"] == "PASS", gate
        db = run_reality_check(fixture)
        assert db["validation"] == "PASS", db
        assert db["counts"]["sqlite_files"] == 1, db
        assert db["counts"]["prisma_schemas"] == 1, db
        assert db["counts"]["ghost_relations"] >= 1, db
        manifest = run_todo_plus(fixture, out / "todo")
        assert manifest["validation"] == "PASS", manifest
    print("ATLAS PLUS SMOKE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
