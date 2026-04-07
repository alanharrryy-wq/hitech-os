from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SESSIONS_PATH = ROOT / "golden_sessions" / "golden_sessions_v1.json"
PREMIUM_CONTRACT_PATH = ROOT / "contracts" / "premium_capabilities_100.md"
BASELINE_ROOT = ROOT / "baselines" / "ux_release_proof" / "v1"
SEMANTIC_BASELINE_PATH = ROOT / "baselines" / "ux_release_proof" / "v1" / "semantic_baseline.json"
VISUAL_BASELINE_PATH = ROOT / "baselines" / "ux_release_proof" / "v1" / "visual_baseline_manifest.json"
BASELINE_VERSION = "v1"


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def load_golden_sessions() -> dict[str, Any]:
    payload = load_json_file(GOLDEN_SESSIONS_PATH)
    sessions = payload.get("sessions", [])
    if not isinstance(sessions, list):
        payload["sessions"] = []
    return payload


def load_semantic_baseline() -> dict[str, Any]:
    return load_json_file(SEMANTIC_BASELINE_PATH)


def load_visual_baseline_manifest() -> dict[str, Any]:
    return load_json_file(VISUAL_BASELINE_PATH)
