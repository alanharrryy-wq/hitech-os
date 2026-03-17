from pathlib import Path
import json

FORBIDDEN_PARTS = {
    "_local",
    ".git",
    "__pycache__",
}

FORBIDDEN_SUFFIXES = {
    ".tmp",
    ".bak",
}

def evaluate_promotion_gate(candidate_root, diff_payload: dict) -> dict:
    candidate_root = Path(candidate_root)

    violations = []

    for path in candidate_root.rglob("*"):
        rel = path.relative_to(candidate_root)

        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            violations.append({
                "type": "forbidden_path_part",
                "path": str(rel).replace("\\", "/"),
            })

        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
            violations.append({
                "type": "forbidden_suffix",
                "path": str(rel).replace("\\", "/"),
            })

    total_touched = diff_payload.get("counts", {}).get("total_touched", 0)

    return {
        "allowed": len(violations) == 0,
        "violations": violations,
        "total_touched": total_touched,
        "promotion_mode": "manual_only",
        "notes": [
            "Shadow foundation never promotes automatically.",
            "Manual review is required before any real apply path exists.",
        ],
    }

def assert_promotion_ready(gate_payload: dict):
    if not gate_payload.get("allowed", False):
        raise RuntimeError(
            "Promotion gate blocked candidate changes: "
            + json.dumps(gate_payload.get("violations", []), ensure_ascii=False)
        )
