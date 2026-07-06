from __future__ import annotations

import json
import tempfile
from pathlib import Path

from autogit_engine.ag98_policy import (
    load_policy,
    is_sensitive_named_evidence_allowed,
    classify_commit_group,
    is_generated_at_only_diff,
    classify_preflight_path,
    safe_self_heal_extensions,
)

def assert_true(value, msg):
    if not value:
        raise AssertionError(msg)

def main():
    root = Path(tempfile.mkdtemp(prefix="ag98_selftest_"))
    (root / "autogit" / "config").mkdir(parents=True, exist_ok=True)
    (root / "autogit" / "config" / "autogit_98_policy.json").write_text(json.dumps({"schema": "autogit.ag98_policy.v1"}, indent=2), encoding="utf-8")

    assert_true(is_sensitive_named_evidence_allowed(root, "apps/terminal-de-venta-system/docs/ops/licscope/PII_SECRET_SAFETY_MATRIX.md"), "licscope matrix should be allowlisted by policy")
    assert_true(classify_commit_group(root, "autogit/engine/autogit_engine/ag98_policy.py") == "tooling/autogit", "autogit files should group as tooling/autogit")
    assert_true(classify_commit_group(root, "apps/terminal-de-venta-system/docs/ops/licscope/foo.md") == "docs/licscope-evidence", "licscope evidence group")
    assert_true(classify_preflight_path(root, "apps/synapse-x/data/sqlite/synapse_x.db-wal")["decision"] == "EXCLUDE_SAFE", "db-wal should be excluded")
    assert_true(".md" in safe_self_heal_extensions(root), "markdown should be safe self-heal extension")
    print("AG98_SELFTEST_OK")

if __name__ == "__main__":
    main()
