from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any, Mapping

from .contracts import ContractError


def parse_junit_xml(text: str) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        raise ContractError("JUnit XML must be non-empty text")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ContractError(f"malformed JUnit XML: {exc}") from exc
    suites = [root] if root.tag == "testsuite" else list(root.findall(".//testsuite"))
    tests = failures = errors = skipped = 0
    names: list[str] = []
    for suite in suites:
        tests += int(suite.attrib.get("tests", 0) or 0)
        failures += int(suite.attrib.get("failures", 0) or 0)
        errors += int(suite.attrib.get("errors", 0) or 0)
        skipped += int(suite.attrib.get("skipped", suite.attrib.get("disabled", 0)) or 0)
        if suite.attrib.get("name"):
            names.append(suite.attrib["name"])
    if not suites:
        cases = root.findall(".//testcase")
        tests = len(cases)
        failures = sum(1 for case in cases if case.find("failure") is not None)
        errors = sum(1 for case in cases if case.find("error") is not None)
        skipped = sum(1 for case in cases if case.find("skipped") is not None)
    return {
        "format": "junit",
        "tests": tests,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "suiteNames": sorted(set(names)),
        "passed": tests > 0 and failures == 0 and errors == 0,
    }


def parse_sarif(payload: Mapping[str, Any] | str) -> dict[str, Any]:
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ContractError(f"malformed SARIF JSON: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ContractError("SARIF payload must be an object")
    runs = payload.get("runs")
    if not isinstance(runs, list):
        raise ContractError("SARIF payload requires runs[]")
    levels = {"error": 0, "warning": 0, "note": 0, "none": 0, "unknown": 0}
    rule_ids: set[str] = set()
    result_count = 0
    for run in runs:
        if not isinstance(run, Mapping):
            raise ContractError("SARIF run must be an object")
        for result in run.get("results", []) or []:
            if not isinstance(result, Mapping):
                continue
            result_count += 1
            level = str(result.get("level", "unknown")).lower()
            levels[level if level in levels else "unknown"] += 1
            if result.get("ruleId"):
                rule_ids.add(str(result["ruleId"]))
    return {"format": "sarif", "version": payload.get("version"), "runs": len(runs), "results": result_count, "levels": levels, "ruleIds": sorted(rule_ids)}


def parse_codeowners(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise ContractError("CODEOWNERS content must be text")
    rules: list[dict[str, Any]] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        pattern, owners = parts[0], parts[1:]
        rules.append({"pattern": pattern, "owners": owners, "line": line_number})
    return {"format": "codeowners-style-ownership", "ruleCount": len(rules), "rules": rules}


def parse_coverage_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ContractError("coverage summary must be an object")
    total = payload.get("total", payload)
    if not isinstance(total, Mapping):
        raise ContractError("coverage summary total must be an object")
    result: dict[str, Any] = {"format": "coverage-summary", "metrics": {}}
    for metric in ("lines", "statements", "functions", "branches"):
        row = total.get(metric)
        if isinstance(row, Mapping):
            pct = row.get("pct")
            if pct is not None and not isinstance(pct, (int, float)):
                raise ContractError(f"coverage {metric}.pct must be numeric")
            result["metrics"][metric] = {"pct": pct, "covered": row.get("covered"), "total": row.get("total")}
    if not result["metrics"]:
        raise ContractError("coverage summary contains no recognized metrics")
    return result


def normalize_ci_result(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ContractError("CI result must be an object")
    status = str(payload.get("status", "")).lower()
    conclusion = str(payload.get("conclusion", "")).lower()
    if status not in {"queued", "in_progress", "completed"}:
        raise ContractError("CI status is invalid")
    if status == "completed" and conclusion not in {"success", "failure", "cancelled", "skipped", "neutral", "timed_out", "action_required"}:
        raise ContractError("CI conclusion is invalid")
    checks = payload.get("checks", [])
    if not isinstance(checks, list):
        raise ContractError("CI checks must be a list")
    return {"format": "github-actions-style-ci", "status": status, "conclusion": conclusion or None, "checkCount": len(checks), "checks": checks}
