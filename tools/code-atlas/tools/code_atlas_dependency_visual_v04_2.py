#!/usr/bin/env python3
"""Code Atlas Dependency Visual V04.2.

Offline HTML renderer for Code Atlas dependency consumer graph JSON.
Black Glass + Gold Accents edition: dark, elegant, premium, and still fully
read-only. It consumes graph/summary artifacts and writes one standalone HTML.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

VERSION = "4.2.0"
TOOL = "code-atlas dependency visual"

STDLIB_HINTS = {
    "__future__", "argparse", "ast", "base64", "collections", "ctypes", "dataclasses",
    "datetime", "fnmatch", "hashlib", "hmac", "http", "json", "os", "pathlib",
    "py_compile", "re", "secrets", "shutil", "socket", "sqlite3", "subprocess",
    "sys", "tempfile", "threading", "time", "typing", "unicodedata", "urllib",
    "uuid", "zipfile",
}

TOOLING_SEGMENTS = {
    "tools", "tooling", "scripts", "script", "fixtures", "fixture", "tests", "test",
    "__pycache__", ".pytest_cache", ".next", "node_modules",
}

RUNTIME_SEGMENTS = {"app", "src", "components", "shared"}


def now_stamp() -> str:
    return _dt.datetime.now().strftime("%y%m%d_%H%M%S")


def iso_now() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] invalid JSON: {path}: {exc}")


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    value = value.strip("._-") or "dependency_visual"
    return value[:100]


def node_path(node: Dict[str, Any]) -> str:
    return str(node.get("path") or node.get("label") or node.get("id") or "")


def node_workspace(node: Dict[str, Any]) -> str:
    meta = node.get("metadata") or {}
    return str(node.get("workspace") or meta.get("workspace") or "(unknown)")


def is_stdlib_external(node: Dict[str, Any]) -> bool:
    if node.get("kind") != "external":
        return False
    raw = str((node.get("metadata") or {}).get("raw") or node.get("path") or node.get("label") or "")
    root = raw.split(".", 1)[0].split("/", 1)[0]
    return root in STDLIB_HINTS


def is_tooling_path(path: str) -> bool:
    clean = path.replace("\\", "/").strip("/")
    parts = [p.lower() for p in clean.split("/") if p]
    if not parts:
        return False
    if parts[0] in {"tooling", "tools", "scripts", "prisma"}:
        return True
    return any(p in TOOLING_SEGMENTS for p in parts)


def is_runtime_node(node: Dict[str, Any]) -> bool:
    kind = node.get("kind")
    if kind in {"workspace", "external", "unresolved"}:
        return True
    path = node_path(node).replace("\\", "/")
    if is_tooling_path(path):
        return False
    parts = [p.lower() for p in path.split("/") if p]
    if any(p in RUNTIME_SEGMENTS for p in parts):
        return True
    return path.startswith("shared/") or "/shared/" in path


def enrich_graph(graph: Dict[str, Any], summary: Dict[str, Any] | None) -> Dict[str, Any]:
    nodes = list(graph.get("nodes") or [])
    edges = list(graph.get("edges") or [])

    workspace_counts: Dict[str, int] = {}
    runtime_count = 0
    tooling_count = 0
    stdlib_count = 0
    for n in nodes:
        ws = node_workspace(n)
        workspace_counts[ws] = workspace_counts.get(ws, 0) + 1
        runtime = is_runtime_node(n)
        stdlib = is_stdlib_external(n)
        if runtime:
            runtime_count += 1
        else:
            tooling_count += 1
        if stdlib:
            stdlib_count += 1
        n["workspace"] = ws
        n["degree"] = int(n.get("inbound") or 0) + int(n.get("outbound") or 0)
        n["runtime"] = runtime
        n["stdlib_external"] = stdlib

    edge_classes: Dict[str, int] = {}
    edge_kinds: Dict[str, int] = {}
    package_edges = 0
    unresolved_edges: List[Dict[str, Any]] = []
    ignored_edges: List[Dict[str, Any]] = []
    for e in edges:
        cls = str(e.get("classification") or "unknown")
        kind = str(e.get("kind") or "unknown")
        weight = int(e.get("weight") or 1)
        edge_classes[cls] = edge_classes.get(cls, 0) + weight
        edge_kinds[kind] = edge_kinds.get(kind, 0) + weight
        if cls == "unresolved" or "unresolved" in kind:
            unresolved_edges.append(e)
        if cls == "ignored" or "ignored" in kind:
            ignored_edges.append(e)
        if kind == "package-dependency":
            package_edges += 1

    top_files = sorted(nodes, key=lambda n: int(n.get("degree") or 0), reverse=True)[:120]
    top_external = sorted(
        [n for n in nodes if n.get("kind") == "external"],
        key=lambda n: int(n.get("inbound") or 0),
        reverse=True,
    )[:60]

    dep_summary = dict((summary or {}).get("dependency_summary") or {})
    profile = dict((summary or {}).get("project_profile") or {})
    if not dep_summary:
        dep_summary = {
            "files_scanned": None,
            "source_files": None,
            "edges": len(edges),
            "internal_edges": edge_classes.get("internal", 0),
            "external_edges": edge_classes.get("external", 0),
            "unresolved_edges": edge_classes.get("unresolved", len(unresolved_edges)),
            "ignored_edges": edge_classes.get("ignored", len(ignored_edges)),
            "salvage_edges": 0,
        }

    return {
        "tool": TOOL,
        "version": VERSION,
        "generated_at": iso_now(),
        "graph_version": graph.get("version"),
        "graph_generated_at": graph.get("generated_at"),
        "project_profile": profile,
        "dependency_summary": dep_summary,
        "workspace_counts": workspace_counts,
        "runtime_count": runtime_count,
        "tooling_count": tooling_count,
        "stdlib_external_count": stdlib_count,
        "edge_class_counts": edge_classes,
        "edge_kind_counts": edge_kinds,
        "package_edges": package_edges,
        "top_external": [
            {
                "id": n.get("id"),
                "label": n.get("label"),
                "path": n.get("path"),
                "inbound": n.get("inbound"),
                "raw": (n.get("metadata") or {}).get("raw"),
                "stdlib_external": n.get("stdlib_external"),
            }
            for n in top_external
        ],
        "top_files": [
            {
                "id": n.get("id"),
                "label": n.get("label"),
                "path": n.get("path"),
                "workspace": n.get("workspace"),
                "kind": n.get("kind"),
                "inbound": n.get("inbound"),
                "outbound": n.get("outbound"),
                "degree": n.get("degree"),
                "runtime": n.get("runtime"),
            }
            for n in top_files
        ],
        "unresolved_edges": unresolved_edges,
        "ignored_edges": ignored_edges,
        "unresolved_unique_edges": len({(e.get("source"), e.get("target"), e.get("raw")) for e in unresolved_edges}),
        "nodes": nodes,
        "edges": edges,
    }


def html_shell(model: Dict[str, Any], title: str, graph_path: Path, summary_path: Path | None) -> str:
    model_json = json.dumps(model, ensure_ascii=False, separators=(",", ":"))
    title_html = html.escape(title)
    graph_html = html.escape(str(graph_path))
    summary_html = html.escape(str(summary_path) if summary_path else "(none)")
    package = html.escape(str((model.get("project_profile") or {}).get("package_name") or "unknown"))
    manager = html.escape(str((model.get("project_profile") or {}).get("package_manager") or "unknown"))
    frameworks = (model.get("project_profile") or {}).get("frameworks") or []
    framework_badges = "".join(f'<span class="badge">{html.escape(str(f))}</span>' for f in frameworks)

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_html}</title>
<style>
:root {{
  --bg:#0a0a0b; --bg2:#111113; --glass:rgba(18,18,21,.72); --glass2:rgba(22,22,26,.62);
  --panel:rgba(16,16,19,.84); --line:rgba(230,199,138,.12); --line-strong:rgba(230,199,138,.28);
  --gold:#e6c78a; --gold-soft:#b89a5e; --gold-glow:rgba(230,199,138,.28);
  --text:#ece8e1; --soft:#bfb7aa; --muted:#80786c; --white-glow:rgba(255,255,255,.18);
  --accent-red:#c75c5c; --accent-ink:#060606; --shadow:rgba(0,0,0,.56);
  --radius:22px; --mono:"Cascadia Mono","SFMono-Regular",Consolas,monospace;
  --sans:Inter,"Segoe UI",Aptos,system-ui,sans-serif;
}}
*{{box-sizing:border-box}} html,body{{min-height:100%}}
body{{margin:0;color:var(--text);font-family:var(--sans);background:var(--bg);overflow-x:hidden}}
body:before{{content:"";position:fixed;inset:0;z-index:-3;background:
  radial-gradient(circle at 16% 12%,rgba(230,199,138,.12),transparent 18rem),
  radial-gradient(circle at 84% 12%,rgba(255,255,255,.06),transparent 20rem),
  radial-gradient(circle at 50% 100%,rgba(230,199,138,.08),transparent 28rem),
  linear-gradient(180deg,#070708,#0a0a0b 28%,#0c0c0d 70%,#090909)}}
body:after{{content:"";position:fixed;inset:0;z-index:-2;pointer-events:none;opacity:.2;background:
  linear-gradient(transparent 0 96%, rgba(230,199,138,.05) 96% 100%),
  linear-gradient(90deg, transparent 0 96%, rgba(230,199,138,.04) 96% 100%); background-size:100% 44px,44px 100%;mask-image:radial-gradient(circle at 50% 32%, black, transparent 88%)}}
@keyframes floaty{{0%,100%{{transform:translate3d(0,0,0)}}50%{{transform:translate3d(0,-10px,0)}}}}
@keyframes reveal{{0%{{opacity:0;transform:translateY(10px);filter:blur(8px)}}100%{{opacity:1;transform:translateY(0);filter:blur(0)}}}}
@keyframes drawLine{{from{{stroke-dashoffset:120}}to{{stroke-dashoffset:0}}}}
@keyframes glowPulse{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}
@keyframes sweep{{0%{{transform:translateX(-120%)}}100%{{transform:translateX(120%)}}}}
@media (prefers-reduced-motion:reduce){{*,*:before,*:after{{animation:none!important;transition:none!important}}}}

.shell{{width:min(100%,1640px);margin:0 auto;padding:24px 24px 40px;animation:reveal .9s ease both}}
.glass{{background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.012)),var(--glass);border:1px solid var(--line);box-shadow:0 32px 84px var(--shadow), inset 0 1px 0 var(--white-glow);backdrop-filter:blur(14px)}}
.hero{{position:relative;display:grid;grid-template-columns:1.05fr .95fr;gap:22px;padding:28px;min-height:290px;border-radius:30px;overflow:hidden}}
.hero:before{{content:"";position:absolute;inset:0;background:linear-gradient(120deg,transparent 0%,rgba(230,199,138,.03) 24%,rgba(255,255,255,.08) 48%,rgba(230,199,138,.06) 60%,transparent 100%);animation:sweep 9s linear infinite;pointer-events:none}}
.eyebrow{{margin:0 0 10px;color:var(--gold);letter-spacing:.24em;text-transform:uppercase;font:900 11px var(--mono)}}
.hero h1{{margin:0;font-family:var(--sans);font-size:clamp(40px,6.2vw,86px);line-height:.88;letter-spacing:-.07em;color:#f2eee6;text-shadow:0 0 24px rgba(230,199,138,.08)}}
.subtitle{{max-width:80ch;color:var(--soft);line-height:1.68;font-size:15px;margin:16px 0 14px}}
.meta{{font:12px var(--mono);color:var(--muted);overflow-wrap:anywhere;line-height:1.5}}
.badges{{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;align-content:flex-start}}
.badge{{border:1px solid var(--line);background:rgba(230,199,138,.06);border-radius:999px;padding:7px 11px;font:800 12px var(--mono);color:var(--soft)}}
.exec-card{{display:flex;flex-direction:column;justify-content:space-between}}
.executive-note{{margin-top:14px;padding:14px 16px;border-radius:18px;border:1px solid rgba(230,199,138,.10);background:rgba(255,255,255,.02);position:relative;overflow:hidden}}
.executive-note:before{{content:"";position:absolute;inset:0;background:linear-gradient(120deg,transparent,rgba(230,199,138,.12),transparent);transform:translateX(-120%);animation:sweep 12s linear infinite;opacity:.5}}
.executive-note b{{color:var(--gold)}}
.orbit{{position:relative;min-height:230px;border-radius:28px;border:1px solid var(--line);background:radial-gradient(circle at 50% 50%,rgba(230,199,138,.09),transparent 8rem),linear-gradient(135deg,rgba(255,255,255,.02),rgba(230,199,138,.04));overflow:hidden;animation:floaty 9s ease-in-out infinite}}
.orbit canvas{{display:block;width:100%;height:230px}}
.metrics{{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:12px;margin:18px 0}}
.metric{{position:relative;padding:15px;border-radius:22px;min-height:102px;overflow:hidden}}
.metric:after{{content:"";position:absolute;inset:auto -30% -50% auto;width:110px;height:110px;border-radius:50%;background:radial-gradient(circle,rgba(230,199,138,.16),transparent 68%);opacity:.8}}
.metric:before{{content:"";position:absolute;left:0;top:18px;bottom:18px;width:2px;background:linear-gradient(180deg,transparent,var(--gold-soft),transparent)}}
.metric span{{display:block;color:var(--muted);letter-spacing:.16em;text-transform:uppercase;font:900 10px var(--mono)}}
.metric strong{{display:block;margin-top:12px;font:950 28px var(--mono);color:#f6f0e2}}
.metric small{{display:block;margin-top:6px;color:var(--soft);font-size:12px}}
.command-bar{{display:grid;grid-template-columns:1.65fr repeat(5,minmax(140px,1fr));gap:10px;align-items:center;padding:15px;border-radius:24px}}
input,select,button{{height:44px;border-radius:14px;padding:0 12px;font:13px var(--sans);outline:none}}
input,select{{background:rgba(9,9,10,.88);border:1px solid rgba(230,199,138,.14);color:var(--text)}}
input:focus,select:focus{{border-color:var(--line-strong);box-shadow:0 0 0 4px rgba(230,199,138,.08)}}
button{{cursor:pointer;border:1px solid rgba(230,199,138,.2);color:#130f09;background:linear-gradient(135deg,#f0deb5,#d7b472 58%,#b38b4d);box-shadow:0 10px 28px rgba(230,199,138,.18);font-weight:900}}
button.ghost{{background:rgba(255,255,255,.04);color:var(--soft);border:1px solid var(--line)}}
.toggles{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}}
.chip{{position:relative;border-radius:999px;padding:10px 12px;font:850 12px var(--mono);cursor:pointer;user-select:none;color:var(--soft);border:1px solid var(--line);background:rgba(255,255,255,.025);overflow:hidden}}
.chip:hover{{border-color:rgba(230,199,138,.24)}}
.chip.active{{color:#130f09;background:linear-gradient(135deg,#f2e4c3,#e6c78a,#b78f56);box-shadow:0 0 0 1px rgba(230,199,138,.18),0 10px 24px rgba(230,199,138,.14)}}
.chip:after{{content:"";position:absolute;inset:0;background:linear-gradient(120deg,transparent,rgba(255,255,255,.18),transparent);transform:translateX(-120%);pointer-events:none}}
.chip:hover:after{{animation:sweep .8s ease}}
.grid{{display:grid;grid-template-columns:420px 1fr;gap:14px}}
.panel{{border-radius:24px;overflow:hidden}}
.panel-head{{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 18px;border-bottom:1px solid var(--line)}}
.panel-head h2{{margin:0;font-size:15px;letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}}
.list{{max-height:720px;overflow:auto}}
.item{{padding:12px 14px;border-bottom:1px solid rgba(230,199,138,.06);cursor:pointer;transition:.2s ease transform,.2s ease background,.2s ease border-color;position:relative}}
.item:hover,.item.active{{background:rgba(230,199,138,.055);transform:translateX(3px)}}
.item:hover:before,.item.active:before{{content:"";position:absolute;left:0;top:12px;bottom:12px;width:2px;background:linear-gradient(180deg,transparent,var(--gold),transparent)}}
.item-title{{font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#f1ebde}}
.item-path{{margin-top:4px;font:11px var(--mono);color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.item-stats{{margin-top:8px;display:flex;gap:6px;flex-wrap:wrap}}
.pill{{border-radius:999px;padding:3px 8px;font:850 10px var(--mono);background:rgba(255,255,255,.04);color:var(--soft);border:1px solid rgba(230,199,138,.08)}}
.file{{color:#d9cfbb}} .external{{color:#b89a5e}} .unresolved{{color:var(--accent-red)}} .workspace{{color:#e6c78a}}
.graph-stage{{position:relative;height:720px;background:radial-gradient(circle at 50% 45%,rgba(230,199,138,.06),transparent 32rem)}}
#graph{{display:block;width:100%;height:720px}}
.hud{{position:absolute;inset:14px auto auto 14px;display:flex;gap:8px;flex-wrap:wrap;max-width:72%}}
.hud span{{border:1px solid var(--line);border-radius:999px;padding:6px 10px;background:rgba(5,5,6,.56);font:850 11px var(--mono);color:var(--soft)}}
.detail{{border-top:1px solid var(--line);padding:18px;background:rgba(0,0,0,.18)}}
.detail h3{{margin:0 0 10px;font-size:24px;letter-spacing:-.045em;color:#f2eee6}}
.detail-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}}
.kv{{border:1px solid rgba(230,199,138,.09);border-radius:16px;padding:10px;background:rgba(255,255,255,.028)}}
.kv span{{display:block;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em}}
.kv b{{display:block;margin-top:5px;font-family:var(--mono);overflow-wrap:anywhere;color:#f6f0e2}}
.tables{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}}
.table-scroll{{max-height:420px;overflow:auto}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th,td{{padding:10px;border-bottom:1px solid rgba(230,199,138,.08);text-align:left;vertical-align:top}}
th{{position:sticky;top:0;background:rgba(12,12,13,.96);color:var(--muted);letter-spacing:.12em;text-transform:uppercase;font:900 10px var(--mono)}}
td.path{{font-family:var(--mono);color:var(--soft);overflow-wrap:anywhere}}
.footer{{margin:16px 0 0;color:var(--muted);font:12px var(--mono)}}
.section-title{{margin:16px 0 10px;color:var(--gold);font:900 11px var(--mono);letter-spacing:.2em;text-transform:uppercase}}
@media(max-width:1280px){{.hero,.grid,.tables,.command-bar{{grid-template-columns:1fr}}.metrics{{grid-template-columns:repeat(2,1fr)}}.badges{{justify-content:flex-start}}}}
</style>
</head>
<body>
<main class="shell">
  <header class="hero glass">
    <section>
      <p class="eyebrow">Code Atlas Visual V04.2 / Black Glass Atlas</p>
      <h1>{title_html}</h1>
      <p class="subtitle">Elegant dark-mode dependency intelligence atlas for Terminal de Venta. It consumes the V03.1 graph, highlights runtime signal over repo noise, and stays fully read-only because uncontrolled writes are how a clean penthouse becomes a bodega with ghosts.</p>
      <p class="meta">Graph: {graph_html}<br>Summary: {summary_html}</p>
      <div class="executive-note glass"><b>Executive view:</b> Start in Runtime Focus, inspect the three remaining risk signals, then open workspaces one by one. Same engine, cleaner suit, less street market, more command room at midnight.</div>
    </section>
    <section class="exec-card">
      <div class="badges"><span class="badge">{package}</span><span class="badge">{manager}</span>{framework_badges}<span class="badge">offline html</span></div>
      <div class="orbit"><canvas id="heroCanvas" width="640" height="230"></canvas></div>
    </section>
  </header>

  <section class="metrics" id="metrics"></section>

  <section class="command-bar glass">
    <input id="search" placeholder="Search node, path, workspace, import...">
    <select id="workspace"></select>
    <select id="kind"><option value="">All kinds</option><option>file</option><option>external</option><option>unresolved</option><option>workspace</option></select>
    <select id="edgeClass"><option value="">All edge classes</option><option>internal</option><option>external</option><option>unresolved</option><option>contains</option></select>
    <select id="degree"><option value="0">Degree 0+</option><option value="2">Degree 2+</option><option value="5">Degree 5+</option><option value="10">Degree 10+</option><option value="20">Degree 20+</option></select>
    <button id="exportJson">Export filtered JSON</button>
  </section>
  <section class="section-title">Executive filters</section>
  <section class="toggles">
    <span class="chip active" data-toggle="runtime">Runtime focus</span>
    <span class="chip active" data-toggle="hideTooling">Hide tooling</span>
    <span class="chip" data-toggle="hideExternal">Hide externals</span>
    <span class="chip active" data-toggle="hideStdlib">Hide stdlib</span>
    <span class="chip" data-toggle="unresolvedOnly">Risk signals only</span>
    <span class="chip" data-toggle="neighbors">Selected neighborhood</span>
    <span class="chip" data-toggle="calm">Calm motion</span>
  </section>

  <section class="grid">
    <aside class="panel glass">
      <div class="panel-head"><h2>Signal nodes</h2><span class="meta" id="nodeCount"></span></div>
      <div class="list" id="nodeList"></div>
    </aside>
    <section class="panel glass">
      <div class="panel-head"><h2>Constellation field</h2><span class="meta" id="fieldMeta"></span></div>
      <div class="graph-stage"><canvas id="graph" width="1120" height="720"></canvas><div class="hud" id="hud"></div></div>
      <div class="detail" id="detail"></div>
    </section>
  </section>

  <section class="tables">
    <section class="panel glass"><div class="panel-head"><h2>Top external surface</h2><span class="meta">packages + stdlib</span></div><div class="table-scroll"><table id="externalTable"></table></div></section>
    <section class="panel glass"><div class="panel-head"><h2>Risk signals</h2><span class="meta">unresolved edges</span></div><div class="table-scroll"><table id="unresolvedTable"></table></div></section>
  </section>
  <p class="footer">Generated by Code Atlas Dependency Visual V04.2 / Black Glass Atlas. Keep Capatch generic. Keep Code Atlas as a consumer. Keep the map elegant enough to show, grounded enough to trust.</p>
</main>
<script id="model" type="application/json">{model_json}</script>
<script>
const MODEL = JSON.parse(document.getElementById('model').textContent);
const NODES = MODEL.nodes || [];
const EDGES = MODEL.edges || [];
const edgeByNode = new Map();
for (const e of EDGES) {{
  if (!edgeByNode.has(e.source)) edgeByNode.set(e.source, []);
  if (!edgeByNode.has(e.target)) edgeByNode.set(e.target, []);
  edgeByNode.get(e.source).push(e); edgeByNode.get(e.target).push(e);
}}
const state = {{ search:'', workspace:'', kind:'', edgeClass:'', degree:0, runtime:true, hideExternal:false, hideStdlib:true, hideTooling:true, unresolvedOnly:false, neighbors:false, calm:false, selected:null }};
const $ = (id)=>document.getElementById(id);
const fmt = (n)=> new Intl.NumberFormat().format(Number(n||0));
const workspaceOrder = ['(root)','products/pc/app','products/tablet/app','products/mobile/app'];
function esc(s){{ return String(s??'').replace(/[&<>"']/g, c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[c])); }}
function colorFor(n){{
  if (n.kind==='unresolved') return '#c75c5c';
  if (n.kind==='workspace') return '#e6c78a';
  if (n.kind==='external') return n.stdlib_external ? '#8b7a57' : '#b89a5e';
  if (n.workspace==='products/mobile/app') return '#d6c29b';
  if (n.workspace==='products/tablet/app') return '#eee0ba';
  if (n.workspace==='products/pc/app') return '#c9b17e';
  return '#e4ddd0';
}}
function alphaForEdge(e){{
  if ((e.classification||'')==='unresolved' || String(e.kind||'').includes('unresolved')) return 'rgba(199,92,92,.62)';
  if ((e.classification||'')==='contains') return 'rgba(230,199,138,.12)';
  if ((e.classification||'')==='external') return 'rgba(184,154,94,.16)';
  return 'rgba(230,199,138,.20)';
}}
function metricCard(label, value, note){{
  return `<article class="metric glass"><span>${{esc(label)}}</span><strong>${{esc(fmt(value))}}</strong><small>${{esc(note)}}</small></article>`;
}}
function renderMetrics(){{
  const ds = MODEL.dependency_summary || {{}};
  $('metrics').innerHTML = [
    metricCard('Source files', ds.source_files, 'Analyzed source surface'),
    metricCard('Edges', ds.edges, 'Total dependency edges'),
    metricCard('Internal', ds.internal_edges, 'In-repo relationships'),
    metricCard('External', ds.external_edges, 'Packages + stdlib surface'),
    metricCard('Unresolved', ds.unresolved_edges, 'Risk signals still open'),
    metricCard('Ignored', ds.ignored_edges||0, 'Malformed/import-like noise'),
    metricCard('Runtime nodes', MODEL.runtime_count, 'Product-facing graph'),
    metricCard('Tooling nodes', MODEL.tooling_count, 'Repo operational layer'),
  ].join('');
}}
function populateFilters(){{
  const workspaces = [...new Set(NODES.map(n=>n.workspace||'(unknown)'))].sort((a,b)=>{{
    const ai = workspaceOrder.indexOf(a), bi = workspaceOrder.indexOf(b);
    if (ai>=0 || bi>=0) return (ai<0?999:ai)-(bi<0?999:bi);
    return a.localeCompare(b);
  }});
  $('workspace').innerHTML = '<option value="">All workspaces</option>' + workspaces.map(w=>`<option>${{esc(w)}}</option>`).join('');
}}
function matchesNode(n){{
  if (state.workspace && n.workspace !== state.workspace) return false;
  if (state.kind && n.kind !== state.kind) return false;
  if (Number(n.degree||0) < state.degree) return false;
  if (state.runtime && !n.runtime && n.kind!=='workspace' && n.kind!=='unresolved') return false;
  if (state.hideTooling && !n.runtime && n.kind==='file') return false;
  if (state.hideExternal && n.kind==='external') return false;
  if (state.hideStdlib && n.stdlib_external) return false;
  if (state.unresolvedOnly) {{
    const edges = edgeByNode.get(n.id) || [];
    if (!edges.some(e => (e.classification||'')==='unresolved' || String(e.kind||'').includes('unresolved'))) return false;
  }}
  const q = state.search.trim().toLowerCase();
  if (q) {{
    const hay = [n.id, n.label, n.path, n.workspace, n.kind, (n.metadata||{{}}).raw].join(' ').toLowerCase();
    if (!hay.includes(q)) return false;
  }}
  return true;
}}
function filteredNodes(){{
  let nodes = NODES.filter(matchesNode);
  if (state.neighbors && state.selected) {{
    const keep = new Set([state.selected]);
    for (const e of edgeByNode.get(state.selected) || []) {{ keep.add(e.source); keep.add(e.target); }}
    nodes = nodes.filter(n=>keep.has(n.id));
  }}
  return nodes.sort((a,b)=>(Number(b.degree||0)-Number(a.degree||0)) || String(a.label||a.id).localeCompare(String(b.label||b.id)));
}}
function filteredEdges(nodes){{
  const ids = new Set(nodes.map(n=>n.id));
  return EDGES.filter(e=>ids.has(e.source) && ids.has(e.target) && (!state.edgeClass || (e.classification||'')===state.edgeClass));
}}
function renderList(nodes){{
  $('nodeCount').textContent = `${{fmt(nodes.length)}} visible nodes`;
  $('nodeList').innerHTML = nodes.slice(0,220).map(n=>`
    <div class="item ${{state.selected===n.id?'active':''}}" data-id="${{esc(n.id)}}">
      <div class="item-title">${{esc(n.label || n.id)}}</div>
      <div class="item-path">${{esc(n.path || n.id)}}</div>
      <div class="item-stats">
        <span class="pill workspace">${{esc(n.workspace||'(unknown)')}}</span>
        <span class="pill ${{esc(n.kind)}}">${{esc(n.kind)}}</span>
        <span class="pill">deg ${{fmt(n.degree)}}</span>
        <span class="pill">in ${{fmt(n.inbound)}}</span>
        <span class="pill">out ${{fmt(n.outbound)}}</span>
      </div>
    </div>
  `).join('');
  document.querySelectorAll('#nodeList .item').forEach(el=>el.onclick=()=>{{ state.selected = el.dataset.id; renderAll(); }});
  if (!state.selected && nodes[0]) state.selected = nodes[0].id;
}}
function renderDetail(){{
  const node = NODES.find(n=>n.id===state.selected);
  if (!node) {{ $('detail').innerHTML = '<div class="meta">Select a node to inspect its neighborhood.</div>'; return; }}
  const incident = (edgeByNode.get(node.id)||[]).slice(0,18);
  $('detail').innerHTML = `
    <h3>${{esc(node.label || node.id)}}</h3>
    <div class="meta">${{esc(node.path || node.id)}}</div>
    <div class="detail-grid" style="margin-top:12px">
      <div class="kv"><span>Workspace</span><b>${{esc(node.workspace||'(unknown)')}}</b></div>
      <div class="kv"><span>Kind</span><b>${{esc(node.kind||'unknown')}}</b></div>
      <div class="kv"><span>Inbound</span><b>${{fmt(node.inbound)}}</b></div>
      <div class="kv"><span>Outbound</span><b>${{fmt(node.outbound)}}</b></div>
      <div class="kv"><span>Degree</span><b>${{fmt(node.degree)}}</b></div>
      <div class="kv"><span>Runtime</span><b>${{node.runtime ? 'yes' : 'no'}}</b></div>
      <div class="kv"><span>Stdlib external</span><b>${{node.stdlib_external ? 'yes' : 'no'}}</b></div>
      <div class="kv"><span>Node id</span><b>${{esc(node.id)}}</b></div>
    </div>
    <div class="section-title">Selected neighborhood</div>
    <div class="meta">${{incident.map(e=>`${{esc(e.source)}} → ${{esc(e.target)}} (${{esc(e.classification||e.kind||'edge')}})`).join('<br>') || 'No adjacent edges visible.'}}</div>
  `;
}}
function renderTables(){{
  $('externalTable').innerHTML = `<thead><tr><th>External</th><th>Inbound</th><th>Class</th></tr></thead><tbody>${{(MODEL.top_external||[]).slice(0,80).map(r=>`<tr><td class="path">${{esc(r.raw || r.label || r.path)}}</td><td>${{fmt(r.inbound)}}</td><td>${{r.stdlib_external ? 'stdlib' : 'package'}}</td></tr>`).join('')}}</tbody>`;
  $('unresolvedTable').innerHTML = `<thead><tr><th>Source</th><th>Target</th><th>Kind</th></tr></thead><tbody>${{(MODEL.unresolved_edges||[]).map(r=>`<tr><td class="path">${{esc(r.source)}}</td><td class="path">${{esc(r.raw || r.target)}}</td><td>${{esc(r.kind || r.classification || 'unresolved')}}</td></tr>`).join('')}}</tbody>`;
}}
let positions = new Map();
function workspaceCenter(groups, index, w, h){{
  const cols = Math.min(3, groups.length || 1);
  const rows = Math.max(1, Math.ceil(groups.length / cols));
  const col = index % cols, row = Math.floor(index / cols);
  const x = w * (0.18 + (cols===1 ? 0.32 : (0.64 * (col / Math.max(1, cols-1)))));
  const y = h * (0.20 + (rows===1 ? 0.30 : (0.58 * (row / Math.max(1, rows-1)))));
  return [x, y];
}}
function drawGraph(nodes, edges){{
  const canvas = $('graph'); const ctx = canvas.getContext('2d'); const w = canvas.width, h = canvas.height;
  const t = performance.now()/1000; ctx.clearRect(0,0,w,h);
  const drawNodes = nodes.slice(0,420);
  const ids = new Set(drawNodes.map(n=>n.id));
  const groups = [...new Set(drawNodes.map(n=>n.workspace || '[none]'))];
  const centers = new Map(groups.map((g,i)=>[g, workspaceCenter(groups, i, w, h)]));
  const groupIndex = {{}};
  ctx.save();
  for (const [g, c] of centers.entries()) {{
    ctx.strokeStyle = 'rgba(230,199,138,.09)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.ellipse(c[0], c[1], 120, 54, Math.sin(t*.15 + c[0]*.001)*.22, 0, Math.PI*2); ctx.stroke();
    ctx.fillStyle = 'rgba(230,199,138,.42)'; ctx.font = '11px Segoe UI'; ctx.fillText(g, c[0]-54, c[1]-66);
  }}
  ctx.restore();
  for (const n of drawNodes) {{
    const c = centers.get(n.workspace || '[none]') || [w/2, h/2];
    groupIndex[n.workspace] = (groupIndex[n.workspace] || 0) + 1;
    const i = groupIndex[n.workspace];
    const r = 40 + Math.sqrt(i)*17 + (n.kind==='workspace' ? 16 : 0);
    const a = i*2.399 + (state.calm ? 0 : t*.05);
    const x = c[0] + Math.cos(a)*r;
    const y = c[1] + Math.sin(a)*(r*.62);
    positions.set(n.id, [x,y]);
  }}
  ctx.lineWidth = 1;
  for (const e of edges.slice(0,2200)) {{
    if (!ids.has(e.source) || !ids.has(e.target)) continue;
    const a = positions.get(e.source), b = positions.get(e.target); if (!a || !b) continue;
    ctx.strokeStyle = alphaForEdge(e);
    ctx.shadowColor = (e.classification==='unresolved') ? 'rgba(199,92,92,.32)' : 'rgba(230,199,138,.12)';
    ctx.shadowBlur = (e.classification==='unresolved' || state.selected===e.source || state.selected===e.target) ? 8 : 0;
    ctx.beginPath();
    ctx.moveTo(a[0], a[1]);
    const mx = (a[0] + b[0]) / 2;
    const my = (a[1] + b[1]) / 2 - 16;
    ctx.quadraticCurveTo(mx, my, b[0], b[1]);
    ctx.stroke();
    ctx.shadowBlur = 0;
  }}
  for (const n of drawNodes) {{
    const p = positions.get(n.id); if (!p) continue;
    const deg = Math.min(28, 5 + Math.sqrt(n.degree || 1) * 2.2);
    ctx.beginPath();
    ctx.fillStyle = colorFor(n);
    ctx.shadowColor = colorFor(n);
    ctx.shadowBlur = state.selected===n.id ? 22 : 8;
    ctx.arc(p[0], p[1], state.selected===n.id ? deg+4 : deg, 0, Math.PI*2);
    ctx.fill();
    ctx.shadowBlur = 0;
    if ((n.degree || 0) > 18 || state.selected===n.id) {{
      ctx.fillStyle = 'rgba(242,238,230,.92)';
      ctx.font = '11px Segoe UI';
      ctx.fillText((n.label || n.id).slice(0, 30), p[0] + deg + 5, p[1] + 4);
    }}
  }}
  $('fieldMeta').textContent = `${{fmt(drawNodes.length)}} nodes / ${{fmt(edges.length)}} edges`;
  $('hud').innerHTML = [
    `runtime ${{state.runtime?'on':'off'}}`,
    `tooling ${{state.hideTooling?'hidden':'visible'}}`,
    `externals ${{state.hideExternal?'hidden':'visible'}}`,
    `stdlib ${{state.hideStdlib?'hidden':'visible'}}`,
    `degree ${{state.degree}}+`,
  ].map(x=>`<span>${{x}}</span>`).join('');
}}
function drawHero(){{
  const canvas = $('heroCanvas'); const ctx = canvas.getContext('2d'); const w = canvas.width, h = canvas.height; const t = performance.now()/1000;
  ctx.clearRect(0,0,w,h);
  for (let ring=0; ring<5; ring++) {{
    ctx.strokeStyle = `rgba(230,199,138,${{.14 - ring*.018}})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(w/2, h/2, 80 + ring*38, 28 + ring*17, Math.sin(t*.16 + ring)*.35, 0, Math.PI*2);
    ctx.stroke();
  }}
  for (let i=0; i<48; i++) {{
    const a = i*.61 + t*(.12 + (i%4)*.02);
    const r = 20 + (i%10)*18;
    const x = w/2 + Math.cos(a)*r;
    const y = h/2 + Math.sin(a)*(r*.38);
    ctx.fillStyle = i%7===0 ? '#c75c5c' : (i%3===0 ? '#e6c78a' : '#d8c7a2');
    ctx.shadowColor = ctx.fillStyle;
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.arc(x, y, i%9===0 ? 3.7 : 2.5, 0, Math.PI*2);
    ctx.fill();
  }}
  requestAnimationFrame(drawHero);
}}
function renderAll(){{ const nodes = filteredNodes(); const edges = filteredEdges(nodes); renderList(nodes); renderDetail(); drawGraph(nodes, edges); }}
function bind(){{
  $('search').oninput = e => {{ state.search = e.target.value; renderAll(); }};
  $('workspace').onchange = e => {{ state.workspace = e.target.value; renderAll(); }};
  $('kind').onchange = e => {{ state.kind = e.target.value; renderAll(); }};
  $('edgeClass').onchange = e => {{ state.edgeClass = e.target.value; renderAll(); }};
  $('degree').onchange = e => {{ state.degree = Number(e.target.value || 0); renderAll(); }};
  document.querySelectorAll('.chip').forEach(ch => ch.onclick = () => {{ const k = ch.dataset.toggle; state[k] = !state[k]; ch.classList.toggle('active', state[k]); renderAll(); }});
  $('graph').onclick = e => {{
    const rect = e.target.getBoundingClientRect();
    const x = (e.clientX - rect.left) * ($('graph').width / rect.width);
    const y = (e.clientY - rect.top) * ($('graph').height / rect.height);
    let best = null, bd = 999;
    for (const [id,p] of positions) {{ const d = Math.hypot(p[0]-x,p[1]-y); if (d < bd) {{ bd = d; best = id; }} }}
    if (best && bd < 34) {{ state.selected = best; renderAll(); }}
  }};
  $('exportJson').onclick = () => {{
    const nodes = filteredNodes();
    const ids = new Set(nodes.map(n=>n.id));
    const edges = EDGES.filter(e=>ids.has(e.source) && ids.has(e.target));
    const blob = new Blob([JSON.stringify({{tool:'code-atlas dependency visual filtered export',version:'4.2.0',generated_at:new Date().toISOString(),theme:'black_glass_gold',nodes,edges}}, null, 2)], {{type:'application/json'}});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'code_atlas_filtered_dependency_graph_black_glass.json'; a.click(); URL.revokeObjectURL(a.href);
  }};
}}
renderMetrics(); populateFilters(); renderTables(); bind(); renderAll(); drawHero();
function tick(){{ if(!state.calm) renderAll(); requestAnimationFrame(tick); }} requestAnimationFrame(tick);
</script>
</body>
</html>'''


def render(args: argparse.Namespace) -> int:
    graph_path = Path(args.graph_json).expanduser().resolve()
    summary_path = Path(args.summary_json).expanduser().resolve() if args.summary_json else None
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    graph = load_json(graph_path)
    summary = load_json(summary_path) if summary_path else None
    model = enrich_graph(graph, summary)
    title = args.title or "Terminal de Venta Black Glass Atlas"
    html_doc = html_shell(model, title, graph_path, summary_path)
    out = output_dir / f"code_atlas_dependency_visual_v04_2_{safe_name(title)}_{now_stamp()}.html"
    out.write_text(html_doc, encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "tool": TOOL,
        "version": VERSION,
        "theme": "black_glass_gold",
        "output": str(out),
        "nodes": len(model["nodes"]),
        "edges": len(model["edges"]),
        "unresolved_edges": model["dependency_summary"].get("unresolved_edges"),
    }, indent=2))
    return 0


def verify(args: argparse.Namespace) -> int:
    graph_path = Path(args.graph_json).expanduser().resolve()
    summary_path = Path(args.summary_json).expanduser().resolve() if args.summary_json else None
    graph = load_json(graph_path)
    summary = load_json(summary_path) if summary_path else None
    model = enrich_graph(graph, summary)
    failures: List[str] = []

    if args.expect_graph_version and str(model.get("graph_version")) != str(args.expect_graph_version):
        failures.append(f"graph version mismatch: expected {args.expect_graph_version}, got {model.get('graph_version')}")
    if len(model["nodes"]) <= 0:
        failures.append("graph has no nodes")
    if len(model["edges"]) <= 0:
        failures.append("graph has no edges")
    unresolved = int((model.get("dependency_summary") or {}).get("unresolved_edges") or 0)
    if args.max_unresolved is not None and unresolved > int(args.max_unresolved):
        failures.append(f"unresolved edges {unresolved} exceed max {args.max_unresolved}")
    for prefix in args.forbid_source_prefix or []:
        for e in model["edges"]:
            src_node = str(e.get("source") or "")
            src = src_node.replace("file:", "", 1)
            if src.startswith(prefix):
                failures.append(f"forbidden source prefix {prefix}: {src}")
                break
    if any(str(n.get("id") or "") == "external:" for n in model["nodes"]):
        failures.append("empty external node id found")
    for bad in ("json", "pathlib", "__future__"):
        if any(str(n.get("id")) == f"file:{bad}" for n in model["nodes"]):
            failures.append(f"stdlib import still classified as file node: {bad}")

    result = {
        "ok": not failures,
        "tool": TOOL,
        "version": VERSION,
        "theme": "black_glass_gold",
        "graph_version": model.get("graph_version"),
        "nodes": len(model["nodes"]),
        "edges": len(model["edges"]),
        "unresolved_edges": unresolved,
        "unresolved_unique_edges": model.get("unresolved_unique_edges"),
        "runtime_nodes": model.get("runtime_count"),
        "tooling_nodes": model.get("tooling_count"),
        "stdlib_external_nodes": model.get("stdlib_external_count"),
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Render or verify a premium black-glass offline Code Atlas dependency visual.")
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("render", help="render a standalone HTML black-glass atlas")
    r.add_argument("--graph-json", required=True, help="Code Atlas V03.1 graph JSON")
    r.add_argument("--summary-json", required=False, help="Code Atlas V03.1 summary JSON")
    r.add_argument("--output-dir", required=True, help="directory for generated HTML")
    r.add_argument("--title", default="Terminal de Venta Black Glass Atlas", help="HTML title and hero heading")
    r.set_defaults(func=render)

    v = sub.add_parser("verify", help="verify graph/summary before rendering or handoff")
    v.add_argument("--graph-json", required=True, help="Code Atlas V03.1 graph JSON")
    v.add_argument("--summary-json", required=False, help="Code Atlas V03.1 summary JSON")
    v.add_argument("--max-unresolved", type=int, default=None)
    v.add_argument("--forbid-source-prefix", action="append", default=[])
    v.add_argument("--expect-graph-version", default=None)
    v.set_defaults(func=verify)
    return p


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
