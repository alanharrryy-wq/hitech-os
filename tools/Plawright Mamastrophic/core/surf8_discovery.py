#!/usr/bin/env python3
# PRISMA surf8 discovery: filesystem-first target discovery for Playwright capture.
# arr4: surface selection, explicit inventories, dynamic/filter reporting.
from __future__ import annotations
import argparse, json, os, re, sys
from pathlib import Path
from datetime import datetime
from typing import Any

MACROS = [
    {"id":"chart-lab", "port":3000, "root":"products/chart-lab/app", "source":"repo convention + package scripts"},
    {"id":"web", "port":3110, "root":"products/web/app", "source":"repo convention + package scripts"},
    {"id":"tablet", "port":3120, "root":"products/tablet/app", "source":"repo convention + package scripts"},
    {"id":"pc", "port":3130, "root":"products/pc/app", "source":"package.json dev -p 3130"},
    {"id":"mobile", "port":3140, "root":"products/mobile/app", "source":"repo convention + package scripts"},
    {"id":"control-center", "port":3150, "root":"prisma-control-center", "source":"repo convention + launcher scripts"},
]

SURFACE_ALIASES = {
    "all":"all", "todo":"all", "todos":"all", "*":"all",
    "3000":"chart-lab", "chart":"chart-lab", "chartlab":"chart-lab", "chart_lab":"chart-lab", "chart-lab":"chart-lab",
    "3110":"web", "web":"web", "eit":"web", "eit_web":"web", "eit-web":"web",
    "3120":"tablet", "tablet":"tablet", "pos":"tablet", "tablet_pos":"tablet", "tablet-pos":"tablet",
    "3130":"pc", "pc":"pc", "backoffice":"pc", "pc_backoffice":"pc", "pc-backoffice":"pc",
    "3140":"mobile", "mobile":"mobile", "app":"mobile", "app_mobile":"mobile", "app-mobile":"mobile",
    "3150":"control-center", "control":"control-center", "control_center":"control-center", "control-center":"control-center", "prisma_control_center":"control-center", "prisma-control-center":"control-center",
}

CRITICAL_PC_ROUTES = {"/", "/dashboard", "/catalog", "/stock", "/sync", "/settings", "/referencia-visual", "/referencia-visual/liquid-glass"}
CRITICAL_TABLET = {"/", "/pos", "/shift", "/catalog", "/stock", "/sales/today", "/sync", "/offline", "/settings/license"}
TEXT_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".html", ".py", ".md", ".json"}
EXCLUDE_DIRS = {"node_modules", ".git", ".next", "dist", "build", "coverage", "test-results", "playwright-report", "__pycache__"}


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def normalize_surface(value: Any) -> str:
    raw = str(value or "all").strip().lower().replace(" ", "_")
    raw = raw.replace("/", "_")
    out = SURFACE_ALIASES.get(raw, raw)
    if out not in {"all", *(m["id"] for m in MACROS)}:
        valid = ", ".join(sorted(SURFACE_ALIASES.keys()))
        raise SystemExit(f"Surface invalida '{value}'. Valores validos/alias: {valid}")
    return out


def include_surface(requested: str, macro_id: str) -> bool:
    return requested == "all" or requested == macro_id


def find_terminal_root(start: Path | None = None) -> Path:
    candidates: list[Path] = []
    env = os.environ.get("PRISMA_TERMINAL_ROOT")
    if env:
        candidates.append(Path(env))
    if start:
        candidates.append(start)
    candidates.extend([
        Path.cwd(),
        Path(r"F:\repos\hitech-os\apps\terminal-de-venta-system"),
        Path(r"F:\repos\hitech-os") / "apps" / "terminal-de-venta-system",
    ])
    try:
        import subprocess
        cp = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(Path.cwd()), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
        if cp.returncode == 0:
            root = Path(cp.stdout.strip())
            candidates.append(root / "apps" / "terminal-de-venta-system")
    except Exception:
        pass
    expanded: list[Path] = []
    for c in candidates:
        try:
            c = c.resolve()
        except Exception:
            continue
        expanded.append(c)
        for parent in [c, *c.parents]:
            expanded.append(parent / "apps" / "terminal-de-venta-system")
            if parent.name == "terminal-de-venta-system":
                expanded.append(parent)
    seen = set()
    for c in expanded:
        key = str(c).lower()
        if key in seen:
            continue
        seen.add(key)
        if not c.exists() or not c.is_dir():
            continue
        if (c / "products" / "pc" / "app" / "package.json").exists():
            if c.name != "terminal-de-venta-system":
                continue
            return c
    raise SystemExit("No pude detectar apps/terminal-de-venta-system. Usa --repo-root o PRISMA_TERMINAL_ROOT.")


def route_from_page(app_root: Path, page: Path) -> str:
    rel = page.parent.relative_to(app_root).as_posix()
    if rel == ".":
        return "/"
    parts = [p for p in rel.split("/") if not (p.startswith("(") and p.endswith(")"))]
    return "/" + "/".join(parts) if parts else "/"


def scan_next_routes(product_root: Path) -> list[dict]:
    app_root = product_root / "app"
    routes: list[dict] = []
    if not app_root.exists():
        return routes
    page_files = []
    for suffix in ("page.tsx", "page.ts", "page.jsx", "page.js"):
        page_files.extend(app_root.rglob(suffix))
    for page in sorted(page_files):
        if any(part in EXCLUDE_DIRS for part in page.parts):
            continue
        route = route_from_page(app_root, page)
        dynamic = "[" in route or "]" in route
        routes.append({"route": route, "file": str(page), "dynamic": dynamic})
    out, seen = [], set()
    for r in routes:
        if r["route"] in seen:
            continue
        seen.add(r["route"]); out.append(r)
    return out


def parse_tablet_nav(term_root: Path) -> list[dict]:
    nav = term_root / "products" / "tablet" / "app" / "components" / "tablet-shell" / "tablet-nav.ts"
    if not nav.exists():
        return []
    txt = nav.read_text(encoding="utf-8", errors="replace")
    items = []
    for m in re.finditer(r"\{\s*href:\s*['\"]([^'\"]+)['\"]\s*,\s*label:\s*['\"]([^'\"]+)['\"](?P<body>.*?)\}", txt, re.S):
        body = m.group("body")
        short = re.search(r"shortLabel:\s*['\"]([^'\"]+)['\"]", body)
        primary = bool(re.search(r"primary\s*:\s*true", body))
        items.append({"href": m.group(1), "label": m.group(2), "shortLabel": short.group(1) if short else m.group(2), "primary": primary, "file": str(nav)})
    return items


def parse_chart_lab(term_root: Path) -> tuple[list[str], list[str], list[str], list[str]]:
    root = term_root / "products" / "chart-lab" / "app"
    chart_ids: list[str] = []
    tabs: list[str] = []
    frames = ["pc", "tablet", "mobile"]
    sources: list[str] = []
    if not root.exists():
        return chart_ids, tabs, frames, sources
    src = root / "src"
    if src.exists():
        for p in src.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}:
                try:
                    txt = p.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                if "chartLabRegistry" in txt or "chart-lab-registry" in str(p).lower():
                    sources.append(str(p))
                    for m in re.finditer(r"\bid\s*:\s*['\"]([a-zA-Z0-9_.-]+)['\"]", txt):
                        cid = m.group(1)
                        if cid.startswith(("pc.", "tablet.", "mobile.", "ops.", "example.")):
                            chart_ids.append(cid)
    shell = root / "src" / "components" / "PrismaChartLabShell.tsx"
    if shell.exists():
        txt = shell.read_text(encoding="utf-8", errors="replace")
        sources.append(str(shell))
        for candidate in ["visual", "motion", "interaction", "labels", "data", "advanced", "code"]:
            if re.search(rf"['\"]{re.escape(candidate)}['\"]", txt, re.I):
                tabs.append(candidate)
        for candidate in ["pc", "tablet", "mobile"]:
            if re.search(rf"['\"]{candidate}['\"]", txt, re.I) and candidate not in frames:
                frames.append(candidate)
    return uniq(chart_ids), uniq(tabs), uniq(frames), uniq(sources)


def parse_control_center(term_root: Path) -> tuple[list[str], list[str], list[str]]:
    roots = [term_root / "prisma-control-center" / "internal", term_root / "products" / "control-center" / "app"]
    targets, markers, sources = [], [], []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
                continue
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            hit = False
            for m in re.finditer(r"data-prisma-interface-target\s*=\s*['\"]([^'\"]+)['\"]", txt):
                targets.append(m.group(1)); hit = True
            for m in re.finditer(r"dataset\.prismaInterfaceTarget\s*=\s*['\"]([^'\"]+)['\"]", txt):
                targets.append(m.group(1)); hit = True
            for m in re.finditer(r"(?:id\s*=\s*['\"]|#|\.)((?:lifecycleSurface|qualityBaySurface|licenseOpsSurface|prismoConsoleSurface))", txt):
                markers.append(m.group(1)); hit = True
            if hit:
                sources.append(str(p))
    order = {"operation":0, "quality":1, "license":2, "lifecycle":3, "prismo":4}
    return sorted(uniq(targets), key=lambda x: order.get(x, 99)), uniq(markers), uniq(sources)


def uniq(xs):
    out=[]; seen=set()
    for x in xs:
        if x not in seen:
            seen.add(x); out.append(x)
    return out


def macro_map(term_root: Path, requested_surface: str) -> dict:
    out = {}
    for m in MACROS:
        if not include_surface(requested_surface, m["id"]):
            continue
        root = term_root / m["root"]
        out[m["id"]] = {**m, "rootAbs": str(root), "exists": root.exists(), "baseUrl": f"http://127.0.0.1:{m['port']}"}
    return out


def add_target(targets: list[dict], filtered: list[dict], mode: str, include: bool, reason: str, **kw) -> None:
    if not kw.get("id"):
        return
    if include:
        targets.append(kw)
    else:
        filtered.append({"id": kw.get("id"), "macro": kw.get("macro"), "kind": kw.get("kind"), "route": kw.get("route"), "reason": reason, "mode": mode, "source": kw.get("source"), "file": kw.get("file")})


def build_plan(term_root: Path, mode: str, workers: int, surface: str) -> dict:
    surface = normalize_surface(surface)
    macros = macro_map(term_root, surface)
    targets: list[dict] = []
    filtered: list[dict] = []
    dynamic_skipped: list[dict] = []
    route_inventory: dict[str, Any] = {}

    # PC routes: real App Router pages only. Dynamic routes are inventoried, not captured.
    pc_routes = scan_next_routes(term_root / "products" / "pc" / "app")
    route_inventory["pc"] = pc_routes
    if include_surface(surface, "pc"):
        for r in pc_routes:
            tid = f"pc.route.{r['route'].strip('/').replace('/','.') or 'home'}"
            if r["dynamic"]:
                dynamic_skipped.append({"id": tid, "macro":"pc", "route":r["route"], "file":r["file"], "reason":"dynamic route needs params"})
                continue
            include = not (mode == "critical" and r["route"] not in CRITICAL_PC_ROUTES) and not (mode == "quick" and r["route"] not in CRITICAL_PC_ROUTES and not r["route"].startswith("/referencia-visual"))
            reason = "outside quick/critical PC route contract"
            add_target(targets, filtered, mode, include, reason, id=tid, macro="pc", port=3130, baseUrl=macros["pc"]["baseUrl"], kind="route", route=r["route"], source="pc app router", file=r["file"], tags=["@pc", "@route"])

    # Tablet: menu items are the contract, plus direct routes from App Router in full.
    tablet_nav = parse_tablet_nav(term_root)
    tablet_routes = scan_next_routes(term_root / "products" / "tablet" / "app")
    route_inventory["tablet"] = {"nav": tablet_nav, "appRoutes": tablet_routes}
    if include_surface(surface, "tablet"):
        for item in tablet_nav:
            include = not (mode == "critical" and item["href"] not in CRITICAL_TABLET)
            reason = "outside critical tablet route contract"
            add_target(targets, filtered, mode, include, reason, id=f"tablet.nav.{item['href'].strip('/').replace('/','.') or 'home'}", macro="tablet", port=3120, baseUrl=macros["tablet"]["baseUrl"], kind="tablet-nav", route=item["href"], label=item["label"], shortLabel=item["shortLabel"], source="TABLET_NAV_ITEMS", file=item["file"], tags=["@tablet", "@nav"])
        known_nav_routes = {x["href"] for x in tablet_nav}
        for r in tablet_routes:
            tid = f"tablet.route.{r['route'].strip('/').replace('/','.') or 'home'}"
            if r["dynamic"]:
                dynamic_skipped.append({"id": tid, "macro":"tablet", "route":r["route"], "file":r["file"], "reason":"dynamic route needs params"})
                continue
            if r["route"] in known_nav_routes:
                filtered.append({"id":tid, "macro":"tablet", "kind":"route", "route":r["route"], "reason":"already represented by TABLET_NAV_ITEMS", "mode":mode, "source":"tablet app router", "file":r["file"]})
                continue
            include = mode == "full"
            add_target(targets, filtered, mode, include, "tablet app route captured only in full mode", id=tid, macro="tablet", port=3120, baseUrl=macros["tablet"]["baseUrl"], kind="route", route=r["route"], source="tablet app router", file=r["file"], tags=["@tablet", "@route"])

    # Chart Lab: registry charts + real tabs + frames.
    chart_ids, chart_tabs, chart_frames, chart_sources = parse_chart_lab(term_root)
    route_inventory["chart-lab"] = {"chartIds": chart_ids, "tabs": chart_tabs, "frames": chart_frames, "sources": chart_sources}
    if include_surface(surface, "chart-lab"):
        first_chart = chart_ids[0] if chart_ids else ""
        for cid in chart_ids:
            include = not (mode == "critical" and not (cid.startswith("pc.") or cid.startswith("ops.")))
            add_target(targets, filtered, mode, include, "outside critical chart-lab contract", id=f"chartlab.chart.{cid}", macro="chart-lab", port=3000, baseUrl=macros["chart-lab"]["baseUrl"], kind="chart-lab-chart", route=f"/?chart={cid}", chartId=cid, source="chartLabRegistry", tags=["@chartlab", "@chart"])
        for tab in chart_tabs:
            include = mode in {"full", "quick"}
            add_target(targets, filtered, mode, include, "chart-lab tabs captured only in quick/full", id=f"chartlab.tab.{tab}", macro="chart-lab", port=3000, baseUrl=macros["chart-lab"]["baseUrl"], kind="chart-lab-tab", route=f"/?chart={first_chart}" if first_chart else "/", tab=tab, source="PrismaChartLabShell tabs", tags=["@chartlab", "@tab"])
        for frame in chart_frames:
            include = mode in {"full", "quick"}
            add_target(targets, filtered, mode, include, "chart-lab frames captured only in quick/full", id=f"chartlab.frame.{frame}", macro="chart-lab", port=3000, baseUrl=macros["chart-lab"]["baseUrl"], kind="chart-lab-frame", route=f"/?chart={first_chart}" if first_chart else "/", frame=frame, source="PrismaChartLabShell target frames", tags=["@chartlab", "@frame"])

    # Mobile and Web route inventory.
    for macro_id, port in [("mobile",3140), ("web",3110)]:
        routes = scan_next_routes(term_root / "products" / macro_id / "app")
        route_inventory[macro_id] = routes
        if not include_surface(surface, macro_id):
            continue
        for r in routes:
            tid = f"{macro_id}.route.{r['route'].strip('/').replace('/','.') or 'home'}"
            if r["dynamic"]:
                dynamic_skipped.append({"id": tid, "macro":macro_id, "route":r["route"], "file":r["file"], "reason":"dynamic route needs params"})
                continue
            include = not (mode == "critical" and r["route"] != "/")
            add_target(targets, filtered, mode, include, "only home route is critical for this macro", id=tid, macro=macro_id, port=port, baseUrl=macros[macro_id]["baseUrl"], kind="route", route=r["route"], source=f"{macro_id} app router", file=r["file"], tags=[f"@{macro_id}", "@route"])

    # Control Center: only real data-prisma-interface-target values discovered from source.
    cc_targets, cc_markers, cc_sources = parse_control_center(term_root)
    route_inventory["control-center"] = {"targets": cc_targets, "markers": cc_markers, "sources": cc_sources}
    if include_surface(surface, "control-center"):
        for target in cc_targets:
            include = not (mode == "critical" and target not in {"operation", "lifecycle"})
            add_target(targets, filtered, mode, include, "outside critical control-center target contract", id=f"controlcenter.target.{target}", macro="control-center", port=3150, baseUrl=macros["control-center"]["baseUrl"], kind="control-center-target", route="/", interfaceTarget=target, source="data-prisma-interface-target", tags=["@controlcenter", "@target"])
        if "lifecycle" in cc_targets or any("lifecycle" in x.lower() for x in cc_markers):
            include = True
            add_target(targets, filtered, mode, include, "", id="controlcenter.lifecycle.surface", macro="control-center", port=3150, baseUrl=macros["control-center"]["baseUrl"], kind="control-center-lifecycle", route="/", interfaceTarget="lifecycle", source="#lifecycleSurface/.lifecycleSurface source marker", tags=["@controlcenter", "@lifecycle", "@critical"])

    # De-dupe by id.
    dedup=[]; seen=set()
    for t in targets:
        if t["id"] in seen:
            continue
        seen.add(t["id"]); dedup.append(t)

    macro_summaries = []
    for macro in macros.values():
        mid = macro["id"]
        macro_summaries.append({
            "macro": mid,
            "expectedTargets": len([t for t in dedup if t.get("macro") == mid]),
            "filteredOut": len([t for t in filtered if t.get("macro") == mid]),
            "dynamicSkipped": len([t for t in dynamic_skipped if t.get("macro") == mid]),
            "rootExists": macro.get("exists"),
            "port": macro.get("port"),
            "baseUrl": macro.get("baseUrl"),
        })

    plan = {
        "schema":"prisma.surf8.capture-plan.v2",
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "terminalRoot": str(term_root),
        "mode": mode,
        "surface": surface,
        "defaultWorkers": workers,
        "macros": list(macros.values()),
        "macroSummaries": macro_summaries,
        "discovery": {
            "pcRoutes": len(pc_routes),
            "tabletNav": len(tablet_nav),
            "tabletRoutes": len(tablet_routes),
            "chartIds": len(chart_ids),
            "chartTabs": len(chart_tabs),
            "chartFrames": chart_frames,
            "mobileRoutes": len(route_inventory.get("mobile", [])),
            "webRoutes": len(route_inventory.get("web", [])),
            "controlCenterTargets": cc_targets,
            "controlCenterMarkers": cc_markers,
            "filteredOutCount": len(filtered),
            "dynamicSkippedCount": len(dynamic_skipped),
        },
        "routeInventory": route_inventory,
        "filteredOut": filtered,
        "dynamicSkipped": dynamic_skipped,
        "targets": dedup,
        "targetCount": len(dedup),
    }
    return plan


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="", help="Exact terminal-de-venta-system root. Monorepo root is not accepted unless it contains apps/terminal-de-venta-system.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["discovery", "critical", "quick", "full"], default="full")
    ap.add_argument("--surface", default="all", help="Surface/port: all, pc/3130, tablet/3120, mobile/app/3140, web/3110, chart-lab/3000, control-center/3150")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    root_arg = Path(args.repo_root) if args.repo_root else None
    term_root = find_terminal_root(root_arg)
    plan_mode = "full" if args.mode == "discovery" else args.mode
    surface = normalize_surface(args.surface)
    plan = build_plan(term_root, plan_mode, max(1, args.workers), surface)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"plan escrito: {out}")
    log(f"terminalRoot={term_root}")
    log(f"mode={plan_mode} surface={surface} targets={plan['targetCount']} macros={len(plan['macros'])}")
    if plan["targetCount"] <= 0:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
