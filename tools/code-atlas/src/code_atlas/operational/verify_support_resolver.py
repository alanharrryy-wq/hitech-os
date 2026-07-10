from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from .support_resolver import VERSION, run_support_resolver_atlas

REQUIRED_KEYS = {
    "supportResolverSummary",
    "supportCapabilityMatrix",
    "supportErrorCodeCoverage",
    "supportActionCoverage",
    "supportUiRouteMap",
    "supportE2eCoverage",
    "supportDuplicateImplementations",
    "supportDoNotRebuildMap",
    "supportContractCoverage",
    "supportSecurityRisks",
}


def verify(repo: str | Path, out: str | Path, result_root: str | Path | None = None) -> dict:
    result = run_support_resolver_atlas(repo, out, result_root)
    payload = result.get("payload", {})
    missing = sorted(REQUIRED_KEYS.difference(payload))
    support_out = Path(out).resolve() / "support_resolver"
    required_files = [
        support_out / "SUPPORT_ATLAS_MANIFEST.json",
        support_out / "SUPPORT_CAN_PATCH_DECISION.md",
        support_out / "supportCapabilityMatrix.csv",
        support_out / "supportErrorCodeCoverage.csv",
        support_out / "supportActionCoverage.csv",
        support_out / "supportUiRouteMap.csv",
        support_out / "supportDuplicateImplementations.csv",
        support_out / "supportSecurityRisks.csv",
        support_out / "supportDoNotRebuildMap.csv",
    ]
    absent_files = [str(path) for path in required_files if not path.exists()]
    summary = result.get("summary", {})
    route_rows = payload.get("supportUiRouteMap", [])
    invalid_routes = [row.get("path", "") for row in route_rows if row.get("artifactType") not in {"UI_ROUTE", "API_ROUTE"}]
    duplicate_rows = payload.get("supportDuplicateImplementations", [])
    support_duplicate = next((row for row in duplicate_rows if row.get("concept") == "support_resolver_api"), {})
    duplicate_paths = [path for path in str(support_duplicate.get("allPaths", "")).split("|") if path]
    false_duplicate_consumers = [path for path in duplicate_paths if Path(path).name.lower() != "support_resolver_api.py"]
    security_rows = payload.get("supportSecurityRisks", [])
    invalid_security = [
        row.get("path", "") for row in security_rows
        if not {"patternClass", "severity", "confidence", "blocking", "lineNumber"}.issubset(row)
        or any(forbidden in row for forbidden in ("value", "matchedText", "secret"))
    ]
    ok = (
        not missing
        and not absent_files
        and summary.get("version") == VERSION == "1.1.0"
        and summary.get("errorCodeCount") == 68
        and summary.get("doNotRebuild") is True
        and not invalid_routes
        and not false_duplicate_consumers
        and not invalid_security
    )
    return {
        "status": "PASS_SUPPORT_RESOLVER_CONSUMER_VERIFY" if ok else "FAIL_SUPPORT_RESOLVER_CONSUMER_VERIFY",
        "version": VERSION,
        "missingPayloadKeys": missing,
        "missingFiles": absent_files,
        "invalidRouteRows": invalid_routes,
        "falseDuplicateConsumers": false_duplicate_consumers,
        "invalidSecurityRows": invalid_security,
        "summaryStatus": summary.get("status"),
        "errorCodeCount": summary.get("errorCodeCount"),
        "resolverActionCount": summary.get("resolverActionCount"),
        "testArtifactsDetected": summary.get("errorCatalogVerifierCount", 0) + summary.get("actionCatalogVerifierCount", 0),
        "supportRouteCount": summary.get("supportRouteCount"),
        "blockingSecretRiskCount": summary.get("blockingSecretRiskCount"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--result-root", default=None)
    args = parser.parse_args(argv)
    if args.out:
        result = verify(args.repo, args.out, args.result_root)
    else:
        with tempfile.TemporaryDirectory(prefix="support_resolver_verify_") as td:
            result = verify(args.repo, td, args.result_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
