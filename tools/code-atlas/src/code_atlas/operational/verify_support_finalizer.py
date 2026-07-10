from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .support_finalizer import ALLOWED_ACTION, ALLOWED_STATUS, EXPECTED_CANONICAL_PATHS, GAP_CLASSIFICATIONS, VERSION

FORBIDDEN_SECRET_KEYS = {"secret", "secretValue", "matchedText", "privateKey", "tokenValue", "authorizationValue", "passwordValue"}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(repo_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    app = repo / "apps" / "terminal-de-venta-system" if (repo / "apps" / "terminal-de-venta-system").exists() else repo
    root = app / "prisma-support-resolver"
    manifest_path = root / "SUPPORT_RESOLVER_FINAL_MANIFEST.json"
    feed_path = root / "generated/ui/support-resolver-ui-feed.json"
    schema_path = root / "generated/ui/support-resolver-ui-feed.schema.json"
    handoff_path = root / "SUPPORT_RESOLVER_UI_HANDOFF.json"
    gaps_path = root / "SUPPORT_RESOLVER_GAP_REGISTER.json"
    required = [manifest_path, feed_path, schema_path, handoff_path, gaps_path, root / "SUPPORT_RESOLVER_FINAL_MANIFEST.md", root / "SUPPORT_RESOLVER_UI_HANDOFF.md", root / "SUPPORT_RESOLVER_GAP_REGISTER.md", root / "generated/ui/support-resolver-ui-types.ts"]
    missing_files = [str(p) for p in required if not p.exists()]
    if missing_files:
        return {"status": "FAIL_SUPPORT_DATA_SPINE_VERIFY", "missingFiles": missing_files}
    manifest, feed, schema, handoff, gap_register = map(_load, [manifest_path, feed_path, schema_path, handoff_path, gaps_path])
    errors = feed.get("errorCodes", [])
    actions = feed.get("actions", [])
    artifact_records = manifest.get("artifacts", [])
    expected_set = {str(Path("prisma-support-resolver") / p).replace("/", "\\") for p in EXPECTED_CANONICAL_PATHS}
    recorded_set = {str(x.get("canonicalPath", "")) for x in artifact_records}
    missing_inventory = sorted(expected_set - recorded_set)
    invalid_status = [x.get("id") for x in artifact_records if x.get("currentStatus") not in ALLOWED_STATUS]
    invalid_action = [x.get("id") for x in artifact_records if x.get("action") not in ALLOWED_ACTION]
    invalid_gap = [x.get("id") for x in gap_register.get("gaps", []) if x.get("classification") not in GAP_CLASSIFICATIONS]
    dup_codes = sorted({x.get("code") for x in errors if sum(1 for y in errors if y.get("code") == x.get("code")) > 1})
    dup_actions = sorted({x.get("id") for x in actions if sum(1 for y in actions if y.get("id") == x.get("id")) > 1})
    data_keys = set(feed.keys())
    invalid_bindings = []
    for screen in feed.get("screens", []):
        for key in screen.get("dataKeys", []):
            if key not in data_keys:
                invalid_bindings.append(f"{screen.get('id')}:{key}")
    forbidden_hits = []
    stack = [("feed", feed)]
    while stack:
        loc, value = stack.pop()
        if isinstance(value, dict):
            for k, v in value.items():
                if k in FORBIDDEN_SECRET_KEYS:
                    forbidden_hits.append(f"{loc}.{k}")
                stack.append((f"{loc}.{k}", v))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                stack.append((f"{loc}[{i}]", v))
    checks = {
        "finalizerVersion": manifest.get("generator", {}).get("version") == VERSION,
        "uiFeedReady": manifest.get("uiDataStatus") == "PASS_SUPPORT_DATA_SPINE_READY_FOR_UI",
        "runtimeNotFalselyCertified": manifest.get("runtimeCertified") is False and feed.get("summary", {}).get("runtimeCertified") is False,
        "errorCodeCount68": len(errors) == 68,
        "actionCount13": len(actions) == 13,
        "noDuplicateCodes": not dup_codes,
        "noDuplicateActions": not dup_actions,
        "expectedInventoryRecorded": not missing_inventory,
        "artifactStatusesValid": not invalid_status,
        "artifactActionsValid": not invalid_action,
        "gapClassificationsValid": not invalid_gap,
        "screenBindingsValid": not invalid_bindings,
        "noSecretValuesExported": not forbidden_hits,
        "schemaVersion": schema.get("properties", {}).get("schemaVersion", {}).get("const") == "1.0.0",
        "handoffPointsToFeed": handoff.get("feedPath") == "generated/ui/support-resolver-ui-feed.json",
        "doNotRebuild": manifest.get("doNotRebuild") is True,
    }
    ok = all(checks.values())
    return {
        "status": "PASS_SUPPORT_DATA_SPINE_VERIFY" if ok else "FAIL_SUPPORT_DATA_SPINE_VERIFY",
        "checks": checks, "missingFiles": missing_files, "missingInventory": missing_inventory,
        "invalidStatuses": invalid_status, "invalidActions": invalid_action, "invalidGaps": invalid_gap,
        "duplicateCodes": dup_codes, "duplicateActions": dup_actions, "invalidBindings": invalid_bindings,
        "forbiddenSecretFields": forbidden_hits, "finalRuntimeStatus": manifest.get("finalStatus"),
        "gapCount": feed.get("summary", {}).get("gapCount"), "blockingGapCount": feed.get("summary", {}).get("blockingGapCount"),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    args = p.parse_args(argv)
    result = verify(args.repo)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
