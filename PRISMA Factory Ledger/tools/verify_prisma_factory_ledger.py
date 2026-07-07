#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys, re, hashlib
from pathlib import Path
from datetime import datetime

ALLOWED_CLASSIFICATIONS = {"DONE", "VERIFY", "FIX", "BUILD", "EXTERNAL"}
ALLOWED_STATUSES = {
    "NOT_STARTED", "DESIGNED", "SOURCE_READY", "LOCAL_VERIFIED", "RUNTIME_VERIFIED",
    "LIVE_CERTIFIED", "VISUAL_CERTIFIED", "DISTRIBUTABLE_READY", "FROZEN",
    "EXTERNAL_BLOCKED", "VERIFY_REQUIRED"
}
REQUIRED_FILES = [
    "PRISMA_FACTORY_LEDGER.md",
    "PRISMA_FACTORY_LEDGER.json",
    "PRISMA_FACTORY_LEDGER.schema.json",
    "PRISMA_EVIDENCE_INDEX.md",
    "PRISMA_EVIDENCE_INDEX.json",
    "PRISMA_FACTORY_LEDGER_AGENT_GATE.md",
    "PRISMA_FACTORY_PROMPT_BASE.md",
]
FORBIDDEN_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)(PRISMA_ADMIN_TOKEN|CLOUDFLARE_API_TOKEN|GITHUB_TOKEN)\s*=\s*['\"][^'\"]{8,}['\"]"),
]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if root.name != "PRISMA Factory Ledger":
        if (root / "PRISMA Factory Ledger").exists():
            root = root / "PRISMA Factory Ledger"
    errors = []
    warnings = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    ledger_path = root / "PRISMA_FACTORY_LEDGER.json"
    evidence_path = root / "PRISMA_EVIDENCE_INDEX.json"
    if errors:
        print("FAIL_FACTORY_LEDGER_MISSING_FILES")
        for e in errors:
            print("ERROR", e)
        return 1

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    ids = set()
    for cap in ledger.get("capabilities", []):
        cid = cap.get("id")
        if not cid:
            errors.append("capability missing id")
            continue
        if cid in ids:
            errors.append(f"duplicate capability id: {cid}")
        ids.add(cid)
        if cap.get("classification") not in ALLOWED_CLASSIFICATIONS:
            errors.append(f"{cid}: invalid classification {cap.get('classification')}")
        if cap.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{cid}: invalid status {cap.get('status')}")
        if not cap.get("evidence"):
            errors.append(f"{cid}: evidence required")
        if "doesNotProve" not in cap or not cap.get("doesNotProve"):
            errors.append(f"{cid}: doesNotProve required")
        if cap.get("doNotRebuild") is True and cap.get("classification") == "BUILD":
            errors.append(f"{cid}: cannot be BUILD with doNotRebuild=true")
        if cap.get("status") == "EXTERNAL_BLOCKED" and cap.get("classification") != "EXTERNAL":
            warnings.append(f"{cid}: EXTERNAL_BLOCKED should normally be classification EXTERNAL")

    for art in evidence.get("artifacts", []):
        if not art.get("artifact"):
            errors.append("evidence artifact missing artifact name")
        if not art.get("proves"):
            errors.append(f"{art.get('artifact')}: proves required")
        if not art.get("doesNotProve"):
            errors.append(f"{art.get('artifact')}: doesNotProve required")

    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".ps1", ".py", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pat in FORBIDDEN_SECRET_PATTERNS:
                if pat.search(text):
                    errors.append(f"secret-like literal detected in {path.relative_to(root)}")

    report = {
        "status": "PASS_FACTORY_LEDGER_VERIFY" if not errors else "FAIL_FACTORY_LEDGER_VERIFY",
        "verifiedAt": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "capabilities": len(ledger.get("capabilities", [])),
        "evidenceArtifacts": len(evidence.get("artifacts", [])),
        "errors": errors,
        "warnings": warnings,
        "files": {rel: sha256(root / rel) for rel in REQUIRED_FILES if (root / rel).exists()},
    }
    out_dir = root / "verification"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "last_verify_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "last_verify_report.md").write_text(
        "# PRISMA Factory Ledger Verification\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Capabilities: {report['capabilities']}\n\n"
        f"Evidence artifacts: {report['evidenceArtifacts']}\n\n"
        f"Errors: {len(errors)}\n\n"
        f"Warnings: {len(warnings)}\n",
        encoding="utf-8"
    )
    print(report["status"])
    print(f"capabilities={report['capabilities']} evidenceArtifacts={report['evidenceArtifacts']} errors={len(errors)} warnings={len(warnings)}")
    for e in errors:
        print("ERROR", e)
    for w in warnings:
        print("WARN", w)
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
