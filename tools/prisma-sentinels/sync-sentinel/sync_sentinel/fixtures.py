from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any


def sentinel_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_fixture_registry(root: Path | None = None) -> dict[str, Any]:
    base = root or sentinel_root()
    path = base / "fixtures/registry.v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise RuntimeError("BLOCKED_FIXTURE_REGISTRY_EMPTY")
    ids = [str(item.get("fixtureId", "")) for item in fixtures if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        raise RuntimeError("BLOCKED_FIXTURE_REGISTRY_DUPLICATE_ID")
    return data


def fixture_matrix_csv(registry: dict[str, Any]) -> str:
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow([
        "fixtureId",
        "direction",
        "topic",
        "kind",
        "expectedOutcome",
        "expectedFaultZone",
        "implemented",
        "mandatoryAssertions",
    ])
    for item in registry.get("fixtures", []):
        writer.writerow([
            item.get("fixtureId", ""),
            item.get("direction", ""),
            item.get("topic", ""),
            item.get("kind", ""),
            item.get("expectedOutcome", ""),
            item.get("expectedFaultZone") or "",
            str(bool(item.get("implemented"))).lower(),
            ";".join(str(v) for v in item.get("mandatoryAssertions", [])),
        ])
    return out.getvalue()


def mandatory_fixture_readiness(registry: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for item in registry.get("fixtures", []):
        fixture_id = str(item.get("fixtureId", "UNKNOWN"))
        if not item.get("implemented"):
            missing.append(fixture_id)
        if not item.get("expectedOutcome") or not item.get("mandatoryAssertions"):
            invalid.append(fixture_id)
    return {
        "implemented": len(registry.get("fixtures", [])) - len(missing),
        "total": len(registry.get("fixtures", [])),
        "missingImplementations": missing,
        "invalidDefinitions": invalid,
        "ready": not missing and not invalid,
    }
