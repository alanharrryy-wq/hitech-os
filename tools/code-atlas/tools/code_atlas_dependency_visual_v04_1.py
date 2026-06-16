#!/usr/bin/env python3
"""Code Atlas Dependency Visual V04.1.

Offline HTML renderer for Code Atlas dependency consumer graph JSON.
It reads existing graph/summary artifacts and writes one standalone HTML file.
It never scans projects, patches code, or mutates graph inputs.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

VERSION = "4.1.0"
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
    node_by_id = {str(n.get("id")): n for n in nodes}

    workspace_counts: Dict[str, int] = {}
    runtime_count = 0
    tooling_count = 0
    stdlib_count = 0
    for n in nodes:
        ws = node_workspace(n)
        workspace_counts[ws] = workspace_counts.get(ws, 0) + 1
        if is_runtime_node(n):
            runtime_count += 1
        else:
            tooling_count += 1
        if is_stdlib_external(n):
            stdlib_count += 1
        n["workspace"] = ws
        n["degree"] = int(n.get("inbound") or 0) + int(n.get("outbound") or 0)
        n["runtime"] = is_runtime_node(n)
        n["stdlib_external"] = is_stdlib_external(n)

    edge_classes: Dict[str, int] = {}
    edge_kinds: Dict[str, int] = {}
    package_edges = 0
    unresolved_edges: List[Dict[str, Any]] = []
    for e in edges:
        cls = str(e.get("classification") or "unknown")
        kind = str(e.get("kind") or "unknown")
        edge_classes[cls] = edge_classes.get(cls, 0) + int(e.get("weight") or 1)
        edge_kinds[kind] = edge_kinds.get(kind, 0) + int(e.get("weight") or 1)
        if cls == "unresolved" or "unresolved" in kind:
            unresolved_edges.append(e)
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
            "ignored_edges": edge_classes.get("ignored", 0),
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
  --bg0:#02030a; --bg1:#07111d; --bg2:#0b1830; --glass:rgba(12,18,31,.72);
  --glass2:rgba(18,26,44,.62); --line:rgba(163,210,255,.18); --line2:rgba(163,210,255,.34);
  --text:#f3f8ff; --soft:#c6d4e8; --muted:#7f91aa; --cyan:#7df2ff; --blue:#7aa7ff;
  --violet:#bd8cff; --green:#87f6c7; --amber:#ffd27d; --red:#ff7c9a; --pink:#ff8ee6;
  --shadow:rgba(0,0,0,.55); --radius:22px; --mono:"Cascadia Mono","SFMono-Regular",Consolas,monospace;
  --sans:"Segoe UI",Aptos,Inter,system-ui,sans-serif;
}}
*{{box-sizing:border-box}} html,body{{min-height:100%}} body{{margin:0;color:var(--text);font-family:var(--sans);overflow-x:hidden;background:var(--bg0)}}
body:before{{content:"";position:fixed;inset:-20%;z-index:-3;background:
  radial-gradient(circle at 15% 10%,rgba(125,242,255,.18),transparent 26rem),
  radial-gradient(circle at 82% 8%,rgba(189,140,255,.18),transparent 32rem),
  radial-gradient(circle at 50% 90%,rgba(135,246,199,.12),transparent 34rem),linear-gradient(135deg,var(--bg0),var(--bg1) 48%,#030611)}}
body:after{{content:"";position:fixed;inset:0;z-index:-2;opacity:.22;background-image:linear-gradient(rgba(125,242,255,.15) 1px,transparent 1px),linear-gradient(90deg,rgba(125,242,255,.15) 1px,transparent 1px);background-size:42px 42px;mask-image:radial-gradient(circle at 50% 30%,#000,transparent 78%)}}
@keyframes floaty{{0%,100%{{transform:translate3d(0,0,0)}}50%{{transform:translate3d(0,-12px,0)}}}}
@keyframes pulse{{0%,100%{{opacity:.65;filter:blur(0)}}50%{{opacity:1;filter:blur(.8px)}}}}
@keyframes sweep{{0%{{transform:translateX(-110%)}}100%{{transform:translateX(110%)}}}}
@media (prefers-reduced-motion:reduce){{*,*:before,*:after{{animation:none;transition:none;scroll-behavior:auto}}}}
.shell{{width:min(100%,1580px);margin:0 auto;padding:24px}}
.hero,.panel,.metric,.chip,.command-bar{{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.085),rgba(255,255,255,.025)),var(--glass);box-shadow:0 30px 90px var(--shadow),inset 0 1px 0 rgba(255,255,255,.18);backdrop-filter:blur(18px)}}
.hero{{position:relative;overflow:hidden;border-radius:30px;padding:28px;display:grid;grid-template-columns:1.1fr .9fr;gap:24px;min-height:260px}}
.hero:before{{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 0%,rgba(125,242,255,.08) 42%,rgba(255,255,255,.18) 50%,rgba(189,140,255,.08) 58%,transparent 100%);animation:sweep 8s linear infinite;pointer-events:none}}
.eyebrow{{margin:0 0 10px;color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font:900 12px var(--mono)}}
h1{{margin:0;font-size:clamp(36px,5.8vw,88px);letter-spacing:-.075em;line-height:.86;text-shadow:0 0 34px rgba(125,242,255,.18)}}
.subtitle{{max-width:82ch;color:var(--soft);line-height:1.65;font-size:15px}}
.meta{{font:12px var(--mono);color:var(--muted);overflow-wrap:anywhere}}
.badges{{display:flex;gap:8px;flex-wrap:wrap;align-content:flex-start;justify-content:flex-end}}.badge{{border:1px solid var(--line);background:rgba(255,255,255,.055);border-radius:999px;padding:7px 11px;font:800 12px var(--mono);color:var(--soft)}}
.orbital{{position:relative;min-height:220px;border-radius:26px;background:radial-gradient(circle at 50% 50%,rgba(125,242,255,.18),transparent 7rem),linear-gradient(135deg,rgba(125,242,255,.08),rgba(189,140,255,.08));border:1px solid var(--line);overflow:hidden;animation:floaty 8s ease-in-out infinite}}
.orbital canvas{{width:100%;height:220px;display:block}}
.metrics{{display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:10px;margin:14px 0}}.metric{{border-radius:20px;padding:14px;min-height:96px;position:relative;overflow:hidden}}.metric:after{{content:"";position:absolute;inset:auto -20% -60% -20%;height:90%;background:radial-gradient(circle,rgba(125,242,255,.15),transparent 70%);opacity:.75}}
.metric span{{display:block;color:var(--muted);letter-spacing:.13em;text-transform:uppercase;font:900 10px var(--mono)}}.metric strong{{display:block;margin-top:10px;font:950 26px var(--mono)}}
.command-bar{{border-radius:24px;padding:14px;margin-bottom:14px;display:grid;grid-template-columns:1.8fr repeat(5, minmax(130px,1fr));gap:10px;align-items:center}}
input,select,button{{height:42px;border:1px solid var(--line);border-radius:14px;background:rgba(3,7,14,.76);color:var(--text);padding:0 12px;font:13px var(--sans);outline:none}}input:focus,select:focus{{border-color:rgba(125,242,255,.8);box-shadow:0 0 0 4px rgba(125,242,255,.11)}}button{{cursor:pointer;border:0;font-weight:950;color:#031018;background:linear-gradient(135deg,var(--cyan),var(--violet));box-shadow:0 10px 28px rgba(125,242,255,.18)}}button.ghost{{background:rgba(255,255,255,.07);color:var(--soft);border:1px solid var(--line)}}
.toggles{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}}.chip{{border-radius:999px;padding:9px 11px;font:850 12px var(--mono);cursor:pointer;user-select:none;color:var(--soft)}}.chip.active{{color:#031018;background:linear-gradient(135deg,var(--green),var(--cyan));box-shadow:0 0 28px rgba(125,242,255,.22)}}
.grid{{display:grid;grid-template-columns:410px 1fr;gap:14px}}.panel{{border-radius:24px;overflow:hidden}}.panel-head{{padding:15px 16px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:12px}}.panel-head h2{{margin:0;font-size:16px;letter-spacing:-.02em}}
.list{{max-height:690px;overflow:auto}}.item{{padding:11px 13px;border-bottom:1px solid rgba(163,210,255,.08);cursor:pointer;transition:.18s ease transform,.18s ease background}}.item:hover,.item.active{{background:rgba(125,242,255,.09);transform:translateX(3px)}}.item-title{{font-weight:950;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.item-path{{margin-top:4px;font:11px var(--mono);color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.item-stats{{margin-top:7px;display:flex;gap:6px;flex-wrap:wrap}}.pill{{border-radius:999px;padding:3px 7px;font:850 10px var(--mono);background:rgba(255,255,255,.07);color:var(--soft)}}.file{{color:var(--green)}}.external{{color:var(--blue)}}.unresolved{{color:var(--red)}}.workspace{{color:var(--amber)}}
.graph-stage{{position:relative;height:690px;background:radial-gradient(circle at 50% 45%,rgba(125,242,255,.08),transparent 30rem)}}#graph{{width:100%;height:690px;display:block}}.hud{{position:absolute;inset:14px auto auto 14px;display:flex;gap:8px;flex-wrap:wrap;max-width:72%}}.hud span{{border:1px solid var(--line);border-radius:999px;padding:6px 9px;background:rgba(0,0,0,.36);font:850 11px var(--mono)}}
.detail{{border-top:1px solid var(--line);padding:16px;background:rgba(0,0,0,.18)}}.detail h3{{margin:0 0 10px;font-size:22px;letter-spacing:-.04em}}.detail-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}}.kv{{border:1px solid rgba(163,210,255,.11);border-radius:16px;padding:9px;background:rgba(255,255,255,.035)}}.kv span{{display:block;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}}.kv b{{font-family:var(--mono);overflow-wrap:anywhere}}
.tables{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}}table{{width:100%;border-collapse:collapse;font-size:12px}}th,td{{padding:9px 10px;border-bottom:1px solid rgba(163,210,255,.09);text-align:left;vertical-align:top}}th{{position:sticky;top:0;background:rgba(10,16,28,.96);color:var(--muted);letter-spacing:.12em;text-transform:uppercase;font:900 10px var(--mono)}}td.path{{font-family:var(--mono);color:var(--soft);overflow-wrap:anywhere}}.table-scroll{{max-height:420px;overflow:auto}}
.footer{{margin:16px 0 0;color:var(--muted);font:12px var(--mono)}}
@media(max-width:1200px){{.hero,.grid,.tables,.command-bar{{grid-template-columns:1fr}}.metrics{{grid-template-columns:repeat(2,1fr)}}.badges{{justify-content:flex-start}}}}
</style>
</head>
<body>
<main class="shell">
  <header class="hero">
    <section>
      <p class="eyebrow">Code Atlas Visual V04.1 / Neon Ops Deck</p>
      <h1>{title_html}</h1>
      <p class="subtitle">Standalone dependency command deck for Terminal de Venta. It reads the V03.1 graph, renders a high-signal visual map, and stays read-only because hidden writes are how repos become haunted houses.</p>
      <p class="meta">Graph: {graph_html}<br>Summary: {summary_html}</p>
    </section>
    <section>
      <div class="badges"><span class="badge">{package}</span><span class="badge">{manager}</span>{framework_badges}<span class="badge">offline html</span></div>
      <div class="orbital"><canvas id="heroCanvas" width="640" height="220"></canvas></div>
    </section>
  </header>

  <section class="metrics" id="metrics"></section>

  <section class="command-bar">
    <input id="search" placeholder="Search node, path, package, import...">
    <select id="workspace"></select>
    <select id="kind"><option value="">All kinds</option><option>file</option><option>external</option><option>unresolved</option><option>workspace</option></select>
    <select id="edgeClass"><option value="">All edge classes</option><option>internal</option><option>external</option><option>unresolved</option><option>contains</option></select>
    <select id="degree"><option value="0">Degree 0+</option><option value="2">Degree 2+</option><option value="5">Degree 5+</option><option value="10">Degree 10+</option><option value="20">Degree 20+</option></select>
    <button id="exportJson">Export filtered JSON</button>
  </section>
  <section class="toggles">
    <span class="chip active" data-toggle="runtime">Runtime focus</span>
    <span class="chip" data-toggle="hideExternal">Hide externals</span>
    <span class="chip active" data-toggle="hideStdlib">Hide stdlib</span>
    <span class="chip" data-toggle="unresolvedOnly">Unresolved only</span>
    <span class="chip" data-toggle="neighbors">Selected neighborhood</span>
    <span class="chip" data-toggle="calm">Calm motion</span>
  </section>

  <section class="grid">
    <aside class="panel"><div class="panel-head"><h2>Signal nodes</h2><span class="meta" id="nodeCount"></span></div><div class="list" id="nodeList"></div></aside>
    <section class="panel"><div class="panel-head"><h2>Animated dependency field</h2><span class="meta" id="fieldMeta"></span></div><div class="graph-stage"><canvas id="graph" width="1040" height="690"></canvas><div class="hud" id="hud"></div></div><div class="detail" id="detail"></div></section>
  </section>

  <section class="tables">
    <section class="panel"><div class="panel-head"><h2>Top external imports</h2><span class="meta">package + stdlib</span></div><div class="table-scroll"><table id="externalTable"></table></div></section>
    <section class="panel"><div class="panel-head"><h2>Unresolved imports</h2><span class="meta">weight-aware</span></div><div class="table-scroll"><table id="unresolvedTable"></table></div></section>
  </section>
  <p class="footer">Generated by Code Atlas Dependency Visual V04.1. Keep Capatch generic. Keep Code Atlas as a consumer. Keep the graph useful, not decorative confetti.</p>
</main>
<script id="model" type="application/json">{model_json}</script>
<script>
const MODEL = JSON.parse(document.getElementById('model').textContent);
const NODES = MODEL.nodes || [];
const EDGES = MODEL.edges || [];
const byId = new Map(NODES.map(n => [n.id, n]));
const edgeByNode = new Map();
for (const e of EDGES) {{
  if (!edgeByNode.has(e.source)) edgeByNode.set(e.source, []);
  if (!edgeByNode.has(e.target)) edgeByNode.set(e.target, []);
  edgeByNode.get(e.source).push(e); edgeByNode.get(e.target).push(e);
}}
const state = {{ search:'', workspace:'', kind:'', edgeClass:'', degree:0, runtime:true, hideExternal:false, hideStdlib:true, unresolvedOnly:false, neighbors:false, calm:false, selected:null }};
const $ = id => document.getElementById(id);
const fmt = n => (n===null || n===undefined) ? 'n/a' : Number(n).toLocaleString();
function kindClass(n){{ return n.kind === 'external' ? 'external' : n.kind === 'unresolved' ? 'unresolved' : n.kind === 'workspace' ? 'workspace' : 'file'; }}
function runtimeOk(n){{ return !state.runtime || n.runtime || n.kind === 'workspace' || n.kind === 'unresolved'; }}
function matchesSearch(n){{ if(!state.search) return true; const q=state.search.toLowerCase(); return [n.id,n.label,n.path,n.workspace,JSON.stringify(n.metadata||{{}})].join(' ').toLowerCase().includes(q); }}
function hasEdgeClass(n){{ if(!state.edgeClass) return true; return (edgeByNode.get(n.id)||[]).some(e => (e.classification||'') === state.edgeClass); }}
function selectedNeighborIds(){{ if(!state.selected || !state.neighbors) return null; const ids = new Set([state.selected]); for(const e of (edgeByNode.get(state.selected)||[])){{ ids.add(e.source); ids.add(e.target); }} return ids; }}
function filteredNodes(){{
  const neigh = selectedNeighborIds();
  return NODES.filter(n => {{
    if(neigh && !neigh.has(n.id)) return false;
    if(state.unresolvedOnly && n.kind !== 'unresolved' && !(edgeByNode.get(n.id)||[]).some(e => e.classification === 'unresolved')) return false;
    if(state.workspace && n.workspace !== state.workspace) return false;
    if(state.kind && n.kind !== state.kind) return false;
    if(Number(n.degree||0) < state.degree) return false;
    if(state.hideExternal && n.kind === 'external') return false;
    if(state.hideStdlib && n.stdlib_external) return false;
    return runtimeOk(n) && matchesSearch(n) && hasEdgeClass(n);
  }}).sort((a,b)=>(b.degree||0)-(a.degree||0));
}}
function filteredEdges(nodes){{ const ids = new Set(nodes.map(n=>n.id)); return EDGES.filter(e => ids.has(e.source) && ids.has(e.target) && (!state.edgeClass || e.classification === state.edgeClass)); }}
function renderMetrics(){{ const d=MODEL.dependency_summary||{{}}; const cards=[['Graph',MODEL.graph_version],['Files',d.source_files],['Edges',d.edges],['Internal',d.internal_edges],['External',d.external_edges],['Unresolved',d.unresolved_edges],['Ignored',d.ignored_edges],['Runtime',MODEL.runtime_count],['Tooling',MODEL.tooling_count]]; $('metrics').innerHTML=cards.map(([k,v])=>`<section class="metric"><span>${{k}}</span><strong>${{fmt(v)}}</strong></section>`).join(''); }}
function populateFilters(){{ const ws=[...new Set(NODES.map(n=>n.workspace).filter(Boolean))].sort(); $('workspace').innerHTML='<option value="">All workspaces</option>'+ws.map(w=>`<option>${{w}}</option>`).join(''); }}
function renderList(nodes){{ $('nodeCount').textContent=`${{fmt(nodes.length)}} shown / ${{fmt(NODES.length)}} total`; $('nodeList').innerHTML=nodes.slice(0,600).map(n=>`<div class="item ${{state.selected===n.id?'active':''}}" data-id="${{n.id}}"><div class="item-title">${{escapeHtml(n.label||n.id)}}</div><div class="item-path">${{escapeHtml(n.path||n.id)}}</div><div class="item-stats"><span class="pill ${{kindClass(n)}}">${{n.kind}}</span><span class="pill">deg ${{fmt(n.degree||0)}}</span><span class="pill">in ${{fmt(n.inbound||0)}}</span><span class="pill">out ${{fmt(n.outbound||0)}}</span><span class="pill">${{escapeHtml(n.workspace||'')}}</span></div></div>`).join(''); document.querySelectorAll('.item').forEach(el=>el.onclick=()=>{{state.selected=el.dataset.id; renderAll();}}); }}
function renderDetail(){{ const n=byId.get(state.selected); if(!n){{ $('detail').innerHTML='<h3>Select a node</h3><p class="meta">Click a row or a dot. Use runtime focus to hide tooling noise.</p>'; return; }} const edges=(edgeByNode.get(n.id)||[]).slice(0,12); $('detail').innerHTML=`<h3>${{escapeHtml(n.label||n.id)}}</h3><div class="detail-grid"><div class="kv"><span>Kind</span><b>${{n.kind}}</b></div><div class="kv"><span>Workspace</span><b>${{escapeHtml(n.workspace||'')}}</b></div><div class="kv"><span>Inbound</span><b>${{fmt(n.inbound||0)}}</b></div><div class="kv"><span>Outbound</span><b>${{fmt(n.outbound||0)}}</b></div></div><p class="meta">${{escapeHtml(n.path||n.id)}}</p><table><thead><tr><th>Class</th><th>Kind</th><th>Edge</th></tr></thead><tbody>${{edges.map(e=>`<tr><td>${{escapeHtml(e.classification||'')}}</td><td>${{escapeHtml(e.kind||'')}}</td><td class="path">${{escapeHtml(e.source)}} -> ${{escapeHtml(e.target)}}<br><span class="meta">${{escapeHtml(e.raw||'')}}</span></td></tr>`).join('')}}</tbody></table>`; }}
function renderTables(){{ const ext=MODEL.top_external||[]; $('externalTable').innerHTML='<thead><tr><th>Name</th><th>Edges</th><th>Raw</th></tr></thead><tbody>'+ext.slice(0,50).map(e=>`<tr><td class="path">${{escapeHtml(e.label||e.path||'')}}</td><td>${{fmt(e.inbound||0)}}</td><td class="path">${{escapeHtml(e.raw||'')}}</td></tr>`).join('')+'</tbody>'; const un=MODEL.unresolved_edges||[]; $('unresolvedTable').innerHTML='<thead><tr><th>Source</th><th>Target</th><th>Weight</th></tr></thead><tbody>'+un.map(e=>`<tr><td class="path">${{escapeHtml(e.source||'')}}</td><td class="path">${{escapeHtml(e.raw||e.target||'')}}</td><td>${{fmt(e.weight||1)}}</td></tr>`).join('')+'</tbody>'; }}
function escapeHtml(s){{ return String(s??'').replace(/[&<>"']/g, c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[c])); }}
let positions = new Map();
function colorFor(n){{ if(n.kind==='external') return '#7aa7ff'; if(n.kind==='unresolved') return '#ff7c9a'; if(n.kind==='workspace') return '#ffd27d'; if(n.workspace==='products/mobile/app') return '#87f6c7'; if(n.workspace==='products/tablet/app') return '#7df2ff'; if(n.workspace==='products/pc/app') return '#bd8cff'; return '#c6d4e8'; }}
function drawGraph(nodes, edges){{ const canvas=$('graph'), ctx=canvas.getContext('2d'), w=canvas.width, h=canvas.height; const t=performance.now()/1000; ctx.clearRect(0,0,w,h); const drawNodes=nodes.slice(0,360); const ids=new Set(drawNodes.map(n=>n.id)); const groups=[...new Set(drawNodes.map(n=>n.workspace||'[none]'))]; const centers=new Map(groups.map((g,i)=>[g, [w*(.18+.64*((i%3)/2)), h*(.22+.56*(Math.floor(i/3)/Math.max(1,Math.ceil(groups.length/3)-1 || 1)))] ])); let gi={{}}; for(const n of drawNodes){{ const c=centers.get(n.workspace||'[none]') || [w/2,h/2]; gi[n.workspace]=(gi[n.workspace]||0)+1; const i=gi[n.workspace]; const r=34+Math.sqrt(i)*16+(n.kind==='workspace'?10:0); const a=i*2.399 + (state.calm?0:t*.08); const x=c[0]+Math.cos(a)*r; const y=c[1]+Math.sin(a)*r; positions.set(n.id, [x,y]); }}
 ctx.lineWidth=1; for(const e of edges.slice(0,1800)){{ if(!ids.has(e.source)||!ids.has(e.target)) continue; const a=positions.get(e.source), b=positions.get(e.target); if(!a||!b) continue; const cls=e.classification; ctx.strokeStyle=cls==='unresolved'?'rgba(255,124,154,.55)':cls==='external'?'rgba(122,167,255,.18)':cls==='contains'?'rgba(255,210,125,.14)':'rgba(125,242,255,.22)'; ctx.beginPath(); ctx.moveTo(a[0],a[1]); const mx=(a[0]+b[0])/2, my=(a[1]+b[1])/2-18; ctx.quadraticCurveTo(mx,my,b[0],b[1]); ctx.stroke(); }}
 for(const n of drawNodes){{ const p=positions.get(n.id); if(!p) continue; const deg=Math.min(28,5+Math.sqrt(n.degree||1)*2.4); ctx.beginPath(); ctx.fillStyle=colorFor(n); ctx.shadowColor=colorFor(n); ctx.shadowBlur=state.selected===n.id?28:12; ctx.arc(p[0],p[1],state.selected===n.id?deg+5:deg,0,Math.PI*2); ctx.fill(); ctx.shadowBlur=0; if((n.degree||0)>20||state.selected===n.id){{ ctx.fillStyle='rgba(243,248,255,.92)'; ctx.font='11px Segoe UI'; ctx.fillText((n.label||n.id).slice(0,28),p[0]+deg+4,p[1]+4); }} }}
 $('fieldMeta').textContent=`${{fmt(drawNodes.length)}} nodes / ${{fmt(edges.length)}} edges`; $('hud').innerHTML=[`runtime ${{state.runtime?'on':'off'}}`,`stdlib ${{state.hideStdlib?'hidden':'visible'}}`,`externals ${{state.hideExternal?'hidden':'visible'}}`,`degree ${{state.degree}}+`].map(x=>`<span>${{x}}</span>`).join(''); }}
function drawHero(){{ const canvas=$('heroCanvas'), ctx=canvas.getContext('2d'), w=canvas.width,h=canvas.height,t=performance.now()/1000; ctx.clearRect(0,0,w,h); for(let ring=0;ring<5;ring++){{ ctx.strokeStyle=`rgba(125,242,255,${{.12-ring*.015}})`; ctx.lineWidth=1; ctx.beginPath(); ctx.ellipse(w/2,h/2,80+ring*38,24+ring*18,Math.sin(t*.18+ring)*.45,0,Math.PI*2); ctx.stroke(); }} for(let i=0;i<52;i++){{ const a=i*.63+t*(.15+i%3*.03); const r=28+(i%9)*18; const x=w/2+Math.cos(a)*r; const y=h/2+Math.sin(a)*(r*.35); ctx.fillStyle=i%7===0?'#ff7c9a':i%5===0?'#bd8cff':'#7df2ff'; ctx.shadowColor=ctx.fillStyle; ctx.shadowBlur=14; ctx.beginPath(); ctx.arc(x,y,i%7===0?3.6:2.4,0,Math.PI*2); ctx.fill(); }} requestAnimationFrame(drawHero); }}
function renderAll(){{ const nodes=filteredNodes(); const edges=filteredEdges(nodes); renderList(nodes); renderDetail(); drawGraph(nodes,edges); }}
function bind(){{ $('search').oninput=e=>{{state.search=e.target.value;renderAll();}}; $('workspace').onchange=e=>{{state.workspace=e.target.value;renderAll();}}; $('kind').onchange=e=>{{state.kind=e.target.value;renderAll();}}; $('edgeClass').onchange=e=>{{state.edgeClass=e.target.value;renderAll();}}; $('degree').onchange=e=>{{state.degree=Number(e.target.value||0);renderAll();}}; document.querySelectorAll('.chip').forEach(ch=>ch.onclick=()=>{{ const k=ch.dataset.toggle; state[k]=!state[k]; ch.classList.toggle('active',state[k]); renderAll(); }}); $('graph').onclick=e=>{{ const rect=e.target.getBoundingClientRect(); const x=(e.clientX-rect.left)*($('graph').width/rect.width), y=(e.clientY-rect.top)*($('graph').height/rect.height); let best=null,bd=999; for(const [id,p] of positions){{ const d=Math.hypot(p[0]-x,p[1]-y); if(d<bd){{bd=d;best=id;}} }} if(best&&bd<32){{state.selected=best;renderAll();}} }}; $('exportJson').onclick=()=>{{ const nodes=filteredNodes(); const ids=new Set(nodes.map(n=>n.id)); const edges=EDGES.filter(e=>ids.has(e.source)&&ids.has(e.target)); const blob=new Blob([JSON.stringify({{tool:'code-atlas dependency visual filtered export',version:'4.1.0',generated_at:new Date().toISOString(),nodes,edges}},null,2)],{{type:'application/json'}}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='code_atlas_filtered_dependency_graph.json'; a.click(); URL.revokeObjectURL(a.href); }}; }}
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
    title = args.title or "Code Atlas Dependency Command Deck"
    html_doc = html_shell(model, title, graph_path, summary_path)
    out = output_dir / f"code_atlas_dependency_visual_v04_1_{safe_name(title)}_{now_stamp()}.html"
    out.write_text(html_doc, encoding="utf-8")
    print(json.dumps({"ok": True, "tool": TOOL, "version": VERSION, "output": str(out), "nodes": len(model["nodes"]), "edges": len(model["edges"]), "unresolved_edges": model["dependency_summary"].get("unresolved_edges")}, indent=2))
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
    p = argparse.ArgumentParser(description="Render or verify a high-polish offline Code Atlas dependency visual.")
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("render", help="render a standalone HTML command deck")
    r.add_argument("--graph-json", required=True, help="Code Atlas V03.1 graph JSON")
    r.add_argument("--summary-json", required=False, help="Code Atlas V03.1 summary JSON")
    r.add_argument("--output-dir", required=True, help="directory for generated HTML")
    r.add_argument("--title", default="Terminal de Venta Dependency Map", help="HTML title and hero heading")
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
