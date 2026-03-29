
#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import shutil
import zipfile
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
import sys

try:
    from graphviz import Digraph
except Exception as exc:  # pragma: no cover - import guard
    raise RuntimeError(
        "No se pudo importar graphviz. Instala el paquete Python 'graphviz' "
        "y asegúrate de tener Graphviz CLI disponible en PATH."
    ) from exc


DEFAULT_REPO_PATH = Path(r"F:\repos\hitech-os")
DEFAULT_TOOLS_ROOT = DEFAULT_REPO_PATH / "tools" / "graphviz"
DEFAULT_OUTPUT_ROOT = DEFAULT_TOOLS_ROOT / "graphs"
DEFAULT_STATE_FILE = DEFAULT_TOOLS_ROOT / ".graphviz_state.json"
DEFAULT_MANIFEST_FILE = DEFAULT_TOOLS_ROOT / ".graphviz_manifest.json"
DEFAULT_INDEX_FILE = DEFAULT_OUTPUT_ROOT / "index.html"
DEFAULT_SCOPE_INDEX_FILE = DEFAULT_OUTPUT_ROOT / "scope_index.html"
DEFAULT_RUN_SUMMARY_FILE = DEFAULT_OUTPUT_ROOT / "run_summary.json"
DEFAULT_BACKUP_ROOT = Path(r"F:\OneDrive\Descargas chido\10.Obsoleto\Graphos_Obs")

INCLUDE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py",
}
EXCLUDE_DIRS = {
    ".git", ".next", ".turbo", ".venv", "venv", "__pycache__",
    "node_modules", "dist", "build", "coverage", "tmp", "temp",
    "out", ".cache", ".idea", ".vscode",
}
EXCLUDE_FILE_SUFFIXES = {
    ".d.ts", ".min.js", ".min.css", ".map", ".snap",
    ".stories.ts", ".stories.tsx", ".stories.js", ".stories.jsx",
    ".story.ts", ".story.tsx", ".story.js", ".story.jsx",
    ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx",
    ".test.ts", ".test.tsx", ".test.js", ".test.jsx",
    ".spec.py", ".test.py",
}
EXCLUDE_PATH_PARTS = {
    "__mocks__", "__fixtures__", "__snapshots__", "fixtures", "mocks", "mock",
    "generated", "gen", "docs",
}

JS_IMPORT_FROM = re.compile(r'import\s+[\s\S]*?\s+from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE)
JS_IMPORT_BARE = re.compile(r'(?m)^\s*import\s+[\'"]([^\'"]+)[\'"]')
JS_REQUIRE = re.compile(r'require\(\s*[\'"]([^\'"]+)[\'"]\s*\)')
JS_DYNAMIC_IMPORT = re.compile(r'import\(\s*[\'"]([^\'"]+)[\'"]\s*\)')
PY_FROM_IMPORT = re.compile(r'(?m)^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+')
PY_IMPORT = re.compile(r'(?m)^\s*import\s+([A-Za-z0-9_\. ,]+)')

FOCUS_PREFIXES = ("apps/", "services/", "packages/", "tools/")
NOISE_PREFIXES = (
    ".agents/",
    ".codex/",
    "_attic/",
    "_reports/",
    "artifacts/",
    "tools/_local/",
    "tools/codex/worktrees/",
    "tools/codex/runs/",
    "tools/codex/_triage/",
    "docs/",
)

SVG_BACKGROUND = "transparent"
GRAPH_TITLE_COLOR = "#E6F6FF"
GRAPH_TEXT_COLOR = "#CFE9F6"
GRAPH_EDGE_COLOR = "#8BE9FD"
GRAPH_EDGE_GLOW = "#7DD3FC"
FILE_NODE_FILL = "#0F2233"
FILE_NODE_FILL_2 = "#123149"
FILE_NODE_BORDER = "#67E8F9"
FILE_NODE_TEXT = "#ECFEFF"
EXTERNAL_NODE_FILL = "#1B2338"
EXTERNAL_NODE_FILL_2 = "#23304C"
EXTERNAL_NODE_BORDER = "#93C5FD"
EXTERNAL_NODE_TEXT = "#DBEAFE"

RENDER_STYLE_VERSION = "full-refresh-backup-filtered-v1"


@dataclass(slots=True)
class GraphRunConfig:
    repo_path: Path = DEFAULT_REPO_PATH
    tools_root: Path = DEFAULT_TOOLS_ROOT
    output_root: Path = DEFAULT_OUTPUT_ROOT
    state_file: Path = DEFAULT_STATE_FILE
    manifest_file: Path = DEFAULT_MANIFEST_FILE
    index_file: Path = DEFAULT_INDEX_FILE
    scope_index_file: Path = DEFAULT_SCOPE_INDEX_FILE
    run_summary_file: Path = DEFAULT_RUN_SUMMARY_FILE
    backup_root: Path = DEFAULT_BACKUP_ROOT
    backup_prefix: str = "repo_graphs"
    output_label: str = "repo_graphs"
    include_extensions: set[str] = field(default_factory=lambda: set(INCLUDE_EXTENSIONS))
    exclude_dirs: set[str] = field(default_factory=lambda: set(EXCLUDE_DIRS))
    exclude_file_suffixes: set[str] = field(default_factory=lambda: set(EXCLUDE_FILE_SUFFIXES))
    exclude_path_parts: set[str] = field(default_factory=lambda: set(EXCLUDE_PATH_PARTS))
    include_external_packages: bool = False
    internal_only: bool = True
    only_connected_folders: bool = True
    only_connected_files: bool = True
    min_edge_count: int = 1
    max_edges_per_folder: int = 700
    max_label_length: int = 84
    open_index_on_finish: bool = False
    pause_on_exit: bool = False
    include_path_prefixes: tuple[str, ...] = ()
    ignore_path_prefixes: tuple[str, ...] = ()
    alias_roots: tuple[str, ...] = ("src", "apps", "services", "packages", "tools", "lib", "components")
    extra_metadata: dict[str, object] = field(default_factory=dict)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def format_progress(current: int, total: int, width: int = 28) -> str:
    if total <= 0:
        total = 1
    ratio = max(0.0, min(1.0, current / total))
    filled = int(ratio * width)
    bar = "#" * filled + "-" * (width - filled)
    percent = int(round(ratio * 100))
    return f"[{bar}] {percent:3d}%"


def safe_print(*args, **kwargs) -> None:
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        clean = " ".join(str(arg).encode("ascii", "replace").decode("ascii") for arg in args)
        print(clean, **kwargs)


def is_windows() -> bool:
    return os.name == "nt"


def open_path(path: Path) -> None:
    if not is_windows():
        return
    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
    except Exception:
        pass


def maybe_pause(message: str, enabled: bool) -> None:
    if not enabled:
        return
    if not sys.stdin or not sys.stdin.isatty():
        return
    try:
        input(message)
    except EOFError:
        return


def hash_text(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8", errors="ignore")).hexdigest()


def slugify_folder(rel_folder: str) -> str:
    if rel_folder in (".", ""):
        return "root"
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", rel_folder.replace("\\", "_").replace("/", "_"))
    cleaned = cleaned.strip("._")
    return cleaned or "unnamed"


def stable_folder_id(rel_folder: str) -> str:
    slug = slugify_folder(rel_folder)
    short_hash = hash_text(rel_folder)[:10]
    return f"{slug}__{short_hash}"


def node_id(label: str) -> str:
    return "n_" + hash_text(label)


def normalize_rel_path(path: str | Path) -> str:
    return str(path).replace("\\", "/").strip("/")


def truncate_label(value: str, max_len: int = 84) -> str:
    value = value.replace("\\", "/")
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="strict")
        except Exception:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def should_skip_dir_path(path: Path, config: GraphRunConfig) -> bool:
    parts = {part.lower() for part in path.parts}
    return any(item.lower() in parts for item in config.exclude_dirs)


def should_skip_file(path: Path, config: GraphRunConfig) -> bool:
    if path.suffix.lower() not in config.include_extensions:
        return True

    lower_name = path.name.lower()
    if any(lower_name.endswith(sfx.lower()) for sfx in config.exclude_file_suffixes):
        return True

    lowered_parts = {part.lower() for part in path.parts}
    if any(item.lower() in lowered_parts for item in config.exclude_path_parts):
        return True

    return False


def matches_prefix_filters(rel_path: str, config: GraphRunConfig) -> bool:
    rel_path = normalize_rel_path(rel_path)

    if config.include_path_prefixes:
        if not any(rel_path.startswith(prefix.rstrip("/") + "/") or rel_path == prefix.rstrip("/")
                   for prefix in config.include_path_prefixes):
            return False

    if config.ignore_path_prefixes:
        if any(rel_path.startswith(prefix.rstrip("/") + "/") or rel_path == prefix.rstrip("/")
               for prefix in config.ignore_path_prefixes):
            return False

    return True


def iter_repo_files(config: GraphRunConfig) -> list[Path]:
    repo_path = config.repo_path
    files: list[Path] = []

    for root, dirs, filenames in os.walk(repo_path):
        root_path = Path(root)
        dirs[:] = [dirname for dirname in dirs if dirname not in config.exclude_dirs]
        if should_skip_dir_path(root_path, config):
            continue

        for filename in filenames:
            path = root_path / filename
            try:
                rel_path = path.relative_to(repo_path).as_posix()
            except Exception:
                continue

            if not matches_prefix_filters(rel_path, config):
                continue
            if should_skip_file(path, config):
                continue
            files.append(path)

    return files


def collect_js_imports(text: str) -> list[str]:
    imports: list[str] = []
    imports.extend(JS_IMPORT_FROM.findall(text))
    imports.extend(JS_IMPORT_BARE.findall(text))
    imports.extend(JS_REQUIRE.findall(text))
    imports.extend(JS_DYNAMIC_IMPORT.findall(text))
    return [item.strip() for item in imports if item.strip()]


def collect_python_imports(text: str) -> list[str]:
    imports: list[str] = []
    imports.extend(PY_FROM_IMPORT.findall(text))
    for raw in PY_IMPORT.findall(text):
        for part in raw.split(","):
            candidate = part.strip()
            if candidate:
                imports.append(candidate)
    return imports


def collect_imports(path: Path, text: str) -> list[str]:
    ext = path.suffix.lower()
    if ext == ".py":
        return collect_python_imports(text)
    return collect_js_imports(text)


def is_external_import(spec: str) -> bool:
    if not spec:
        return False
    if spec.startswith((".", "/", "@/","~/")):
        return False
    if spec.startswith("pkg::"):
        return True
    return True


def is_within_repo(path: Path, repo_path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_path.resolve())
        return True
    except Exception:
        return False


def _candidate_internal_paths(base: Path, extensions: Iterable[str]) -> list[Path]:
    candidates = [base]
    for ext in extensions:
        candidates.append(base.with_suffix(ext))
    for ext in extensions:
        candidates.append(base / f"index{ext}")
    return candidates


def resolve_js_specifier(spec: str, current_file: Path, config: GraphRunConfig) -> Path | None:
    repo_path = config.repo_path
    spec = spec.strip()

    if spec.startswith("."):
        base = (current_file.parent / spec).resolve()
        for candidate in _candidate_internal_paths(base, config.include_extensions):
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    alias_roots: list[Path] = []
    spec_tail = spec
    if spec.startswith("@/"):
        spec_tail = spec[2:]
        alias_roots = [repo_path / root for root in config.alias_roots] + [repo_path]
    elif spec.startswith("~/"):
        spec_tail = spec[2:]
        alias_roots = [repo_path / "src", repo_path]
    elif spec.startswith("/"):
        spec_tail = spec[1:]
        alias_roots = [repo_path]
    else:
        return None

    for root in alias_roots:
        base = (root / spec_tail).resolve()
        for candidate in _candidate_internal_paths(base, config.include_extensions):
            if candidate.exists() and candidate.is_file():
                return candidate

    return None


def resolve_python_specifier(spec: str, current_file: Path, config: GraphRunConfig) -> Path | None:
    repo_path = config.repo_path
    spec = spec.strip()
    if not spec:
        return None

    if spec.startswith("."):
        dot_count = len(spec) - len(spec.lstrip("."))
        remainder = spec[dot_count:]
        parent = current_file.parent
        for _ in range(max(dot_count - 1, 0)):
            parent = parent.parent
        base = parent / remainder.replace(".", "/") if remainder else parent
        for candidate in _candidate_internal_paths(base, {".py"}):
            if candidate.exists() and candidate.is_file():
                return candidate
        init_candidate = base / "__init__.py"
        if init_candidate.exists():
            return init_candidate
        return None

    dotted = spec.replace(".", "/")
    roots = [repo_path] + [repo_path / root for root in config.alias_roots]
    for root in roots:
        base = root / dotted
        for candidate in _candidate_internal_paths(base, {".py"}):
            if candidate.exists() and candidate.is_file():
                return candidate
        init_candidate = base / "__init__.py"
        if init_candidate.exists():
            return init_candidate
    return None


def resolve_specifier(spec: str, current_file: Path, config: GraphRunConfig) -> Path | None:
    if current_file.suffix.lower() == ".py":
        return resolve_python_specifier(spec, current_file, config)
    return resolve_js_specifier(spec, current_file, config)


def classify_scope(rel_folder: str) -> str:
    rel_folder = normalize_rel_path(rel_folder)
    for prefix in FOCUS_PREFIXES:
        if rel_folder.startswith(prefix):
            return prefix.rstrip("/")
    if rel_folder == ".":
        return "root"
    return rel_folder.split("/", 1)[0] if "/" in rel_folder else rel_folder


def is_noise_folder(rel_folder: str) -> bool:
    rel_folder = normalize_rel_path(rel_folder)
    return any(rel_folder.startswith(prefix) for prefix in NOISE_PREFIXES)


def add_node(graph: Digraph, label: str, kind: str, max_label_length: int) -> str:
    nid = node_id(label)
    display_label = truncate_label(label, max_label_length)

    if kind == "file":
        graph.node(
            nid,
            label=display_label,
            shape="box",
            style="rounded,filled",
            fillcolor=f"{FILE_NODE_FILL}:{FILE_NODE_FILL_2}",
            gradientangle="90",
            color=FILE_NODE_BORDER,
            fontcolor=FILE_NODE_TEXT,
            penwidth="1.45",
            margin="0.18,0.11",
        )
    elif kind == "external":
        graph.node(
            nid,
            label=display_label,
            shape="ellipse",
            style="filled,dashed",
            fillcolor=f"{EXTERNAL_NODE_FILL}:{EXTERNAL_NODE_FILL_2}",
            gradientangle="90",
            color=EXTERNAL_NODE_BORDER,
            fontcolor=EXTERNAL_NODE_TEXT,
            penwidth="1.25",
            margin="0.14,0.09",
        )
    else:
        graph.node(nid, label=display_label, color=GRAPH_TEXT_COLOR, fontcolor=GRAPH_TEXT_COLOR)

    return nid


def file_fingerprint(path: Path) -> str:
    try:
        stat = path.stat()
        seed = f"{path}:{stat.st_size}:{stat.st_mtime_ns}"
    except Exception:
        seed = str(path)
    return hash_text(seed)


def build_folder_payloads(files: list[Path], config: GraphRunConfig) -> dict[str, dict]:
    repo_path = config.repo_path
    payloads: dict[str, dict] = {}

    for file_path in files:
        rel_file = file_path.relative_to(repo_path).as_posix()
        rel_folder = file_path.parent.relative_to(repo_path).as_posix() if file_path.parent != repo_path else "."

        bucket = payloads.setdefault(
            rel_folder,
            {
                "folder": rel_folder,
                "scope": classify_scope(rel_folder),
                "is_noise": is_noise_folder(rel_folder),
                "source_files": set(),
                "nodes": set(),
                "edges": set(),
                "external_nodes": set(),
                "fingerprints": {},
            },
        )
        bucket["source_files"].add(rel_file)
        bucket["fingerprints"][rel_file] = file_fingerprint(file_path)

        try:
            text = read_text(file_path)
        except Exception:
            continue

        imports = collect_imports(file_path, text)
        for raw_spec in imports:
            spec = raw_spec.strip()
            if not spec:
                continue

            resolved = resolve_specifier(spec, file_path, config)

            if resolved and resolved.exists() and is_within_repo(resolved, repo_path):
                try:
                    target_rel = resolved.resolve().relative_to(repo_path.resolve()).as_posix()
                except Exception:
                    continue
                bucket["nodes"].add(rel_file)
                bucket["nodes"].add(target_rel)
                bucket["edges"].add((rel_file, target_rel))
            elif not config.internal_only and is_external_import(spec):
                pkg_node = f"pkg::{spec}"
                bucket["nodes"].add(rel_file)
                bucket["nodes"].add(pkg_node)
                bucket["external_nodes"].add(pkg_node)
                bucket["edges"].add((rel_file, pkg_node))

    return filter_payloads(payloads, config)


def filter_payloads(payloads: dict[str, dict], config: GraphRunConfig) -> dict[str, dict]:
    filtered: dict[str, dict] = {}
    for rel_folder, payload in payloads.items():
        edge_count = len(payload["edges"])
        if config.only_connected_folders and edge_count < config.min_edge_count:
            continue

        if config.only_connected_files:
            connected_nodes = {node for edge in payload["edges"] for node in edge}
            payload["nodes"] = connected_nodes
        else:
            payload["nodes"].update(payload["source_files"])

        if not payload["nodes"]:
            continue

        filtered[rel_folder] = payload

    return filtered


def compute_folder_digest(payload: dict) -> str:
    digest_seed = json.dumps(
        {
            "folder": payload["folder"],
            "scope": payload["scope"],
            "source_files": sorted(payload["source_files"]),
            "nodes": sorted(payload["nodes"]),
            "edges": sorted(payload["edges"]),
            "externals": sorted(payload["external_nodes"]),
            "fingerprints": payload["fingerprints"],
            "render_style_version": RENDER_STYLE_VERSION,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hash_text(digest_seed)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_existing_outputs(config: GraphRunConfig, run_id: str) -> Path | None:
    config.backup_root.mkdir(parents=True, exist_ok=True)

    has_graph_outputs = config.output_root.exists() and any(config.output_root.iterdir())
    has_metadata = any(path.exists() for path in (config.state_file, config.manifest_file))

    if not has_graph_outputs and not has_metadata:
        return None

    backup_zip = config.backup_root / f"{config.backup_prefix}_{run_id}.zip"

    with zipfile.ZipFile(backup_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        if config.output_root.exists():
            for file_path in config.output_root.rglob("*"):
                if file_path.is_file():
                    arcname = Path("graphs") / file_path.relative_to(config.output_root)
                    zf.write(file_path, arcname.as_posix())

        for metadata_path in (config.state_file, config.manifest_file):
            if metadata_path.exists():
                zf.write(metadata_path, metadata_path.name)

    return backup_zip


def clean_output_targets(config: GraphRunConfig) -> None:
    if config.output_root.exists():
        shutil.rmtree(config.output_root)
    config.output_root.mkdir(parents=True, exist_ok=True)

    for metadata_path in (config.state_file, config.manifest_file):
        if metadata_path.exists():
            metadata_path.unlink()


def render_folder_graph(display_index: int, payload: dict, config: GraphRunConfig) -> dict:
    rel_folder = payload["folder"]
    folder_id = stable_folder_id(rel_folder)
    out_dir = config.output_root / folder_id
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = Digraph(name=f"folder_{folder_id}")
    graph.attr(
        rankdir="LR",
        splines="true",
        overlap="false",
        bgcolor=SVG_BACKGROUND,
        pad="0.34",
        margin="0.12",
        nodesep="0.42",
        ranksep="0.82",
        outputorder="edgesfirst",
    )
    graph.attr("graph", color=GRAPH_TEXT_COLOR, fontname="Segoe UI", fontsize="18", fontcolor=GRAPH_TITLE_COLOR)
    graph.attr("node", fontname="Segoe UI", fontsize="10", color=FILE_NODE_BORDER, fontcolor=FILE_NODE_TEXT)
    graph.attr(
        "edge",
        fontname="Segoe UI",
        fontsize="9",
        color=GRAPH_EDGE_COLOR,
        fontcolor=GRAPH_EDGE_GLOW,
        penwidth="1.35",
        arrowsize="0.78",
    )
    graph.attr(label=rel_folder, labelloc="t", fontsize="18", fontname="Segoe UI Semibold", fontcolor=GRAPH_TITLE_COLOR)

    file_nodes = sorted(node for node in payload["nodes"] if not node.startswith("pkg::"))
    external_nodes = sorted(node for node in payload["nodes"] if node.startswith("pkg::"))
    limited_edges = sorted(payload["edges"])[: config.max_edges_per_folder]

    for rel_file in file_nodes:
        add_node(graph, rel_file, "file", config.max_label_length)
    if config.include_external_packages and not config.internal_only:
        for pkg in external_nodes:
            add_node(graph, pkg, "external", config.max_label_length)

    for source, target in limited_edges:
        if target.startswith("pkg::") and (config.internal_only or not config.include_external_packages):
            continue
        graph.edge(node_id(source), node_id(target))

    dot_path = out_dir / "graph.dot"
    svg_base = out_dir / "graph"
    graph.save(str(dot_path))
    graph.render(str(svg_base), format="svg", cleanup=True)

    summary = {
        "folder_id": folder_id,
        "folder": rel_folder,
        "display_index": display_index,
        "scope": payload["scope"],
        "is_noise": payload["is_noise"],
        "source_file_count": len(payload["source_files"]),
        "connected_node_count": len(payload["nodes"]),
        "edge_count_total": len(payload["edges"]),
        "edge_count_rendered": len(limited_edges),
        "external_count": len(payload["external_nodes"]),
        "rendered_at": now_utc(),
        "render_style_version": RENDER_STYLE_VERSION,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.txt").write_text(
        "\n".join(
            [
                f"Folder: {rel_folder}",
                f"Folder ID: {folder_id}",
                f"Display index: {display_index:03d}",
                f"Source files: {len(payload['source_files'])}",
                f"Connected nodes: {len(payload['nodes'])}",
                f"Edges total: {len(payload['edges'])}",
                f"Edges rendered: {len(limited_edges)}",
                f"External nodes: {len(payload['external_nodes'])}",
                f"Rendered at: {now_utc()}",
                "",
                "Connected nodes in this folder graph:",
                *file_nodes[:800],
            ]
        ),
        encoding="utf-8",
    )

    digest = compute_folder_digest(payload)
    return {
        "folder": rel_folder,
        "folder_id": folder_id,
        "dir_name": folder_id,
        "scope": payload["scope"],
        "is_noise": payload["is_noise"],
        "source_file_count": len(payload["source_files"]),
        "connected_node_count": len(payload["nodes"]),
        "edge_count_total": len(payload["edges"]),
        "edge_count_rendered": len(limited_edges),
        "external_count": len(payload["external_nodes"]),
        "digest": digest,
        "graph_svg": f"./{folder_id}/graph.svg",
        "summary_json": f"./{folder_id}/summary.json",
        "last_seen_at": now_utc(),
    }


def write_json(path: Path, payload: dict | list) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def build_manifest(rows: list[dict], config: GraphRunConfig, run_id: str, backup_zip: Path | None) -> dict:
    folders = {}
    for index, row in enumerate(rows, start=1):
        row_copy = dict(row)
        row_copy["display_index"] = index
        folders[row["folder"]] = row_copy

    return {
        "version": 3,
        "mode": "full_refresh_backup",
        "run_id": run_id,
        "generated_at": now_utc(),
        "repo_path": str(config.repo_path),
        "output_root": str(config.output_root),
        "backup_root": str(config.backup_root),
        "backup_zip": str(backup_zip) if backup_zip else None,
        "only_connected_folders": config.only_connected_folders,
        "only_connected_files": config.only_connected_files,
        "min_edge_count": config.min_edge_count,
        "render_style_version": RENDER_STYLE_VERSION,
        "folders": folders,
    }


def build_state(rows: list[dict], run_id: str) -> dict:
    return {
        "version": 3,
        "mode": "full_refresh_backup",
        "run_id": run_id,
        "generated_at": now_utc(),
        "folders": {
            row["folder"]: {
                "digest": row["digest"],
                "folder_id": row["folder_id"],
                "dir_name": row["dir_name"],
                "last_index": index,
                "last_seen_at": row["last_seen_at"],
            }
            for index, row in enumerate(rows, start=1)
        },
    }


def write_master_index(rows: list[dict], config: GraphRunConfig, run_id: str, backup_zip: Path | None) -> None:
    count_noise = sum(1 for row in rows if row["is_noise"])
    count_focus = len(rows) - count_noise
    backup_label = html.escape(str(backup_zip)) if backup_zip else "sin backup previo"

    cards = []
    for index, row in enumerate(rows, start=1):
        cards.append(
            f"""
            <tr>
              <td>{index:03d}</td>
              <td>{html.escape(row['folder'])}</td>
              <td>{html.escape(row['scope'])}</td>
              <td>{row['source_file_count']}</td>
              <td>{row['connected_node_count']}</td>
              <td>{row['edge_count_total']}</td>
              <td><a href="./{html.escape(row['dir_name'])}/graph.svg">graph.svg</a></td>
              <td><a href="./{html.escape(row['dir_name'])}/summary.json">summary.json</a></td>
            </tr>
            """
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HITECH Graphviz Index</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; background: #08131f; color: #e6f6ff; }}
    a {{ color: #7dd3fc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .panel {{ background: #102133; border: 1px solid #1d3952; border-radius: 16px; padding: 16px 18px; margin-bottom: 16px; }}
    .muted {{ color: #8eabc0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #18334a; padding: 9px 8px; text-align: left; vertical-align: top; }}
    th {{ color: #93c5fd; }}
  </style>
</head>
<body>
  <div class="panel">
    <h1>HITECH Graphviz Index</h1>
    <p class="muted">Corrida full refresh con backup previo. No se preservan históricos dentro del output activo.</p>
    <p>run_id={html.escape(run_id)} | folders={len(rows)} | focus={count_focus} | noise={count_noise}</p>
    <p>backup={backup_label}</p>
  </div>
  <div class="panel">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>folder</th>
          <th>scope</th>
          <th>source_files</th>
          <th>connected_nodes</th>
          <th>edges</th>
          <th>graph</th>
          <th>summary</th>
        </tr>
      </thead>
      <tbody>
        {''.join(cards)}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
    config.index_file.write_text(document, encoding="utf-8")


def run_graph_refresh(config: GraphRunConfig) -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    backup_zip = backup_existing_outputs(config, run_id)
    clean_output_targets(config)

    files = iter_repo_files(config)
    payloads = build_folder_payloads(files, config)

    rows: list[dict] = []
    ordered_folders = sorted(payloads.keys())
    total_folders = len(ordered_folders)
    for index, rel_folder in enumerate(ordered_folders, start=1):
        row = render_folder_graph(index, payloads[rel_folder], config)
        rows.append(row)
        progress = format_progress(index, total_folders)
        safe_print(
            f"{progress} [{index:04d}/{total_folders:04d}] "
            f"{rel_folder} -> {row['dir_name']} ({row['edge_count_total']} edges)"
        )

    manifest = build_manifest(rows, config, run_id, backup_zip)
    state = build_state(rows, run_id)

    write_json(config.manifest_file, manifest)
    write_json(config.state_file, state)
    write_master_index(rows, config, run_id, backup_zip)

    run_summary = {
        "version": 1,
        "run_id": run_id,
        "generated_at": now_utc(),
        "repo_path": str(config.repo_path),
        "files_scanned": len(files),
        "folders_generated": len(rows),
        "backup_zip": str(backup_zip) if backup_zip else None,
        "config": {
            "output_label": config.output_label,
            "only_connected_folders": config.only_connected_folders,
            "only_connected_files": config.only_connected_files,
            "min_edge_count": config.min_edge_count,
            "include_external_packages": config.include_external_packages,
            "internal_only": config.internal_only,
            "include_path_prefixes": list(config.include_path_prefixes),
            "ignore_path_prefixes": list(config.ignore_path_prefixes),
        },
        "extra_metadata": config.extra_metadata,
    }
    write_json(config.run_summary_file, run_summary)

    return {
        "run_id": run_id,
        "files_scanned": len(files),
        "folders_generated": len(rows),
        "backup_zip": backup_zip,
        "manifest_path": config.manifest_file,
        "state_path": config.state_file,
        "index_path": config.index_file,
        "scope_index_path": config.scope_index_file,
        "run_summary_path": config.run_summary_file,
        "output_root": config.output_root,
    }
