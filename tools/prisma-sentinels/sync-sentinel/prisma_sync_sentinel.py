#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sync_sentinel.evidence import build_bundle, now_iso
from sync_sentinel.model import Verdict
from sync_sentinel.orchestration import certify, diagnose, scan
from sync_sentinel.safety import detect_repo


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PRISMA Sync Sentinel: fail-closed Tablet↔PC sync verification tooling")
    p.add_argument("mode", choices=["scan", "diagnose", "certify", "self-test"])
    p.add_argument("--repo", default=None)
    p.add_argument("--expected-head", default=None)
    p.add_argument("--evidence-dir", default=None)
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--keep-work", action="store_true")
    return p


def self_test() -> int:
    import unittest
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS_SYNC_SENTINEL_SELF_TEST")
        return 0
    print("FAIL_SYNC_SENTINEL_SELF_TEST")
    return 1


def main() -> int:
    args = parser().parse_args()
    if args.mode == "self-test":
        return self_test()
    try:
        repo = detect_repo(args.repo)
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED_SYNC_SENTINEL", "error": str(exc)}, indent=2))
        return 2

    evidence_dir = Path(args.evidence_dir).resolve() if args.evidence_dir else repo / "tools/_local/reports/sync-sentinel"
    if args.mode == "scan":
        report = scan(repo, args.expected_head, workers=args.workers)
        payload = report.to_dict() | {"status": f"{report.verdict.value}_SYNC_SCAN", "generatedAt": now_iso(), "repoHead": report.facts.get("repoHead"), "productionCertified": False}
        bundle, secret_count, _ = build_bundle(evidence_dir, payload)
        payload["evidenceBundle"] = str(bundle)
        payload["secretFindings"] = secret_count
        print(json.dumps(payload, indent=2))
        return 0 if report.verdict == Verdict.PASS and secret_count == 0 else 1
    if args.mode == "diagnose":
        report = diagnose(repo, args.expected_head)
        payload = report.to_dict() | {"status": f"{report.verdict.value}_SYNC_DIAGNOSE", "generatedAt": now_iso(), "repoHead": report.facts.get("repoHead"), "productionCertified": False}
        bundle, secret_count, _ = build_bundle(evidence_dir, payload)
        payload["evidenceBundle"] = str(bundle)
        payload["secretFindings"] = secret_count
        print(json.dumps(payload, indent=2))
        return 0 if report.verdict == Verdict.PASS and secret_count == 0 else 1

    report, bundle = certify(repo, evidence_dir, args.expected_head, args.keep_work, workers=args.workers)
    success = report.verdict == Verdict.PASS and bundle is not None
    final = report.to_dict() | {
        "status": "PASS_SYNC_CERTIFICATION" if success else f"{report.verdict.value}_SYNC_CERTIFICATION",
        "repoHead": report.facts.get("repoHead") or args.expected_head,
        "evidenceBundle": str(bundle) if bundle else None,
        "productionCertified": False,
    }
    print(json.dumps(final, indent=2))
    if success:
        print("PASS_SYNC_CERTIFICATION")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
