#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def csv_safe(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_safe(row.get(field)) for field in fields})


def safe_name(value: Any) -> str:
    raw = str(value or "route").strip()
    out = []
    for ch in raw:
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        elif ch in "/\\ :?&=#":
            out.append("-")
        else:
            out.append("-")
    name = "".join(out).strip("-")
    while "--" in name:
        name = name.replace("--", "-")
    return (name or "route")[:140]


def route_safe_name(target: dict[str, Any]) -> str:
    raw = target.get("route") or target.get("label") or target.get("chartId") or target.get("tab") or target.get("frame") or target.get("interfaceTarget") or target.get("id") or "route"
    route_name = "home" if raw == "/" else safe_name(str(raw).lstrip("/"))
    return f"{safe_name(target.get('id') or target.get('macro'))}--{route_name}"


def target_url(target: dict[str, Any]) -> str:
    base = str(target.get("baseUrl") or "").rstrip("/")
    route = str(target.get("route") or "/")
    if not route.startswith("/"):
        route = "/" + route
    return base + route


def synthesize_offline_records(plan: dict[str, Any], dom_dir: Path) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    for target in plan.get("targets") or []:
        surface = safe_name(target.get("macro") or "surface")
        base = route_safe_name(target)
        computed_path = dom_dir / surface / f"{base}.computed.json"
        dom_path = dom_dir / surface / f"{base}.dom.json"
        if computed_path.exists():
            continue
        url = target_url(target)
        record = {
            "status": "skipped_offline",
            "surface": target.get("macro"),
            "route": target.get("route"),
            "url": url,
            "expectedUrl": url,
            "targetId": target.get("id"),
            "kind": target.get("kind"),
            "capturedAt": now,
            "viewport": {"width": 0, "height": 0},
            "title": None,
            "console": [],
            "networkFailures": [],
            "elements": [],
            "error": None,
            "reason": f"{target.get('baseUrl')} was offline in visualqa preflight",
            "reasonType": "offline_port",
        }
        write_json(computed_path, record)
        write_json(dom_path, {
            "status": "skipped_offline",
            "surface": target.get("macro"),
            "route": target.get("route"),
            "url": url,
            "targetId": target.get("id"),
            "capturedAt": now,
            "title": None,
            "viewport": {"width": 0, "height": 0},
            "document": {},
            "domSnapshot": None,
            "reason": record["reason"],
            "reasonType": "offline_port",
        })


def collect_records(dom_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for p in sorted(dom_dir.glob("**/*.computed.json")):
        data = read_json(p, {})
        if not isinstance(data, dict):
            continue
        data["_computedFile"] = str(p)
        records.append(data)
    return records


def summarize_records(plan: dict[str, Any], records: list[dict[str, Any]], ports: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    by_target = {str(r.get("targetId")): r for r in records if r.get("targetId")}
    targets = plan.get("targets") or []
    missing_targets = []
    for t in targets:
        tid = str(t.get("id"))
        if tid not in by_target:
            missing_targets.append({
                "targetId": tid,
                "surface": t.get("macro"),
                "route": t.get("route"),
                "url": target_url(t),
                "reason": "no computed record was produced",
            })

    captured = [r for r in records if r.get("status") == "captured"]
    skipped = [r for r in records if r.get("status") in {"skipped", "skipped_offline"}]
    skipped_offline = [r for r in records if r.get("status") == "skipped_offline" or r.get("reasonType") == "offline_port"]
    failed = [r for r in records if r.get("status") == "failed"]
    console_count = sum(len(r.get("console") or []) for r in records)
    network_count = sum(len(r.get("networkFailures") or []) for r in records)
    obstruction_count = 0
    element_count = 0
    scroll_coverage_complete = 0
    scroll_coverage_partial = 0
    scroll_coverage_failed = 0
    for r in records:
        coverage = r.get("scrollCoverage") or {}
        coverage_status = str(coverage.get("status") or "")
        if coverage_status == "complete":
            scroll_coverage_complete += 1
        elif coverage_status == "partial":
            scroll_coverage_partial += 1
        elif coverage_status == "failed":
            scroll_coverage_failed += 1
        elements = r.get("elements") or []
        element_count += len(elements)
        for el in elements:
            flags = el.get("flags") or {}
            if flags.get("mayObscureBackground"):
                obstruction_count += 1

    pw_code = int(args.playwright_exit_code or 0)
    partial_failure = bool(scroll_coverage_partial and not getattr(args, "allow_partial", False))
    real_failure = bool(failed or missing_targets or pw_code != 0 or partial_failure or scroll_coverage_failed)
    if real_failure:
        status = "FAIL"
    elif skipped and args.strict:
        status = "FAIL"
    elif skipped:
        status = "PARTIAL_PASS"
    else:
        status = "PASS"

    by_surface: dict[str, dict[str, Any]] = {}
    for t in targets:
        surface = str(t.get("macro") or "unknown")
        by_surface.setdefault(surface, {"surface": surface, "expected": 0, "captured": 0, "skipped_offline": 0, "failed": 0, "missing": 0})
        by_surface[surface]["expected"] += 1
    for r in records:
        surface = str(r.get("surface") or "unknown")
        by_surface.setdefault(surface, {"surface": surface, "expected": 0, "captured": 0, "skipped_offline": 0, "failed": 0, "missing": 0})
        if r.get("status") == "captured":
            by_surface[surface]["captured"] += 1
        elif r.get("status") == "failed":
            by_surface[surface]["failed"] += 1
        elif r.get("status") == "skipped_offline":
            by_surface[surface]["skipped_offline"] += 1
    for m in missing_targets:
        surface = str(m.get("surface") or "unknown")
        by_surface.setdefault(surface, {"surface": surface, "expected": 0, "captured": 0, "skipped_offline": 0, "failed": 0, "missing": 0})
        by_surface[surface]["missing"] += 1

    return {
        "status": status,
        "mode": args.mode,
        "surface": args.surface,
        "strict": bool(args.strict),
        "workers": args.workers,
        "capturedAt": datetime.now().isoformat(timespec="seconds"),
        "targetCount": len(targets),
        "recordCount": len(records),
        "capturedCount": len(captured),
        "skippedCount": len(skipped),
        "skippedOfflineCount": len(skipped_offline),
        "failedCount": len(failed),
        "missingCount": len(missing_targets),
        "consoleIssueCount": console_count,
        "networkFailureCount": network_count,
        "computedElementCount": element_count,
        "backgroundObstructionCandidateCount": obstruction_count,
        "scrollCoverageCompleteCount": scroll_coverage_complete,
        "scrollCoveragePartialCount": scroll_coverage_partial,
        "scrollCoverageFailedCount": scroll_coverage_failed,
        "playwrightExitCode": pw_code,
        "resultZip": args.result_zip,
        "failZip": args.fail_zip,
        "ports": ports,
        "bySurface": sorted(by_surface.values(), key=lambda x: x["surface"]),
        "missing": missing_targets,
    }


def build_rows(records: list[dict[str, Any]], summary: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    console_rows: list[dict[str, Any]] = []
    network_rows: list[dict[str, Any]] = []
    layers_rows: list[dict[str, Any]] = []
    obstruction_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []

    for r in records:
        route_rows.append({
            "surface": r.get("surface"),
            "route": r.get("route"),
            "url": r.get("url") or r.get("expectedUrl"),
            "status": r.get("status"),
            "targetId": r.get("targetId"),
            "kind": r.get("kind"),
            "title": r.get("title"),
            "consoleCount": len(r.get("console") or []),
            "networkFailureCount": len(r.get("networkFailures") or []),
            "elementCount": len(r.get("elements") or []),
            "screenshot": r.get("screenshot"),
            "screenshotViewport": r.get("screenshotViewport"),
            "screenshotFullPage": r.get("screenshotFullPage"),
            "scrollCoverageStatus": (r.get("scrollCoverage") or {}).get("status"),
            "pageTileCount": len(((r.get("scrollCoverage") or {}).get("pageTiles") or [])),
            "scrollContainerCount": len(((r.get("scrollCoverage") or {}).get("scrollContainers") or [])),
            "computedFile": r.get("_computedFile"),
            "reason": r.get("reason"),
        })

        for issue in r.get("console") or []:
            console_rows.append({
                "surface": r.get("surface"),
                "route": r.get("route"),
                "url": r.get("url"),
                "targetId": r.get("targetId"),
                "type": issue.get("type"),
                "text": issue.get("text"),
                "location": issue.get("location"),
            })

        for issue in r.get("networkFailures") or []:
            network_rows.append({
                "surface": r.get("surface"),
                "route": r.get("route"),
                "url": r.get("url"),
                "targetId": r.get("targetId"),
                "type": issue.get("type"),
                "requestUrl": issue.get("url"),
                "method": issue.get("method") or issue.get("requestMethod"),
                "resourceType": issue.get("resourceType"),
                "status": issue.get("status"),
                "statusText": issue.get("statusText"),
                "failure": issue.get("failure"),
            })

        for el in r.get("elements") or []:
            computed = el.get("computed") or {}
            flags = el.get("flags") or {}
            readability = el.get("readability") or {}
            row = {
                "surface": r.get("surface"),
                "route": r.get("route"),
                "url": r.get("url"),
                "targetId": r.get("targetId"),
                "selectorGuess": el.get("selectorGuess"),
                "tag": el.get("tag"),
                "id": el.get("id"),
                "className": el.get("className"),
                "x": (el.get("bbox") or {}).get("x"),
                "y": (el.get("bbox") or {}).get("y"),
                "width": (el.get("bbox") or {}).get("width"),
                "height": (el.get("bbox") or {}).get("height"),
                "position": computed.get("position"),
                "display": computed.get("display"),
                "visibility": computed.get("visibility"),
                "opacity": computed.get("opacity"),
                "zIndex": computed.get("zIndex"),
                "color": computed.get("color"),
                "fontSize": computed.get("fontSize"),
                "background": computed.get("background"),
                "backgroundColor": computed.get("backgroundColor"),
                "backgroundImage": computed.get("backgroundImage"),
                "backdropFilter": computed.get("backdropFilter"),
                "filter": computed.get("filter"),
                "overflow": computed.get("overflow"),
                "isolation": computed.get("isolation"),
                "pointerEvents": computed.get("pointerEvents"),
                "coversViewport": flags.get("coversViewport"),
                "hasNonTransparentBackground": flags.get("hasNonTransparentBackground"),
                "mayObscureBackground": flags.get("mayObscureBackground"),
                "isOverlay": flags.get("isOverlay"),
                "isPanelOrCard": flags.get("isPanelOrCard"),
                "isShellOrViewport": flags.get("isShellOrViewport"),
                "hasZIndex": flags.get("hasZIndex"),
                "hasBackdropFilter": flags.get("hasBackdropFilter"),
                "hasBackgroundImage": flags.get("hasBackgroundImage"),
                "contrastApprox": readability.get("contrastApprox"),
                "textSample": el.get("textSample"),
            }
            layers_rows.append(row)
            if flags.get("mayObscureBackground"):
                obstruction_rows.append(row)
    return console_rows, network_rows, layers_rows, obstruction_rows, route_rows


def make_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# VisualQA render summary")
    lines.append("")
    lines.append(f"- status: `{summary['status']}`")
    lines.append(f"- mode: `{summary['mode']}`")
    lines.append(f"- surface: `{summary['surface']}`")
    lines.append(f"- strict: `{summary['strict']}`")
    lines.append(f"- targets: `{summary['targetCount']}`")
    lines.append(f"- records: `{summary['recordCount']}`")
    lines.append(f"- captured: `{summary['capturedCount']}`")
    lines.append(f"- skipped offline: `{summary['skippedOfflineCount']}`")
    lines.append(f"- failed: `{summary['failedCount']}`")
    lines.append(f"- missing: `{summary['missingCount']}`")
    lines.append(f"- console issues: `{summary['consoleIssueCount']}`")
    lines.append(f"- network failures / HTTP >= 400: `{summary['networkFailureCount']}`")
    lines.append(f"- computed elements: `{summary['computedElementCount']}`")
    lines.append(f"- background obstruction candidates: `{summary['backgroundObstructionCandidateCount']}`")
    lines.append(f"- scroll coverage complete: `{summary.get('scrollCoverageCompleteCount', 0)}`")
    lines.append(f"- scroll coverage partial: `{summary.get('scrollCoveragePartialCount', 0)}`")
    lines.append(f"- scroll coverage failed: `{summary.get('scrollCoverageFailedCount', 0)}`")
    lines.append(f"- playwright exit code: `{summary['playwrightExitCode']}`")
    lines.append("")
    lines.append("## Surface status")
    lines.append("")
    lines.append("| surface | expected | captured | skipped_offline | failed | missing |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for row in summary.get("bySurface") or []:
        lines.append(f"| {row.get('surface')} | {row.get('expected')} | {row.get('captured')} | {row.get('skipped_offline')} | {row.get('failed')} | {row.get('missing')} |")
    lines.append("")
    lines.append("## Port evidence")
    lines.append("")
    lines.append("| macro | port | online | baseUrl |")
    lines.append("| --- | ---: | :---: | --- |")
    for p in summary.get("ports") or []:
        lines.append(f"| {p.get('macro')} | {p.get('port')} | {'yes' if p.get('online') else 'no'} | {p.get('baseUrl')} |")
    if summary.get("missing"):
        lines.append("")
        lines.append("## Missing records")
        lines.append("")
        for item in summary.get("missing") or []:
            lines.append(f"- `{item.get('surface')}` `{item.get('route')}` `{item.get('targetId')}`: {item.get('reason')}")
    lines.append("")
    lines.append("## How to read this")
    lines.append("")
    lines.append("- `visual_layer_map/` tells you what layers exist in code.")
    lines.append("- `visualqa` tells you what layers actually materialized in a browser viewport.")
    lines.append("- `background-obstructions.csv` is the money table: likely panels, shells, overlays, fixed layers, and opaque backgrounds that can hide the intended background.")
    return "\n".join(lines) + "\n"


def write_continuation(out_dir: Path, summary: dict[str, Any]) -> None:
    text = f"""# CONTINUATION

VisualQA run status: {summary.get('status')}

Tool policy preserved:
- no start
- no kill
- no DB
- no deploy
- no CSS/TSX/source app modification by the QA phase

Important files:
- reports/SUMMARY.md
- reports/visualqa.summary.json
- reports/visualqa.full.json
- reports/computed-layers.csv
- reports/background-obstructions.csv
- reports/route-status.csv
- dom/<surface>/*.computed.json
- dom/<surface>/*.dom.json
- screens/<surface>/*.png
- logs/run.log
- logs/playwright.stdout.log
- logs/playwright.stderr.log

Next recommended analysis:
1. Compare reports/background-obstructions.csv against visual_layer_map/ static findings.
2. Prioritize rows with mayObscureBackground=true, coversViewport=true, hasNonTransparentBackground=true, or hasBackdropFilter=true.
3. Treat PARTIAL_PASS as operationally valid only when skips are offline surfaces and Strict was not requested.
"""
    write_text(out_dir / "CONTINUATION.md", text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--reports-dir", required=True)
    ap.add_argument("--dom-dir", required=True)
    ap.add_argument("--screens-dir", required=True)
    ap.add_argument("--logs-dir", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--ports", required=True)
    ap.add_argument("--playwright-exit-code", type=int, default=0)
    ap.add_argument("--surface", default="all")
    ap.add_argument("--mode", default="visualqa")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--offline-only", action="store_true")
    ap.add_argument("--result-zip", default="")
    ap.add_argument("--fail-zip", default="")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    reports_dir = Path(args.reports_dir)
    dom_dir = Path(args.dom_dir)
    screens_dir = Path(args.screens_dir)
    logs_dir = Path(args.logs_dir)
    for d in [out_dir, reports_dir, dom_dir, screens_dir, logs_dir]:
        d.mkdir(parents=True, exist_ok=True)

    plan = read_json(Path(args.plan), {})
    ports = read_json(Path(args.ports), [])
    if args.offline_only:
        synthesize_offline_records(plan, dom_dir)

    records = collect_records(dom_dir)
    summary = summarize_records(plan, records, ports if isinstance(ports, list) else [], args)
    console_rows, network_rows, layers_rows, obstruction_rows, route_rows = build_rows(records, summary)

    write_json(reports_dir / "visualqa.full.json", {"summary": summary, "records": records})
    write_json(reports_dir / "visualqa.summary.json", summary)
    write_json(reports_dir / "summary.json", summary)
    write_text(reports_dir / "SUMMARY.md", make_markdown(summary))

    write_csv(reports_dir / "console-errors.csv", console_rows, ["surface", "route", "url", "targetId", "type", "text", "location"])
    write_csv(reports_dir / "network-failures.csv", network_rows, ["surface", "route", "url", "targetId", "type", "requestUrl", "method", "resourceType", "status", "statusText", "failure"])
    write_csv(reports_dir / "computed-layers.csv", layers_rows, [
        "surface", "route", "url", "targetId", "selectorGuess", "tag", "id", "className",
        "x", "y", "width", "height", "position", "display", "visibility", "opacity", "zIndex",
        "color", "fontSize", "background", "backgroundColor", "backgroundImage", "backdropFilter",
        "filter", "overflow", "isolation", "pointerEvents", "coversViewport", "hasNonTransparentBackground",
        "mayObscureBackground", "isOverlay", "isPanelOrCard", "isShellOrViewport", "hasZIndex",
        "hasBackdropFilter", "hasBackgroundImage", "contrastApprox", "textSample",
    ])
    write_csv(reports_dir / "background-obstructions.csv", obstruction_rows, [
        "surface", "route", "url", "targetId", "selectorGuess", "tag", "id", "className",
        "x", "y", "width", "height", "position", "display", "visibility", "opacity", "zIndex",
        "backgroundColor", "backgroundImage", "backdropFilter", "filter", "coversViewport",
        "hasNonTransparentBackground", "mayObscureBackground", "isOverlay", "isPanelOrCard",
        "isShellOrViewport", "hasZIndex", "hasBackdropFilter", "hasBackgroundImage", "textSample",
    ])
    write_csv(reports_dir / "route-status.csv", route_rows, [
        "surface", "route", "url", "status", "targetId", "kind", "title", "consoleCount",
        "networkFailureCount", "elementCount", "screenshot", "screenshotViewport", "screenshotFullPage", "scrollCoverageStatus", "pageTileCount", "scrollContainerCount", "computedFile", "reason",
    ])
    write_continuation(out_dir, summary)

    print(json.dumps({"status": summary["status"], "records": len(records), "captured": summary["capturedCount"], "skippedOffline": summary["skippedOfflineCount"], "failed": summary["failedCount"], "missing": summary["missingCount"]}, ensure_ascii=False))
    return 0 if summary["status"] in {"PASS", "PARTIAL_PASS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
