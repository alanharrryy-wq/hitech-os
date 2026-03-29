#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
IMPORT_PATTERN = re.compile(
    r"(?:import|export)\s+[^;]*?\s+from\s+['\"]([^'\"]+)['\"]|require\(\s*['\"]([^'\"]+)['\"]\s*\)|import\(\s*['\"]([^'\"]+)['\"]\s*\)",
    re.MULTILINE | re.DOTALL,
)

BOUNDARY_PATHS = {
    "console-core": "apps/keystone/components/dev-console/console-core",
    "runtime-debug-console": "apps/keystone/components/dev-console/runtime-debug-console",
    "live-scene-composer": "apps/keystone/components/live-scene-composer",
    "runtime-mutation-bridge": "apps/keystone/components/runtime-mutation-bridge",
    "pitch-runtime": "apps/keystone/components/pitch",
    "scene-studio": "apps/keystone/components/scene-studio",
}


@dataclass(frozen=True)
class StrategicEdge:
    edge_id: str
    source: str
    target: str
    relationship: str
    policy_status: str
    note: str


STRATEGIC_EDGES: Tuple[StrategicEdge, ...] = (
    StrategicEdge(
        "SE-001",
        "runtime-debug-console",
        "console-core",
        "allowed",
        "required",
        "Runtime Debug Console reuses shared shell/registry/events from console-core.",
    ),
    StrategicEdge(
        "SE-002",
        "live-scene-composer",
        "console-core",
        "allowed",
        "required",
        "Live Scene Composer may reuse console-core infrastructure only.",
    ),
    StrategicEdge(
        "SE-003",
        "live-scene-composer",
        "runtime-mutation-bridge",
        "write-path",
        "required",
        "All write-capable composer actions must route through runtime-mutation-bridge.",
    ),
    StrategicEdge(
        "SE-004",
        "runtime-mutation-bridge",
        "pitch-runtime",
        "write-path",
        "required",
        "Bridge adapters mediate writes into pitch runtime state.",
    ),
    StrategicEdge(
        "SE-005",
        "runtime-mutation-bridge",
        "scene-studio",
        "write-path",
        "required",
        "Bridge adapters mediate writes into scene-studio state.",
    ),
    StrategicEdge(
        "SE-006",
        "pitch-runtime",
        "runtime-debug-console",
        "read-path",
        "allowed",
        "Pitch debug tooling mounts and feeds Runtime Debug Console.",
    ),
    StrategicEdge(
        "SE-007",
        "console-core",
        "scene-studio",
        "read-path",
        "allowed",
        "console-core diagnostics transport reads shared scene-studio diagnostics schema/messages.",
    ),
    StrategicEdge(
        "SE-008",
        "runtime-mutation-bridge",
        "live-scene-composer",
        "questionable",
        "temporary",
        "Current bridge contract imports SceneLookModelPatch type from composer. Keep under review.",
    ),
    StrategicEdge(
        "SE-009",
        "live-scene-composer",
        "runtime-debug-console",
        "forbidden",
        "forbidden",
        "Composer must not depend on Runtime Debug Console internals.",
    ),
    StrategicEdge(
        "SE-010",
        "runtime-debug-console",
        "live-scene-composer",
        "forbidden",
        "forbidden",
        "Runtime Debug Console must not register composer modules or editor logic.",
    ),
    StrategicEdge(
        "SE-011",
        "live-scene-composer",
        "pitch-runtime",
        "forbidden",
        "forbidden",
        "Composer direct runtime writes are forbidden bypasses outside the bridge.",
    ),
    StrategicEdge(
        "SE-012",
        "live-scene-composer",
        "scene-studio",
        "forbidden",
        "forbidden",
        "Composer direct scene-studio write coupling is forbidden; use bridge adapters.",
    ),
)


def normalize(path: Path) -> str:
    return str(path).replace("\\", "/")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def iter_source_files(base: Path) -> Iterable[Path]:
    if not base.exists():
        return []
    return (
        path
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS
    )


def extract_imports(source: str) -> List[str]:
    imports: List[str] = []
    for match in IMPORT_PATTERN.findall(source):
        candidate = match[0] or match[1] or match[2]
        if candidate:
            imports.append(candidate.replace("\\", "/").strip())
    return imports


def resolve_relative_import(source_file: Path, specifier: str) -> Optional[Path]:
    if not specifier.startswith("."):
        return None

    base = (source_file.parent / specifier).resolve()
    candidates: List[Path] = []

    if base.suffix:
        candidates.append(base)
    else:
        candidates.append(base)
        for ext in SOURCE_EXTENSIONS:
            candidates.append(base.with_suffix(ext))
            candidates.append(base / f"index{ext}")

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def classify_path_to_area(path: Path, boundary_roots: Dict[str, Path]) -> Optional[str]:
    for area, root in boundary_roots.items():
        try:
            path.relative_to(root)
            return area
        except ValueError:
            continue
    return None


def classify_specifier_to_area(specifier: str) -> Optional[str]:
    value = specifier.replace("\\", "/")
    if "components/dev-console/console-core" in value:
        return "console-core"
    if "components/dev-console/runtime-debug-console" in value:
        return "runtime-debug-console"
    if "components/dev-console/domains/inspect" in value:
        return "runtime-debug-console"
    if "components/dev-console/panels" in value:
        return "runtime-debug-console"
    if "components/dev-console/DevConsole" in value:
        return "runtime-debug-console"
    if "components/dev-console/DevConsoleContext" in value:
        return "runtime-debug-console"
    if "components/live-scene-composer" in value:
        return "live-scene-composer"
    if "components/runtime-mutation-bridge" in value:
        return "runtime-mutation-bridge"
    if "components/pitch" in value:
        return "pitch-runtime"
    if "components/scene-studio" in value:
        return "scene-studio"
    if "lib/scene-studio" in value:
        return "scene-studio"
    return None


def build_observed_edges(repo_root: Path) -> Dict[Tuple[str, str], List[Dict[str, str]]]:
    boundary_roots = {name: repo_root / rel for name, rel in BOUNDARY_PATHS.items()}
    edges: Dict[Tuple[str, str], List[Dict[str, str]]] = {}

    for source_area, source_root in boundary_roots.items():
        for file_path in iter_source_files(source_root):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            imports = extract_imports(text)
            for specifier in imports:
                target_area: Optional[str] = None
                resolved = resolve_relative_import(file_path, specifier)
                if resolved is not None:
                    target_area = classify_path_to_area(resolved, boundary_roots)
                if target_area is None:
                    target_area = classify_specifier_to_area(specifier)
                if target_area is None or target_area == source_area:
                    continue
                key = (source_area, target_area)
                bucket = edges.setdefault(key, [])
                if len(bucket) >= 16:
                    continue
                bucket.append(
                    {
                        "file": normalize(file_path.relative_to(repo_root)),
                        "specifier": specifier,
                    }
                )

    return edges


def strategic_edge_style(relationship: str) -> Dict[str, str]:
    if relationship == "allowed":
        return {"color": "#2ca02c", "style": "solid", "penwidth": "1.6", "legend": "allowed"}
    if relationship == "read-path":
        return {"color": "#1f77b4", "style": "solid", "penwidth": "1.8", "legend": "read-only"}
    if relationship == "write-path":
        return {"color": "#d62728", "style": "solid", "penwidth": "2.4", "legend": "write-path"}
    if relationship == "forbidden":
        return {"color": "#d62728", "style": "dashed", "penwidth": "1.7", "legend": "forbidden"}
    return {"color": "#ff7f0e", "style": "dotted", "penwidth": "1.5", "legend": "questionable"}


def build_boundaries_dot(observed_edges: Dict[Tuple[str, str], List[Dict[str, str]]]) -> str:
    node_defs = {
        "console-core": "console-core\\n(shared infrastructure only)",
        "runtime-debug-console": "runtime-debug-console\\n(runtime diagnostics product)",
        "live-scene-composer": "live-scene-composer\\n(authoring product boundary)",
        "runtime-mutation-bridge": "runtime-mutation-bridge\\n(controlled runtime write boundary)",
        "pitch-runtime": "pitch-runtime\\n(runtime surface)",
        "scene-studio": "scene-studio\\n(scene subsystem)",
    }

    lines: List[str] = []
    lines.append("digraph live_scene_composer_architecture_boundaries {")
    lines.append("  rankdir=TB;")
    lines.append('  graph [fontname="Segoe UI", fontsize=11, pad=0.25, nodesep=0.42, ranksep=0.8, splines=true];')
    lines.append('  node [shape=box, style="rounded,filled", fontname="Segoe UI", fontsize=10, fillcolor="#f7f9fc"];')
    lines.append('  edge [fontname="Segoe UI", fontsize=9];')
    lines.append("")
    lines.append('  "console-core" [fillcolor="#deecff", color="#1f77b4"];')
    lines.append('  "runtime-debug-console" [fillcolor="#e8f7e8", color="#2ca02c"];')
    lines.append('  "live-scene-composer" [fillcolor="#fff1dd", color="#ff7f0e"];')
    lines.append('  "runtime-mutation-bridge" [fillcolor="#ffe4e4", color="#d62728"];')
    lines.append('  "pitch-runtime" [fillcolor="#efe7fb", color="#9467bd"];')
    lines.append('  "scene-studio" [fillcolor="#f5ece8", color="#8c564b"];')
    lines.append("")
    for node, label in node_defs.items():
        lines.append(f'  "{node}" [label="{label}"];')
    lines.append("")

    for edge in STRATEGIC_EDGES:
        style = strategic_edge_style(edge.relationship)
        evidence = observed_edges.get((edge.source, edge.target), [])
        evidence_label = "observed" if evidence else "policy"
        label = f"{style['legend']} ({evidence_label})"
        lines.append(
            f'  "{edge.source}" -> "{edge.target}" '
            f'[label="{label}", color="{style["color"]}", style="{style["style"]}", penwidth={style["penwidth"]}];'
        )

    lines.append("}")
    return "\n".join(lines) + "\n"


def build_deps_dot(observed_edges: Dict[Tuple[str, str], List[Dict[str, str]]]) -> str:
    lines: List[str] = []
    lines.append("digraph live_scene_composer_architecture_deps {")
    lines.append("  rankdir=LR;")
    lines.append('  graph [fontname="Segoe UI", fontsize=11, pad=0.2, nodesep=0.34, ranksep=0.5, splines=true, overlap=false];')
    lines.append('  node [shape=box, style="rounded,filled", fontname="Segoe UI", fontsize=9, fillcolor="#fafafa"];')
    lines.append('  edge [fontname="Segoe UI", fontsize=8.5, arrowsize=0.7];')
    lines.append("")

    lines.append('  subgraph cluster_console_core { label="console-core"; color="#1f77b4"; style="rounded";')
    lines.append('    "cc.shell" [label="console-core-shell.tsx\\nPROTECTED", fillcolor="#deecff", peripheries=2];')
    lines.append('    "cc.registry" [label="console-core-registry.ts\\nPROTECTED", fillcolor="#deecff", peripheries=2];')
    lines.append('    "cc.events" [label="console-core-events.ts", fillcolor="#deecff"];')
    lines.append('    "cc.contracts" [label="console-core-contracts.ts\\nPROTECTED", fillcolor="#deecff", peripheries=2];')
    lines.append('    "cc.diagnostics" [label="console-core-diagnostics.ts", fillcolor="#deecff"];')
    lines.append('  }')

    lines.append('  subgraph cluster_runtime_debug { label="runtime-debug-console"; color="#2ca02c"; style="rounded";')
    lines.append('    "rd.console" [label="DevConsole.tsx", fillcolor="#e8f7e8"];')
    lines.append('    "rd.context" [label="DevConsoleContext.tsx", fillcolor="#e8f7e8"];')
    lines.append('    "rd.registry" [label="DevConsoleRegistry.tsx\\nPROTECTED seam", fillcolor="#e8f7e8", peripheries=2];')
    lines.append('    "rd.panels" [label="runtime-debug-console-panels.tsx", fillcolor="#e8f7e8"];')
    lines.append('    "rd.inspect" [label="domains/inspect/*", fillcolor="#e8f7e8"];')
    lines.append('  }')

    lines.append('  subgraph cluster_live_scene_composer { label="live-scene-composer"; color="#ff7f0e"; style="rounded";')
    lines.append('    "lsc.contracts" [label="contracts.ts", fillcolor="#fff1dd"];')
    lines.append('    "lsc.scene_model" [label="scene-look-model.ts\\nPROTECTED", fillcolor="#fff1dd", peripheries=2];')
    lines.append('    "lsc.provider" [label="LiveSceneComposerProvider\\nplanned seam", fillcolor="#fff7eb", style="rounded,dashed"];')
    lines.append('    "lsc.registry" [label="composer module registry\\nplanned seam", fillcolor="#fff7eb", style="rounded,dashed"];')
    lines.append('  }')

    lines.append('  subgraph cluster_bridge { label="runtime-mutation-bridge"; color="#d62728"; style="rounded";')
    lines.append('    "rmb.contract" [label="contract.ts\\nPROTECTED", fillcolor="#ffe4e4", peripheries=2];')
    lines.append('    "rmb.validators" [label="validateRuntimeMutationCommand", fillcolor="#ffe4e4"];')
    lines.append('    "rmb.apply" [label="applyRuntimeMutationThroughBridge", fillcolor="#ffe4e4"];')
    lines.append('    "rmb.adapters" [label="bridge adapters\\nplanned seam", fillcolor="#fff1f1", style="rounded,dashed"];')
    lines.append('  }')

    lines.append('  subgraph cluster_pitch_runtime { label="pitch-runtime"; color="#9467bd"; style="rounded";')
    lines.append('    "pr.mount" [label="pitch-layer-dev-tools.tsx\\nPROTECTED seam", fillcolor="#efe7fb", peripheries=2];')
    lines.append('    "pr.runtime_bridge" [label="pitch-scene-runtime-bridge.tsx", fillcolor="#efe7fb"];')
    lines.append('    "pr.stability" [label="pitch-dev-console-stability-helpers.tsx", fillcolor="#efe7fb"];')
    lines.append('  }')

    lines.append('  subgraph cluster_scene_studio { label="scene-studio"; color="#8c564b"; style="rounded";')
    lines.append('    "ss.page" [label="scene-studio-page.tsx", fillcolor="#f5ece8"];')
    lines.append('    "ss.editor" [label="scene-studio-editor.tsx", fillcolor="#f5ece8"];')
    lines.append('    "ss.state" [label="use-scene-studio-state.ts", fillcolor="#f5ece8"];')
    lines.append('  }')

    lines.append('  subgraph cluster_governance { label="governance"; color="#7f7f7f"; style="rounded";')
    lines.append('    "gov.guard" [label="tools/dev-console/architecture_guard.py\\nPROTECTED", fillcolor="#f3f3f3", peripheries=2];')
    lines.append('    "gov.policy" [label="tools/dev-console/dependency-policy.json\\nPROTECTED", fillcolor="#f3f3f3", peripheries=2];')
    lines.append('    "gov.protected_map" [label="protected-nodes-map.json", fillcolor="#f3f3f3"];')
    lines.append('  }')
    lines.append("")

    def add_edge(src: str, dst: str, label: str, relationship: str) -> None:
        style = strategic_edge_style(relationship)
        lines.append(
            f'  "{src}" -> "{dst}" [label="{label}", color="{style["color"]}", '
            f'style="{style["style"]}", penwidth={style["penwidth"]}];'
        )

    add_edge("rd.console", "cc.shell", "allowed shared shell", "allowed")
    add_edge("rd.registry", "cc.registry", "allowed registry primitives", "allowed")
    add_edge("rd.context", "cc.events", "diagnostics + action events", "read-path")
    add_edge("rd.panels", "rd.inspect", "runtime inspection panels", "allowed")
    add_edge("pr.mount", "rd.console", "mount runtime-debug console", "read-path")
    add_edge("pr.runtime_bridge", "cc.events", "snapshot transport", "read-path")
    add_edge("pr.stability", "cc.events", "heartbeat listeners", "read-path")
    add_edge("cc.diagnostics", "ss.state", "diagnostics schema linkage", "read-path")

    add_edge("lsc.provider", "cc.shell", "shared shell reuse (planned)", "allowed")
    add_edge("lsc.registry", "cc.registry", "module registration seam (planned)", "allowed")
    add_edge("lsc.provider", "rmb.contract", "bridge-only write path", "write-path")
    add_edge("rmb.contract", "rmb.validators", "command policy validation", "allowed")
    add_edge("rmb.validators", "rmb.apply", "validated execution path", "allowed")
    add_edge("rmb.apply", "rmb.adapters", "adapter mediation", "write-path")
    add_edge("rmb.adapters", "pr.runtime_bridge", "controlled runtime write", "write-path")
    add_edge("rmb.adapters", "ss.state", "controlled scene write", "write-path")

    add_edge("rmb.contract", "lsc.scene_model", "current type coupling (observed)", "questionable")
    add_edge("lsc.provider", "pr.runtime_bridge", "forbidden direct write bypass", "forbidden")
    add_edge("lsc.provider", "rd.registry", "forbidden sibling product import", "forbidden")
    add_edge("rd.registry", "lsc.registry", "forbidden composer registration in debug", "forbidden")

    observed_bridge_to_composer = observed_edges.get(("runtime-mutation-bridge", "live-scene-composer"), [])
    if observed_bridge_to_composer:
        add_edge("rmb.contract", "lsc.scene_model", "observed import evidence", "questionable")

    add_edge("gov.guard", "gov.policy", "enforced policy source", "allowed")
    add_edge("gov.protected_map", "gov.guard", "protected seam review context", "allowed")

    lines.append("}")
    return "\n".join(lines) + "\n"


def build_protected_nodes_map() -> Dict[str, object]:
    return {
        "generated_at": utc_now(),
        "nodes": [
            {
                "id": "PN-001",
                "name": "console-core registry seam",
                "path": "apps/keystone/components/dev-console/console-core/console-core-registry.ts",
                "rationale": "Controls panel registration composition across modules.",
                "risky_changes": [
                    "Changing registry merge semantics",
                    "Removing validation on duplicate panel IDs",
                    "Adding domain logic in shared infra",
                ],
                "required_validation": [
                    "python tools/dev-console/architecture_guard.py --repo-root . --strict",
                    "pnpm -C apps/keystone typecheck",
                ],
                "review_owners": ["console platform maintainers", "runtime debug maintainers"],
            },
            {
                "id": "PN-002",
                "name": "runtime-mutation bridge contract",
                "path": "apps/keystone/components/runtime-mutation-bridge/contract.ts",
                "rationale": "Defines the only sanctioned write-capable mutation command boundary.",
                "risky_changes": [
                    "Adding broad mutation commands without domain validation",
                    "Weakening safeMode constraints",
                    "Bypassing adapter mediation requirements",
                ],
                "required_validation": [
                    "pnpm -C apps/keystone test -- tests/dev-console-platform-architecture.test.ts",
                    "pnpm -C apps/keystone typecheck",
                ],
                "review_owners": ["composer platform maintainers", "runtime integration maintainers"],
            },
            {
                "id": "PN-003",
                "name": "composer scene look model",
                "path": "apps/keystone/components/live-scene-composer/scene-look-model.ts",
                "rationale": "Canonical visual model normalization boundary for future composer operations.",
                "risky_changes": [
                    "Changing enum values without migration",
                    "Breaking normalization semantics",
                    "Mutating runtime directly from model helpers",
                ],
                "required_validation": [
                    "pnpm -C apps/keystone typecheck",
                    "python tools/dev-console/architecture_guard.py --repo-root . --strict",
                ],
                "review_owners": ["composer maintainers", "design systems maintainers"],
            },
            {
                "id": "PN-004",
                "name": "runtime mount seam",
                "path": "apps/keystone/components/pitch/debug/pitch-layer-dev-tools.tsx",
                "rationale": "Primary runtime attachment point for debug tooling and bridge helpers.",
                "risky_changes": [
                    "Reintroducing scene binding couplings",
                    "Adding composer registration in debug path",
                    "Dropping runtime invariants layer",
                ],
                "required_validation": [
                    "pnpm -C apps/keystone test -- tests/pitch-layer-dev-tools-gating.test.tsx",
                    "python tools/dev-console/architecture_guard.py --repo-root . --strict",
                ],
                "review_owners": ["runtime debug maintainers", "pitch runtime maintainers"],
            },
            {
                "id": "PN-005",
                "name": "dependency policy and guard rules",
                "path": "tools/dev-console/dependency-policy.json",
                "rationale": "Single source of truth for allowed/forbidden architecture dependencies.",
                "risky_changes": [
                    "Loosening forbidden boundaries without ADR",
                    "Adding exceptions not enforced in guard",
                    "Divergence between policy and docs",
                ],
                "required_validation": [
                    "python tools/dev-console/architecture_guard.py --repo-root . --strict",
                    "python tools/live-scene-composer/validate_docs_architecture_guard.py --repo-root . --docs-root docs/live-scene-composer --write-report",
                ],
                "review_owners": ["architecture governance maintainers"],
            },
        ],
    }


def build_dependency_inventory(
    repo_root: Path,
    observed_edges: Dict[Tuple[str, str], List[Dict[str, str]]],
) -> Dict[str, object]:
    boundary_status = []
    for area, rel in BOUNDARY_PATHS.items():
        area_root = repo_root / rel
        file_count = sum(1 for _ in iter_source_files(area_root))
        boundary_status.append(
            {
                "area": area,
                "path": rel,
                "exists": area_root.exists(),
                "source_file_count": file_count,
            }
        )

    edges: List[Dict[str, object]] = []

    strategic_lookup = {(edge.source, edge.target): edge for edge in STRATEGIC_EDGES}
    for edge in STRATEGIC_EDGES:
        evidence = observed_edges.get((edge.source, edge.target), [])
        if evidence:
            evidence_type = "observed+policy"
        else:
            evidence_type = "policy-only"
        edges.append(
            {
                "id": edge.edge_id,
                "from": edge.source,
                "to": edge.target,
                "relationship": edge.relationship,
                "policy_status": edge.policy_status,
                "evidence_type": evidence_type,
                "write_path": edge.relationship == "write-path",
                "note": edge.note,
                "evidence": evidence,
            }
        )

    incidental_counter = 1
    for (source, target), evidence in sorted(observed_edges.items()):
        if (source, target) in strategic_lookup:
            continue
        edges.append(
            {
                "id": f"OE-{incidental_counter:03d}",
                "from": source,
                "to": target,
                "relationship": "questionable",
                "policy_status": "review",
                "evidence_type": "observed",
                "write_path": False,
                "note": "Observed architecture-relevant edge not in strategic map; review if intentional.",
                "evidence": evidence,
            }
        )
        incidental_counter += 1

    return {
        "generated_at": utc_now(),
        "repo_root": normalize(repo_root),
        "selection_scope": "Architecture-relevant boundary edges only (not full import dump).",
        "boundary_status": boundary_status,
        "edges": edges,
        "observed_edge_count": len(observed_edges),
        "strategic_edge_count": len(STRATEGIC_EDGES),
    }


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def maybe_render_svg(dot_path: Path) -> Optional[Path]:
    dot_binary = shutil.which("dot")
    if dot_binary is None:
        return None
    svg_path = dot_path.with_suffix(".svg")
    subprocess.run([dot_binary, "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)
    return svg_path


def build_manifest(output_dir: Path, generated: Dict[str, Dict[str, str]]) -> Dict[str, object]:
    files = []
    for file_name, info in generated.items():
        artifact_path = output_dir / file_name
        files.append(
            {
                "file": file_name,
                "purpose": info["purpose"],
                "generation_notes": info["generation_notes"],
                "exists": artifact_path.exists(),
            }
        )
    return {
        "generated_at": utc_now(),
        "output_dir": normalize(output_dir),
        "generator": "tools/live-scene-composer/generate_architecture_artifacts.py",
        "artifacts": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Live Scene Composer architecture artifacts package.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument(
        "--output-dir",
        default="docs/live-scene-composer/architecture-artifacts",
        help="Output artifacts directory",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    observed_edges = build_observed_edges(repo_root)
    boundaries_dot = build_boundaries_dot(observed_edges)
    deps_dot = build_deps_dot(observed_edges)
    inventory = build_dependency_inventory(repo_root, observed_edges)
    protected_nodes = build_protected_nodes_map()

    boundaries_dot_path = output_dir / "live-scene-composer-architecture-boundaries.dot"
    deps_dot_path = output_dir / "live-scene-composer-architecture-deps.dot"
    boundaries_dot_path.write_text(boundaries_dot, encoding="utf-8")
    deps_dot_path.write_text(deps_dot, encoding="utf-8")

    write_json(output_dir / "dependency-inventory.json", inventory)
    write_json(output_dir / "protected-nodes-map.json", protected_nodes)

    rendered = {}
    boundaries_svg = maybe_render_svg(boundaries_dot_path)
    deps_svg = maybe_render_svg(deps_dot_path)
    if boundaries_svg is not None:
        rendered["live-scene-composer-architecture-boundaries.svg"] = {
            "purpose": "Rendered strategic architecture boundaries graph.",
            "generation_notes": "Generated with Graphviz dot from strategic .dot source.",
        }
    if deps_svg is not None:
        rendered["live-scene-composer-architecture-deps.svg"] = {
            "purpose": "Rendered tactical architecture dependencies graph.",
            "generation_notes": "Generated with Graphviz dot from tactical .dot source.",
        }

    generated_manifest_items: Dict[str, Dict[str, str]] = {
        "README.md": {
            "purpose": "Human guide to architecture artifacts package.",
            "generation_notes": "Maintained manually; reviewed alongside generated outputs.",
        },
        "GRAPH_LEGEND.md": {
            "purpose": "Legend defining node/edge semantics and risk codes.",
            "generation_notes": "Maintained manually; used by humans and tooling references.",
        },
        "live-scene-composer-architecture-boundaries.dot": {
            "purpose": "Strategic top-level architecture boundaries graph.",
            "generation_notes": "Generated from strategic edge model plus observed edge evidence.",
        },
        "live-scene-composer-architecture-deps.dot": {
            "purpose": "Tactical dependency and seam graph.",
            "generation_notes": "Generated from tactical seam model plus observed edge evidence.",
        },
        "dependency-inventory.json": {
            "purpose": "Machine-readable architecture-relevant edge inventory.",
            "generation_notes": "Derived from import scanning and strategic boundary model.",
        },
        "protected-nodes-map.json": {
            "purpose": "Machine-readable protected node metadata.",
            "generation_notes": "Generated from maintained protected seam map.",
        },
        **rendered,
    }

    manifest = build_manifest(output_dir, generated_manifest_items)
    write_json(output_dir / "ARTIFACT_MANIFEST.json", manifest)

    print("Generated architecture artifacts:")
    for name in sorted(generated_manifest_items):
        print(f"  - {normalize((output_dir / name).relative_to(repo_root))}")
    print(f"  - {normalize((output_dir / 'ARTIFACT_MANIFEST.json').relative_to(repo_root))}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
