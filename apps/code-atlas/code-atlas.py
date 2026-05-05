#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#COMO AGREGAR UN TEMA NUEVO

#Regla de oro:
#Todo lo relacionado con temas visuales vive solo en el modulo 09.
#No registres temas en otro modulo. No dupliques listas. No agregues labels por fuera.

#Formato correcto para dar de alta un tema nuevo:
#1. Ve al modulo "09. TEMAS VISUALES".
#2. Duplica una funcion de tema existente, por ejemplo theme_dark() o theme_light().
#3. Cambia:
#   - id
#   - label
#   - svg_defs
#   - is_default si aplica
#4. Agrega la funcion al catalogo maestro en collect_theme_bundles().
#5. No toques nada mas.

#Contrato del modulo 09:
#- Declara los temas.
#- Publica el catalogo final consumible.
#- Resuelve dropdown, registry, labels y default.
#- El resto del sistema solo consume ese resultado.

#Smoke check:
#Si para agregar un tema nuevo necesitas editar otro modulo aparte del 09,
#la arquitectura ya se descompuso.

# ============================================================
# 01. IMPORTS Y CONSTANTES
# ============================================================

from __future__ import annotations

import ast
import html
import json
import math
import os
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Literal, Optional


# ----------------------------
# Tipos base del sistema
# ----------------------------

NodeKind = Literal["package", "module", "external", "note"]
EdgeKind = Literal["import", "contains", "warning"]
GraphView = Literal["package", "module", "focus"]
VisibilityPreset = Literal["executive", "engineering", "raw"]
OutputMode = Literal["svg", "tree", "tree_html"]


# ----------------------------
# Metadata general
# ----------------------------

APP_TITLE = "Dependency Graph SVG"
CODE_ATLAS_FRAME_DEPTH_FIX_V1 = "outer-frame-transparent-dynamic-depth"

DEFAULT_THEME_ID = "silver_frost_cyan"
DEFAULT_VIEW: GraphView = "package"
ENABLE_VISUAL_CONTROL_SIDECAR = (
    os.environ.get("CODE_ATLAS_VISUAL_GUIDE", "1").strip().lower()
    not in {"0", "false", "off", "no"}
)
ENABLE_EDGE_FORENSICS = (
    os.environ.get("CODE_ATLAS_EDGE_FORENSICS", "1").strip().lower()
    not in {"0", "false", "off", "no"}
)
EDGE_FORENSIC_EVIDENCE_LIMIT = max(
    3,
    int(os.environ.get("CODE_ATLAS_EDGE_EVIDENCE_LIMIT", "12") or "12"),
)

SUPPORTED_SOURCE_EXTENSIONS: tuple[str, ...] = (".py",)

# Directorios que normalmente no aportan valor arquitectónico
EXCLUDED_DIR_NAMES: set[str] = {
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "node_modules",
    "_chatgpt_patch_backups",
}

# Límites de seguridad
MAX_FILES_ANALYZED = 3000
MAX_EDGES = 12000
MAX_IMPORTS_PER_FILE = 400
MAX_PARSE_ERRORS = 120

# Salida dinámica: se crea dentro de la ruta seleccionada
OUTPUT_SUBDIR_NAME = "_dependency_graphs"
OUTPUT_FILE_PREFIX = "dependency_graph"
TREE_OUTPUT_DIR = Path(r"F:\trees")
TREE_OUTPUT_FILE_PREFIX = "dependency_tree"
TREE_HTML_OUTPUT_FILE_PREFIX = "dependency_tree_premium"
# None means: scan until the filesystem naturally ends. No fake depth=10 ceiling.
TREE_SCAN_MAX_DEPTH: int | None = None
DATE_STAMP_FORMAT = "%Y%m%d_%H%M%S"

TREE_EXCLUDED_DIR_NAMES: set[str] = EXCLUDED_DIR_NAMES | {
    ".next",
    ".turbo",
    "coverage",
}

# Layout y presentación
TOP_MARGIN = 140
LEFT_MARGIN = 60
RIGHT_MARGIN = 72
BOTTOM_MARGIN = 64

COLUMN_STEP = 360
ROW_GAP = 28
NODE_HEIGHT = 42
NODE_MIN_WIDTH = 196
NODE_MAX_WIDTH = 380
LABEL_LIMIT = 42

# Umbrales visuales / semánticos
HUB_INBOUND_THRESHOLD = 6
HUB_OUTBOUND_THRESHOLD = 6
ISLAND_INBOUND_THRESHOLD = 0
DEFAULT_VISIBILITY_PRESET: VisibilityPreset = "executive"
MAX_VISIBLE_EXTERNAL_LABELS = 32

# ============================================================
# 02. MODELOS DE GRAFO Y ESTADO
# ============================================================

@dataclass(slots=True)
class DependencyNode:
    """
    Nodo lógico del grafo.

    kind:
      - package  -> agrupación tipo apps / tools / forgeos
      - module   -> archivo o módulo Python individual
      - external -> librería externa detectada (si luego decides mostrarla)
      - note     -> advertencias o límites
    """
    key: str
    label: str
    path: str
    kind: NodeKind
    group: str

    inbound: int = 0
    outbound: int = 0

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_island(self) -> bool:
        return self.inbound <= ISLAND_INBOUND_THRESHOLD

    @property
    def is_hub(self) -> bool:
        return (
            self.inbound >= HUB_INBOUND_THRESHOLD
            or self.outbound >= HUB_OUTBOUND_THRESHOLD
        )


@dataclass(slots=True)
class DependencyEdge:
    """
    Relación dirigida.
    source -> target significa: source depende de target
    """
    source: str
    target: str
    kind: EdgeKind = "import"
    weight: int = 1
    evidence: set[str] = field(default_factory=set)

    def add_evidence(self, item: str) -> None:
        cleaned = item.strip()
        if cleaned:
            self.evidence.add(cleaned)


@dataclass(slots=True)
class AnalysisIssue:
    level: Literal["info", "warning", "error"]
    code: str
    message: str
    path: str = ""


@dataclass(slots=True)
class SelectionResult:
    path: Optional[str]
    theme: str = DEFAULT_THEME_ID
    view: GraphView = DEFAULT_VIEW
    focus_target: str = ""
    visibility_preset: VisibilityPreset = DEFAULT_VISIBILITY_PRESET
    output_mode: OutputMode = "svg"


@dataclass(slots=True)
class FileTreeEntry:
    path: Path
    relative_path: str
    name: str
    depth: int
    is_dir: bool
    size_bytes: int
    cumulative_size_bytes: int
    modified_ts: float
    child_count: int
    file_count: int
    folder_count: int
    suffix: str


@dataclass(slots=True)
class FileTreeSummary:
    total_files: int
    total_folders: int
    total_size_bytes: int
    max_depth: int
    scanned_at: str


@dataclass(slots=True)
class AnalysisState:
    """
    Estado general del análisis. Va creciendo a medida que escaneamos.
    """
    selected_path: str = ""
    project_root: str = ""
    theme: str = DEFAULT_THEME_ID
    view: GraphView = DEFAULT_VIEW
    focus_target: str = ""
    visibility_preset: VisibilityPreset = DEFAULT_VISIBILITY_PRESET

    total_files_seen: int = 0
    source_files_seen: int = 0
    parsed_files: int = 0
    skipped_files: int = 0
    parse_errors: int = 0

    total_nodes: int = 0
    total_edges: int = 0

    external_import_total: int = 0
    external_roots_total: int = 0
    external_top_roots: tuple[str, ...] = ()
    hidden_issue_count: int = 0
    visible_external_bucket_count: int = 0
    visible_external_bucket_labels: tuple[str, ...] = ()

    truncated: bool = False
    limit_reason: str = ""

    def mark_truncated(self, reason: str) -> None:
        self.truncated = True
        self.limit_reason = reason.strip()

    def register_parse_error(self) -> None:
        self.parse_errors += 1
        if self.parse_errors >= MAX_PARSE_ERRORS:
            self.mark_truncated(
                f"Se alcanzó el límite de errores de parseo: {MAX_PARSE_ERRORS}"
            )


@dataclass
class DependencyGraph:
    """
    Contenedor central del grafo.
    """
    nodes: dict[str, DependencyNode] = field(default_factory=dict)
    edges: dict[tuple[str, str, EdgeKind], DependencyEdge] = field(default_factory=dict)
    issues: list[AnalysisIssue] = field(default_factory=list)

    def upsert_node(
        self,
        *,
        key: str,
        label: str,
        path: str,
        kind: NodeKind,
        group: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> DependencyNode:
        node = self.nodes.get(key)

        if node is None:
            node = DependencyNode(
                key=key,
                label=label,
                path=path,
                kind=kind,
                group=group,
                metadata=dict(metadata or {}),
            )
            self.nodes[key] = node
            return node

        if label:
            node.label = label
        if path:
            node.path = path
        if group:
            node.group = group
        if kind != "note":
            node.kind = kind
        if metadata:
            node.metadata.update(metadata)

        return node

    def add_edge(
        self,
        source: str,
        target: str,
        *,
        kind: EdgeKind = "import",
        evidence: str = "",
    ) -> DependencyEdge:
        edge_key = (source, target, kind)
        edge = self.edges.get(edge_key)

        if edge is None:
            edge = DependencyEdge(source=source, target=target, kind=kind)
            self.edges[edge_key] = edge
        else:
            edge.weight += 1

        edge.add_evidence(evidence)
        return edge

    def add_issue(
        self,
        level: Literal["info", "warning", "error"],
        code: str,
        message: str,
        path: str = "",
    ) -> None:
        self.issues.append(
            AnalysisIssue(level=level, code=code, message=message, path=path)
        )

    def finalize_metrics(self) -> None:
        for node in self.nodes.values():
            node.inbound = 0
            node.outbound = 0

        for edge in self.edges.values():
            source_node = self.nodes.get(edge.source)
            target_node = self.nodes.get(edge.target)

            if source_node is not None:
                source_node.outbound += edge.weight
            if target_node is not None:
                target_node.inbound += edge.weight

    def iter_nodes_sorted(self) -> list[DependencyNode]:
        return sorted(
            self.nodes.values(),
            key=lambda node: (node.group.lower(), node.kind, node.label.lower()),
        )

    def iter_edges_sorted(self) -> list[DependencyEdge]:
        return sorted(
            self.edges.values(),
            key=lambda edge: (edge.source.lower(), edge.target.lower(), edge.kind),
        )


# ============================================================
# 03. HELPERS GENERALES
# ============================================================

def clean_text(value: str) -> str:
    return " ".join((value or "").replace("\n", " ").split()).strip()


def short_name(name: str, limit: int = LABEL_LIMIT) -> str:
    cleaned = clean_text(name) or "(sin nombre)"
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def short_path(path: str, limit: int = 120) -> str:
    cleaned = clean_text(path)
    if len(cleaned) <= limit:
        return cleaned

    head = max(18, int(limit * 0.45))
    tail = max(14, limit - head - 3)
    return f"{cleaned[:head]}...{cleaned[-tail:]}"


def safe_slug(value: str) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return "graph"

    forbidden = '<>:"/\\|?*'
    safe = "".join(ch if ch not in forbidden else "_" for ch in cleaned)
    safe = safe.replace(" ", "_").strip("._")
    return safe or "graph"


def dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def measure_text_width(text: str, extra_badges: int = 0) -> int:
    """
    Aproximación suficiente para SVG sin depender de medidas reales de fuente.
    """
    base = (9.1 * len(text)) + 72
    badges_extra = extra_badges * 42
    estimated = int(base + badges_extra)
    return max(NODE_MIN_WIDTH, min(NODE_MAX_WIDTH, estimated))


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def selection_anchor_path(selected_path: str) -> Path:
    """
    Si eliges una carpeta, esa carpeta es el ancla.
    Si eliges un archivo, su carpeta padre es el ancla.
    """
    candidate = Path(selected_path).expanduser().resolve()
    return candidate if candidate.is_dir() else candidate.parent


def derive_project_root(selected_path: str) -> Path:
    return selection_anchor_path(selected_path)


def resolve_output_dir(selected_path: str) -> Path:
    """
    Nada fijo a F:\\ ni cosas así.
    El SVG cae dentro de la carpeta analizada, en una subcarpeta propia.
    """
    return derive_project_root(selected_path) / OUTPUT_SUBDIR_NAME


def make_output_path(
    selected_path: str,
    theme: str,
    view: GraphView,
    focus_target: str = "",
) -> Path:
    output_dir = resolve_output_dir(selected_path)
    ensure_output_dir(output_dir)

    stamp = datetime.now().strftime(DATE_STAMP_FORMAT)
    anchor = derive_project_root(selected_path)

    base_name = safe_slug(anchor.name or "project")
    focus_suffix = f"_{safe_slug(focus_target)}" if focus_target else ""

    filename = (
        f"{OUTPUT_FILE_PREFIX}_{view}_{theme}_{base_name}{focus_suffix}_{stamp}.svg"
    )
    return output_dir / filename


def make_tree_output_path(
    selected_path: str,
    view: GraphView,
    focus_target: str = "",
) -> Path:
    ensure_output_dir(TREE_OUTPUT_DIR)

    stamp = datetime.now().strftime(DATE_STAMP_FORMAT)
    anchor = derive_project_root(selected_path)
    base_name = safe_slug(anchor.name or "project")
    focus_suffix = f"_{safe_slug(focus_target)}" if focus_target else ""

    filename = f"{TREE_OUTPUT_FILE_PREFIX}_{view}_{base_name}{focus_suffix}_{stamp}.txt"
    return TREE_OUTPUT_DIR / filename


def make_tree_html_output_path(
    selected_path: str,
    view: GraphView,
    focus_target: str = "",
) -> Path:
    ensure_output_dir(TREE_OUTPUT_DIR)

    stamp = datetime.now().strftime(DATE_STAMP_FORMAT)
    anchor = derive_project_root(selected_path)
    base_name = safe_slug(anchor.name or "project")
    focus_suffix = f"_{safe_slug(focus_target)}" if focus_target else ""

    filename = f"{TREE_HTML_OUTPUT_FILE_PREFIX}_{base_name}_{stamp}.html"
    if view == "focus" and focus_suffix:
        filename = f"{TREE_HTML_OUTPUT_FILE_PREFIX}_{base_name}{focus_suffix}_{stamp}.html"
    return TREE_OUTPUT_DIR / filename


def is_excluded_dir_name(name: str) -> bool:
    return name.strip() in EXCLUDED_DIR_NAMES


def should_exclude_tree_dir(path: Path) -> bool:
    return path.name.strip() in TREE_EXCLUDED_DIR_NAMES


def should_exclude_tree_file(path: Path) -> bool:
    return False


def is_supported_source_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_SOURCE_EXTENSIONS


def iter_source_files(project_root: Path) -> Iterator[Path]:
    """
    Recorre el proyecto de forma genérica.
    No asume apps/, tools/, forgeos/ ni ningún nombre especial.
    """
    for current_root, dir_names, file_names in os.walk(project_root):
        dir_names[:] = sorted(
            d for d in dir_names
            if not is_excluded_dir_name(d)
        )

        for file_name in sorted(file_names):
            candidate = Path(current_root) / file_name
            if is_supported_source_file(candidate):
                yield candidate


def module_name_from_path(project_root: Path, file_path: Path) -> str:
    """
    Convierte:
      /repo/forgeos/core.py -> forgeos.core
      /repo/tools/__init__.py -> tools
    """
    relative = file_path.resolve().relative_to(project_root.resolve())
    parts = list(relative.with_suffix("").parts)

    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    if not parts:
        return project_root.name

    return ".".join(parts)


def root_group_from_module_name(module_name: str) -> str:
    """
    forgeos.core.engine -> forgeos
    app.main -> app
    """
    cleaned = clean_text(module_name)
    if not cleaned:
        return "(root)"
    return cleaned.split(".", 1)[0]


def display_label_from_module_name(module_name: str) -> str:
    cleaned = clean_text(module_name)
    if not cleaned:
        return "(módulo)"
    return cleaned.split(".")[-1]


def package_label_from_group(group_name: str) -> str:
    cleaned = clean_text(group_name)
    return cleaned or "(root)"


def safe_relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def _module_path_from_info(item: ModuleSourceInfo, project_root: Path) -> Path:
    file_path = Path(item.file_path)
    if file_path.is_absolute():
        return file_path
    return project_root / file_path


def collect_relevant_module_paths(
    *,
    graph: DependencyGraph,
    module_catalog: dict[str, ModuleSourceInfo],
    project_root: Path,
) -> list[Path]:
    module_names: set[str] = set()
    root_groups: set[str] = set()
    direct_paths: list[Path] = []

    for node in graph.nodes.values():
        if node.kind == "module":
            module_name = clean_text(str(node.metadata.get("module_name", "")))
            if module_name:
                module_names.add(module_name)
            elif node.path:
                direct_paths.append(Path(node.path))
            continue

        if node.kind == "package":
            root_group = clean_text(str(node.metadata.get("root_group", node.group)))
            if root_group:
                root_groups.add(root_group)

    selected_paths: list[Path] = []
    for module_name, item in module_catalog.items():
        if module_names and module_name in module_names:
            selected_paths.append(_module_path_from_info(item, project_root))
            continue
        if root_groups and item.root_group in root_groups:
            selected_paths.append(_module_path_from_info(item, project_root))

    if direct_paths:
        selected_paths.extend(direct_paths)

    if not selected_paths:
        selected_paths = [
            _module_path_from_info(item, project_root)
            for item in module_catalog.values()
        ]

    resolved: dict[str, Path] = {}
    for path in selected_paths:
        try:
            resolved[str(path.expanduser().resolve())] = path.expanduser().resolve()
        except Exception:
            resolved[str(path)] = path

    return sorted(
        resolved.values(),
        key=lambda path: safe_relative_path(path, project_root).lower(),
    )


def _format_tree_path_lines(relative_paths: Iterable[str]) -> list[str]:
    lines: list[str] = []
    seen_dirs: set[tuple[str, ...]] = set()

    for relative_path in relative_paths:
        parts = [part for part in relative_path.replace("\\", "/").split("/") if part]
        if not parts:
            continue

        for depth, part in enumerate(parts):
            prefix = tuple(parts[: depth + 1])
            is_file = depth == len(parts) - 1
            if not is_file and prefix in seen_dirs:
                continue
            if not is_file:
                seen_dirs.add(prefix)

            indent = "  " * depth
            marker = "- " if is_file else "+ "
            lines.append(f"{indent}{marker}{part}")

    return lines


def format_size_bytes(size_bytes: int) -> str:
    value = float(max(0, int(size_bytes)))
    units = ("B", "KB", "MB", "GB", "TB")
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(value)} B"
    if value >= 100:
        return f"{value:.0f} {units[unit_index]}"
    if value >= 10:
        return f"{value:.1f} {units[unit_index]}"
    return f"{value:.2f} {units[unit_index]}"


def _safe_file_stat(path: Path) -> os.stat_result | None:
    try:
        return path.lstat() if path.is_symlink() else path.stat()
    except OSError:
        return None


def _safe_modified_ts(path: Path) -> float:
    stat = _safe_file_stat(path)
    return float(stat.st_mtime) if stat is not None else 0.0


def _format_modified_ts(modified_ts: float) -> str:
    if modified_ts <= 0:
        return "-"
    try:
        return datetime.fromtimestamp(modified_ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"


def _tree_entry_type(entry: FileTreeEntry) -> str:
    if entry.is_dir:
        return "Folder"
    suffix = clean_text(entry.suffix).lstrip(".")
    return suffix.upper() if suffix else "File"


def _tree_icon_class(entry: FileTreeEntry) -> str:
    """Return CSS classes for premium Tree HTML icons.

    Keep this dependency-free: icons are drawn with CSS/text badges in the
    generated standalone HTML, so the report still works offline.
    """
    if entry.is_dir:
        return "folder icon-folder"

    suffix = clean_text(entry.suffix).lower().lstrip(".")
    name = clean_text(entry.name).lower()

    if name in {"package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock"}:
        return "file icon-package"
    if name in {"readme.md", "readme"}:
        return "file icon-readme"
    if name in {"dockerfile"} or suffix in {"dockerfile"}:
        return "file icon-docker"
    if name.startswith(".env"):
        return "file icon-env"

    groups = {
        "md": "icon-md",
        "markdown": "icon-md",
        "json": "icon-json",
        "jsonc": "icon-json",
        "py": "icon-py",
        "pyw": "icon-py",
        "ts": "icon-ts",
        "tsx": "icon-tsx",
        "js": "icon-js",
        "jsx": "icon-jsx",
        "mjs": "icon-js",
        "cjs": "icon-js",
        "css": "icon-css",
        "scss": "icon-css",
        "sass": "icon-css",
        "html": "icon-html",
        "htm": "icon-html",
        "svg": "icon-svg",
        "png": "icon-image",
        "jpg": "icon-image",
        "jpeg": "icon-image",
        "webp": "icon-image",
        "gif": "icon-image",
        "ico": "icon-image",
        "prisma": "icon-prisma",
        "sql": "icon-sql",
        "db": "icon-db",
        "sqlite": "icon-db",
        "sqlite3": "icon-db",
        "toml": "icon-config",
        "yaml": "icon-config",
        "yml": "icon-config",
        "ini": "icon-config",
        "cfg": "icon-config",
        "lock": "icon-lock",
        "txt": "icon-text",
        "log": "icon-log",
        "zip": "icon-archive",
        "7z": "icon-archive",
        "rar": "icon-archive",
    }

    return f"file {groups.get(suffix, 'icon-generic')}"


def collect_filesystem_tree_entries(
    project_root: Path,
) -> tuple[list[FileTreeEntry], FileTreeSummary]:
    root = project_root.expanduser().resolve()
    scanned_at = datetime.now().isoformat(timespec="seconds")
    entries: list[FileTreeEntry] = []
    visited_dirs: set[str] = set()

    def scan(path: Path, depth: int) -> FileTreeEntry:
        resolved_path = path.expanduser().resolve()
        is_symlink = path.is_symlink()
        is_dir = path.is_dir() and not is_symlink
        stat = _safe_file_stat(path)
        modified_ts = float(stat.st_mtime) if stat is not None else 0.0

        if not is_dir:
            size_bytes = int(stat.st_size) if stat is not None else 0
            entry = FileTreeEntry(
                path=resolved_path,
                relative_path=safe_relative_path(resolved_path, root),
                name=resolved_path.name or str(resolved_path),
                depth=depth,
                is_dir=False,
                size_bytes=size_bytes,
                cumulative_size_bytes=size_bytes,
                modified_ts=modified_ts,
                child_count=0,
                file_count=1,
                folder_count=0,
                suffix=resolved_path.suffix.lower(),
            )
            entries.append(entry)
            return entry

        entry = FileTreeEntry(
            path=resolved_path,
            relative_path="." if resolved_path == root else safe_relative_path(resolved_path, root),
            name=resolved_path.name or str(resolved_path),
            depth=depth,
            is_dir=True,
            size_bytes=0,
            cumulative_size_bytes=0,
            modified_ts=modified_ts,
            child_count=0,
            file_count=0,
            folder_count=1,
            suffix="",
        )
        entries.append(entry)

        visit_key = str(resolved_path).lower()
        if visit_key in visited_dirs:
            return entry
        visited_dirs.add(visit_key)

        if TREE_SCAN_MAX_DEPTH is not None and depth >= TREE_SCAN_MAX_DEPTH:
            return entry

        try:
            children = sorted(
                path.iterdir(),
                key=lambda child: (not child.is_dir(), child.name.lower()),
            )
        except OSError:
            children = []

        for child in children:
            if child.is_dir() and not child.is_symlink():
                if should_exclude_tree_dir(child):
                    continue
            elif should_exclude_tree_file(child):
                continue

            child_entry = scan(child, depth + 1)
            entry.child_count += 1
            entry.file_count += child_entry.file_count
            entry.folder_count += child_entry.folder_count
            entry.cumulative_size_bytes += child_entry.cumulative_size_bytes

        return entry

    root_entry = scan(root, 0)
    summary = FileTreeSummary(
        total_files=root_entry.file_count,
        total_folders=root_entry.folder_count,
        total_size_bytes=root_entry.cumulative_size_bytes,
        max_depth=max((entry.depth for entry in entries), default=0),
        scanned_at=scanned_at,
    )
    return entries, summary


def build_tree_node_model(entries: list[FileTreeEntry]) -> list[dict[str, Any]]:
    node_ids: dict[str, str] = {}
    nodes: list[dict[str, Any]] = []

    for index, entry in enumerate(entries):
        entry_id = f"node-{index}"
        node_ids[entry.relative_path] = entry_id
        parent_relative = "."
        if entry.relative_path != ".":
            parent = Path(entry.relative_path).parent
            parent_relative = "." if str(parent) == "." else str(parent)

        nodes.append(
            {
                "id": entry_id,
                "parent_id": "" if entry.relative_path == "." else node_ids.get(parent_relative, ""),
                "entry": entry,
            }
        )

    return nodes


def build_filesystem_tree_text(
    *,
    selected_path: str,
    project_root: Path,
    entries: list[FileTreeEntry],
    summary: FileTreeSummary,
) -> str:
    lines = [
        "Code Atlas Filesystem Tree",
        f"Generated: {summary.scanned_at}",
        f"Selected path: {selected_path}",
        f"Project root: {project_root}",
        f"Total folders: {summary.total_folders}",
        f"Total files: {summary.total_files}",
        f"Total size: {format_size_bytes(summary.total_size_bytes)}",
        f"Max depth: {summary.max_depth}",
        "",
        "Tree:",
    ]

    for entry in entries:
        indent = "  " * entry.depth
        marker = "+ " if entry.is_dir else "- "
        size = format_size_bytes(entry.cumulative_size_bytes if entry.is_dir else entry.size_bytes)
        lines.append(f"{indent}{marker}{entry.name}  [{size}]")

    return "\n".join(lines) + "\n"


def _html_escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _json_for_script(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_premium_tree_html(
    *,
    selected_path: str,
    project_root: Path,
    entries: list[FileTreeEntry],
    summary: FileTreeSummary,
) -> str:
    nodes = build_tree_node_model(entries)
    tree_text = build_filesystem_tree_text(
        selected_path=selected_path,
        project_root=project_root,
        entries=entries,
        summary=summary,
    )
    rows: list[str] = []

    for node in nodes:
        entry: FileTreeEntry = node["entry"]
        entry_id = str(node["id"])
        parent_id = str(node["parent_id"])
        kind = "folder" if entry.is_dir else "file"
        size_bytes = entry.cumulative_size_bytes if entry.is_dir else entry.size_bytes
        size_text = format_size_bytes(size_bytes)
        modified_text = _format_modified_ts(entry.modified_ts)
        type_text = _tree_entry_type(entry)
        icon_class = _tree_icon_class(entry)
        modified_sort_value = f"{entry.modified_ts:.6f}"
        toggle = (
            f'<button class="twisty" type="button" aria-label="Toggle {_html_escape(entry.name)}" '
            f'data-toggle="{_html_escape(entry_id)}"></button>'
            if entry.is_dir and entry.child_count > 0
            else '<span class="twisty ghost"></span>'
        )
        selected_class = " is-selected" if entry.depth == 0 else ""
        rows.append(
            "\n".join(
                [
                    (
                        f'<tr class="tree-row {kind}{selected_class}" '
                        f'data-id="{_html_escape(entry_id)}" '
                        f'data-parent="{_html_escape(parent_id)}" '
                        f'data-depth="{entry.depth}" '
                        f'data-kind="{kind}" '
                        f'data-type="{_html_escape(type_text)}" '
                        f'data-size-bytes="{size_bytes}" '
                        f'data-modified-ts="{_html_escape(modified_sort_value)}" '
                        f'data-path="{_html_escape(entry.relative_path)}" '
                        f'data-name="{_html_escape(entry.name)}" '
                        f'style="--depth:{entry.depth};">'
                    ),
                    (
                        '<td class="name-cell">'
                        f'<span class="indent"></span>{toggle}'
                        f'<span class="tree-icon {icon_class}" aria-hidden="true"></span>'
                        f'<span class="entry-name">{_html_escape(entry.name)}</span>'
                        f'<span class="entry-path">{_html_escape(entry.relative_path)}</span>'
                        '</td>'
                    ),
                    (
                        f'<td class="size-cell" data-bytes="{size_bytes}">'
                        f'{_html_escape(size_text)}</td>'
                    ),
                    f'<td class="type-cell">{_html_escape(type_text)}</td>',
                    f'<td class="modified-cell">{_html_escape(modified_text)}</td>',
                    '</tr>',
                ]
            )
        )

    html_rows = "\n".join(rows)
    export_name = f"{TREE_HTML_OUTPUT_FILE_PREFIX}_{safe_slug(project_root.name or 'project')}_{datetime.now().strftime(DATE_STAMP_FORMAT)}.txt"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Code Atlas Tree Premium</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #090a0c;
      --panel: rgba(22, 24, 27, 0.88);
      --panel-strong: rgba(33, 35, 39, 0.92);
      --line: rgba(220, 226, 235, 0.16);
      --line-strong: rgba(232, 237, 245, 0.26);
      --silver: #d8dde5;
      --silver-soft: #aeb6c1;
      --muted: #818a96;
      --blue: #7fb3d5;
      --blue-soft: rgba(96, 150, 190, 0.18);
      --champagne: #d6bd86;
      --shadow: rgba(0, 0, 0, 0.48);
      --row-h: 2.35rem;
      --radius: 0.5rem;
      --mono: "Cascadia Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      --sans: "Segoe UI", "Aptos", system-ui, sans-serif;
    }}

    * {{ box-sizing: border-box; }}

    html {{
      min-height: 100%;
      background:
        radial-gradient(circle at 20% -10%, rgba(116, 142, 164, 0.18), transparent 34rem),
        linear-gradient(135deg, #060708 0%, #111316 42%, #08090b 100%);
    }}

    body {{
      min-height: 100vh;
      margin: 0;
      color: var(--silver);
      font-family: var(--sans);
      letter-spacing: 0;
      background:
        repeating-linear-gradient(102deg, rgba(255,255,255,0.022) 0 1px, transparent 1px 11px),
        linear-gradient(180deg, rgba(255,255,255,0.035), transparent 18rem);
    }}

    .report-shell {{
      width: min(100%, 118rem);
      min-height: 100vh;
      margin: 0 auto;
      padding: clamp(1rem, 2vw, 2rem);
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 0.85rem;
    }}

    .report-header,
    .tree-panel,
    .summary-strip {{
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background:
        linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.015)),
        var(--panel);
      box-shadow:
        0 1.25rem 3.5rem var(--shadow),
        inset 0 1px 0 rgba(255,255,255,0.16),
        inset 0 -1px 0 rgba(0,0,0,0.5);
    }}

    .report-header::before,
    .tree-panel::before {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(112deg, transparent 0%, rgba(255,255,255,0.08) 18%, transparent 34%),
        repeating-linear-gradient(0deg, rgba(255,255,255,0.018) 0 1px, transparent 1px 5px);
      opacity: 0.38;
    }}

    .report-header {{
      padding: 1rem;
      display: grid;
      grid-template-columns: minmax(16rem, 1fr) minmax(22rem, 38rem);
      gap: 1rem;
      align-items: end;
    }}

    .title-block,
    .toolbar,
    .tree-scroll,
    .summary-strip > * {{
      position: relative;
      z-index: 1;
    }}

    .eyebrow {{
      margin: 0 0 0.35rem;
      color: var(--champagne);
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }}

    h1 {{
      margin: 0;
      color: #f2f4f7;
      font-size: clamp(1.55rem, 2.5vw, 2.65rem);
      font-weight: 650;
      line-height: 1.05;
      text-shadow: 0 1px 0 rgba(255,255,255,0.08), 0 0 2rem rgba(152,175,193,0.18);
    }}

    .subtitle {{
      margin: 0.45rem 0 0;
      color: var(--silver-soft);
      font-size: 0.95rem;
    }}

    .meta-line {{
      margin: 0.65rem 0 0;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.78rem;
      overflow-wrap: anywhere;
    }}

    .toolbar {{
      display: grid;
      grid-template-columns: 1fr auto auto auto;
      gap: 0.55rem;
      align-items: center;
    }}

    .search {{
      width: 100%;
      min-width: 0;
      height: 2.45rem;
      padding: 0 0.85rem;
      color: var(--silver);
      border: 1px solid rgba(232, 237, 245, 0.18);
      border-radius: 0.42rem;
      outline: none;
      background: rgba(4, 5, 7, 0.58);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
      font: 0.9rem var(--sans);
    }}

    .search:focus {{
      border-color: rgba(127, 179, 213, 0.56);
      box-shadow: 0 0 0 3px rgba(127, 179, 213, 0.12), inset 0 1px 0 rgba(255,255,255,0.1);
    }}

    .tool-button {{
      height: 2.45rem;
      border: 1px solid rgba(232, 237, 245, 0.2);
      border-radius: 0.42rem;
      color: var(--silver);
      background:
        linear-gradient(180deg, rgba(255,255,255,0.095), rgba(255,255,255,0.02)),
        rgba(18, 20, 23, 0.9);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.13);
      cursor: pointer;
      white-space: nowrap;
      font: 700 0.78rem var(--sans);
      padding: 0 0.78rem;
    }}

    .tool-button.export {{
      color: #f4e4bd;
      border-color: rgba(214, 189, 134, 0.34);
      background:
        linear-gradient(180deg, rgba(214,189,134,0.18), rgba(255,255,255,0.035)),
        rgba(23, 21, 17, 0.88);
    }}

    .tool-button:hover {{
      transform: translateY(-1px);
      border-color: var(--line-strong);
    }}

    .tree-panel {{
      min-height: 28rem;
      display: grid;
      grid-template-rows: auto 1fr;
    }}

    .table-head {{
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: minmax(26rem, 1fr) 9rem 8rem 11rem;
      min-width: 54rem;
      border-bottom: 1px solid var(--line-strong);
      background:
        linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)),
        rgba(12, 14, 16, 0.92);
    }}

    .table-head span {{
      padding: 0.72rem 0.85rem;
      color: var(--silver-soft);
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }}

    .table-head .right {{ text-align: right; }}


    .head-button {{
      appearance: none;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      max-width: 100%;
      padding: 0;
      color: inherit;
      background: transparent;
      border: 0;
      cursor: pointer;
      font: inherit;
      text-transform: inherit;
      letter-spacing: inherit;
    }}

    .head-button.right {{
      justify-content: flex-end;
      width: 100%;
    }}

    .head-button:hover,
    .head-button.is-active {{
      color: #f4f7fb;
      text-shadow: 0 0 0.9rem rgba(127, 179, 213, 0.20);
    }}

    .sort-mark::before {{
      content: "↕";
      color: rgba(174, 182, 193, 0.55);
      font-size: 0.68rem;
    }}

    .head-button.is-active[data-dir="asc"] .sort-mark::before {{ content: "↑"; color: var(--blue); }}
    .head-button.is-active[data-dir="desc"] .sort-mark::before {{ content: "↓"; color: var(--blue); }}

    .type-head {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      min-width: 0;
    }}

    .type-filter {{
      min-width: 4.7rem;
      max-width: 6.4rem;
      height: 1.55rem;
      padding: 0 1.45rem 0 0.45rem;
      color: rgba(232, 237, 245, 0.86);
      border: 1px solid rgba(232, 237, 245, 0.16);
      border-radius: 0.34rem;
      background: rgba(6, 8, 10, 0.70);
      font: 700 0.68rem var(--sans);
      outline: none;
    }}

    .type-filter:focus {{
      border-color: rgba(127, 179, 213, 0.52);
      box-shadow: 0 0 0 3px rgba(127, 179, 213, 0.10);
    }}

    .tree-scroll {{
      overflow: auto;
      min-width: 0;
    }}

    table {{
      width: max-content;
      min-width: 100%;
      border-collapse: collapse;
      table-layout: auto;
      font-size: 0.88rem;
    }}

    col.name {{ width: auto; min-width: 42rem; }}
    col.size {{ width: 9rem; }}
    col.type {{ width: 8rem; }}
    col.modified {{ width: 11rem; }}

    .tree-row {{
      height: var(--row-h);
      color: rgba(216, 221, 229, 0.72);
      border-bottom: 1px solid rgba(232, 237, 245, 0.075);
      background: rgba(255,255,255,0.012);
      transition: background 160ms ease, color 160ms ease, box-shadow 160ms ease;
    }}

    .tree-row:hover {{
      color: rgba(245,247,250,0.92);
      background: rgba(255,255,255,0.045);
    }}

    .tree-row.is-selected {{
      color: #f5f8fb;
      background:
        linear-gradient(90deg, rgba(192, 205, 219, 0.18), rgba(127, 179, 213, 0.13), rgba(255,255,255,0.035));
      box-shadow:
        inset 0 0 0 1px rgba(230, 235, 242, 0.28),
        inset 0.28rem 0 0 rgba(214, 226, 238, 0.54),
        0 0 1.4rem rgba(127, 179, 213, 0.12);
    }}

    .tree-row.is-selected .name-cell::after {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: linear-gradient(108deg, transparent 0%, rgba(255,255,255,0.16) 45%, transparent 72%);
      animation: selectedSweep 3.8s ease-in-out infinite;
    }}

    td {{
      height: var(--row-h);
      padding: 0 0.85rem;
      vertical-align: middle;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .name-cell {{
      position: relative;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      min-width: max-content;
      overflow: visible;
      text-overflow: clip;
    }}

    .name-cell::before {{
      content: "";
      position: absolute;
      left: calc(1rem + (var(--depth) * 1.35rem));
      top: 0;
      bottom: 0;
      border-left: 1px solid rgba(220, 226, 235, 0.12);
    }}

    .indent {{
      flex: 0 0 calc(var(--depth) * 1.35rem);
    }}

    .twisty {{
      width: 1.1rem;
      height: 1.1rem;
      flex: 0 0 1.1rem;
      border: 1px solid rgba(220,226,235,0.18);
      border-radius: 0.25rem;
      background: rgba(255,255,255,0.035);
      cursor: pointer;
      position: relative;
    }}

    .twisty::before {{
      content: "";
      position: absolute;
      left: 0.36rem;
      top: 0.28rem;
      width: 0.33rem;
      height: 0.33rem;
      border-right: 1px solid var(--silver-soft);
      border-bottom: 1px solid var(--silver-soft);
      transform: rotate(45deg);
      transition: transform 160ms ease;
    }}

    .tree-row.is-collapsed .twisty::before {{
      transform: rotate(-45deg) translate(-1px, 1px);
    }}

    .twisty.ghost {{
      border-color: transparent;
      background: transparent;
      cursor: default;
    }}

    .twisty.ghost::before {{ display: none; }}

    .tree-icon {{
      width: 1.08rem;
      height: 1.08rem;
      flex: 0 0 1.08rem;
      position: relative;
      opacity: 0.92;
      filter: drop-shadow(0 0 0.35rem rgba(160, 184, 205, 0.08));
    }}

    .tree-icon.folder::before {{
      content: "";
      position: absolute;
      inset: 0.25rem 0.05rem 0.08rem;
      border: 1px solid rgba(222, 229, 238, 0.44);
      border-radius: 0.18rem;
      background:
        linear-gradient(180deg, rgba(230,235,242,0.34), rgba(86,98,111,0.18)),
        rgba(90, 104, 118, 0.12);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.28), 0 0 0.55rem rgba(127,179,213,0.07);
    }}

    .tree-icon.folder::after {{
      content: "";
      position: absolute;
      left: 0.13rem;
      top: 0.11rem;
      width: 0.5rem;
      height: 0.25rem;
      border-radius: 0.13rem 0.13rem 0 0;
      background: linear-gradient(180deg, rgba(225, 233, 244, 0.62), rgba(128, 148, 168, 0.28));
      border: 1px solid rgba(224, 231, 240, 0.22);
      border-bottom: 0;
    }}

    .tree-icon.file::before {{
      content: "";
      position: absolute;
      inset: 0.08rem 0.18rem;
      border: 1px solid rgba(222, 229, 238, 0.34);
      border-radius: 0.16rem;
      background:
        linear-gradient(145deg, rgba(235,239,245,0.26), rgba(72,82,94,0.16)),
        rgba(255,255,255,0.02);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.18);
    }}

    .tree-icon.file::after {{
      content: "";
      position: absolute;
      right: 0.18rem;
      top: 0.08rem;
      width: 0.28rem;
      height: 0.28rem;
      border-left: 1px solid rgba(222,229,238,0.35);
      border-bottom: 1px solid rgba(222,229,238,0.35);
      background: rgba(127,179,213,0.14);
    }}

    .tree-icon.file {{ --badge: ""; --accent: rgba(174, 182, 193, 0.48); }}
    .tree-icon.file.icon-md {{ --badge: "MD"; --accent: rgba(118, 169, 210, 0.62); }}
    .tree-icon.file.icon-readme {{ --badge: "RD"; --accent: rgba(127, 196, 159, 0.60); }}
    .tree-icon.file.icon-json {{ --badge: "{{}}"; --accent: rgba(231, 191, 111, 0.66); }}
    .tree-icon.file.icon-package {{ --badge: "PK"; --accent: rgba(233, 166, 113, 0.68); }}
    .tree-icon.file.icon-py {{ --badge: "PY"; --accent: rgba(106, 156, 219, 0.68); }}
    .tree-icon.file.icon-ts {{ --badge: "TS"; --accent: rgba(79, 154, 217, 0.70); }}
    .tree-icon.file.icon-tsx {{ --badge: "TX"; --accent: rgba(96, 174, 225, 0.72); }}
    .tree-icon.file.icon-js {{ --badge: "JS"; --accent: rgba(232, 203, 94, 0.66); }}
    .tree-icon.file.icon-jsx {{ --badge: "JX"; --accent: rgba(232, 203, 94, 0.66); }}
    .tree-icon.file.icon-css {{ --badge: "#"; --accent: rgba(104, 158, 230, 0.66); }}
    .tree-icon.file.icon-html {{ --badge: "<>"; --accent: rgba(236, 136, 96, 0.68); }}
    .tree-icon.file.icon-svg {{ --badge: "◈"; --accent: rgba(201, 143, 238, 0.64); }}
    .tree-icon.file.icon-image {{ --badge: "IMG"; --accent: rgba(108, 194, 190, 0.64); }}
    .tree-icon.file.icon-prisma {{ --badge: "PR"; --accent: rgba(120, 210, 194, 0.64); }}
    .tree-icon.file.icon-sql {{ --badge: "SQL"; --accent: rgba(164, 144, 236, 0.64); }}
    .tree-icon.file.icon-db {{ --badge: "DB"; --accent: rgba(178, 158, 230, 0.62); }}
    .tree-icon.file.icon-config {{ --badge: "⚙"; --accent: rgba(184, 196, 207, 0.62); }}
    .tree-icon.file.icon-env {{ --badge: "ENV"; --accent: rgba(117, 190, 140, 0.62); }}
    .tree-icon.file.icon-lock {{ --badge: "LK"; --accent: rgba(209, 180, 118, 0.64); }}
    .tree-icon.file.icon-text {{ --badge: "TXT"; --accent: rgba(174, 182, 193, 0.56); }}
    .tree-icon.file.icon-log {{ --badge: "LOG"; --accent: rgba(178, 159, 124, 0.60); }}
    .tree-icon.file.icon-archive {{ --badge: "ZIP"; --accent: rgba(207, 168, 108, 0.62); }}
    .tree-icon.file.icon-docker {{ --badge: "DK"; --accent: rgba(95, 159, 220, 0.66); }}
    .tree-icon.file.icon-generic {{ --badge: "•"; --accent: rgba(174, 182, 193, 0.48); }}

    .tree-icon.file::before {{ border-color: color-mix(in srgb, var(--accent) 54%, rgba(222,229,238,0.28)); }}

    .tree-icon.file > span {{ display: none; }}

    .tree-icon.file::after {{
      content: var(--badge);
      right: -0.12rem;
      top: 0.58rem;
      width: auto;
      min-width: 0.72rem;
      height: 0.42rem;
      padding: 0 0.08rem;
      border: 1px solid color-mix(in srgb, var(--accent) 68%, rgba(255,255,255,0.16));
      border-radius: 0.16rem;
      background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 38%, rgba(12,14,16,0.96)), rgba(8,10,12,0.86));
      color: rgba(244, 248, 252, 0.88);
      font: 700 0.34rem/0.42rem var(--mono);
      text-align: center;
      letter-spacing: 0.015em;
      box-shadow: 0 0 0.45rem color-mix(in srgb, var(--accent) 22%, transparent);
    }}

    .entry-name {{
      overflow: visible;
      text-overflow: clip;
      min-width: max-content;
    }}

    .entry-path {{
      color: rgba(174, 182, 193, 0.55);
      font-family: var(--mono);
      font-size: 0.72rem;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .size-cell {{
      text-align: right;
      color: rgba(232, 237, 245, 0.82);
      font-family: var(--mono);
      font-variant-numeric: tabular-nums;
    }}

    .type-cell,
    .modified-cell {{
      color: rgba(174, 182, 193, 0.7);
      font-family: var(--mono);
      font-size: 0.78rem;
    }}

    .summary-strip {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 0;
      min-height: 4.25rem;
    }}

    .summary-item {{
      padding: 0.85rem 1rem;
      border-right: 1px solid var(--line);
    }}

    .summary-item:last-child {{ border-right: 0; }}

    .summary-label {{
      color: var(--muted);
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}

    .summary-value {{
      margin-top: 0.25rem;
      color: #f2f4f7;
      font-family: var(--mono);
      font-size: 0.94rem;
      overflow-wrap: anywhere;
    }}

    @keyframes selectedSweep {{
      0%, 46% {{ transform: translateX(-120%); opacity: 0; }}
      58% {{ opacity: 0.55; }}
      100% {{ transform: translateX(120%); opacity: 0; }}
    }}

    @media (max-width: 56rem) {{
      .report-header {{
        grid-template-columns: 1fr;
      }}
      .toolbar {{
        grid-template-columns: 1fr 1fr;
      }}
      .search {{
        grid-column: 1 / -1;
      }}
      .summary-strip {{
        grid-template-columns: 1fr 1fr;
      }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition: none !important;
      }}
    }}

    @media print {{
      body, html {{ background: #fff; color: #111; }}
      .report-header, .tree-panel, .summary-strip {{
        box-shadow: none;
        background: #fff;
        border-color: #aaa;
      }}
      .toolbar {{ display: none; }}
      .tree-row, .tree-row.is-selected {{ color: #111; background: #fff; box-shadow: none; }}
      .entry-path, .type-cell, .modified-cell, .summary-label {{ color: #333; }}
    }}
  </style>
</head>
<body>
  <main class="report-shell">
    <header class="report-header">
      <section class="title-block">
        <p class="eyebrow">Filesystem inventory</p>
        <h1>Code Atlas Tree Premium</h1>
        <p class="subtitle">HTML Filesystem Tree Report</p>
        <p class="meta-line">Selected: {_html_escape(selected_path)}</p>
        <p class="meta-line">Root: {_html_escape(project_root)}</p>
      </section>
      <section class="toolbar" aria-label="Tree controls">
        <input id="treeSearch" class="search" type="search" placeholder="Search folders and files" autocomplete="off">
        <button id="expandAll" class="tool-button" type="button">Expand All</button>
        <button id="collapseAll" class="tool-button" type="button">Collapse All</button>
        <button id="exportTree" class="tool-button export" type="button">Export Tree</button>
      </section>
    </header>

    <section class="tree-panel" aria-label="Filesystem tree">
      <div class="table-head" role="row">
        <span><button class="head-button sort-button" type="button" data-sort="name" aria-label="Sort by name">Name <b class="sort-mark" aria-hidden="true"></b></button></span>
        <span class="right"><button class="head-button sort-button right" type="button" data-sort="size" aria-label="Sort by size">Size <b class="sort-mark" aria-hidden="true"></b></button></span>
        <span class="type-head"><button class="head-button sort-button" type="button" data-sort="type" aria-label="Sort by type">Type <b class="sort-mark" aria-hidden="true"></b></button><select id="typeFilter" class="type-filter" aria-label="Filter by type"><option value="">All</option></select></span>
        <span><button class="head-button sort-button" type="button" data-sort="modified" aria-label="Sort by modified date">Modified <b class="sort-mark" aria-hidden="true"></b></button></span>
      </div>
      <div class="tree-scroll">
        <table>
          <colgroup>
            <col class="name">
            <col class="size">
            <col class="type">
            <col class="modified">
          </colgroup>
          <tbody id="treeBody">
{html_rows}
          </tbody>
        </table>
      </div>
    </section>

    <footer class="summary-strip">
      <section class="summary-item">
        <div class="summary-label">Total Folders</div>
        <div class="summary-value">{summary.total_folders}</div>
      </section>
      <section class="summary-item">
        <div class="summary-label">Total Files</div>
        <div class="summary-value">{summary.total_files}</div>
      </section>
      <section class="summary-item">
        <div class="summary-label">Total Size</div>
        <div class="summary-value">{_html_escape(format_size_bytes(summary.total_size_bytes))}</div>
      </section>
      <section class="summary-item">
        <div class="summary-label">Max Depth</div>
        <div class="summary-value">{summary.max_depth}</div>
      </section>
      <section class="summary-item">
        <div class="summary-label">Scanned</div>
        <div class="summary-value">{_html_escape(summary.scanned_at)}</div>
      </section>
    </footer>
  </main>

  <script>
    const TREE_TEXT = {_json_for_script(tree_text)};
    const EXPORT_NAME = {_json_for_script(export_name)};

    (() => {{
      const treeBody = document.getElementById("treeBody");
      let rows = Array.from(document.querySelectorAll(".tree-row"));
      const byId = new Map(rows.map((row) => [row.dataset.id, row]));
      const search = document.getElementById("treeSearch");
      const expandAll = document.getElementById("expandAll");
      const collapseAll = document.getElementById("collapseAll");
      const exportTree = document.getElementById("exportTree");
      const typeFilter = document.getElementById("typeFilter");
      const sortButtons = Array.from(document.querySelectorAll("[data-sort]"));
      const sortState = {{ key: "name", direction: "asc" }};

      function refreshRows() {{
        rows = Array.from(treeBody.querySelectorAll(".tree-row"));
      }}

      function childrenOf(id) {{
        return rows.filter((row) => row.dataset.parent === id);
      }}

      function descendantsOf(id) {{
        const result = [];
        const stack = childrenOf(id);
        while (stack.length) {{
          const row = stack.shift();
          result.push(row);
          stack.unshift(...childrenOf(row.dataset.id));
        }}
        return result;
      }}

      function ancestorIds(row) {{
        const ids = [];
        let parent = row.dataset.parent;
        while (parent && byId.has(parent)) {{
          ids.push(parent);
          parent = byId.get(parent).dataset.parent;
        }}
        return ids;
      }}

      function isHiddenByCollapse(row) {{
        let parent = row.dataset.parent;
        while (parent && byId.has(parent)) {{
          const parentRow = byId.get(parent);
          if (parentRow.classList.contains("is-collapsed")) {{
            return true;
          }}
          parent = parentRow.dataset.parent;
        }}
        return false;
      }}

      function normalizeText(value) {{
        return String(value || "").trim().toLowerCase();
      }}

      function numericValue(row, field) {{
        if (field === "size") {{ return Number(row.dataset.sizeBytes || "0"); }}
        if (field === "modified") {{ return Number(row.dataset.modifiedTs || "0"); }}
        return 0;
      }}

      function textValue(row, field) {{
        if (field === "type") {{ return normalizeText(row.dataset.type); }}
        if (field === "name") {{ return normalizeText(row.dataset.name); }}
        return normalizeText(row.dataset.path);
      }}

      function compareRows(a, b) {{
        const dir = sortState.direction === "desc" ? -1 : 1;
        let result = 0;

        if (sortState.key === "size" || sortState.key === "modified") {{
          result = numericValue(a, sortState.key) - numericValue(b, sortState.key);
        }} else {{
          result = textValue(a, sortState.key).localeCompare(textValue(b, sortState.key), undefined, {{ numeric: true, sensitivity: "base" }});
        }}

        if (result === 0) {{
          result = textValue(a, "name").localeCompare(textValue(b, "name"), undefined, {{ numeric: true, sensitivity: "base" }});
        }}
        if (result === 0) {{
          result = textValue(a, "type").localeCompare(textValue(b, "type"), undefined, {{ numeric: true, sensitivity: "base" }});
        }}
        return result * dir;
      }}

      function appendSortedBranch(parentId, fragment) {{
        const children = childrenOf(parentId).slice().sort(compareRows);
        children.forEach((child) => {{
          fragment.appendChild(child);
          appendSortedBranch(child.dataset.id, fragment);
        }});
      }}

      function sortTree() {{
        const selectedId = (document.querySelector(".tree-row.is-selected") || {{ dataset: {{}} }}).dataset.id || "";
        const fragment = document.createDocumentFragment();
        appendSortedBranch("", fragment);
        treeBody.appendChild(fragment);
        refreshRows();
        if (selectedId && byId.has(selectedId)) {{
          rows.forEach((row) => row.classList.remove("is-selected"));
          byId.get(selectedId).classList.add("is-selected");
        }}
        updateSortButtons();
        applyVisibility();
      }}

      function updateSortButtons() {{
        sortButtons.forEach((button) => {{
          const active = button.dataset.sort === sortState.key;
          button.classList.toggle("is-active", active);
          button.dataset.dir = active ? sortState.direction : "";
          button.setAttribute("aria-sort", active ? (sortState.direction === "asc" ? "ascending" : "descending") : "none");
        }});
      }}

      function populateTypeFilter() {{
        if (!typeFilter) return;
        const types = Array.from(new Set(rows.map((row) => row.dataset.type || "").filter(Boolean)))
          .sort((a, b) => a.localeCompare(b, undefined, {{ numeric: true, sensitivity: "base" }}));
        const fragment = document.createDocumentFragment();
        types.forEach((type) => {{
          const option = document.createElement("option");
          option.value = type;
          option.textContent = type;
          fragment.appendChild(option);
        }});
        typeFilter.appendChild(fragment);
      }}

      function applyVisibility() {{
        const query = normalizeText(search.value);
        const selectedType = typeFilter ? typeFilter.value : "";
        const hasQuery = Boolean(query);
        const hasType = Boolean(selectedType);
        const activeFilter = hasQuery || hasType;
        const visibleForFilter = new Set();

        if (activeFilter) {{
          rows.forEach((row) => {{
            const haystack = `${{row.dataset.name || ""}} ${{row.dataset.path || ""}}`.toLowerCase();
            const queryMatch = !hasQuery || haystack.includes(query);
            const typeMatch = !hasType || row.dataset.type === selectedType;
            if (queryMatch && typeMatch) {{
              visibleForFilter.add(row.dataset.id);
              ancestorIds(row).forEach((id) => visibleForFilter.add(id));
              if (hasQuery && row.dataset.kind === "folder") {{
                descendantsOf(row.dataset.id).forEach((desc) => visibleForFilter.add(desc.dataset.id));
              }}
            }}
          }});
        }}

        rows.forEach((row) => {{
          const filterHidden = activeFilter && !visibleForFilter.has(row.dataset.id);
          const collapseHidden = !activeFilter && isHiddenByCollapse(row);
          row.hidden = Boolean(filterHidden || collapseHidden);
        }});
      }}

      rows.forEach((row) => {{
        row.addEventListener("click", (event) => {{
          if (event.target && event.target.matches("[data-toggle]")) {{
            return;
          }}
          rows.forEach((item) => item.classList.remove("is-selected"));
          row.classList.add("is-selected");
        }});
      }});

      document.querySelectorAll("[data-toggle]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const row = byId.get(button.dataset.toggle);
          if (!row) return;
          row.classList.toggle("is-collapsed");
          applyVisibility();
        }});
      }});

      sortButtons.forEach((button) => {{
        button.addEventListener("click", () => {{
          const nextKey = button.dataset.sort || "name";
          if (sortState.key === nextKey) {{
            sortState.direction = sortState.direction === "asc" ? "desc" : "asc";
          }} else {{
            sortState.key = nextKey;
            sortState.direction = nextKey === "name" || nextKey === "type" ? "asc" : "desc";
          }}
          sortTree();
        }});
      }});

      expandAll.addEventListener("click", () => {{
        rows.forEach((row) => row.classList.remove("is-collapsed"));
        applyVisibility();
      }});

      collapseAll.addEventListener("click", () => {{
        rows.forEach((row) => {{
          if (row.dataset.kind === "folder" && row.dataset.parent) {{
            row.classList.add("is-collapsed");
          }}
        }});
        applyVisibility();
      }});

      search.addEventListener("input", applyVisibility);
      if (typeFilter) {{ typeFilter.addEventListener("change", applyVisibility); }}

      exportTree.addEventListener("click", () => {{
        const blob = new Blob([TREE_TEXT], {{ type: "text/plain;charset=utf-8" }});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = EXPORT_NAME;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      }});

      populateTypeFilter();
      sortTree();
      applyVisibility();
    }})();
  </script>
</body>
</html>
"""


def build_relevant_tree_text(
    *,
    selected_path: str,
    state: AnalysisState,
    graph: DependencyGraph,
    module_catalog: dict[str, ModuleSourceInfo],
    import_refs: Iterable[ImportReference],
    module_paths: Iterable[Path],
) -> str:
    project_root = Path(state.project_root or str(derive_project_root(selected_path)))
    paths = list(module_paths)
    relative_paths = [
        safe_relative_path(path, project_root)
        for path in paths
    ]
    relative_paths = sorted(dedupe_preserve_order(relative_paths), key=str.lower)
    import_refs_list = list(import_refs)

    lines = [
        "Code Atlas Dependency Tree",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Selected path: {selected_path}",
        f"Project root: {project_root}",
        f"View: {state.view}",
        f"Theme: {state.theme}",
        f"Visibility preset: {state.visibility_preset}",
        f"Modules in catalog: {len(module_catalog)}",
        f"Relevant modules: {len(relative_paths)}",
        f"Import references: {len(import_refs_list)}",
        f"Visible nodes: {len(graph.nodes)}",
        f"Visible edges: {len(graph.edges)}",
        "",
        "Tree:",
    ]

    tree_lines = _format_tree_path_lines(relative_paths)
    lines.extend(tree_lines or ["- (sin archivos relevantes)"])

    if graph.issues:
        lines.extend(["", "Issues:"])
        for issue in graph.issues:
            location = f" [{issue.path}]" if issue.path else ""
            lines.append(f"- {issue.level.upper()} {issue.code}: {issue.message}{location}")

    return "\n".join(lines) + "\n"


def build_state_summary(state: AnalysisState) -> str:
    chunks = [
        f"{state.source_files_seen} fuentes",
        f"{state.parsed_files} parseados",
        f"{state.total_nodes} nodos",
        f"{state.total_edges} relaciones",
        f"vista {state.view}",
        f"tema {state.theme}",
    ]

    if state.visibility_preset:
        chunks.append(f"preset {state.visibility_preset}")

    if state.hidden_issue_count > 0:
        chunks.append(f"issues ocultos {state.hidden_issue_count}")

    if state.external_roots_total > 0:
        chunks.append(f"externos {state.external_roots_total} roots")

    if state.visible_external_bucket_count > 0:
        chunks.append(f"externos visibles {state.visible_external_bucket_count}")

    if state.truncated:
        chunks.append("análisis truncado")

    return " • ".join(chunks)


def _top_external_roots_text(counts: dict[str, int], *, limit: int = 4) -> tuple[str, ...]:
    ranked = sorted(
        counts.items(),
        key=lambda item: (-item[1], item[0].lower()),
    )
    return tuple(f"{name} ×{count}" for name, count in ranked[:limit])


def resolve_visibility_preset(view: GraphView) -> VisibilityPreset:
    if view == "package":
        return "executive"
    if view in {"module", "focus"}:
        return "engineering"
    return DEFAULT_VISIBILITY_PRESET


def should_surface_issue_notes(state: AnalysisState) -> bool:
    return state.visibility_preset == "raw"


def clone_graph_for_visible_subset(
    graph: DependencyGraph,
    selected_node_keys: set[str],
) -> DependencyGraph:
    visible = DependencyGraph()

    for node_key in selected_node_keys:
        node = graph.nodes.get(node_key)
        if node is None:
            continue

        visible.upsert_node(
            key=node.key,
            label=node.label,
            path=node.path,
            kind=node.kind,
            group=node.group,
            metadata=dict(node.metadata),
        )

    for edge in graph.edges.values():
        if edge.source not in selected_node_keys or edge.target not in selected_node_keys:
            continue

        cloned = visible.add_edge(
            edge.source,
            edge.target,
            kind=edge.kind,
        )
        cloned.weight = edge.weight
        cloned.evidence.update(edge.evidence)

    for issue in graph.issues:
        visible.issues.append(issue)

    visible.finalize_metrics()
    return visible


def _visible_node_sort_key(node: DependencyNode) -> tuple[int, int, int, str]:
    return (
        -(node.inbound + node.outbound),
        -node.inbound,
        -node.outbound,
        node.label.lower(),
    )


def _capture_visible_external_state(
    graph: DependencyGraph,
    state: AnalysisState,
) -> None:
    external_nodes = sorted(
        (node for node in graph.nodes.values() if node.kind == "external"),
        key=lambda node: node.label.lower(),
    )
    state.visible_external_bucket_count = len(external_nodes)
    state.visible_external_bucket_labels = tuple(
        node.label
        for node in external_nodes[:MAX_VISIBLE_EXTERNAL_LABELS]
    )


def _external_edge_sort_key(
    edge: DependencyEdge,
    graph: DependencyGraph,
    focus_key: str,
) -> tuple[int, int, int, int, str]:
    touches_focus = 1 if focus_key and (edge.source == focus_key or edge.target == focus_key) else 0

    internal_node: DependencyNode | None = None
    if edge.source in graph.nodes and graph.nodes[edge.source].kind != "external":
        internal_node = graph.nodes[edge.source]
    elif edge.target in graph.nodes and graph.nodes[edge.target].kind != "external":
        internal_node = graph.nodes[edge.target]

    internal_degree = 0
    internal_inbound = 0
    label = ""
    if internal_node is not None:
        internal_degree = internal_node.inbound + internal_node.outbound
        internal_inbound = internal_node.inbound
        label = internal_node.label.lower()

    return (
        -touches_focus,
        -edge.weight,
        -internal_degree,
        -internal_inbound,
        label,
    )


def attach_engineering_external_buckets(
    source_graph: DependencyGraph,
    visible_graph: DependencyGraph,
    state: AnalysisState,
) -> DependencyGraph:
    if state.visibility_preset != "engineering":
        return visible_graph

    if state.view not in {"module", "focus"}:
        return visible_graph

    internal_visible_keys = {
        node.key
        for node in visible_graph.nodes.values()
        if node.kind not in {"external", "note"}
    }
    if not internal_visible_keys:
        return visible_graph

    focus_key = ""
    if state.view == "focus":
        focus_key = resolve_focus_node_key(visible_graph, state.focus_target)

    candidate_edges: dict[str, list[DependencyEdge]] = {}
    candidate_groups: dict[str, set[str]] = {}

    for edge in source_graph.edges.values():
        source_node = source_graph.nodes.get(edge.source)
        target_node = source_graph.nodes.get(edge.target)
        if source_node is None or target_node is None:
            continue

        external_node: DependencyNode | None = None
        internal_node: DependencyNode | None = None

        if source_node.kind == "external" and target_node.key in internal_visible_keys:
            external_node = source_node
            internal_node = target_node
        elif target_node.kind == "external" and source_node.key in internal_visible_keys:
            external_node = target_node
            internal_node = source_node

        if external_node is None or internal_node is None:
            continue

        candidate_edges.setdefault(external_node.key, []).append(edge)
        if internal_node.group:
            candidate_groups.setdefault(external_node.key, set()).add(internal_node.group)

    if not candidate_edges:
        return visible_graph

    bucket_limit = 4 if state.view == "focus" else 6
    max_edges_per_bucket = 2 if state.view == "focus" else 3
    max_external_edges_total = 8 if state.view == "focus" else 12

    ranked_external_keys = sorted(
        candidate_edges,
        key=lambda external_key: (
            -(
                1
                if focus_key
                and any(
                    edge.source == focus_key or edge.target == focus_key
                    for edge in candidate_edges[external_key]
                )
                else 0
            ),
            -len(candidate_groups.get(external_key, set())),
            -sum(edge.weight for edge in candidate_edges[external_key]),
            -max((edge.weight for edge in candidate_edges[external_key]), default=0),
            source_graph.nodes[external_key].label.lower(),
        ),
    )

    added_external_edges = 0
    for external_key in ranked_external_keys[:bucket_limit]:
        remaining_slots = max_external_edges_total - added_external_edges
        if remaining_slots <= 0:
            break

        ranked_edges = sorted(
            candidate_edges[external_key],
            key=lambda edge: _external_edge_sort_key(edge, visible_graph, focus_key),
        )
        chosen_edges = ranked_edges[: min(max_edges_per_bucket, remaining_slots)]
        if not chosen_edges:
            continue

        external_node = source_graph.nodes.get(external_key)
        if external_node is None:
            continue

        visible_graph.upsert_node(
            key=external_node.key,
            label=external_node.label,
            path=external_node.path,
            kind=external_node.kind,
            group=external_node.group,
            metadata=dict(external_node.metadata),
        )

        for edge in chosen_edges:
            if edge.source not in visible_graph.nodes or edge.target not in visible_graph.nodes:
                continue

            cloned = visible_graph.add_edge(
                edge.source,
                edge.target,
                kind=edge.kind,
            )
            cloned.weight = edge.weight
            cloned.evidence.update(edge.evidence)
            added_external_edges += 1

    return visible_graph


def _trim_module_visible_graph(
    graph: DependencyGraph,
    *,
    max_nodes_per_group: int = 12,
    max_nodes_total: int = 48,
) -> DependencyGraph:
    if len(graph.nodes) <= max_nodes_total:
        return graph

    grouped: dict[str, list[DependencyNode]] = {}
    for node in graph.nodes.values():
        grouped.setdefault(node.group, []).append(node)

    selected: set[str] = set()
    for group_name, nodes in grouped.items():
        keep = max_nodes_per_group
        if group_name in {ISSUE_NOTE_GROUP, "[external]"}:
            keep = min(keep, 4)

        ranked = sorted(nodes, key=_visible_node_sort_key)
        for node in ranked[:keep]:
            selected.add(node.key)

    if len(selected) > max_nodes_total:
        ranked_selected = sorted(
            (graph.nodes[node_key] for node_key in selected if node_key in graph.nodes),
            key=_visible_node_sort_key,
        )
        selected = {node.key for node in ranked_selected[:max_nodes_total]}

    return clone_graph_for_visible_subset(graph, selected)


def _trim_focus_visible_graph(
    graph: DependencyGraph,
    state: AnalysisState,
) -> DependencyGraph:
    focus_key = resolve_focus_node_key(graph, state.focus_target)
    if not focus_key or focus_key not in graph.nodes:
        return graph

    relation_map = _focus_relation_map(graph, focus_key)
    selected = {focus_key}

    budgets = {
        "inbound": 8,
        "outbound": 8,
        "mixed": 6,
        "context": 4,
    }
    if state.visibility_preset == "executive":
        budgets = {
            "inbound": 4,
            "outbound": 4,
            "mixed": 4,
            "context": 2,
        }

    for relation, budget in budgets.items():
        ranked = sorted(
            (
                node for node in graph.nodes.values()
                if relation_map.get(node.key) == relation
            ),
            key=_visible_node_sort_key,
        )
        for node in ranked[:budget]:
            selected.add(node.key)

    if not selected:
        return graph

    return clone_graph_for_visible_subset(graph, selected)


def simplify_visible_graph(
    graph: DependencyGraph,
    state: AnalysisState,
) -> DependencyGraph:
    """
    Simplificación conservadora:
    - jamás toca discovery
    - jamás toca source_files_seen / parsed_files
    - solo limpia ruido visual después de construir el grafo base
    """
    preset = state.visibility_preset

    if preset == "raw":
        state.hidden_issue_count = 0
        graph.finalize_metrics()
        _capture_visible_external_state(graph, state)
        state.total_nodes = len(graph.nodes)
        state.total_edges = len(graph.edges)
        return graph

    selected_node_keys = {
        node.key
        for node in graph.nodes.values()
        if node.kind != "note"
    }

    if preset in {"executive", "engineering"}:
        selected_node_keys = {
            node_key
            for node_key in selected_node_keys
            if graph.nodes[node_key].kind != "external"
            and graph.nodes[node_key].group != "[external]"
        }

    visible = clone_graph_for_visible_subset(graph, selected_node_keys)
    state.hidden_issue_count = len(visible.issues)

    if state.view in {"module", "focus"}:
        visible.finalize_metrics()

        focus_key = ""
        if state.view == "focus":
            focus_key = resolve_focus_node_key(visible, state.focus_target)

        connected_keys = {edge.source for edge in visible.edges.values()}
        connected_keys.update(edge.target for edge in visible.edges.values())

        retained_node_keys = {
            node.key
            for node in visible.nodes.values()
            if node.key in connected_keys
            or node.kind == "package"
            or node.key == focus_key
        }

        if not retained_node_keys and visible.nodes:
            ranked = sorted(
                visible.nodes.values(),
                key=_visible_node_sort_key,
            )
            retained_node_keys.add(ranked[0].key)

        visible = clone_graph_for_visible_subset(visible, retained_node_keys)

        if state.view == "focus":
            visible = _trim_focus_visible_graph(visible, state)
        elif state.view == "module":
            visible = _trim_module_visible_graph(visible)

        visible = attach_engineering_external_buckets(graph, visible, state)

    visible.finalize_metrics()
    _capture_visible_external_state(visible, state)
    state.total_nodes = len(visible.nodes)
    state.total_edges = len(visible.edges)
    return visible


# ============================================================
# 04. CONSTRUCCION DEL GRAFO
# ============================================================

@dataclass(slots=True)
class ImportReference:
    """
    Representa una dependencia detectada en el código fuente.

    importer_module:
      módulo que hace el import

    imported_module:
      módulo resuelto o semi-resuelto al que apunta

    imported_symbol:
      símbolo importado, si aplica
      ejemplo: from forgeos.core import Engine -> Engine

    is_relative:
      marca si vino de un import relativo

    line_no:
      línea donde se detectó, para evidencia y debugging visual
    """
    importer_module: str
    imported_module: str
    imported_symbol: str = ""
    is_relative: bool = False
    line_no: int = 0


@dataclass(slots=True)
class ModuleSourceInfo:
    """
    Metadata mínima del módulo analizado.
    """
    module_name: str
    file_path: str
    root_group: str
    relative_path: str


def make_module_key(module_name: str) -> str:
    return f"module:{clean_text(module_name)}"


def make_package_key(group_name: str) -> str:
    return f"package:{clean_text(group_name)}"


def is_internal_module_name(module_name: str, known_modules: set[str]) -> bool:
    """
    Un módulo es interno si:
    - existe exactamente, o
    - pertenece a un namespace cuyo padre existe
      ej. forgeos.core.engine sigue siendo interno si forgeos.core existe
    """
    cleaned = clean_text(module_name)
    if not cleaned:
        return False

    if cleaned in known_modules:
        return True

    probe = cleaned
    while "." in probe:
        probe = probe.rsplit(".", 1)[0]
        if probe in known_modules:
            return True

    return False


def choose_best_internal_target(
    imported_module: str,
    known_modules: set[str],
) -> str:
    """
    Trata de aterrizar un import al módulo interno más razonable.

    Casos:
    - import forgeos.core          -> forgeos.core
    - from forgeos.core import x   -> forgeos.core
    - from forgeos import core     -> forgeos
    - import forgeos.core.engine   -> si no existe exacto, intenta padres
    """
    cleaned = clean_text(imported_module)
    if not cleaned:
        return ""

    if cleaned in known_modules:
        return cleaned

    probe = cleaned
    while "." in probe:
        probe = probe.rsplit(".", 1)[0]
        if probe in known_modules:
            return probe

    return ""


def build_external_import_summary(
    import_refs: Iterable[ImportReference],
    module_catalog: dict[str, ModuleSourceInfo],
) -> tuple[int, int, tuple[str, ...]]:
    known_modules = set(module_catalog.keys())
    counts: dict[str, int] = {}
    total_refs = 0

    for ref in import_refs:
        imported_module = clean_text(ref.imported_module)
        if not imported_module:
            continue

        if is_internal_module_name(imported_module, known_modules):
            continue

        external_root = imported_module.split(".", 1)[0]
        if not external_root:
            continue

        total_refs += 1
        counts[external_root] = counts.get(external_root, 0) + 1

    return total_refs, len(counts), _top_external_roots_text(counts)


def apply_analysis_summaries(
    state: AnalysisState,
    module_catalog: dict[str, ModuleSourceInfo],
    import_refs: Iterable[ImportReference],
) -> None:
    (
        state.external_import_total,
        state.external_roots_total,
        state.external_top_roots,
    ) = build_external_import_summary(import_refs, module_catalog)


def build_module_catalog(
    project_root: Path,
    source_files: Iterable[Path],
) -> dict[str, ModuleSourceInfo]:
    """
    Crea el catálogo base de módulos internos detectados por path.
    """
    catalog: dict[str, ModuleSourceInfo] = {}

    for file_path in source_files:
        module_name = module_name_from_path(project_root, file_path)
        group_name = root_group_from_module_name(module_name)

        catalog[module_name] = ModuleSourceInfo(
            module_name=module_name,
            file_path=str(file_path),
            root_group=group_name,
            relative_path=safe_relative_path(file_path, project_root),
        )

    return catalog


def seed_internal_module_nodes(
    graph: DependencyGraph,
    module_catalog: dict[str, ModuleSourceInfo],
) -> None:
    """
    Registra nodos tipo módulo para todos los archivos internos encontrados.
    """
    for item in module_catalog.values():
        graph.upsert_node(
            key=make_module_key(item.module_name),
            label=display_label_from_module_name(item.module_name),
            path=item.file_path,
            kind="module",
            group=item.root_group,
            metadata={
                "module_name": item.module_name,
                "relative_path": item.relative_path,
                "root_group": item.root_group,
            },
        )


def seed_internal_package_nodes(
    graph: DependencyGraph,
    module_catalog: dict[str, ModuleSourceInfo],
) -> None:
    """
    Registra nodos agregados por paquete raíz.
    """
    groups = dedupe_preserve_order(
        item.root_group
        for item in sorted(module_catalog.values(), key=lambda x: x.root_group.lower())
    )

    for group_name in groups:
        graph.upsert_node(
            key=make_package_key(group_name),
            label=package_label_from_group(group_name),
            path=group_name,
            kind="package",
            group=group_name,
            metadata={
                "root_group": group_name,
            },
        )


def attach_external_nodes_for_module_view(
    graph: DependencyGraph,
    import_refs: Iterable[ImportReference],
    known_modules: set[str],
) -> None:
    """
    Crea nodos externos solo para vista de módulos.
    En vista de paquetes normalmente estorban más de lo que ayudan.
    """
    external_names: list[str] = []

    for ref in import_refs:
        imported_name = clean_text(ref.imported_module)
        if not imported_name:
            continue

        if is_internal_module_name(imported_name, known_modules):
            continue

        external_names.append(imported_name.split(".", 1)[0])

    for external_root in dedupe_preserve_order(sorted(external_names, key=str.lower)):
        graph.upsert_node(
            key=make_module_key(f"[external].{external_root}"),
            label=external_root,
            path=external_root,
            kind="external",
            group="[external]",
            metadata={
                "module_name": external_root,
                "root_group": "[external]",
                "external": True,
            },
        )


def build_module_view_edges(
    graph: DependencyGraph,
    import_refs: Iterable[ImportReference],
    module_catalog: dict[str, ModuleSourceInfo],
    *,
    include_external: bool = False,
) -> None:
    """
    Construye edges módulo -> módulo.

    source -> target significa:
    source depende de target
    """
    known_modules = set(module_catalog.keys())

    for ref in import_refs:
        source_module = clean_text(ref.importer_module)
        imported_module = clean_text(ref.imported_module)

        if not source_module or source_module not in known_modules:
            continue

        source_key = make_module_key(source_module)
        resolved_target = choose_best_internal_target(imported_module, known_modules)

        if resolved_target:
            target_key = make_module_key(resolved_target)
            evidence = (
                f"{source_module} -> {resolved_target}"
                + (f" @L{ref.line_no}" if ref.line_no > 0 else "")
            )
            graph.add_edge(
                source_key,
                target_key,
                kind="import",
                evidence=evidence,
            )
            continue

        if include_external and imported_module:
            external_root = imported_module.split(".", 1)[0]
            external_key = make_module_key(f"[external].{external_root}")

            graph.upsert_node(
                key=external_key,
                label=external_root,
                path=external_root,
                kind="external",
                group="[external]",
                metadata={
                    "module_name": external_root,
                    "root_group": "[external]",
                    "external": True,
                },
            )

            evidence = (
                f"{source_module} -> external:{external_root}"
                + (f" @L{ref.line_no}" if ref.line_no > 0 else "")
            )
            graph.add_edge(
                source_key,
                external_key,
                kind="import",
                evidence=evidence,
            )


def build_package_view_edges(
    graph: DependencyGraph,
    import_refs: Iterable[ImportReference],
    module_catalog: dict[str, ModuleSourceInfo],
) -> None:
    """
    Construye edges agregados paquete -> paquete.

    Ejemplo:
      apps.main -> forgeos.core
    se agrega como:
      apps -> forgeos
    """
    known_modules = set(module_catalog.keys())

    for ref in import_refs:
        source_module = clean_text(ref.importer_module)
        imported_module = clean_text(ref.imported_module)

        source_info = module_catalog.get(source_module)
        if source_info is None:
            continue

        resolved_target = choose_best_internal_target(imported_module, known_modules)
        if not resolved_target:
            continue

        target_info = module_catalog.get(resolved_target)
        if target_info is None:
            continue

        source_key = make_package_key(source_info.root_group)
        target_key = make_package_key(target_info.root_group)

        evidence = (
            f"{source_info.root_group} -> {target_info.root_group}"
            f" ({source_module} -> {resolved_target})"
        )

        graph.add_edge(
            source_key,
            target_key,
            kind="import",
            evidence=evidence,
        )


def filter_focus_graph(
    graph: DependencyGraph,
    focus_target: str,
) -> DependencyGraph:
    """
    Reduce el grafo a:
    - el nodo objetivo
    - sus entradas
    - sus salidas

    focus_target puede venir como:
    - forgeos
    - forgeos.core
    - package:forgeos
    - module:forgeos.core
    """
    cleaned = clean_text(focus_target)
    result = DependencyGraph()

    if not cleaned:
        return graph

    exact_key_candidates = [
        cleaned,
        make_package_key(cleaned),
        make_module_key(cleaned),
    ]

    target_key = ""
    for candidate in exact_key_candidates:
        if candidate in graph.nodes:
            target_key = candidate
            break

    if not target_key:
        for node in graph.nodes.values():
            module_name = clean_text(str(node.metadata.get("module_name", "")))
            root_group = clean_text(str(node.metadata.get("root_group", "")))

            if cleaned in {node.label, module_name, root_group, node.key}:
                target_key = node.key
                break

    if not target_key:
        result.add_issue(
            "warning",
            "focus_target_not_found",
            f"No se encontró el foco solicitado: {cleaned}",
        )
        return result

    related_keys: set[str] = {target_key}

    for edge in graph.edges.values():
        if edge.source == target_key or edge.target == target_key:
            related_keys.add(edge.source)
            related_keys.add(edge.target)

    for key in related_keys:
        node = graph.nodes.get(key)
        if node is None:
            continue

        result.upsert_node(
            key=node.key,
            label=node.label,
            path=node.path,
            kind=node.kind,
            group=node.group,
            metadata=dict(node.metadata),
        )

    for edge in graph.edges.values():
        if edge.source in related_keys and edge.target in related_keys:
            cloned = result.add_edge(
                edge.source,
                edge.target,
                kind=edge.kind,
            )
            cloned.weight = edge.weight
            cloned.evidence.update(edge.evidence)

    for issue in graph.issues:
        result.issues.append(issue)

    result.finalize_metrics()
    return result


def construct_dependency_graph(
    *,
    state: AnalysisState,
    module_catalog: dict[str, ModuleSourceInfo],
    import_refs: Iterable[ImportReference],
    include_external_in_module_view: bool = False,
) -> DependencyGraph:
    """
    Punto central para construir el grafo final según la vista elegida.

    state.view:
      - package -> grafo agregado por carpetas raíz
      - module  -> grafo por módulos/archivos
      - focus   -> grafo reducido alrededor del objetivo
    """
    graph = DependencyGraph()

    if state.view == "package":
        seed_internal_package_nodes(graph, module_catalog)
        build_package_view_edges(graph, import_refs, module_catalog)

    elif state.view == "module":
        seed_internal_module_nodes(graph, module_catalog)

        if include_external_in_module_view:
            attach_external_nodes_for_module_view(
                graph,
                import_refs,
                set(module_catalog.keys()),
            )

        build_module_view_edges(
            graph,
            import_refs,
            module_catalog,
            include_external=include_external_in_module_view,
        )

    elif state.view == "focus":
        seed_internal_module_nodes(graph, module_catalog)
        build_module_view_edges(
            graph,
            import_refs,
            module_catalog,
            include_external=include_external_in_module_view,
        )
        graph = filter_focus_graph(graph, state.focus_target)

    else:
        graph.add_issue(
            "warning",
            "unknown_view",
            f"Vista no reconocida: {state.view}. Se usará 'package'.",
        )
        seed_internal_package_nodes(graph, module_catalog)
        build_package_view_edges(graph, import_refs, module_catalog)

    graph.finalize_metrics()

    state.total_nodes = len(graph.nodes)
    state.total_edges = len(graph.edges)

    if state.total_edges >= MAX_EDGES:
        state.mark_truncated(
            f"Se alcanzó el límite de relaciones visibles: {MAX_EDGES}"
        )

    return graph


# ============================================================
# 05. UI: SELECTOR Y PROGRESO (PySide6)
# ============================================================

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional

from PySide6.QtCore import Qt, QEvent, QObject, QPoint, QPointF, QRect, QRectF, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from forgeos.shared.pyside6_glass.controls import create_button as shared_create_button
from forgeos.shared.pyside6_glass.scene import (
    build_glass_dialog_scene as shared_build_glass_dialog_scene,
)
from forgeos.shared.pyside6_glass.theme import build_stylesheet as shared_build_stylesheet


VIEW_LABEL_TO_ID: dict[str, GraphView] = {
    "Paquetes": "package",
    "Módulos": "module",
    "Foco": "focus",
}

VIEW_ID_TO_LABEL: dict[GraphView, str] = {
    value: key for key, value in VIEW_LABEL_TO_ID.items()
}

VIEW_DROPDOWN_LABELS: list[str] = list(VIEW_LABEL_TO_ID.keys())


@dataclass(frozen=True, slots=True)
class _ThemeChoice:
    id: str
    label: str
    is_default: bool = False


@dataclass(frozen=True, slots=True)
class _ThemeCatalog:
    choices: tuple[_ThemeChoice, ...]
    label_to_id: dict[str, str]
    id_to_label: dict[str, str]
    labels: tuple[str, ...]
    default_id: str


@dataclass(frozen=True, slots=True)
class _PathState:
    raw: str
    normalized: str
    exists: bool
    kind: str
    display: str
    path_obj: Optional[Path]
    anchor_dir: Optional[Path]


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).strip()


def _app_title() -> str:
    return APP_TITLE


def _default_theme_id() -> str:
    return DEFAULT_THEME_ID


def _default_view_id() -> GraphView:
    return DEFAULT_VIEW


def _output_subdir_name() -> str:
    return OUTPUT_SUBDIR_NAME


def _normalize_path_text(path_text: Any) -> str:
    text = str(path_text or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1].strip()
    return text


def _short_path(path_text: str, limit: int = 92) -> str:
    cleaned = _clean_text(path_text)
    if len(cleaned) <= limit:
        return cleaned
    head = max(18, int(limit * 0.48))
    tail = max(16, limit - head - 3)
    return f"{cleaned[:head]}...{cleaned[-tail:]}"


def _coerce_view(value: Any) -> GraphView:
    cleaned = _clean_text(value).lower()
    if cleaned in VIEW_ID_TO_LABEL:
        return cleaned  # type: ignore[return-value]

    for label, view_id in VIEW_LABEL_TO_ID.items():
        if _clean_text(label).lower() == cleaned:
            return view_id

    return _default_view_id()


def _coerce_output_mode(value: Any) -> OutputMode:
    cleaned = _clean_text(value).lower()
    if cleaned in {"tree_html", "html", "premium_html", "tree premium", "tree_html_premium"}:
        return "tree_html"
    if cleaned in {"tree", "txt", "text", "dependency_tree"}:
        return "tree"
    return "svg"


def _coerce_theme_choice(item: Any) -> Optional[_ThemeChoice]:
    if item is None:
        return None

    if isinstance(item, _ThemeChoice):
        return item

    if isinstance(item, Mapping):
        theme_id = _clean_text(item.get("id", ""))
        label = _clean_text(item.get("label", theme_id))
        is_default = bool(item.get("is_default", False))
        if theme_id and label:
            return _ThemeChoice(id=theme_id, label=label, is_default=is_default)
        return None

    if isinstance(item, (tuple, list)):
        if len(item) >= 2:
            theme_id = _clean_text(item[0])
            label = _clean_text(item[1])
            is_default = bool(item[2]) if len(item) >= 3 else False
            if theme_id and label:
                return _ThemeChoice(id=theme_id, label=label, is_default=is_default)
        return None

    theme_id = _clean_text(getattr(item, "id", ""))
    label = _clean_text(getattr(item, "label", theme_id))
    is_default = bool(getattr(item, "is_default", False))
    if theme_id and label:
        return _ThemeChoice(id=theme_id, label=label, is_default=is_default)

    return None


def _resolve_theme_catalog(
    *,
    theme_items: Optional[Iterable[Any]] = None,
    theme_label_to_id: Optional[Mapping[str, str]] = None,
    theme_id_to_label: Optional[Mapping[str, str]] = None,
    theme_dropdown_labels: Optional[Iterable[str]] = None,
    default_theme: Optional[str] = None,
) -> _ThemeCatalog:
    choices: list[_ThemeChoice] = []

    source_items = theme_items
    if source_items is None:
        source_items = THEME_BUNDLES

    if source_items is not None:
        for item in source_items:
            choice = _coerce_theme_choice(item)
            if choice is not None:
                choices.append(choice)

    if not choices:
        label_to_id = dict(
            theme_label_to_id
            or THEME_LABEL_TO_ID
            or {}
        )
        id_to_label = dict(
            theme_id_to_label
            or THEME_ID_TO_LABEL
            or {}
        )
        dropdown_labels = list(
            theme_dropdown_labels
            or THEME_DROPDOWN_LABELS
            or []
        )

        if not label_to_id and id_to_label:
            label_to_id = {label: theme_id for theme_id, label in id_to_label.items()}
        if not id_to_label and label_to_id:
            id_to_label = {theme_id: label for label, theme_id in label_to_id.items()}

        if dropdown_labels:
            for label in dropdown_labels:
                clean_label = _clean_text(label)
                if not clean_label:
                    continue
                theme_id = _clean_text(label_to_id.get(clean_label, clean_label))
                choices.append(_ThemeChoice(id=theme_id, label=clean_label, is_default=False))

        if not choices:
            ordered_ids: list[str] = list(id_to_label.keys())
            for _, theme_id in label_to_id.items():
                if theme_id not in ordered_ids:
                    ordered_ids.append(theme_id)

            for theme_id in ordered_ids:
                clean_id = _clean_text(theme_id)
                if not clean_id:
                    continue
                label = _clean_text(id_to_label.get(clean_id, clean_id)) or clean_id
                choices.append(_ThemeChoice(id=clean_id, label=label, is_default=False))

    if not choices:
        fallback_id = _default_theme_id()
        choices = [_ThemeChoice(id=fallback_id, label=fallback_id.capitalize(), is_default=True)]

    deduped: list[_ThemeChoice] = []
    seen_ids: set[str] = set()
    seen_labels: set[str] = set()
    for choice in choices:
        theme_id = _clean_text(choice.id)
        label = _clean_text(choice.label)
        if not theme_id or not label:
            continue
        if theme_id in seen_ids or label in seen_labels:
            continue
        seen_ids.add(theme_id)
        seen_labels.add(label)
        deduped.append(_ThemeChoice(id=theme_id, label=label, is_default=choice.is_default))

    if not deduped:
        fallback_id = _default_theme_id()
        deduped = [_ThemeChoice(id=fallback_id, label=fallback_id.capitalize(), is_default=True)]

    default_candidate = _clean_text(default_theme or _default_theme_id())
    default_id = ""

    if default_candidate:
        lowered = default_candidate.lower()
        for choice in deduped:
            if choice.id.lower() == lowered or choice.label.lower() == lowered:
                default_id = choice.id
                break

    if not default_id:
        for choice in deduped:
            if choice.is_default:
                default_id = choice.id
                break

    if not default_id:
        default_id = deduped[0].id

    label_to_id = {choice.label: choice.id for choice in deduped}
    id_to_label = {choice.id: choice.label for choice in deduped}

    return _ThemeCatalog(
        choices=tuple(deduped),
        label_to_id=label_to_id,
        id_to_label=id_to_label,
        labels=tuple(choice.label for choice in deduped),
        default_id=default_id,
    )


def _normalize_theme_from_catalog(theme_value: Any, catalog: _ThemeCatalog) -> str:
    cleaned = _clean_text(theme_value)
    if not cleaned:
        return catalog.default_id

    lowered = cleaned.lower()
    for choice in catalog.choices:
        if choice.id.lower() == lowered or choice.label.lower() == lowered:
            return choice.id

    return catalog.default_id


def _inspect_path(path_text: str) -> _PathState:
    raw = path_text or ""
    normalized = _normalize_path_text(raw)

    if not normalized:
        return _PathState(
            raw=raw,
            normalized="",
            exists=False,
            kind="none",
            display="(ninguna)",
            path_obj=None,
            anchor_dir=None,
        )

    candidate = Path(normalized).expanduser()
    exists = candidate.exists()

    if exists:
        try:
            candidate = candidate.resolve()
        except Exception:
            pass

    if exists and candidate.is_dir():
        return _PathState(
            raw=raw,
            normalized=str(candidate),
            exists=True,
            kind="folder",
            display=str(candidate),
            path_obj=candidate,
            anchor_dir=candidate,
        )

    if exists and candidate.is_file():
        return _PathState(
            raw=raw,
            normalized=str(candidate),
            exists=True,
            kind="file",
            display=str(candidate),
            path_obj=candidate,
            anchor_dir=candidate.parent if candidate.parent.exists() else None,
        )

    anchor_dir: Optional[Path] = None
    try:
        parent = candidate.parent
        if str(parent) and parent.exists():
            anchor_dir = parent.resolve()
    except Exception:
        anchor_dir = None

    return _PathState(
        raw=raw,
        normalized=normalized,
        exists=False,
        kind="manual",
        display=normalized,
        path_obj=candidate,
        anchor_dir=anchor_dir,
    )


def _picker_start_directory(path_text: str) -> str:
    state = _inspect_path(path_text)

    if state.kind == "folder" and state.path_obj is not None:
        return str(state.path_obj)

    if state.kind == "file" and state.anchor_dir is not None:
        return str(state.anchor_dir)

    if state.anchor_dir is not None:
        return str(state.anchor_dir)

    try:
        return str(Path.cwd())
    except Exception:
        return ""


def _output_anchor_text(path_state: _PathState) -> str:
    if path_state.kind == "folder":
        return path_state.display
    if path_state.kind == "file" and path_state.anchor_dir is not None:
        return str(path_state.anchor_dir)
    if path_state.kind == "manual" and path_state.anchor_dir is not None:
        return str(path_state.anchor_dir)
    return "(se resolverá al validar la ruta)"


def _make_selection_result(
    *,
    path: Optional[str],
    theme: str,
    view: GraphView,
    focus_target: str,
    output_mode: OutputMode = "svg",
) -> SelectionResult:
    return SelectionResult(
        path=path,
        theme=theme,
        view=view,
        focus_target=focus_target,
        output_mode=_coerce_output_mode(output_mode),
    )


def ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
        app.setQuitOnLastWindowClosed(False)
    return app


def apply_shadow(
    widget: QWidget,
    *,
    blur: float = 22.0,
    x_offset: float = 0.0,
    y_offset: float = 6.0,
    alpha: int = 68,
    color: Optional[QColor] = None,
    enabled: bool = True,
) -> None:
    if widget is None:
        return

    if not enabled:
        widget.setGraphicsEffect(None)
        return

    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        effect = QGraphicsDropShadowEffect(widget)
        widget.setGraphicsEffect(effect)

    effect.setBlurRadius(max(0.0, float(blur)))
    effect.setOffset(float(x_offset), float(y_offset))
    effect.setColor(color or QColor(0, 0, 0, max(0, min(255, int(alpha)))))


def repolish(widget: QWidget, recursive: bool = False) -> None:
    if widget is None:
        return

    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()

    if recursive:
        for child in widget.findChildren(QWidget):
            child_style = child.style()
            child_style.unpolish(child)
            child_style.polish(child)
            child.update()



def apply_window_transparency(host: QWidget) -> None:
    """Remove the rectangular OS/backdrop fill around frameless glass dialogs."""
    if host is None:
        return
    host.setAttribute(Qt.WA_TranslucentBackground, True)
    host.setAttribute(Qt.WA_NoSystemBackground, True)
    host.setAutoFillBackground(False)
    # CODE_ATLAS_FRAME_DEPTH_FIX_V1: keep the floating glass shell without the pale rectangular frame.


@dataclass(frozen=True, slots=True)
class _GlassPalette:
    canvas_top: QColor
    canvas_bottom: QColor
    wash: QColor
    border: QColor
    line: QColor
    sheen: QColor
    orb_a: QColor
    orb_b: QColor
    orb_c: QColor
    sparkle: QColor
    star_soft: QColor
    star_bright: QColor


def _qcolor_from_value(value: Any, alpha: float = 1.0) -> QColor:
    cleaned = clean_text(str(value or ""))
    color = QColor(cleaned or "#808080")
    if not color.isValid():
        color = QColor("#808080")
    color.setAlphaF(max(0.0, min(1.0, float(alpha))))
    return color


def _is_silver_theme_id(theme_id: str) -> bool:
    lowered = clean_text(theme_id).lower()
    return any(tag in lowered for tag in ("silver", "frost", "argent", "mercury"))


def _glass_palette(theme_id: str, variant: str = "selector") -> _GlassPalette:
    render = resolve_render_theme(theme_id)
    t = render.tokens
    dark = render.is_dark
    silver_theme = _is_silver_theme_id(theme_id)

    selector_variant = clean_text(variant).lower() != "progress"

    if silver_theme:
        canvas_top = _qcolor_from_value("#04070d", 1.0)
        canvas_bottom = _qcolor_from_value("#0f1824", 1.0)
        wash = _qcolor_from_value("#eef6ff", 0.022 if selector_variant else 0.028)
        border = _qcolor_from_value("#e8f6ff", 0.20 if selector_variant else 0.16)
        line = _qcolor_from_value("#8cefff", 0.05)
        sheen = _qcolor_from_value("#ffffff", 0.08)
        orb_a = _qcolor_from_value("#eff7ff", 0.18 if selector_variant else 0.14)
        orb_b = _qcolor_from_value("#8cefff", 0.15 if selector_variant else 0.12)
        orb_c = _qcolor_from_value("#d7e1ff", 0.10 if selector_variant else 0.08)
        sparkle = _qcolor_from_value("#ffffff", 0.88)
        star_soft = _qcolor_from_value("#eef6ff", 0.18)
        star_bright = _qcolor_from_value("#ffffff", 0.62)

        return _GlassPalette(
            canvas_top=canvas_top,
            canvas_bottom=canvas_bottom,
            wash=wash,
            border=border,
            line=line,
            sheen=sheen,
            orb_a=orb_a,
            orb_b=orb_b,
            orb_c=orb_c,
            sparkle=sparkle,
            star_soft=star_soft,
            star_bright=star_bright,
        )

    canvas_top = _qcolor_from_value(
        _mix_hex(t["canvas_bg"], t["header_fill"], 0.18 if dark else 0.05),
        1.0,
    )
    canvas_bottom = _qcolor_from_value(
        _mix_hex(t["canvas_bg"], t["legend_fill"], 0.32 if dark else 0.10),
        1.0,
    )
    wash = _qcolor_from_value(
        _mix_hex(t["header_fill"], t["legend_fill"], 0.50 if dark else 0.20),
        0.30 if dark else 0.76,
    )
    border = _qcolor_from_value(
        _mix_hex(t["focus"], t["legend_stroke"], 0.26 if dark else 0.12),
        0.26 if dark else 0.42,
    )
    line = _qcolor_from_value(t["header_stroke"], 0.10 if dark else 0.18)
    sheen = _qcolor_from_value("#ffffff", 0.09 if dark else 0.16)
    orb_a = _qcolor_from_value(
        t["halo_a"],
        0.22 if selector_variant and dark else 0.16 if selector_variant else 0.18 if dark else 0.12,
    )
    orb_b = _qcolor_from_value(
        t["halo_b"],
        0.16 if selector_variant and dark else 0.11 if selector_variant else 0.14 if dark else 0.10,
    )
    orb_c = _qcolor_from_value(
        t["focus"],
        0.14 if dark else 0.09,
    )
    sparkle = _qcolor_from_value("#ffffff", 0.34 if dark else 0.42)
    star_soft = _qcolor_from_value("#ffffff", 0.12 if dark else 0.18)
    star_bright = _qcolor_from_value("#ffffff", 0.28 if dark else 0.34)

    return _GlassPalette(
        canvas_top=canvas_top,
        canvas_bottom=canvas_bottom,
        wash=wash,
        border=border,
        line=line,
        sheen=sheen,
        orb_a=orb_a,
        orb_b=orb_b,
        orb_c=orb_c,
        sparkle=sparkle,
        star_soft=star_soft,
        star_bright=star_bright,
    )


class FrostedGlassBackdrop(QWidget):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        theme_id: str = DEFAULT_THEME_ID,
        variant: str = "selector",
    ) -> None:
        super().__init__(parent)
        self._variant = clean_text(variant).lower() or "selector"
        self._theme_id = normalize_theme(theme_id)
        self._palette = _glass_palette(self._theme_id, self._variant)
        self._motion_enabled = True
        self._motion_epoch = time.monotonic()
        self._motion_timer = QTimer(self)
        self._motion_timer.setInterval(24)
        self._motion_timer.timeout.connect(self._advance_motion)
        self.setObjectName("FrostedGlassBackdrop")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self._sync_motion_timer()

    def _advance_motion(self) -> None:
        if not self.isVisible():
            return
        self.update()

    def _motion_time(self) -> float:
        return max(0.0, time.monotonic() - self._motion_epoch)

    def _sync_motion_timer(self) -> None:
        should_run = self._motion_enabled and _is_silver_theme_id(self._theme_id)
        if should_run and not self._motion_timer.isActive():
            self._motion_timer.start()
        elif not should_run and self._motion_timer.isActive():
            self._motion_timer.stop()

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._sync_motion_timer()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        if self._motion_timer.isActive():
            self._motion_timer.stop()
        super().hideEvent(event)

    def apply_theme(self, theme_id: str) -> None:
        resolved = normalize_theme(theme_id or DEFAULT_THEME)
        if resolved == self._theme_id:
            return
        self._theme_id = resolved
        self._palette = _glass_palette(self._theme_id, self._variant)
        self._sync_motion_timer()
        self.update()

    def _orb_specs(
        self,
        rect: QRectF,
        *,
        motion_phase: float = 0.0,
    ) -> list[tuple[QColor, float, float, float]]:
        if self._variant == "progress":
            base_specs = [
                (self._palette.orb_a, 0.76, 0.18, 0.46, 0.10, 0.08),
                (self._palette.orb_b, 0.16, 0.82, 0.30, 0.12, 0.10),
                (self._palette.orb_c, 0.50, 0.58, 0.24, 0.14, 0.09),
            ]
        else:
            base_specs = [
                (self._palette.orb_a, 0.58, 0.16, 0.54, 0.08, 0.06),
                (self._palette.orb_b, 0.18, 0.72, 0.34, 0.12, 0.09),
                (self._palette.orb_c, 0.90, 0.62, 0.38, 0.10, 0.07),
            ]

        specs: list[tuple[QColor, float, float, float]] = []
        for index, (color, x_factor, y_factor, radius_factor, x_speed, y_speed) in enumerate(base_specs, start=1):
            x_wobble = math.sin((motion_phase * x_speed) + (index * 0.9)) * 0.026
            y_wobble = math.cos((motion_phase * y_speed) + (index * 1.3)) * 0.033
            radius_wobble = 1.0 + (0.055 * math.sin((motion_phase * 0.08) + (index * 1.7)))
            specs.append(
                (
                    color,
                    rect.width() * (x_factor + x_wobble),
                    rect.height() * (y_factor + y_wobble),
                    rect.width() * radius_factor * radius_wobble,
                )
            )
        return specs

    def _noise01(self, seed: float) -> float:
        value = math.sin((seed * 12.9898) + 78.233) * 43758.5453123
        return value - math.floor(value)

    def _flash_interval_seconds(self, event_index: int) -> float:
        step = event_index % 3
        if step == 0:
            return 20.0
        if step == 1:
            return 30.0
        return 40.0

    def _ensure_flash_events(self, until_time: float) -> None:
        if not hasattr(self, '_flash_events'):
            self._flash_events: list[dict[str, float]] = []
            self._flash_schedule_cursor = 0.0
            self._flash_schedule_index = 0

        while self._flash_schedule_cursor <= until_time:
            event_index = int(self._flash_schedule_index)
            interval = self._flash_interval_seconds(event_index)
            self._flash_schedule_cursor += interval

            pair_count = 1 if self._noise01(8000.0 + (event_index * 1.91)) < 0.78 else 2
            for pair_index in range(pair_count):
                seed = 9100.0 + (event_index * 13.0) + (pair_index * 2.7)
                start = self._flash_schedule_cursor + (0.0 if pair_index == 0 else (0.55 + (self._noise01(seed + 3.2) * 1.05)))
                duration = 1.10 + (self._noise01(seed + 4.8) * 1.25)
                self._flash_events.append(
                    {
                        'start': start,
                        'end': start + duration,
                        'x_factor': 0.08 + (self._noise01(seed + 7.1) * 0.84),
                        'y_factor': 0.10 + (self._noise01(seed + 9.4) * 0.72),
                        'radius': 12.0 + (self._noise01(seed + 12.7) * 20.0),
                        'strength': 0.74 + (self._noise01(seed + 14.9) * 0.42),
                        'cross': 4.0 + (self._noise01(seed + 17.3) * 5.6),
                    }
                )

            self._flash_schedule_index += 1

        prune_before = max(0.0, until_time - 48.0)
        self._flash_events = [event for event in self._flash_events if event['end'] >= prune_before]

    def _active_flash_events(self, at_time: float) -> list[dict[str, float]]:
        self._ensure_flash_events(at_time + 45.0)
        return [
            event
            for event in getattr(self, '_flash_events', [])
            if event['start'] <= at_time <= event['end']
        ]

    def _paint_spark_flashes(
        self,
        painter: QPainter,
        rect: QRectF,
        *,
        motion_phase: float = 0.0,
    ) -> None:
        active_events = self._active_flash_events(motion_phase)
        if not active_events:
            return

        for event in active_events:
            start = event['start']
            end = event['end']
            duration = max(0.01, end - start)
            progress = max(0.0, min(1.0, (motion_phase - start) / duration))

            if progress < 0.24:
                envelope = progress / 0.24
            elif progress > 0.72:
                envelope = max(0.0, 1.0 - ((progress - 0.72) / 0.28))
            else:
                envelope = 1.0

            shimmer = 0.74 + (0.26 * math.sin((progress * math.tau * 2.0) + (event['x_factor'] * 8.0)))
            strength = max(0.0, envelope * shimmer * event['strength'])
            if strength <= 0.02:
                continue

            x = rect.width() * event['x_factor']
            y = rect.height() * event['y_factor']
            radius = event['radius'] * (0.84 + (0.44 * strength))

            glow = QRadialGradient(x, y, radius)
            glow_color = QColor(self._palette.star_bright)
            glow_color.setAlpha(max(0, min(255, int(112 * strength))))
            mid = QColor(self._palette.star_soft)
            mid.setAlpha(max(0, min(255, int(48 * strength))))
            edge = QColor(glow_color)
            edge.setAlpha(0)
            glow.setColorAt(0.0, glow_color)
            glow.setColorAt(0.34, mid)
            glow.setColorAt(1.0, edge)
            painter.setBrush(glow)
            painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2.0, radius * 2.0))

            core_size = 1.5 + (2.4 * strength)
            painter.setBrush(QColor(255, 255, 255, max(0, min(255, int(205 * strength)))))
            painter.drawEllipse(QRectF(x - (core_size / 2.0), y - (core_size / 2.0), core_size, core_size))

            painter.setPen(QPen(QColor(255, 255, 255, max(0, min(255, int(94 * strength)))), 1.0))
            cross = event['cross'] * (0.68 + (0.36 * strength))
            painter.drawLine(QPointF(x - cross, y), QPointF(x + cross, y))
            painter.drawLine(QPointF(x, y - cross), QPointF(x, y + cross))
            painter.setPen(Qt.NoPen)

    def _paint_star_layer(
        self,
        painter: QPainter,
        rect: QRectF,
        *,
        layer_seed: float,
        total: int,
        size_base: float,
        size_span: float,
        alpha_scale: float,
        drift_min: float,
        drift_span: float,
        wave_min: float,
        wave_span: float,
        sway_min: float,
        sway_span: float,
        motion_phase: float = 0.0,
        band_bias: float = 0.0,
    ) -> None:
        for index in range(total):
            seed = layer_seed + (index * 1.0)
            seed_a = self._noise01((seed * 1.173) + 0.31)
            seed_b = self._noise01((seed * 2.417) + 1.17)
            seed_c = self._noise01((seed * 3.191) + 2.29)
            seed_d = self._noise01((seed * 4.883) + 0.73)
            seed_e = self._noise01((seed * 5.731) + 1.91)
            seed_f = self._noise01((seed * 6.419) + 3.07)
            seed_g = self._noise01((seed * 7.117) + 0.43)
            seed_h = self._noise01((seed * 8.411) + 2.61)
            seed_i = self._noise01((seed * 9.067) + 1.33)
            seed_j = self._noise01((seed * 10.233) + 0.57)
            seed_k = self._noise01((seed * 11.521) + 4.11)
            seed_l = self._noise01((seed * 12.019) + 2.03)
            seed_m = self._noise01((seed * 13.337) + 5.37)
            seed_n = self._noise01((seed * 14.907) + 6.73)

            parallax = 0.70 + (seed_c * 1.45)
            drift_x = (drift_min + (seed_d * drift_span)) * parallax
            wave_speed = wave_min + (seed_e * wave_span)
            wave_amp = 0.0020 + (seed_f * 0.0080)
            wave_offset = seed_g * math.tau * 2.0
            sway_amp = sway_min + (seed_h * sway_span)
            sway_speed = 0.34 + (seed_i * 0.96)

            x = rect.width() * ((seed_a + (motion_phase * drift_x)) % 1.0)
            y_center = seed_b + ((band_bias * 0.34) * (seed_j - 0.5))
            y_offset = math.sin((motion_phase * wave_speed) + wave_offset) * wave_amp
            x_sway = math.cos((motion_phase * sway_speed) + (wave_offset * 0.68)) * sway_amp
            y = rect.height() * ((y_center + y_offset) % 1.0)
            x += rect.width() * x_sway

            size = size_base + (seed_j * size_span)
            if seed_k > 0.90:
                size += 0.32

            color = QColor(self._palette.star_bright if seed_l > 0.80 else self._palette.star_soft)
            twinkle_phase = (motion_phase * (0.72 + (seed_m * 1.84))) + (seed_n * math.tau * 2.0)
            twinkle = 0.64 + (0.38 * (0.5 + (0.5 * math.sin(twinkle_phase))))
            shimmer = 0.86 + (0.16 * math.sin((motion_phase * 0.38 * parallax) + wave_offset))
            alpha = int(color.alpha() * twinkle * shimmer * alpha_scale)
            color.setAlpha(max(0, min(255, alpha)))
            painter.setBrush(color)
            painter.drawEllipse(QRectF(x, y, size, size))

    def _paint_stars(
        self,
        painter: QPainter,
        rect: QRectF,
        *,
        motion_phase: float = 0.0,
    ) -> None:
        if self._variant == 'progress':
            back_total = 120
            mid_total = 88
            front_total = 54
        else:
            back_total = 212
            mid_total = 146
            front_total = 88

        self._paint_star_layer(
            painter,
            rect,
            layer_seed=1400.0,
            total=back_total,
            size_base=0.42,
            size_span=0.78,
            alpha_scale=0.70,
            drift_min=0.00044,
            drift_span=0.00092,
            wave_min=0.22,
            wave_span=0.40,
            sway_min=0.0004,
            sway_span=0.0012,
            motion_phase=motion_phase,
            band_bias=0.10,
        )
        self._paint_star_layer(
            painter,
            rect,
            layer_seed=3200.0,
            total=mid_total,
            size_base=0.58,
            size_span=1.06,
            alpha_scale=0.92,
            drift_min=0.00090,
            drift_span=0.00155,
            wave_min=0.34,
            wave_span=0.62,
            sway_min=0.0008,
            sway_span=0.0018,
            motion_phase=motion_phase,
            band_bias=0.16,
        )
        self._paint_star_layer(
            painter,
            rect,
            layer_seed=5100.0,
            total=front_total,
            size_base=0.76,
            size_span=1.34,
            alpha_scale=1.14,
            drift_min=0.00126,
            drift_span=0.00210,
            wave_min=0.48,
            wave_span=0.82,
            sway_min=0.0011,
            sway_span=0.0028,
            motion_phase=motion_phase,
            band_bias=0.20,
        )

        band_count = 42 if self._variant == 'selector' else 22
        base_y = 0.60 if self._variant == 'selector' else 0.68
        spread = 0.15 if self._variant == 'selector' else 0.11
        for index in range(band_count):
            seed = 7200.0 + (index * 5.0)
            x = rect.width() * (
                (
                    0.02
                    + (self._noise01(seed) * 0.96)
                    + (motion_phase * (0.0011 + (self._noise01(seed + 1.7) * 0.0014)))
                )
                % 1.0
            )
            y = rect.height() * (
                base_y
                + ((self._noise01(seed + 2.3) - 0.5) * spread)
                + (0.010 * math.sin((motion_phase * (0.46 + (self._noise01(seed + 3.9) * 0.38))) + (self._noise01(seed + 5.1) * math.tau * 2.0)))
            )
            size = 0.86 + (self._noise01(seed + 6.7) * 1.08)
            color = QColor(self._palette.star_bright if self._noise01(seed + 8.1) > 0.76 else self._palette.star_soft)
            alpha = int(color.alpha() * (0.68 + (0.26 * (0.5 + (0.5 * math.sin((motion_phase * (0.82 + (self._noise01(seed + 9.9) * 0.42))) + index))))))
            color.setAlpha(max(0, min(255, alpha)))
            painter.setBrush(color)
            painter.drawEllipse(QRectF(x, y, size, size))

    def _paint_star_band(
        self,
        painter: QPainter,
        rect: QRectF,
        *,
        y_factor: float,
        width_factor: float,
        radius_factor: float,
        color: QColor,
        motion_phase: float = 0.0,
        drift_speed: float = 0.0024,
    ) -> None:
        for index in range(16):
            seed = 2100.0 + (index * 9.0)
            cx = rect.width() * (
                (0.04 + (self._noise01(seed) * max(0.24, width_factor)) + (motion_phase * drift_speed * (0.8 + (self._noise01(seed + 1.7) * 2.2)))) % 1.12
            )
            cy = rect.height() * (
                y_factor
                + ((self._noise01(seed + 2.9) - 0.5) * 0.10)
                + (0.020 * math.sin((motion_phase * (0.54 + (self._noise01(seed + 3.8) * 0.50))) + (self._noise01(seed + 5.1) * math.tau * 2.0)))
            )
            radius = rect.width() * (radius_factor * (0.34 + (self._noise01(seed + 6.2) * 0.54)))
            orb = QRadialGradient(cx, cy, radius)
            edge = QColor(color)
            edge.setAlpha(0)
            mid = QColor(color)
            mid.setAlpha(max(0, int(color.alpha() * (0.22 + (self._noise01(seed + 7.9) * 0.18)))))
            core = QColor(color)
            core.setAlpha(max(0, min(255, int(color.alpha() * (0.72 + (0.42 * math.sin((motion_phase * (0.72 + (self._noise01(seed + 8.6) * 0.42))) + index)))))))
            orb.setColorAt(0.0, core)
            orb.setColorAt(0.42, mid)
            orb.setColorAt(1.0, edge)
            painter.setBrush(orb)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0))

    def _paint_silver_field(self, painter: QPainter, rect: QRectF) -> None:
        motion_phase = self._motion_time()

        bg_gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        bg_gradient.setColorAt(0.0, self._palette.canvas_top)
        bg_gradient.setColorAt(1.0, self._palette.canvas_bottom)
        painter.fillRect(rect, bg_gradient)

        top_wash = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
        top_wash.setColorAt(0.0, QColor(255, 255, 255, 18))
        top_wash.setColorAt(0.38, QColor(156, 224, 255, 8))
        top_wash.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, top_wash)

        for color, cx, cy, radius in self._orb_specs(rect, motion_phase=motion_phase):
            orb = QRadialGradient(cx, cy, radius)
            edge = QColor(color)
            edge.setAlpha(0)
            mid = QColor(color)
            mid.setAlpha(max(0, int(color.alpha() * 0.42)))
            orb.setColorAt(0.0, color)
            orb.setColorAt(0.40, mid)
            orb.setColorAt(1.0, edge)
            painter.setBrush(orb)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0))

        self._paint_star_band(
            painter,
            rect,
            y_factor=0.56 if self._variant == 'selector' else 0.68,
            width_factor=0.90,
            radius_factor=0.09 if self._variant == 'selector' else 0.07,
            color=QColor(255, 255, 255, 34 if self._variant == 'selector' else 24),
            motion_phase=motion_phase,
            drift_speed=0.0040 if self._variant == 'selector' else 0.0028,
        )
        self._paint_star_band(
            painter,
            rect,
            y_factor=0.22 if self._variant == 'selector' else 0.28,
            width_factor=0.74,
            radius_factor=0.07 if self._variant == 'selector' else 0.06,
            color=QColor(140, 239, 255, 26 if self._variant == 'selector' else 18),
            motion_phase=motion_phase,
            drift_speed=0.0028 if self._variant == 'selector' else 0.0020,
        )
        self._paint_stars(
            painter,
            rect,
            motion_phase=motion_phase,
        )
        self._paint_spark_flashes(
            painter,
            rect,
            motion_phase=motion_phase,
        )

        vignette = QRadialGradient(rect.center(), max(rect.width(), rect.height()) * 0.78)
        vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
        vignette.setColorAt(0.78, QColor(0, 0, 0, 0))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 76 if self._variant == 'selector' else 58))
        painter.setBrush(vignette)
        painter.drawRect(rect)

        frame_path = QPainterPath()
        frame_path.addRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 30.0, 30.0)
        painter.fillPath(frame_path, self._palette.wash)
        # CODE_ATLAS_FRAME_DEPTH_FIX_V1: outer stage rim intentionally not drawn.

        painter.setPen(QPen(self._palette.sheen, 1.0))
        arc_start = int((18.0 + (math.sin(motion_phase * 0.24) * 14.0)) * 16)
        arc_span = int((122.0 + (math.cos(motion_phase * 0.17) * 10.0)) * 16)
        painter.drawArc(
            QRectF(rect.width() * 0.06, rect.height() * 0.02, rect.width() * 0.88, rect.height() * 0.18),
            arc_start,
            arc_span,
        )

        painter.setBrush(self._palette.sparkle)
        painter.setPen(Qt.NoPen)
        sparkle_size = 8.0 if self._variant == 'progress' else 10.0
        sparkle_x = rect.width() * ((0.88 if self._variant == 'selector' else 0.74) + (0.014 * math.sin(motion_phase * 0.54)))
        sparkle_y = rect.height() * (0.12 + (0.016 * math.cos(motion_phase * 0.46)))
        painter.drawEllipse(
            QRectF(
                sparkle_x,
                sparkle_y,
                sparkle_size,
                sparkle_size,
            )
        )

    def paintEvent(self, event) -> None:  # type: ignore[override]
        rect = QRectF(self.rect())
        if rect.width() <= 1.0 or rect.height() <= 1.0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect.adjusted(0.75, 0.75, -0.75, -0.75), 30.0, 30.0)
        painter.save()
        painter.setClipPath(clip_path)

        if _is_silver_theme_id(self._theme_id):
            self._paint_silver_field(painter, rect)
            painter.restore()
            painter.end()
            return

        motion_phase = self._motion_time()
        bg_gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        bg_gradient.setColorAt(0.0, self._palette.canvas_top)
        bg_gradient.setColorAt(1.0, self._palette.canvas_bottom)
        painter.fillRect(rect, bg_gradient)

        for color, cx, cy, radius in self._orb_specs(rect, motion_phase=motion_phase):
            orb = QRadialGradient(cx, cy, radius)
            edge = QColor(color)
            edge.setAlpha(0)
            orb.setColorAt(0.0, color)
            orb.setColorAt(0.48, QColor(color.red(), color.green(), color.blue(), max(0, int(color.alpha() * 0.46))))
            orb.setColorAt(1.0, edge)
            painter.setBrush(orb)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0))

        self._paint_stars(painter, rect, motion_phase=motion_phase)

        glass_path = QPainterPath()
        glass_path.addRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 30.0, 30.0)
        painter.fillPath(glass_path, self._palette.wash)

        # CODE_ATLAS_FRAME_DEPTH_FIX_V1: outer stage rim intentionally not drawn.

        sheen_path = QPainterPath()
        sheen_path.moveTo(rect.width() * 0.06, rect.height() * 0.12)
        sheen_path.cubicTo(
            rect.width() * 0.32,
            rect.height() * 0.02,
            rect.width() * 0.56,
            rect.height() * 0.10,
            rect.width() * 0.88,
            rect.height() * 0.04,
        )
        painter.setPen(QPen(self._palette.sheen, 1.4))
        painter.drawPath(sheen_path)

        painter.setPen(QPen(self._palette.line, 1.0))
        if self._variant == "progress":
            lines = (0.34, 0.58, 0.80)
        else:
            lines = (0.18, 0.46, 0.74)
        for factor in lines:
            y = rect.height() * factor
            painter.drawLine(
                rect.width() * 0.08,
                y,
                rect.width() * 0.92,
                y - (rect.height() * 0.06),
            )

        painter.setBrush(self._palette.sparkle)
        painter.setPen(Qt.NoPen)
        sparkle_size = 8.0 if self._variant == "progress" else 10.0
        painter.drawEllipse(
            QRectF(
                rect.width() * (0.84 if self._variant == "selector" else 0.72),
                rect.height() * 0.12,
                sparkle_size,
                sparkle_size,
            )
        )
        painter.restore()
        painter.end()

def build_glass_dialog_scene(
    host: QWidget,
    *,
    theme_id: str,
    variant: str,
    margins: tuple[int, int, int, int],
) -> tuple[QVBoxLayout, QWidget, FrostedGlassBackdrop]:
    # R1 bridge: use shared stage composer while keeping code-atlas backdrop behavior.
    def _backdrop_factory(stage: QWidget) -> QWidget:
        return FrostedGlassBackdrop(stage, theme_id=theme_id, variant=variant)

    outer, content, backdrop = shared_build_glass_dialog_scene(
        host,
        theme_id=theme_id,
        variant=variant,
        margins=margins,
        motion_enabled=True,
        apply_stylesheet=False,
        backdrop_factory=_backdrop_factory,
    )
    return outer, content, backdrop


class _HoverCardFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if isinstance(watched, QWidget):
            if event.type() in {QEvent.Enter, QEvent.HoverEnter}:
                watched.setProperty("hover", True)
                repolish(watched)
            elif event.type() in {QEvent.Leave, QEvent.HoverLeave}:
                watched.setProperty("hover", False)
                repolish(watched)
        return False


_CARD_HOVER_FILTER: _HoverCardFilter | None = None


def enable_card_hover(widget: QWidget) -> None:
    global _CARD_HOVER_FILTER
    if widget is None:
        return
    if _CARD_HOVER_FILTER is None:
        _CARD_HOVER_FILTER = _HoverCardFilter()
    widget.setAttribute(Qt.WA_Hover, True)
    widget.setMouseTracking(True)
    widget.setProperty("hoverable", True)
    widget.setProperty("hover", False)
    widget.installEventFilter(_CARD_HOVER_FILTER)


_EDGE_NONE = 0
_EDGE_LEFT = 1
_EDGE_TOP = 2
_EDGE_RIGHT = 4
_EDGE_BOTTOM = 8


def _global_point_from_event(event: Any) -> QPoint:
    try:
        return event.globalPosition().toPoint()
    except Exception:
        return QPoint()


def _local_point_from_event(event: Any) -> QPoint:
    try:
        return event.position().toPoint()
    except Exception:
        return QPoint()


class _FramelessResizeCorner(QWidget):
    def __init__(
        self,
        host: QDialog,
        controller: "FramelessResizeController",
        *,
        edges: int,
        corner: str,
    ) -> None:
        super().__init__(host)
        self._host = host
        self._controller = controller
        self._edges = edges
        self._corner = corner
        self._dragging = False
        self.setObjectName(f"ResizeCorner_{corner}")
        self.setFixedSize(12, 12)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(
            Qt.SizeBDiagCursor if edges == (_EDGE_TOP | _EDGE_RIGHT) else Qt.SizeFDiagCursor
        )
        self.setToolTip("Arrastra para redimensionar")
        self.hide()

    def paintEvent(self, event: Any) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        line = QColor("#dff8ff")
        line.setAlpha(102)
        pen = QPen(line, 1.0)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        w = self.width()
        h = self.height()
        if self._corner == "top_right":
            painter.drawLine(w - 5, 3, w - 2, 6)
            painter.drawLine(w - 8, 3, w - 2, 9)
        else:
            painter.drawLine(w - 5, h - 3, w - 2, h - 6)
            painter.drawLine(w - 8, h - 3, w - 2, h - 9)
        painter.end()

    def mousePressEvent(self, event: Any) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton or self._host.isMaximized():
            super().mousePressEvent(event)
            return
        self._dragging = True
        self.grabMouse()
        self._controller.start_corner_resize(self._edges, _global_point_from_event(event))
        event.accept()

    def mouseMoveEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging and bool(event.buttons() & Qt.LeftButton):
            self._controller.update_corner_resize(_global_point_from_event(event))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging and event.button() == Qt.LeftButton:
            self._dragging = False
            self.releaseMouse()
            self._controller.finish_corner_resize()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def hideEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging:
            self._dragging = False
            self.releaseMouse()
            self._controller.finish_corner_resize()
        super().hideEvent(event)


class FramelessResizeController(QObject):
    def __init__(self, host: QDialog, *, margin: int = 8) -> None:
        self._host = host
        super().__init__(host)
        self._margin = max(4, int(margin))
        self._active_edges = _EDGE_NONE
        self._resizing = False
        self._press_global = QPoint()
        self._start_geometry = QRect()
        self._top_right_corner = _FramelessResizeCorner(
            host,
            self,
            edges=_EDGE_TOP | _EDGE_RIGHT,
            corner="top_right",
        )
        self._bottom_right_corner = _FramelessResizeCorner(
            host,
            self,
            edges=_EDGE_BOTTOM | _EDGE_RIGHT,
            corner="bottom_right",
        )
        self._host.installEventFilter(self)
        self._host.setMouseTracking(True)
        self._layout_corner_handles()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        host = getattr(self, "_host", None)
        if host is None:
            return False
        if watched is not host:
            return False

        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress:
            return self._on_mouse_press(event)
        if event_type == QEvent.Type.MouseMove:
            return self._on_mouse_move(event)
        if event_type == QEvent.Type.MouseButtonRelease:
            return self._on_mouse_release(event)
        if event_type in {QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.WindowStateChange}:
            self._layout_corner_handles()
            return False
        if event_type == QEvent.Type.Leave:
            if not self._resizing:
                self._host.unsetCursor()
            return False
        return False

    def _edge_mask_at(self, pos: QPoint) -> int:
        if self._host.isMaximized():
            return _EDGE_NONE

        rect = self._host.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return _EDGE_NONE

        right = pos.x() >= (rect.width() - self._margin)
        top = pos.y() <= self._margin
        bottom = pos.y() >= (rect.height() - self._margin)

        mask = _EDGE_NONE
        if right and top:
            mask = _EDGE_TOP | _EDGE_RIGHT
        elif right and bottom:
            mask = _EDGE_BOTTOM | _EDGE_RIGHT
        return mask

    def _cursor_for_edges(self, edges: int) -> Qt.CursorShape:
        if edges in {_EDGE_TOP | _EDGE_LEFT, _EDGE_BOTTOM | _EDGE_RIGHT}:
            return Qt.SizeFDiagCursor
        if edges in {_EDGE_TOP | _EDGE_RIGHT, _EDGE_BOTTOM | _EDGE_LEFT}:
            return Qt.SizeBDiagCursor
        if edges in {_EDGE_LEFT, _EDGE_RIGHT}:
            return Qt.SizeHorCursor
        if edges in {_EDGE_TOP, _EDGE_BOTTOM}:
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def _apply_resize_cursor(self, edges: int) -> None:
        cursor_shape = self._cursor_for_edges(edges)
        if cursor_shape == Qt.ArrowCursor:
            self._host.unsetCursor()
            return
        self._host.setCursor(cursor_shape)

    def _on_mouse_press(self, event: Any) -> bool:
        if self._host.isMaximized():
            return False
        if event.button() != Qt.LeftButton:
            return False

        edges = self._edge_mask_at(_local_point_from_event(event))
        if edges == _EDGE_NONE:
            return False

        self.start_corner_resize(edges, _global_point_from_event(event))
        event.accept()
        return True

    def _on_mouse_move(self, event: Any) -> bool:
        if self._host.isMaximized():
            if not self._resizing:
                self._host.unsetCursor()
            return False

        if self._resizing:
            if not bool(event.buttons() & Qt.LeftButton):
                self._resizing = False
                self._active_edges = _EDGE_NONE
                self._host.unsetCursor()
                return False
            self._resize_to(_global_point_from_event(event))
            event.accept()
            return True

        edges = self._edge_mask_at(_local_point_from_event(event))
        self._apply_resize_cursor(edges)
        return False

    def _on_mouse_release(self, event: Any) -> bool:
        if not self._resizing or event.button() != Qt.LeftButton:
            return False

        self.finish_corner_resize()
        event.accept()
        return True

    def _layout_corner_handles(self) -> None:
        if self._host.isMaximized():
            self._top_right_corner.hide()
            self._bottom_right_corner.hide()
            return

        size = self._top_right_corner.width()
        inset = 8
        width = self._host.width()
        height = self._host.height()

        self._top_right_corner.setGeometry(max(0, width - size - inset), inset, size, size)
        self._bottom_right_corner.setGeometry(max(0, width - size - inset), max(0, height - size - inset), size, size)
        self._top_right_corner.show()
        self._bottom_right_corner.show()
        self._top_right_corner.raise_()
        self._bottom_right_corner.raise_()

    def start_corner_resize(self, edges: int, global_pos: QPoint) -> None:
        if self._host.isMaximized() or edges == _EDGE_NONE:
            return
        self._active_edges = edges
        self._resizing = True
        self._press_global = global_pos
        self._start_geometry = self._host.geometry()
        self._apply_resize_cursor(edges)

    def update_corner_resize(self, global_pos: QPoint) -> None:
        self._resize_to(global_pos)

    def finish_corner_resize(self) -> None:
        self._resizing = False
        self._active_edges = _EDGE_NONE
        self._host.unsetCursor()

    def _resize_to(self, global_pos: QPoint) -> None:
        if self._active_edges == _EDGE_NONE:
            return

        dx = global_pos.x() - self._press_global.x()
        dy = global_pos.y() - self._press_global.y()

        geom = QRect(self._start_geometry)
        min_width = max(320, int(self._host.minimumWidth() or 0))
        min_height = max(220, int(self._host.minimumHeight() or 0))

        if self._active_edges & _EDGE_LEFT:
            proposed_left = geom.left() + dx
            max_left = geom.right() - min_width + 1
            geom.setLeft(min(proposed_left, max_left))
        if self._active_edges & _EDGE_RIGHT:
            proposed_right = geom.right() + dx
            min_right = geom.left() + min_width - 1
            geom.setRight(max(proposed_right, min_right))
        if self._active_edges & _EDGE_TOP:
            proposed_top = geom.top() + dy
            max_top = geom.bottom() - min_height + 1
            geom.setTop(min(proposed_top, max_top))
        if self._active_edges & _EDGE_BOTTOM:
            proposed_bottom = geom.bottom() + dy
            min_bottom = geom.top() + min_height - 1
            geom.setBottom(max(proposed_bottom, min_bottom))

        self._host.setGeometry(geom)


class WindowChromeBar(QFrame):
    def __init__(
        self,
        host: QDialog,
        *,
        title: str,
        on_close: Optional[Callable[[], Any]] = None,
        allow_minimize: bool = True,
        allow_maximize: bool = True,
    ) -> None:
        self._host = host
        super().__init__(host)
        self._on_close = on_close
        self._allow_maximize = bool(allow_maximize)
        self._dragging = False
        self._drag_offset = QPoint()

        self.setObjectName("WindowChrome")
        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 6, 5)
        layout.setSpacing(6)

        icon = QLabel("▣", self)
        icon.setProperty("role", "window_icon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedWidth(18)
        layout.addWidget(icon, 0)

        self._title_label = QLabel(clean_text(title) or APP_TITLE, self)
        self._title_label.setProperty("role", "window_title")
        self._title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self._title_label, 1)

        self._min_button = self._make_chrome_button("—", "min", "Minimizar")
        self._max_button = self._make_chrome_button("□", "max", "Maximizar / Restaurar")
        self._close_button = self._make_chrome_button("×", "close", "Cerrar")

        if allow_minimize:
            layout.addWidget(self._min_button, 0)
        else:
            self._min_button.hide()

        if self._allow_maximize:
            layout.addWidget(self._max_button, 0)
        else:
            self._max_button.hide()

        layout.addWidget(self._close_button, 0)

        self._min_button.clicked.connect(self._host.showMinimized)
        self._max_button.clicked.connect(self._toggle_max_restore)
        self._close_button.clicked.connect(self._handle_close)

        self._host.installEventFilter(self)
        self._sync_max_button()

    def _make_chrome_button(self, text: str, kind: str, tooltip: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setProperty("chrome", True)
        button.setProperty("chrome_kind", kind)
        button.setFocusPolicy(Qt.NoFocus)
        button.setToolTip(tooltip)
        button.setFixedSize(30, 22)
        return button

    def _handle_close(self) -> None:
        if callable(self._on_close):
            self._on_close()
            return
        self._host.close()

    def _toggle_max_restore(self) -> None:
        if not self._allow_maximize:
            return
        if self._host.isMaximized():
            self._host.showNormal()
        else:
            self._host.showMaximized()
        self._sync_max_button()

    def _sync_max_button(self) -> None:
        if not self._allow_maximize:
            return
        self._max_button.setText("❐" if self._host.isMaximized() else "□")
        self._max_button.setToolTip("Restaurar" if self._host.isMaximized() else "Maximizar")

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        host = getattr(self, "_host", None)
        if host is None:
            return False
        if watched is not host:
            return False

        if event.type() == QEvent.Type.WindowTitleChange:
            self._title_label.setText(clean_text(self._host.windowTitle()) or APP_TITLE)
        elif event.type() == QEvent.Type.WindowStateChange:
            self._sync_max_button()
        return False

    def _is_pointer_on_button(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        return isinstance(child, QPushButton)

    def mouseDoubleClickEvent(self, event: Any) -> None:  # type: ignore[override]
        if (
            event.button() == Qt.LeftButton
            and self._allow_maximize
            and not self._is_pointer_on_button(_local_point_from_event(event))
        ):
            self._toggle_max_restore()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: Any) -> None:  # type: ignore[override]
        if (
            event.button() == Qt.LeftButton
            and not self._is_pointer_on_button(_local_point_from_event(event))
            and not self._host.isMaximized()
        ):
            self._dragging = True
            self._drag_offset = _global_point_from_event(event) - self._host.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Any) -> None:  # type: ignore[override]
        if self._dragging and bool(event.buttons() & Qt.LeftButton):
            if self._host.isMaximized():
                self._dragging = False
            else:
                self._host.move(_global_point_from_event(event) - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._dragging = False
        super().mouseReleaseEvent(event)


def app_stylesheet(theme_id: Optional[str] = None) -> str:
    resolved_theme = normalize_theme(theme_id or DEFAULT_THEME)
    # Shared template base first; local stylesheet keeps final parity by overriding specifics.
    shared_base = shared_build_stylesheet(resolved_theme)
    local_overrides = build_app_stylesheet(resolved_theme)
    return f"{shared_base}\n{local_overrides}"


def create_button(
    text: str,
    variant: str,
    callback: Optional[Callable[..., Any]] = None,
    *,
    tooltip: str = "",
    default: bool = False,
    auto_default: Optional[bool] = None,
    minimum_width: int = 0,
    enabled: bool = True,
    parent: Optional[QWidget] = None,
) -> QPushButton:
    button = shared_create_button(
        text,
        variant or "secondary",
        callback,
        parent=parent,
        tooltip=tooltip or None,
        default=bool(default),
        minimum_width=int(minimum_width) if minimum_width > 0 else None,
    )
    button.setEnabled(enabled)
    button.setAutoDefault(bool(default) if auto_default is None else bool(auto_default))

    shadow_alpha = {
        "primary": 28,
        "secondary": 14,
        "success": 22,
        "danger": 16,
    }.get((variant or "secondary").strip().lower(), 14)
    shadow_blur = 16.0 if (variant or "").strip().lower() == "primary" else 12.0

    apply_shadow(button, blur=shadow_blur, y_offset=4.0, alpha=shadow_alpha)
    repolish(button)
    return button


def make_separator() -> QFrame:
    line = QFrame()
    line.setObjectName("Line")
    line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    return line


class SelectorDialog(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        window_title: Optional[str] = None,
        initial_path: Optional[str | os.PathLike[str]] = None,
        initial_theme: Optional[str] = None,
        initial_view: Optional[str] = None,
        initial_focus_target: Optional[str] = None,
        theme_items: Optional[Iterable[Any]] = None,
        theme_label_to_id: Optional[Mapping[str, str]] = None,
        theme_id_to_label: Optional[Mapping[str, str]] = None,
        theme_dropdown_labels: Optional[Iterable[str]] = None,
        default_theme: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        ensure_app()

        self.root = self
        self._selection_result: Optional[SelectionResult] = None
        self._theme_catalog = _resolve_theme_catalog(
            theme_items=theme_items,
            theme_label_to_id=theme_label_to_id,
            theme_id_to_label=theme_id_to_label,
            theme_dropdown_labels=theme_dropdown_labels,
            default_theme=default_theme,
        )

        self.setWindowTitle(window_title or _app_title())
        self.setModal(True)
        self.setMinimumSize(920, 660)
        self.resize(980, 700)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        apply_window_transparency(self)
        self._resize_controller = FramelessResizeController(self, margin=8)
        self._applied_theme_id = ""

        self._build_ui()
        self._apply_initial_state(
            initial_path=initial_path,
            initial_theme=initial_theme,
            initial_view=initial_view,
            initial_focus_target=initial_focus_target,
        )
        self.apply_theme_stylesheet()
        self.update_focus_state()
        self.refresh_preview()

    @property
    def selected_path(self) -> Optional[str]:
        text = _normalize_path_text(self.path_entry.text())
        return text or None

    @selected_path.setter
    def selected_path(self, value: Optional[str]) -> None:
        self.path_entry.setText(_normalize_path_text(value or ""))

    @property
    def selected_theme(self) -> str:
        return _normalize_theme_from_catalog(self.theme_combo.currentText(), self._theme_catalog)

    @selected_theme.setter
    def selected_theme(self, value: Optional[str]) -> None:
        theme_id = _normalize_theme_from_catalog(value, self._theme_catalog)
        label = self._theme_catalog.id_to_label.get(theme_id, self._theme_catalog.labels[0])
        self.theme_combo.setCurrentText(label)

    @property
    def selected_view(self) -> GraphView:
        return VIEW_LABEL_TO_ID.get(_clean_text(self.view_combo.currentText()), _default_view_id())

    @selected_view.setter
    def selected_view(self, value: Optional[str]) -> None:
        view_id = _coerce_view(value)
        self.view_combo.setCurrentText(VIEW_ID_TO_LABEL.get(view_id, VIEW_DROPDOWN_LABELS[0]))

    @property
    def selected_focus_target(self) -> str:
        return _clean_text(self.focus_entry.text())

    @selected_focus_target.setter
    def selected_focus_target(self, value: Optional[str]) -> None:
        self.focus_entry.setText(_clean_text(value))

    def apply_theme_stylesheet(self, theme_id: Optional[str] = None) -> None:
        resolved_theme = normalize_theme(theme_id or self.selected_theme or self._theme_catalog.default_id)
        if resolved_theme == self._applied_theme_id:
            return
        self.setStyleSheet(app_stylesheet(resolved_theme))
        if getattr(self, "_glass_backdrop", None) is not None:
            self._glass_backdrop.apply_theme(resolved_theme)
        self._applied_theme_id = resolved_theme

    def on_theme_changed(self) -> None:
        self.apply_theme_stylesheet()
        self.refresh_preview()

    def result_selection(self) -> SelectionResult:
        if self._selection_result is not None:
            return self._selection_result
        return _make_selection_result(
            path=self.selected_path,
            theme=self.selected_theme,
            view=self.selected_view,
            focus_target=self.selected_focus_target,
        )

    def _build_ui(self) -> None:
        outer, content_layer, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._theme_catalog.default_id,
            variant="selector",
            margins=(0, 0, 0, 0),
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content_layer)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("Shell")
        shell.setProperty("variant", "selector")
        apply_shadow(shell, blur=30.0, y_offset=10.0, alpha=58)
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(22, 22, 22, 22)
        shell_layout.setSpacing(18)

        self.window_chrome = WindowChromeBar(
            self,
            title=self.windowTitle(),
            on_close=self.cancel,
            allow_minimize=True,
            allow_maximize=True,
        )
        shell_layout.addWidget(self.window_chrome)

        header = QFrame()
        header.setProperty("card", "hero")
        apply_shadow(header, blur=22.0, y_offset=8.0, alpha=18)
        enable_card_hover(header)
        shell_layout.addWidget(header)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 20, 22, 20)
        header_layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        header_layout.addLayout(top_row)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(6)
        top_row.addLayout(title_stack, 1)

        eyebrow = QLabel("Workspace")
        eyebrow.setProperty("role", "eyebrow")
        title_stack.addWidget(eyebrow, 0, Qt.AlignLeft)

        title = QLabel("Dependency Graph SVG")
        title.setProperty("role", "title")
        title_stack.addWidget(title)

        subtitle = QLabel(
            "Elige la ruta, el tema y la vista. La ruta es editable para pegar, corregir o afinar "
            "sin andar peleándote con el explorador."
        )
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        title_stack.addWidget(subtitle)

        chrome_stack = QVBoxLayout()
        chrome_stack.setSpacing(8)
        top_row.addLayout(chrome_stack, 0)

        self.mode_chip = QLabel("Selector")
        self.mode_chip.setProperty("chip", True)
        self.mode_chip.setProperty("tone", "accent")
        self.mode_chip.setAlignment(Qt.AlignCenter)
        chrome_stack.addWidget(self.mode_chip, 0, Qt.AlignRight)

        scene_chip = QLabel("PySide6 Glass")
        scene_chip.setProperty("chip", True)
        scene_chip.setProperty("tone", "neutral")
        scene_chip.setAlignment(Qt.AlignCenter)
        chrome_stack.addWidget(scene_chip, 0, Qt.AlignRight)
        chrome_stack.addStretch(1)

        header_line = make_separator()
        header_line.setProperty("tone", "glow")
        repolish(header_line)
        header_layout.addWidget(header_line)

        content = QHBoxLayout()
        content.setSpacing(18)
        shell_layout.addLayout(content, 1)

        self.form_card = QFrame()
        self.form_card.setProperty("card", "true")
        self.form_card.setProperty("surface", "crisp")
        apply_shadow(self.form_card, blur=18.0, y_offset=6.0, alpha=16)
        enable_card_hover(self.form_card)
        content.addWidget(self.form_card, 6)

        self.preview_card = QFrame()
        self.preview_card.setProperty("card", "muted")
        self.preview_card.setProperty("surface", "soft")
        apply_shadow(self.preview_card, blur=18.0, y_offset=6.0, alpha=14)
        enable_card_hover(self.preview_card)
        content.addWidget(self.preview_card, 5)

        self._build_form_panel()
        self._build_preview_panel()

        footer = QFrame()
        footer.setProperty("card", "footer")
        apply_shadow(footer, blur=14.0, y_offset=5.0, alpha=10)
        enable_card_hover(footer)
        shell_layout.addWidget(footer)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(18, 14, 18, 14)
        footer_layout.setSpacing(12)

        footer_text_stack = QVBoxLayout()
        footer_text_stack.setSpacing(4)
        footer_layout.addLayout(footer_text_stack, 1)

        footer_label = QLabel("Output")
        footer_label.setProperty("role", "eyebrow")
        footer_text_stack.addWidget(footer_label, 0, Qt.AlignLeft)

        footer_hint = QLabel(
            "SVG se guarda junto al proyecto; los Trees se guardan en F:\\trees."
        )
        footer_hint.setProperty("role", "hint")
        footer_hint.setWordWrap(True)
        footer_text_stack.addWidget(footer_hint)

        self.cancel_button = create_button("Cancelar", "danger", self.cancel, minimum_width=124)
        self.confirm_button = create_button(
            "Generar SVG",
            "primary",
            self.confirm,
            default=True,
            minimum_width=156,
        )
        self.tree_button = create_button(
            "Generar Tree .txt",
            "secondary",
            self.confirm_tree,
            minimum_width=172,
        )
        self.tree_html_button = create_button(
            "Generar Tree HTML Premium",
            "secondary",
            self.confirm_tree_html,
            minimum_width=232,
        )
        footer_layout.addWidget(self.cancel_button, 0)
        footer_layout.addWidget(self.tree_button, 0)
        footer_layout.addWidget(self.tree_html_button, 0)
        footer_layout.addWidget(self.confirm_button, 0)

    def _build_form_panel(self) -> None:
        layout = QVBoxLayout(self.form_card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        section_title = QLabel("Origen")
        section_title.setProperty("role", "section")
        layout.addWidget(section_title)

        path_label = QLabel("Ruta")
        path_label.setProperty("role", "field")
        layout.addWidget(path_label)

        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("Pega una carpeta o archivo aquí")
        self.path_entry.setClearButtonEnabled(True)
        self.path_entry.textChanged.connect(self.refresh_preview)
        layout.addWidget(self.path_entry)

        picker_row = QHBoxLayout()
        picker_row.setSpacing(10)
        layout.addLayout(picker_row)

        self.folder_button = create_button(
            "Elegir carpeta",
            "secondary",
            self.pick_directory,
            tooltip="Selecciona una carpeta a analizar",
        )
        self.file_button = create_button(
            "Elegir archivo",
            "secondary",
            self.pick_file,
            tooltip="Selecciona un archivo Python",
        )
        picker_row.addWidget(self.folder_button)
        picker_row.addWidget(self.file_button)
        picker_row.addStretch(1)

        path_hint = QLabel(
            "Puedes escribir la ruta manualmente. Si ya apunta a un archivo, el selector abrirá desde su carpeta padre."
        )
        path_hint.setProperty("role", "hint")
        path_hint.setWordWrap(True)
        layout.addWidget(path_hint)

        layout.addWidget(make_separator())

        options_title = QLabel("Opciones")
        options_title.setProperty("role", "section")
        layout.addWidget(options_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)
        layout.addLayout(grid)

        theme_label = QLabel("Tema")
        theme_label.setProperty("role", "field")
        grid.addWidget(theme_label, 0, 0)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(self._theme_catalog.labels))
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        grid.addWidget(self.theme_combo, 0, 1)

        view_label = QLabel("Vista")
        view_label.setProperty("role", "field")
        grid.addWidget(view_label, 1, 0)

        self.view_combo = QComboBox()
        self.view_combo.addItems(VIEW_DROPDOWN_LABELS)
        self.view_combo.currentIndexChanged.connect(self.on_view_changed)
        grid.addWidget(self.view_combo, 1, 1)

        self.focus_label = QLabel("Objetivo de foco")
        self.focus_label.setProperty("role", "field")
        grid.addWidget(self.focus_label, 2, 0)

        self.focus_entry = QLineEdit()
        self.focus_entry.setClearButtonEnabled(True)
        self.focus_entry.textChanged.connect(self.refresh_preview)
        grid.addWidget(self.focus_entry, 2, 1)

        self.focus_hint = QLabel("")
        self.focus_hint.setProperty("role", "hint")
        self.focus_hint.setWordWrap(True)
        grid.addWidget(self.focus_hint, 3, 1)

        grid.setColumnStretch(1, 1)
        layout.addStretch(1)

    def _build_preview_panel(self) -> None:
        layout = QVBoxLayout(self.preview_card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        section_title = QLabel("Vista previa")
        section_title.setProperty("role", "section")
        layout.addWidget(section_title)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(8)
        layout.addLayout(chip_row)

        self.path_kind_chip = QLabel("Sin ruta")
        self.path_kind_chip.setProperty("chip", True)
        self.path_kind_chip.setProperty("tone", "neutral")
        chip_row.addWidget(self.path_kind_chip, 0)

        self.focus_state_chip = QLabel("Foco inactivo")
        self.focus_state_chip.setProperty("chip", True)
        self.focus_state_chip.setProperty("tone", "neutral")
        chip_row.addWidget(self.focus_state_chip, 0)

        chip_row.addStretch(1)

        chosen_path_label = QLabel("Ruta actual")
        chosen_path_label.setProperty("role", "field")
        layout.addWidget(chosen_path_label)

        self.path_value = QLabel("(ninguna)")
        self.path_value.setProperty("role", "mono")
        self.path_value.setWordWrap(True)
        self.path_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.path_value)

        layout.addWidget(make_separator())

        summary_title = QLabel("Resumen de selección")
        summary_title.setProperty("role", "field")
        layout.addWidget(summary_title)

        self.summary_value = QLabel("")
        self.summary_value.setProperty("role", "value")
        self.summary_value.setWordWrap(True)
        self.summary_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.summary_value)

        detail_title = QLabel("Contexto útil")
        detail_title.setProperty("role", "field")
        layout.addWidget(detail_title)

        self.detail_value = QLabel("")
        self.detail_value.setProperty("role", "mono")
        self.detail_value.setWordWrap(True)
        self.detail_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.detail_value)

        layout.addStretch(1)

        note = QLabel(
            "Si eliges un archivo, el análisis usa su carpeta como ancla de salida. "
            f"El SVG caerá en la subcarpeta <b>{_output_subdir_name()}</b>."
        )
        note.setProperty("role", "hint")
        note.setWordWrap(True)
        note.setTextFormat(Qt.RichText)
        layout.addWidget(note)

    def _apply_initial_state(
        self,
        *,
        initial_path: Optional[str | os.PathLike[str]],
        initial_theme: Optional[str],
        initial_view: Optional[str],
        initial_focus_target: Optional[str],
    ) -> None:
        self.selected_path = str(initial_path) if initial_path is not None else None
        self.selected_theme = initial_theme or self._theme_catalog.default_id
        self.selected_view = initial_view or _default_view_id()
        self.selected_focus_target = initial_focus_target or ""

    def _set_chip(self, label: QLabel, text: str, tone: str) -> None:
        label.setText(text)
        label.setProperty("tone", tone)
        repolish(label)

    def update_focus_state(self) -> None:
        is_focus = self.selected_view == "focus"
        self.focus_entry.setEnabled(is_focus)

        if is_focus:
            self.focus_label.setText("Objetivo de foco")
            self.focus_entry.setPlaceholderText("Ej. forgeos.core, apps.main, tools.build")
            self.focus_hint.setText(
                "Aplica en vista Foco. Déjalo vacío y el sistema podrá inferirlo después si corresponde."
            )
            self._set_chip(self.focus_state_chip, "Foco activo", "accent")
            self.mode_chip.setText("Vista Foco")
        else:
            self.focus_label.setText("Objetivo de foco")
            self.focus_entry.setPlaceholderText("Solo disponible en vista Foco")
            self.focus_hint.setText(
                "Este campo no afecta las vistas Paquetes o Módulos."
            )
            self._set_chip(self.focus_state_chip, "Foco inactivo", "neutral")
            self.mode_chip.setText("Selector")

    def _preview_summary_lines(self, path_state: _PathState) -> list[str]:
        lines = [
            f"Tema: {self.selected_theme}",
            f"Vista: {self.selected_view}",
        ]

        if self.selected_view == "focus":
            lines.append(
                f"Foco: {self.selected_focus_target or '(auto si el pipeline lo decide)'}"
            )
        else:
            lines.append("Foco: no aplica para la vista actual")

        if path_state.kind == "folder":
            lines.append("Ruta interpretada como: carpeta")
        elif path_state.kind == "file":
            lines.append("Ruta interpretada como: archivo")
        elif path_state.kind == "manual":
            lines.append("Ruta interpretada como: valor manual por validar")
        else:
            lines.append("Ruta interpretada como: sin selección")

        return lines

    def _preview_detail_lines(self, path_state: _PathState) -> list[str]:
        lines = [
            f"Ruta visible: {_short_path(path_state.display if path_state.display != '(ninguna)' else '') or '(ninguna)'}",
            f"Existe: {'sí' if path_state.exists else 'no'}",
            f"Ancla de salida: {_output_anchor_text(path_state)}",
            f"Subcarpeta de salida: {_output_subdir_name()}",
        ]

        if self.selected_view == "focus":
            lines.append(
                f"Estado del foco: {'objetivo definido' if self.selected_focus_target else 'sin objetivo explícito'}"
            )
        else:
            lines.append("Estado del foco: ignorado por la vista actual")

        return lines

    def refresh_preview(self) -> None:
        path_state = _inspect_path(self.path_entry.text())

        shown_path = path_state.display if path_state.display != "(ninguna)" else "(ninguna)"
        self.path_value.setText(shown_path)

        if path_state.kind == "folder":
            self._set_chip(self.path_kind_chip, "Carpeta", "good")
        elif path_state.kind == "file":
            self._set_chip(self.path_kind_chip, "Archivo", "accent")
        elif path_state.kind == "manual":
            self._set_chip(self.path_kind_chip, "Manual", "warn")
        else:
            self._set_chip(self.path_kind_chip, "Sin ruta", "neutral")

        self.summary_value.setText("\n".join(self._preview_summary_lines(path_state)))
        self.detail_value.setText("\n".join(self._preview_detail_lines(path_state)))

        self.confirm_button.setEnabled(bool(self.selected_path))

    def on_view_changed(self) -> None:
        self.update_focus_state()
        self.refresh_preview()

    def pick_directory(self) -> None:
        start_dir = _picker_start_directory(self.path_entry.text())
        selected = QFileDialog.getExistingDirectory(
            self,
            "Selecciona la carpeta a analizar",
            start_dir,
        )
        if selected:
            self.path_entry.setText(selected)

    def pick_file(self) -> None:
        start_dir = _picker_start_directory(self.path_entry.text())
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona el archivo Python a usar como entrada",
            start_dir,
            "Python (*.py);;Todos los archivos (*)",
        )
        if selected:
            self.path_entry.setText(selected)

    def confirm(self) -> None:
        normalized_path = self.selected_path
        if not normalized_path:
            QMessageBox.warning(self, _app_title(), "Primero indica una carpeta o archivo.")
            return

        self._selection_result = _make_selection_result(
            path=normalized_path,
            theme=self.selected_theme,
            view=self.selected_view,
            focus_target=self.selected_focus_target,
            output_mode="svg",
        )
        self.accept()

    def confirm_tree(self) -> None:
        normalized_path = self.selected_path
        if not normalized_path:
            start_dir = _picker_start_directory(self.path_entry.text())
            selected = QFileDialog.getExistingDirectory(
                self,
                "Selecciona la carpeta para generar Tree .txt",
                start_dir,
            )
            if not selected:
                return
            self.path_entry.setText(selected)
            normalized_path = self.selected_path

        if not normalized_path:
            QMessageBox.warning(self, _app_title(), "Primero indica una carpeta o archivo.")
            return

        self._selection_result = _make_selection_result(
            path=normalized_path,
            theme=self.selected_theme,
            view=self.selected_view,
            focus_target=self.selected_focus_target,
            output_mode="tree",
        )
        self.accept()

    def confirm_tree_html(self) -> None:
        normalized_path = self.selected_path
        if not normalized_path:
            start_dir = _picker_start_directory(self.path_entry.text())
            selected = QFileDialog.getExistingDirectory(
                self,
                "Selecciona la carpeta para generar Tree HTML Premium",
                start_dir,
            )
            if not selected:
                return
            self.path_entry.setText(selected)
            normalized_path = self.selected_path

        if not normalized_path:
            QMessageBox.warning(self, _app_title(), "Primero indica una carpeta o archivo.")
            return

        self._selection_result = _make_selection_result(
            path=normalized_path,
            theme=self.selected_theme,
            view=self.selected_view,
            focus_target=self.selected_focus_target,
            output_mode="tree_html",
        )
        self.accept()

    def cancel(self) -> None:
        self._selection_result = _make_selection_result(
            path=None,
            theme=self.selected_theme,
            view=self.selected_view,
            focus_target=self.selected_focus_target,
        )
        self.reject()


class ProgressUI(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        window_title: Optional[str] = None,
        initial_status: str = "Preparando...",
        initial_detail: str = "",
        theme_id: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        ensure_app()

        self.root = self
        self._last_pump = 0.0
        self._finalized = False
        self._spinner_frames = ("Procesando", "Procesando.", "Procesando..", "Procesando...")
        self._spinner_index = 0
        self._theme_id = normalize_theme(theme_id or DEFAULT_THEME)

        self.setWindowTitle(window_title or _app_title())
        self.setModal(False)
        self.setMinimumSize(780, 320)
        self.resize(860, 340)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        apply_window_transparency(self)
        self._resize_controller = FramelessResizeController(self, margin=8)
        self.setStyleSheet(app_stylesheet(self._theme_id))

        self._build_ui()
        self.set_status(initial_status, initial_detail)
        self.set_indeterminate(True)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(240)
        self._pulse_timer.timeout.connect(self._advance_spinner)
        self._pulse_timer.start()

        self.show()
        self.raise_()
        self.activateWindow()
        self._pump_events(force=True)

    def _build_ui(self) -> None:
        outer, content_layer, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._theme_id,
            variant="progress",
            margins=(0, 0, 0, 0),
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content_layer)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("Shell")
        shell.setProperty("variant", "progress")
        apply_shadow(shell, blur=28.0, y_offset=10.0, alpha=54)
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(20, 20, 20, 20)
        shell_layout.setSpacing(16)

        self.window_chrome = WindowChromeBar(
            self,
            title=self.windowTitle(),
            on_close=self.close,
            allow_minimize=True,
            allow_maximize=False,
        )
        shell_layout.addWidget(self.window_chrome)

        hero = QFrame()
        hero.setProperty("card", "hero")
        apply_shadow(hero, blur=20.0, y_offset=6.0, alpha=16)
        enable_card_hover(hero)
        shell_layout.addWidget(hero)

        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(10)

        hero_top = QHBoxLayout()
        hero_top.setSpacing(12)
        hero_layout.addLayout(hero_top)

        hero_stack = QVBoxLayout()
        hero_stack.setSpacing(6)
        hero_top.addLayout(hero_stack, 1)

        eyebrow = QLabel("Pipeline")
        eyebrow.setProperty("role", "eyebrow")
        hero_stack.addWidget(eyebrow, 0, Qt.AlignLeft)

        title = QLabel("Armando el grafo de dependencias")
        title.setProperty("role", "title")
        hero_stack.addWidget(title)

        subtitle = QLabel(
            "Escaneando estructura, resolviendo imports y preparando el SVG final."
        )
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        hero_stack.addWidget(subtitle)

        chip_stack = QVBoxLayout()
        chip_stack.setSpacing(8)
        hero_top.addLayout(chip_stack, 0)

        self.state_chip = QLabel("En curso")
        self.state_chip.setProperty("chip", True)
        self.state_chip.setProperty("tone", "accent")
        self.state_chip.setAlignment(Qt.AlignCenter)
        chip_stack.addWidget(self.state_chip, 0, Qt.AlignRight)

        live_chip = QLabel("Glass Console")
        live_chip.setProperty("chip", True)
        live_chip.setProperty("tone", "neutral")
        live_chip.setAlignment(Qt.AlignCenter)
        chip_stack.addWidget(live_chip, 0, Qt.AlignRight)
        chip_stack.addStretch(1)

        hero_line = make_separator()
        hero_line.setProperty("tone", "glow")
        repolish(hero_line)
        hero_layout.addWidget(hero_line)

        body = QFrame()
        body.setProperty("card", "true")
        apply_shadow(body, blur=16.0, y_offset=6.0, alpha=12)
        enable_card_hover(body)
        shell_layout.addWidget(body)

        layout = QVBoxLayout(body)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.status_label = QLabel("")
        self.status_label.setProperty("role", "section")
        layout.addWidget(self.status_label)

        self.detail_label = QLabel("")
        self.detail_label.setProperty("role", "mono")
        self.detail_label.setWordWrap(True)
        self.detail_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.detail_label)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        footer = QFrame()
        footer.setProperty("card", "muted")
        apply_shadow(footer, blur=14.0, y_offset=5.0, alpha=10)
        enable_card_hover(footer)
        shell_layout.addWidget(footer)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 12)
        footer_layout.setSpacing(10)

        self.footer_hint = QLabel("Esta consola se queda viva mientras corre el pipeline y luego te deja cerrar sin prisas.")
        self.footer_hint.setProperty("role", "hint")
        self.footer_hint.setWordWrap(True)
        self.footer_hint.setTextInteractionFlags(Qt.TextSelectableByMouse)
        footer_layout.addWidget(self.footer_hint, 1)

    def _pump_events(self, *, force: bool = False) -> None:
        app = QApplication.instance()
        if app is None:
            return

        now = time.monotonic()
        if force or (now - self._last_pump) >= 0.08:
            self._last_pump = now
            app.processEvents()

    def _set_state_chip(self, text: str, tone: str) -> None:
        self.state_chip.setText(text)
        self.state_chip.setProperty("tone", tone)
        repolish(self.state_chip)

    def _advance_spinner(self) -> None:
        if self._finalized:
            return

        if self.progress.minimum() == 0 and self.progress.maximum() == 0:
            self._spinner_index = (self._spinner_index + 1) % len(self._spinner_frames)
            self._set_state_chip(self._spinner_frames[self._spinner_index], "accent")

    def refresh(self) -> None:
        self._pump_events()
    def set_indeterminate(self, enabled: bool = True) -> None:
        if enabled:
            self.progress.setRange(0, 0)
            self.progress.setFormat("")
            self._set_state_chip(self._spinner_frames[self._spinner_index], "accent")
        else:
            maximum = max(1, self.progress.maximum())
            self.progress.setRange(0, maximum)
            if self.progress.value() <= 0:
                self.progress.setValue(0)
            self.progress.setFormat("%p%")
            self._set_state_chip("En curso", "accent")
        self._pump_events()

    def set_progress(
        self,
        value: int,
        maximum: Optional[int] = None,
        *,
        status: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        if maximum is not None:
            maximum = max(1, int(maximum))
            self.progress.setRange(0, maximum)
        elif self.progress.minimum() == 0 and self.progress.maximum() == 0:
            self.progress.setRange(0, 100)

        max_value = max(1, self.progress.maximum())
        self.progress.setValue(max(0, min(int(value), max_value)))
        self.progress.setFormat("%p%")
        self._set_state_chip("En curso", "accent")

        if status is not None:
            self.status_label.setText(status)
        if detail is not None:
            self.detail_label.setText(detail)

        self._pump_events()

    def set_status(self, text: str, detail: str = "") -> None:
        self.status_label.setText(text or "")
        self.detail_label.setText(detail or "")
        self._pump_events()

    def set_detail(self, detail: str) -> None:
        self.detail_label.setText(detail or "")
        self._pump_events()

    def set_footer_hint(self, text: str) -> None:
        if getattr(self, "footer_hint", None) is not None:
            self.footer_hint.setText(text or "")
        self._pump_events()

    def finalize(self, text: str, detail: str = "", success: bool = True) -> None:
        self._finalized = True
        if hasattr(self, "_pulse_timer") and self._pulse_timer.isActive():
            self._pulse_timer.stop()

        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setFormat("Listo")
        self.status_label.setText(text or "")
        self.detail_label.setText(detail or "")
        self._set_state_chip("Listo" if success else "Terminado", "good" if success else "warn")
        self._pump_events(force=True)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if hasattr(self, "_pulse_timer") and self._pulse_timer.isActive():
            self._pulse_timer.stop()
        super().closeEvent(event)

    def close(self) -> bool:  # type: ignore[override]
        if hasattr(self, "_pulse_timer") and self._pulse_timer.isActive():
            self._pulse_timer.stop()
        return super().close()


def choose_options() -> SelectionResult:
    ensure_app()
    dialog = SelectorDialog()
    dialog.exec()
    return dialog.result_selection()

# ============================================================
# 06. HELPERS DE NODOS Y PRESENTACION
# ============================================================

ISSUE_NOTE_GROUP = "[issues]"
MAX_ISSUE_NOTES_VISIBLE = 8


def make_issue_note_key(index: int) -> str:
    return f"note:issue:{index}"


def build_issue_note_message(issue: AnalysisIssue) -> str:
    level = clean_text(issue.level).upper() or "INFO"
    code = clean_text(issue.code)
    message = clean_text(issue.message)
    location = short_path(issue.path, 68) if issue.path else ""

    chunks: list[str] = [level]
    if code:
        chunks.append(code)
    if message:
        chunks.append(message)
    if location:
        chunks.append(location)

    return " • ".join(chunks)


def build_issue_note_node(issue: AnalysisIssue, index: int) -> DependencyNode:
    full_message = build_issue_note_message(issue)

    return DependencyNode(
        key=make_issue_note_key(index),
        label=short_name(full_message, LABEL_LIMIT),
        path=issue.path,
        kind="note",
        group=ISSUE_NOTE_GROUP,
        metadata={
            "full_message": full_message,
            "issue_level": issue.level,
            "issue_code": issue.code,
            "issue_path": issue.path,
            "root_group": ISSUE_NOTE_GROUP,
        },
    )


def add_issue_note_nodes(
    graph: DependencyGraph,
    *,
    limit: int = MAX_ISSUE_NOTES_VISIBLE,
) -> int:
    """
    Convierte issues del análisis en nodos visuales tipo note para que el SVG
    también te enseñe advertencias importantes sin tener que abrir logs aparte.
    """
    if limit <= 0 or not graph.issues:
        return 0

    visible_issues = graph.issues[:limit]
    added = 0

    for index, issue in enumerate(visible_issues, start=1):
        node = build_issue_note_node(issue, index=index)
        graph.upsert_node(
            key=node.key,
            label=node.label,
            path=node.path,
            kind=node.kind,
            group=node.group,
            metadata=dict(node.metadata),
        )
        added += 1

    remaining = len(graph.issues) - len(visible_issues)
    if remaining > 0:
        summary_message = f"Hay {remaining} issues adicionales no mostrados."
        graph.upsert_node(
            key="note:issues:more",
            label=short_name(summary_message, LABEL_LIMIT),
            path="",
            kind="note",
            group=ISSUE_NOTE_GROUP,
            metadata={
                "full_message": summary_message,
                "issue_level": "info",
                "issue_code": "issues_remaining",
                "root_group": ISSUE_NOTE_GROUP,
            },
        )
        added += 1

    graph.finalize_metrics()
    return added


def infer_focus_target_from_selected_path(selected_path: str) -> str:
    """
    Si el usuario eligió un archivo Python y la vista es focus, inferimos el
    módulo automáticamente para cumplir con la promesa del UI.
    """
    cleaned = clean_text(selected_path)
    if not cleaned:
        return ""

    candidate = Path(cleaned).expanduser()
    if not candidate.exists() or not candidate.is_file():
        return ""

    if not is_supported_source_file(candidate):
        return ""

    project_root = derive_project_root(str(candidate))

    try:
        return module_name_from_path(project_root, candidate.resolve())
    except Exception:
        return ""


def resolve_effective_focus_target(
    *,
    selected_path: str,
    view: GraphView,
    requested_focus_target: str,
) -> str:
    """
    Prioridad:
    1. foco escrito explícitamente por el usuario
    2. inferencia automática si eligió un archivo Python
    3. vacío, para que el sistema luego elija por conectividad
    """
    explicit_target = clean_text(requested_focus_target)
    if view != "focus":
        return explicit_target

    if explicit_target:
        return explicit_target

    return infer_focus_target_from_selected_path(selected_path)


def presentation_node_label(node: DependencyNode) -> str:
    if node.kind == "note":
        full_message = clean_text(str(node.metadata.get("full_message", "")))
        return short_name(full_message or node.label, LABEL_LIMIT)

    return short_name(node.label, LABEL_LIMIT)


def presentation_node_subtitle(node: DependencyNode) -> str:
    if node.kind == "module":
        relative_path = clean_text(str(node.metadata.get("relative_path", "")))
        return short_name(relative_path, 34) if relative_path else ""

    if node.kind == "external":
        return "externo"

    if node.kind == "package":
        group_name = clean_text(str(node.metadata.get("root_group", node.group)))
        return short_name(group_name, 28)

    if node.kind == "note":
        issue_path = clean_text(str(node.metadata.get("issue_path", node.path)))
        return short_name(issue_path, 34) if issue_path else "issue"

    return ""


def presentation_node_icon(node: DependencyNode) -> str:
    if node.kind == "package":
        return "📦"
    if node.kind == "module":
        return "📄"
    if node.kind == "external":
        return "🌐"
    return "⚠"


def presentation_node_kind_class(node: DependencyNode) -> str:
    if node.kind == "package":
        return "package"
    if node.kind == "module":
        return "module"
    if node.kind == "external":
        return "external"
    return "note"


def presentation_node_state_classes(node: DependencyNode) -> str:
    classes: list[str] = []
    if node.is_hub:
        classes.append("node-hub")
    if node.is_island:
        classes.append("node-island")
    return " ".join(classes)


def enrich_graph_for_presentation(
    graph: DependencyGraph,
    state: AnalysisState,
) -> DependencyGraph:
    """
    Ajustes finales antes de layout/render:
    - mete issues como notes visibles solo cuando el preset lo permite
    - recalcula métricas
    - sincroniza totales en state
    """
    if graph.issues and should_surface_issue_notes(state):
        add_issue_note_nodes(graph)

    graph.finalize_metrics()
    state.total_nodes = len(graph.nodes)
    state.total_edges = len(graph.edges)
    return graph


# ============================================================
# 07. ANALISIS DE DEPENDENCIAS
# ============================================================

def read_python_source(file_path: Path) -> str:
    """
    Lee un archivo Python intentando varias codificaciones razonables.
    """
    encodings = ("utf-8", "utf-8-sig", "latin-1")

    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue

    if last_error is not None:
        raise last_error

    return file_path.read_text(encoding="utf-8", errors="replace")


def current_package_for_module(module_name: str, file_path: Path) -> str:
    """
    Devuelve el contexto de paquete desde el cual se resuelven imports relativos.

    Ejemplos:
      forgeos.core.engine.py   -> forgeos.core
      forgeos/core/__init__.py -> forgeos.core
    """
    cleaned = clean_text(module_name)
    if not cleaned:
        return ""

    if file_path.name == "__init__.py":
        return cleaned

    if "." not in cleaned:
        return ""

    return cleaned.rsplit(".", 1)[0]


def ascend_package(package_name: str, levels_up: int) -> str:
    """
    Sube N niveles sobre un package dotted path.
    """
    cleaned = clean_text(package_name)
    if not cleaned:
        return ""

    if levels_up <= 0:
        return cleaned

    parts = cleaned.split(".")
    if levels_up >= len(parts):
        return ""

    return ".".join(parts[:-levels_up])


def resolve_import_from_base(
    *,
    current_module: str,
    current_file: Path,
    imported_module: str,
    level: int,
) -> str:
    """
    Resuelve la base real de un `from ... import ...`.

    Casos:
      from forgeos.core import Engine
      from .utils import x
      from ..shared import y
      from . import z
    """
    imported_module = clean_text(imported_module)
    package_context = current_package_for_module(current_module, current_file)

    # Import absoluto
    if level <= 0:
        return imported_module

    # Import relativo:
    # level=1 -> paquete actual
    # level=2 -> padre
    # level=3 -> abuelo
    base_package = ascend_package(package_context, max(0, level - 1))

    if imported_module:
        if base_package:
            return f"{base_package}.{imported_module}"
        return imported_module

    return base_package


def choose_from_import_target(
    *,
    base_module: str,
    imported_name: str,
    known_modules: set[str],
) -> tuple[str, str]:
    """
    Decide el target más útil para una sentencia:
      from X import Y

    Regresa:
      (imported_module, imported_symbol)

    Reglas:
    - Si X.Y es módulo interno conocido, apuntamos a X.Y
    - Si no, pero X existe como módulo interno, apuntamos a X y Y queda como símbolo
    - Si nada es interno, conservamos lo más informativo posible
    """
    base_module = clean_text(base_module)
    imported_name = clean_text(imported_name)

    if imported_name == "*":
        return base_module, "*"

    dotted_candidate = (
        f"{base_module}.{imported_name}"
        if base_module and imported_name
        else imported_name or base_module
    )

    if dotted_candidate and is_internal_module_name(dotted_candidate, known_modules):
        return dotted_candidate, ""

    if base_module and is_internal_module_name(base_module, known_modules):
        return base_module, imported_name

    if dotted_candidate:
        return dotted_candidate, imported_name

    return base_module, imported_name


def make_import_reference(
    *,
    importer_module: str,
    imported_module: str,
    imported_symbol: str = "",
    is_relative: bool = False,
    line_no: int = 0,
) -> ImportReference | None:
    """
    Normaliza la referencia antes de agregarla.
    """
    importer_module = clean_text(importer_module)
    imported_module = clean_text(imported_module)
    imported_symbol = clean_text(imported_symbol)

    if not importer_module or not imported_module:
        return None

    return ImportReference(
        importer_module=importer_module,
        imported_module=imported_module,
        imported_symbol=imported_symbol,
        is_relative=is_relative,
        line_no=line_no,
    )


def extract_import_references_from_ast(
    *,
    tree: ast.AST,
    module_name: str,
    file_path: Path,
    known_modules: set[str],
) -> list[ImportReference]:
    """
    Recorre el AST y extrae referencias de import.

    Soporta:
    - import x
    - import x as y
    - from x import y
    - from .x import y
    - from . import y
    """
    refs: list[ImportReference] = []
    import_count = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_count += 1
                if import_count > MAX_IMPORTS_PER_FILE:
                    return refs

                imported_module = clean_text(alias.name)
                ref = make_import_reference(
                    importer_module=module_name,
                    imported_module=imported_module,
                    imported_symbol="",
                    is_relative=False,
                    line_no=getattr(node, "lineno", 0),
                )
                if ref is not None:
                    refs.append(ref)

        elif isinstance(node, ast.ImportFrom):
            import_count += len(node.names)
            if import_count > MAX_IMPORTS_PER_FILE:
                return refs

            base_module = resolve_import_from_base(
                current_module=module_name,
                current_file=file_path,
                imported_module=node.module or "",
                level=int(getattr(node, "level", 0) or 0),
            )

            is_relative = bool(getattr(node, "level", 0))

            for alias in node.names:
                target_module, imported_symbol = choose_from_import_target(
                    base_module=base_module,
                    imported_name=alias.name,
                    known_modules=known_modules,
                )

                ref = make_import_reference(
                    importer_module=module_name,
                    imported_module=target_module,
                    imported_symbol=imported_symbol,
                    is_relative=is_relative,
                    line_no=getattr(node, "lineno", 0),
                )
                if ref is not None:
                    refs.append(ref)

    return refs


def analyze_single_source_file(
    *,
    file_path: Path,
    module_name: str,
    known_modules: set[str],
    graph: DependencyGraph,
    state: AnalysisState,
) -> list[ImportReference]:
    """
    Analiza un solo archivo fuente y devuelve sus imports detectados.
    """
    try:
        source = read_python_source(file_path)
    except Exception as exc:
        graph.add_issue(
            "warning",
            "source_read_error",
            f"No se pudo leer el archivo: {exc}",
            str(file_path),
        )
        state.skipped_files += 1
        return []

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        graph.add_issue(
            "warning",
            "syntax_error",
            f"SyntaxError en línea {exc.lineno or '?'}: {exc.msg}",
            str(file_path),
        )
        state.register_parse_error()
        state.skipped_files += 1
        return []
    except Exception as exc:
        graph.add_issue(
            "warning",
            "ast_parse_error",
            f"No se pudo parsear el archivo: {exc}",
            str(file_path),
        )
        state.register_parse_error()
        state.skipped_files += 1
        return []

    refs = extract_import_references_from_ast(
        tree=tree,
        module_name=module_name,
        file_path=file_path,
        known_modules=known_modules,
    )

    if len(refs) >= MAX_IMPORTS_PER_FILE:
        graph.add_issue(
            "warning",
            "imports_truncated_per_file",
            f"Se truncaron imports por archivo al llegar a {MAX_IMPORTS_PER_FILE}",
            str(file_path),
        )

    state.parsed_files += 1
    return refs


def collect_project_source_files(
    *,
    project_root: Path,
    state: AnalysisState,
) -> list[Path]:
    """
    Recolecta todos los archivos fuente soportados del proyecto.
    """
    files: list[Path] = []

    for candidate in iter_source_files(project_root):
        state.total_files_seen += 1

        if len(files) >= MAX_FILES_ANALYZED:
            state.mark_truncated(
                f"Se alcanzó el límite de archivos fuente analizados: {MAX_FILES_ANALYZED}"
            )
            break

        files.append(candidate)

    state.source_files_seen = len(files)
    return files


def analyze_project_dependencies(
    *,
    selected_path: str,
    state: AnalysisState,
    notify: Callable[[str, str], None],
) -> tuple[dict[str, ModuleSourceInfo], list[ImportReference], DependencyGraph]:
    """
    Pipeline principal del análisis de dependencias.

    Devuelve:
    - module_catalog
    - import_refs
    - graph_issues_holder

    Nota:
    El grafo aquí se usa como contenedor de issues durante el análisis.
    El grafo final real se construye después en el módulo 04.
    """
    project_root = derive_project_root(selected_path)

    state.selected_path = selected_path
    state.project_root = str(project_root)

    notify("Detectando archivos fuente...", str(project_root))
    source_files = collect_project_source_files(
        project_root=project_root,
        state=state,
    )

    analysis_graph = DependencyGraph()

    if not source_files:
        analysis_graph.add_issue(
            "warning",
            "no_source_files",
            "No se encontraron archivos fuente soportados en la ruta seleccionada.",
            str(project_root),
        )
        state.total_nodes = 0
        state.total_edges = 0
        return {}, [], analysis_graph

    notify("Construyendo catálogo de módulos...", f"{len(source_files)} archivos")
    module_catalog = build_module_catalog(project_root, source_files)
    known_modules = set(module_catalog.keys())

    all_refs: list[ImportReference] = []

    for index, file_path in enumerate(source_files, start=1):
        module_name = module_name_from_path(project_root, file_path)
        detail = f"[{index}/{len(source_files)}] {safe_relative_path(file_path, project_root)}"
        notify("Analizando imports...", detail)

        refs = analyze_single_source_file(
            file_path=file_path,
            module_name=module_name,
            known_modules=known_modules,
            graph=analysis_graph,
            state=state,
        )
        all_refs.extend(refs)

        if state.truncated:
            analysis_graph.add_issue(
                "warning",
                "analysis_truncated",
                state.limit_reason or "El análisis fue truncado por límites de seguridad.",
                str(project_root),
            )
            break

    if state.parse_errors > 0:
        analysis_graph.add_issue(
            "info",
            "parse_errors_summary",
            f"Archivos con error de parseo: {state.parse_errors}",
            str(project_root),
        )

    notify(
        "Análisis de dependencias listo.",
        f"{len(module_catalog)} módulos internos • {len(all_refs)} referencias detectadas",
    )

    return module_catalog, all_refs, analysis_graph


def merge_analysis_issues_into_graph(
    target_graph: DependencyGraph,
    analysis_graph: DependencyGraph,
) -> None:
    """
    Copia issues del análisis al grafo final.
    """
    for issue in analysis_graph.issues:
        target_graph.issues.append(issue)


# ============================================================
# 08. LAYOUT DEL GRAFO
# ============================================================

@dataclass(slots=True)
class LayoutLane:
    """
    Carril o columna visual del grafo.

    Campos congelados por contrato:
    - key
    - label
    - x
    - width
    - node_keys
    - node_count
    - inbound_sum
    - outbound_sum

    Campos extra:
    - role
    - visual_emphasis
    - density
    - spacing_mode
    """

    key: str
    label: str
    x: float = 0.0
    width: float = 0.0
    node_keys: list[str] = field(default_factory=list)

    node_count: int = 0
    inbound_sum: int = 0
    outbound_sum: int = 0

    role: str = "group"
    visual_emphasis: float = 1.0
    density: str = "regular"
    spacing_mode: str = "regular"


@dataclass(slots=True)
class LayoutResult:
    """
    Resultado final del layout.
    """

    nodes: list[DependencyNode]
    lanes: list[LayoutLane]
    width: int
    height: int


@dataclass(slots=True)
class _GroupProfile:
    name: str
    role: str
    nodes: list[DependencyNode]
    degree_sum: int = 0
    active_count: int = 0
    hub_count: int = 0
    cross_weight: int = 0
    internal_weight: int = 0
    flow_bias: int = 0
    package_count: int = 0
    external_count: int = 0
    note_count: int = 0
    importance: float = 0.0


DEFAULT_LAYOUT_WIDTH = 1080
DEFAULT_LAYOUT_HEIGHT = 360

LANE_MIN_WIDTH = float(NODE_MIN_WIDTH + 28)
LANE_HEADER_TO_CONTENT_GAP = 44.0
LANE_BASE_PADDING_X = 14.0
LANE_BASE_PADDING_W = 30.0
LANE_SECONDARY_VERTICAL_OFFSET = 16.0
LANE_NOTE_VERTICAL_OFFSET = 26.0
FOCUS_CONTEXT_VERTICAL_OFFSET = 24.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def node_total_degree(node: DependencyNode) -> int:
    return int(node.inbound + node.outbound)


def estimate_badge_slots_for_node(node: DependencyNode) -> int:
    """
    Dejamos espacio para:
    - inbound
    - outbound
    - estado opcional (hub / isla)
    """
    slots = 2
    if node.is_hub or node.is_island:
        slots += 1
    return slots


def _node_secondary_width_basis(node: DependencyNode) -> str:
    if node.kind == "module":
        relative_path = clean_text(str(node.metadata.get("relative_path", "")))
        if relative_path:
            return short_name(relative_path.split("/")[-1].split("\\")[-1], 26)

    if node.kind == "package":
        return short_name(clean_text(str(node.metadata.get("root_group", node.group))), 24)

    if node.kind == "external":
        module_name = clean_text(str(node.metadata.get("module_name", node.label)))
        return short_name(module_name, 22)

    if node.kind == "note":
        issue_code = clean_text(str(node.metadata.get("issue_code", "")))
        if issue_code:
            return short_name(issue_code, 20)

    return ""


def prepare_node_width(node: DependencyNode) -> None:
    """
    Estimación de ancho base sin meter aún semántica de foco.
    """
    label = short_name(node.label, LABEL_LIMIT)
    secondary = _node_secondary_width_basis(node)

    primary_width = measure_text_width(
        label,
        extra_badges=estimate_badge_slots_for_node(node),
    )
    secondary_width = (
        measure_text_width(secondary, extra_badges=0) - 38 if secondary else 0
    )

    width = max(primary_width, secondary_width)

    if node.kind == "package":
        width += 12
    elif node.kind == "external":
        width += 6
    elif node.kind == "note":
        width -= 8

    node.width = float(
        _clamp(float(width), float(NODE_MIN_WIDTH), float(NODE_MAX_WIDTH))
    )


def _node_kind_bucket(node: DependencyNode, lane_role: str) -> int:
    if lane_role in {"note", "annotations"}:
        if node.kind == "note":
            return 0
        if node.kind == "external":
            return 1
        if node.kind == "module":
            return 2
        return 3

    if lane_role == "context":
        if node.kind == "package":
            return 0
        if node.kind == "module":
            return 1
        if node.kind == "external":
            return 2
        return 3

    if node.kind == "package":
        return 0
    if node.is_hub and node.kind == "module":
        return 1
    if node.kind == "module":
        return 2
    if node.kind == "external":
        return 3
    return 4


def _node_prominence_score(node: DependencyNode) -> int:
    score = (node.inbound * 4) + (node.outbound * 3)

    if node.kind == "package":
        score += 18
    elif node.kind == "module":
        score += 10
    elif node.kind == "external":
        score += 2
    else:
        score -= 14

    if node.is_hub:
        score += 16
    if node.is_island:
        score -= 6

    return score


def _initial_lane_node_sort_key(
    node: DependencyNode,
    lane_role: str,
) -> tuple[int, int, int, int, str]:
    prominence = _node_prominence_score(node)

    if lane_role == "inbound":
        directed_bias = node.outbound - node.inbound
    elif lane_role == "outbound":
        directed_bias = node.inbound - node.outbound
    elif lane_role == "mixed":
        directed_bias = -abs(node.inbound - node.outbound)
    else:
        directed_bias = node_total_degree(node)

    return (
        _node_kind_bucket(node, lane_role),
        -prominence,
        -directed_bias,
        -node_total_degree(node),
        node.label.lower(),
    )


def _neighbors_by_node(graph: DependencyGraph) -> dict[str, list[tuple[str, int]]]:
    neighbors: dict[str, list[tuple[str, int]]] = {}

    for edge in graph.edges.values():
        if edge.source == edge.target:
            continue

        neighbors.setdefault(edge.source, []).append((edge.target, edge.weight))
        neighbors.setdefault(edge.target, []).append((edge.source, edge.weight))

    for items in neighbors.values():
        items.sort(key=lambda item: (item[0], item[1]))

    return neighbors


def _build_group_profiles(graph: DependencyGraph) -> dict[str, _GroupProfile]:
    grouped: dict[str, list[DependencyNode]] = {}
    for node in graph.nodes.values():
        grouped.setdefault(node.group, []).append(node)

    profiles: dict[str, _GroupProfile] = {}
    for group_name, nodes in grouped.items():
        if group_name == "[external]":
            role = "external"
        elif group_name == "[issues]":
            role = "note"
        else:
            role = "primary"

        profile = _GroupProfile(
            name=group_name,
            role=role,
            nodes=sorted(nodes, key=lambda item: item.label.lower()),
        )

        profile.degree_sum = sum(node_total_degree(node) for node in nodes)
        profile.active_count = sum(1 for node in nodes if node_total_degree(node) > 0)
        profile.hub_count = sum(1 for node in nodes if node.is_hub)
        profile.package_count = sum(1 for node in nodes if node.kind == "package")
        profile.external_count = sum(1 for node in nodes if node.kind == "external")
        profile.note_count = sum(1 for node in nodes if node.kind == "note")

        profiles[group_name] = profile

    for edge in graph.edges.values():
        source = graph.nodes.get(edge.source)
        target = graph.nodes.get(edge.target)
        if source is None or target is None:
            continue

        source_group = source.group
        target_group = target.group

        if source_group == target_group:
            profile = profiles.get(source_group)
            if profile is not None:
                profile.internal_weight += edge.weight
                profile.flow_bias += 0
            continue

        source_profile = profiles.get(source_group)
        target_profile = profiles.get(target_group)

        if source_profile is not None:
            source_profile.cross_weight += edge.weight
            source_profile.flow_bias += edge.weight

        if target_profile is not None:
            target_profile.cross_weight += edge.weight
            target_profile.flow_bias -= edge.weight

    for profile in profiles.values():
        profile.importance = (
            (profile.degree_sum * 4.0)
            + (profile.cross_weight * 8.0)
            + (profile.internal_weight * 2.0)
            + (profile.active_count * 18.0)
            + (profile.hub_count * 12.0)
            + (profile.package_count * 10.0)
            - (profile.external_count * 4.0)
            - (profile.note_count * 16.0)
        )

    return profiles


def _group_connection_strengths(graph: DependencyGraph) -> dict[str, dict[str, int]]:
    strengths: dict[str, dict[str, int]] = {}

    for edge in graph.edges.values():
        source = graph.nodes.get(edge.source)
        target = graph.nodes.get(edge.target)
        if source is None or target is None:
            continue

        left = source.group
        right = target.group

        if left == right:
            strengths.setdefault(left, {})
            continue

        strengths.setdefault(left, {})
        strengths.setdefault(right, {})

        strengths[left][right] = strengths[left].get(right, 0) + edge.weight
        strengths[right][left] = strengths[right].get(left, 0) + edge.weight

    return strengths


def _directed_group_weight(
    graph: DependencyGraph,
    source_group: str,
    target_group: str,
) -> int:
    total = 0
    for edge in graph.edges.values():
        source = graph.nodes.get(edge.source)
        target = graph.nodes.get(edge.target)
        if source is None or target is None:
            continue
        if source.group == source_group and target.group == target_group:
            total += edge.weight
    return total


def _order_primary_groups(
    profiles: dict[str, _GroupProfile],
    strengths: dict[str, dict[str, int]],
    graph: DependencyGraph,
) -> list[str]:
    primary_names = [
        name for name, profile in profiles.items() if profile.role == "primary"
    ]
    if not primary_names:
        return []

    primary_names.sort(
        key=lambda name: (
            -profiles[name].importance,
            -profiles[name].cross_weight,
            -profiles[name].active_count,
            name.lower(),
        )
    )

    seed = primary_names[0]
    remaining = set(primary_names[1:])
    ordered = [seed]

    while remaining:
        candidate = min(
            remaining,
            key=lambda name: (
                -sum(
                    strengths.get(name, {}).get(placed_name, 0)
                    for placed_name in ordered
                ),
                -profiles[name].importance,
                -profiles[name].cross_weight,
                -profiles[name].active_count,
                abs(profiles[name].flow_bias),
                name.lower(),
            ),
        )

        left_name = ordered[0]
        right_name = ordered[-1]

        left_link = strengths.get(candidate, {}).get(left_name, 0)
        right_link = strengths.get(candidate, {}).get(right_name, 0)

        left_flow = (
            _directed_group_weight(graph, candidate, left_name)
            - _directed_group_weight(graph, left_name, candidate)
        )
        right_flow = (
            _directed_group_weight(graph, candidate, right_name)
            - _directed_group_weight(graph, right_name, candidate)
        )

        left_score = (left_link * 1000) + left_flow + profiles[candidate].flow_bias
        right_score = (right_link * 1000) - right_flow - profiles[candidate].flow_bias

        if left_score > right_score:
            ordered.insert(0, candidate)
        elif right_score > left_score:
            ordered.append(candidate)
        else:
            if profiles[candidate].flow_bias > 0:
                ordered.insert(0, candidate)
            else:
                ordered.append(candidate)

        remaining.remove(candidate)

    return ordered


def _order_special_groups(
    group_names: list[str],
    profiles: dict[str, _GroupProfile],
    strengths: dict[str, dict[str, int]],
    anchor_order: list[str],
) -> list[str]:
    return sorted(
        group_names,
        key=lambda name: (
            -max(
                (strengths.get(name, {}).get(anchor, 0) for anchor in anchor_order),
                default=0,
            ),
            -profiles[name].importance,
            name.lower(),
        ),
    )


def _ordered_group_names(graph: DependencyGraph) -> list[str]:
    profiles = _build_group_profiles(graph)
    strengths = _group_connection_strengths(graph)

    primary_order = _order_primary_groups(profiles, strengths, graph)

    external_groups = [
        name for name, profile in profiles.items() if profile.role == "external"
    ]
    note_groups = [name for name, profile in profiles.items() if profile.role == "note"]

    if primary_order:
        external_order = _order_special_groups(
            external_groups,
            profiles,
            strengths,
            primary_order,
        )
        note_order = _order_special_groups(
            note_groups,
            profiles,
            strengths,
            primary_order,
        )
        return primary_order + external_order + note_order

    all_names = list(profiles.keys())
    return sorted(
        all_names,
        key=lambda name: (
            2 if profiles[name].role == "note"
            else 1 if profiles[name].role == "external"
            else 0,
            -profiles[name].importance,
            name.lower(),
        ),
    )


def _density_for_lane(
    role: str,
    node_count: int,
    lane_nodes: list[DependencyNode],
) -> str:
    note_count = sum(1 for node in lane_nodes if node.kind == "note")
    external_count = sum(1 for node in lane_nodes if node.kind == "external")

    if role == "hero":
        return "airy"
    if role in {"note", "annotations"}:
        return "compact"
    if role == "context":
        return "compact" if node_count >= 4 else "regular"
    if node_count <= 2:
        return "airy"
    if node_count >= 10:
        return "compact"
    if note_count == node_count or external_count == node_count:
        return "compact"
    return "regular"


def _emphasis_for_lane(role: str, lane_nodes: list[DependencyNode]) -> float:
    if role == "hero":
        return 1.45
    if role in {"inbound", "outbound"}:
        return 1.15
    if role == "mixed":
        return 1.12
    if role in {"context", "external"}:
        return 0.88
    if role in {"note", "annotations"}:
        return 0.80

    if any(node.kind == "package" for node in lane_nodes):
        return 1.08
    if any(node.is_hub for node in lane_nodes):
        return 1.04
    return 1.0


def _spacing_mode_for_lane(role: str, density: str) -> str:
    if role == "hero":
        return "hero"
    if role in {"inbound", "outbound", "mixed"}:
        return "flow"
    if role in {"context", "external"}:
        return "support"
    if role in {"note", "annotations"}:
        return "muted"
    if density == "airy":
        return "breathing"
    if density == "compact":
        return "compact"
    return "regular"


def _make_lane(
    *,
    key: str,
    label: str,
    node_keys: list[str],
    role: str,
    graph: DependencyGraph,
) -> LayoutLane:
    lane_nodes = [graph.nodes[node_key] for node_key in node_keys if node_key in graph.nodes]
    density = _density_for_lane(role, len(lane_nodes), lane_nodes)
    emphasis = _emphasis_for_lane(role, lane_nodes)
    spacing_mode = _spacing_mode_for_lane(role, density)

    return LayoutLane(
        key=key,
        label=label,
        node_keys=list(node_keys),
        role=role,
        density=density,
        visual_emphasis=emphasis,
        spacing_mode=spacing_mode,
    )


def _sort_lane_nodes_initial(
    nodes: Iterable[DependencyNode],
    lane_role: str,
) -> list[DependencyNode]:
    return sorted(nodes, key=lambda node: _initial_lane_node_sort_key(node, lane_role))


def build_grouped_lanes(graph: DependencyGraph) -> list[LayoutLane]:
    """
    Construye columnas por grupo raíz con un orden más estructural
    y menos dependiente de un simple grado total.
    """
    nodes_by_group: dict[str, list[DependencyNode]] = {}
    for node in graph.nodes.values():
        nodes_by_group.setdefault(node.group, []).append(node)

    lanes: list[LayoutLane] = []
    for group_name in _ordered_group_names(graph):
        lane_nodes = _sort_lane_nodes_initial(
            nodes_by_group.get(group_name, []),
            "group",
        )

        role = "group"
        if group_name == "[external]":
            role = "external"
        elif group_name == "[issues]":
            role = "note"

        lanes.append(
            _make_lane(
                key=f"lane:{group_name}",
                label=package_label_from_group(group_name),
                node_keys=[node.key for node in lane_nodes],
                role=role,
                graph=graph,
            )
        )

    return lanes


def resolve_focus_node_key(graph: DependencyGraph, focus_target: str) -> str:
    """
    Intenta ubicar el nodo foco por varias llaves razonables.
    Si no viene foco explícito, elige el nodo más útil visualmente.
    """
    cleaned = clean_text(focus_target)

    if cleaned:
        direct_candidates = [
            cleaned,
            make_package_key(cleaned),
            make_module_key(cleaned),
        ]

        for candidate in direct_candidates:
            if candidate in graph.nodes:
                return candidate

        for node in graph.nodes.values():
            module_name = clean_text(str(node.metadata.get("module_name", "")))
            root_group = clean_text(str(node.metadata.get("root_group", "")))

            if cleaned in {node.label, module_name, root_group, node.key}:
                return node.key

    ranked = sorted(
        graph.nodes.values(),
        key=lambda node: (
            -_node_prominence_score(node),
            -node.inbound,
            -node.outbound,
            node.label.lower(),
        ),
    )
    return ranked[0].key if ranked else ""


def _focus_relation_map(
    graph: DependencyGraph,
    focus_key: str,
) -> dict[str, str]:
    relation_by_node: dict[str, str] = {
        node.key: "context" for node in graph.nodes.values()
    }

    if focus_key not in graph.nodes:
        return relation_by_node

    relation_by_node[focus_key] = "hero"

    incoming_sources: set[str] = set()
    outgoing_targets: set[str] = set()

    for edge in graph.edges.values():
        if edge.target == focus_key and edge.source != focus_key:
            incoming_sources.add(edge.source)
        if edge.source == focus_key and edge.target != focus_key:
            outgoing_targets.add(edge.target)

    mixed = incoming_sources & outgoing_targets
    inbound_only = incoming_sources - mixed
    outbound_only = outgoing_targets - mixed

    for node_key in inbound_only:
        relation_by_node[node_key] = "inbound"
    for node_key in outbound_only:
        relation_by_node[node_key] = "outbound"
    for node_key in mixed:
        relation_by_node[node_key] = "mixed"

    return relation_by_node


def build_focus_lanes(
    graph: DependencyGraph,
    focus_key: str,
) -> list[LayoutLane]:
    """
    Layout especializado para vista focus.

    Orden intencional:
    - inbound
    - mixed
    - hero
    - outbound
    - context
    """
    if focus_key not in graph.nodes:
        return []

    relation_by_node = _focus_relation_map(graph, focus_key)

    inbound_nodes = _sort_lane_nodes_initial(
        (node for node in graph.nodes.values() if relation_by_node.get(node.key) == "inbound"),
        "inbound",
    )
    mixed_nodes = _sort_lane_nodes_initial(
        (node for node in graph.nodes.values() if relation_by_node.get(node.key) == "mixed"),
        "mixed",
    )
    outbound_nodes = _sort_lane_nodes_initial(
        (node for node in graph.nodes.values() if relation_by_node.get(node.key) == "outbound"),
        "outbound",
    )
    context_nodes = _sort_lane_nodes_initial(
        (node for node in graph.nodes.values() if relation_by_node.get(node.key) == "context"),
        "context",
    )

    focus_node = graph.nodes[focus_key]

    lanes: list[LayoutLane] = []

    if inbound_nodes:
        lanes.append(
            _make_lane(
                key="lane:focus:incoming",
                label="Entradas",
                node_keys=[node.key for node in inbound_nodes],
                role="inbound",
                graph=graph,
            )
        )

    if mixed_nodes:
        lanes.append(
            _make_lane(
                key="lane:focus:mixed",
                label="Mixtos",
                node_keys=[node.key for node in mixed_nodes],
                role="mixed",
                graph=graph,
            )
        )

    lanes.append(
        _make_lane(
            key="lane:focus:center",
            label=f"Foco: {focus_node.label}",
            node_keys=[focus_node.key],
            role="hero",
            graph=graph,
        )
    )

    if outbound_nodes:
        lanes.append(
            _make_lane(
                key="lane:focus:outgoing",
                label="Salidas",
                node_keys=[node.key for node in outbound_nodes],
                role="outbound",
                graph=graph,
            )
        )

    if context_nodes:
        lanes.append(
            _make_lane(
                key="lane:focus:extra",
                label="Contexto",
                node_keys=[node.key for node in context_nodes],
                role="context",
                graph=graph,
            )
        )

    return lanes


def choose_lanes_for_view(
    graph: DependencyGraph,
    state: AnalysisState,
    focus_key: str = "",
) -> list[LayoutLane]:
    if state.view == "focus":
        return build_focus_lanes(graph, focus_key)
    return build_grouped_lanes(graph)


def _lane_nodes_in_order(
    graph: DependencyGraph,
    lane: LayoutLane,
) -> list[DependencyNode]:
    return [graph.nodes[node_key] for node_key in lane.node_keys if node_key in graph.nodes]


def _node_lane_lookup(lanes: list[LayoutLane]) -> dict[str, int]:
    result: dict[str, int] = {}
    for lane_index, lane in enumerate(lanes):
        for node_key in lane.node_keys:
            result[node_key] = lane_index
    return result


def _node_index_lookup(lanes: list[LayoutLane]) -> dict[str, int]:
    result: dict[str, int] = {}
    for lane in lanes:
        for index, node_key in enumerate(lane.node_keys):
            result[node_key] = index
    return result


def _neighbor_barycenter(
    node_key: str,
    lane_index: int,
    neighbors: dict[str, list[tuple[str, int]]],
    node_to_lane: dict[str, int],
    node_to_index: dict[str, int],
) -> Optional[float]:
    weighted_total = 0.0
    total_weight = 0.0

    for neighbor_key, edge_weight in neighbors.get(node_key, []):
        other_lane_index = node_to_lane.get(neighbor_key)
        other_index = node_to_index.get(neighbor_key)

        if (
            other_lane_index is None
            or other_index is None
            or other_lane_index == lane_index
        ):
            continue

        lane_distance = abs(other_lane_index - lane_index)
        lane_weight = float(edge_weight) / float(max(1, lane_distance))
        weighted_total += float(other_index) * lane_weight
        total_weight += lane_weight

    if total_weight <= 0.0:
        return None

    return weighted_total / total_weight


def _refine_lane_node_order(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
) -> None:
    """
    Pequeño refinamiento por barycenter para reducir cruces aparentes
    sin meternos en graph theory de laboratorio espacial.
    """
    if len(lanes) <= 1:
        return

    neighbors = _neighbors_by_node(graph)

    for sweep in range(3):
        if sweep % 2 == 0:
            lane_indices = range(len(lanes))
        else:
            lane_indices = range(len(lanes) - 1, -1, -1)

        node_to_lane = _node_lane_lookup(lanes)
        node_to_index = _node_index_lookup(lanes)

        for lane_index in lane_indices:
            lane = lanes[lane_index]
            ordered_nodes = _lane_nodes_in_order(graph, lane)
            if len(ordered_nodes) <= 2:
                continue

            decorated: list[tuple[int, float, int, int, str, str]] = []
            for base_index, node in enumerate(ordered_nodes):
                barycenter = _neighbor_barycenter(
                    node.key,
                    lane_index,
                    neighbors,
                    node_to_lane,
                    node_to_index,
                )
                if barycenter is None:
                    barycenter = float(base_index)

                decorated.append(
                    (
                        _node_kind_bucket(node, lane.role),
                        barycenter,
                        -_node_prominence_score(node),
                        -node_total_degree(node),
                        node.label.lower(),
                        node.key,
                    )
                )

            decorated.sort()
            lane.node_keys = [item[-1] for item in decorated]


def _visual_role_for_node(
    node: DependencyNode,
    state: AnalysisState,
    relation: str,
) -> str:
    if state.view == "focus":
        if relation == "hero":
            return "focus_hero"
        if relation == "inbound":
            return "focus_inbound"
        if relation == "outbound":
            return "focus_outbound"
        if relation == "mixed":
            return "focus_mixed"
        return "context_muted"

    if node.kind == "package":
        return "package"
    if node.kind == "external":
        return "external"
    if node.kind == "note":
        return "note"
    return "module"


def _visual_priority_for_node(node: DependencyNode, visual_role: str) -> int:
    base_priority = {
        "focus_hero": 100,
        "focus_mixed": 82,
        "focus_inbound": 76,
        "focus_outbound": 74,
        "context_muted": 34,
        "package": 84,
        "module": 68,
        "external": 40,
        "note": 18,
    }.get(visual_role, 50)

    if node.kind == "package":
        base_priority += 6
    if node.is_hub:
        base_priority += 8
    if node.kind == "note":
        base_priority -= 6
    if node.is_island:
        base_priority -= 3

    return int(base_priority)


def _annotate_semantic_metadata(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
    state: AnalysisState,
    focus_key: str,
) -> None:
    relation_by_node: dict[str, str] = {
        node.key: "none" for node in graph.nodes.values()
    }

    if state.view == "focus" and focus_key:
        relation_by_node = _focus_relation_map(graph, focus_key)

    for lane in lanes:
        for node_key in lane.node_keys:
            node = graph.nodes.get(node_key)
            if node is None:
                continue

            relation = relation_by_node.get(node.key, "none")
            visual_role = _visual_role_for_node(node, state, relation)

            node.metadata["visual_role"] = visual_role
            node.metadata["visual_priority"] = _visual_priority_for_node(
                node,
                visual_role,
            )
            node.metadata["focus_relation"] = relation
            node.metadata["layout_lane_role"] = lane.role
            node.metadata["layout_lane_density"] = lane.density
            node.metadata["layout_lane_spacing_mode"] = lane.spacing_mode
            node.metadata["layout_lane_visual_emphasis"] = lane.visual_emphasis


def _boost_node_widths_for_semantics(graph: DependencyGraph) -> None:
    for node in graph.nodes.values():
        visual_role = clean_text(str(node.metadata.get("visual_role", "")))
        width = float(node.width or NODE_MIN_WIDTH)

        if visual_role == "focus_hero":
            width += 56.0
        elif visual_role == "focus_mixed":
            width += 14.0
        elif visual_role in {"focus_inbound", "focus_outbound"}:
            width += 8.0
        elif visual_role == "context_muted":
            width -= 6.0
        elif visual_role == "package":
            width += 10.0
        elif visual_role == "note":
            width -= 10.0

        node.width = float(
            _clamp(width, float(NODE_MIN_WIDTH), float(NODE_MAX_WIDTH + 76))
        )


def lane_max_node_width(
    graph: DependencyGraph,
    lane: LayoutLane,
) -> float:
    widths = [graph.nodes[node_key].width for node_key in lane.node_keys if node_key in graph.nodes]
    if not widths:
        return float(NODE_MIN_WIDTH)
    return max(float(NODE_MIN_WIDTH), max(float(width) for width in widths))


def _lane_width(graph: DependencyGraph, lane: LayoutLane) -> float:
    base_width = lane_max_node_width(graph, lane)
    padding = LANE_BASE_PADDING_W

    if lane.role == "hero":
        padding += 46.0
    elif lane.role in {"inbound", "outbound", "mixed"}:
        padding += 8.0
    elif lane.role in {"context", "external"}:
        padding -= 2.0
    elif lane.role in {"note", "annotations"}:
        padding -= 4.0

    width = max(LANE_MIN_WIDTH, base_width + padding)
    return float(width)


def _lane_gap(left_lane: LayoutLane, right_lane: LayoutLane) -> float:
    gap = 86.0

    if "hero" in {left_lane.role, right_lane.role}:
        gap += 24.0
    elif {"inbound", "outbound", "mixed"} & {left_lane.role, right_lane.role}:
        gap += 8.0

    if {"context", "external", "note", "annotations"} & {left_lane.role, right_lane.role}:
        gap -= 8.0

    gap += max(
        0.0,
        (max(left_lane.visual_emphasis, right_lane.visual_emphasis) - 1.0) * 16.0,
    )

    return max(72.0, gap)


def _position_lanes_horizontally_grouped(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
) -> None:
    cursor_x = float(LEFT_MARGIN)

    for lane_index, lane in enumerate(lanes):
        lane.width = _lane_width(graph, lane)
        lane.x = cursor_x

        if lane_index < len(lanes) - 1:
            cursor_x += lane.width + _lane_gap(lane, lanes[lane_index + 1])


def _position_lanes_horizontally_focus(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
) -> None:
    if not lanes:
        return

    center_index = 0
    for index, lane in enumerate(lanes):
        if lane.key == "lane:focus:center":
            center_index = index
            break

    for lane in lanes:
        lane.width = _lane_width(graph, lane)

    lanes[center_index].x = 0.0

    for index in range(center_index - 1, -1, -1):
        right_lane = lanes[index + 1]
        current_lane = lanes[index]
        gap = _lane_gap(current_lane, right_lane)
        current_lane.x = right_lane.x - gap - current_lane.width

    for index in range(center_index + 1, len(lanes)):
        left_lane = lanes[index - 1]
        current_lane = lanes[index]
        gap = _lane_gap(left_lane, current_lane)
        current_lane.x = left_lane.x + left_lane.width + gap

    min_x = min(lane.x for lane in lanes)
    shift = float(LEFT_MARGIN) - min_x

    for lane in lanes:
        lane.x += shift


def position_lanes_horizontally(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
    state: AnalysisState,
) -> None:
    if state.view == "focus":
        _position_lanes_horizontally_focus(graph, lanes)
    else:
        _position_lanes_horizontally_grouped(graph, lanes)


def annotate_lane_statistics(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
) -> None:
    """
    Calcula métricas agregadas por carril para que luego el render
    pueda mostrar contexto útil en los encabezados.
    """
    for lane in lanes:
        lane_nodes = _lane_nodes_in_order(graph, lane)
        lane.node_count = len(lane_nodes)
        lane.inbound_sum = sum(node.inbound for node in lane_nodes)
        lane.outbound_sum = sum(node.outbound for node in lane_nodes)


def apply_lane_metadata(
    node: DependencyNode,
    lane: LayoutLane,
    index_in_lane: int,
) -> None:
    node.metadata["layout_lane_key"] = lane.key
    node.metadata["layout_lane_label"] = lane.label
    node.metadata["layout_lane_x"] = lane.x
    node.metadata["layout_lane_width"] = lane.width
    node.metadata["layout_index_in_lane"] = index_in_lane


def _lane_vertical_gap(lane: LayoutLane) -> float:
    gap = 28.0

    if lane.density == "airy":
        gap += 8.0
    elif lane.density == "compact":
        gap -= 6.0

    if lane.role == "hero":
        gap += 8.0
    elif lane.role in {"inbound", "outbound", "mixed"}:
        gap += 2.0
    elif lane.role in {"context", "external"}:
        gap -= 2.0
    elif lane.role in {"note", "annotations"}:
        gap -= 4.0

    if lane.node_count <= 2:
        gap += 6.0
    elif lane.node_count >= 16:
        gap -= 6.0
    elif lane.node_count >= 10:
        gap -= 3.0

    return float(_clamp(gap, 16.0, 42.0))


def _lane_content_height(lane: LayoutLane) -> float:
    if lane.node_count <= 0:
        return 0.0
    gap = _lane_vertical_gap(lane)
    return float((lane.node_count * NODE_HEIGHT) + (max(0, lane.node_count - 1) * gap))


def _lane_start_y_regular(lane: LayoutLane) -> float:
    base_y = float(TOP_MARGIN + LANE_HEADER_TO_CONTENT_GAP)

    if lane.role in {"external", "context"}:
        base_y += LANE_SECONDARY_VERTICAL_OFFSET
    elif lane.role in {"note", "annotations"}:
        base_y += LANE_NOTE_VERTICAL_OFFSET

    if lane.density == "airy":
        base_y += 4.0

    return base_y


def _position_nodes_regular_view(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
) -> list[DependencyNode]:
    ordered_nodes: list[DependencyNode] = []

    for lane in lanes:
        y_cursor = _lane_start_y_regular(lane)
        gap = _lane_vertical_gap(lane)

        for index_in_lane, node in enumerate(_lane_nodes_in_order(graph, lane)):
            node.x = lane.x + LANE_BASE_PADDING_X
            node.y = y_cursor

            apply_lane_metadata(node, lane, index_in_lane)
            ordered_nodes.append(node)

            y_cursor += NODE_HEIGHT + gap

    return ordered_nodes


def _hero_lane_center_y() -> float:
    return float(TOP_MARGIN + 170.0)


def _position_nodes_focus_view(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
) -> list[DependencyNode]:
    ordered_nodes: list[DependencyNode] = []
    lane_lookup = {lane.key: lane for lane in lanes}

    hero_lane = lane_lookup.get("lane:focus:center")
    hero_center_y = _hero_lane_center_y()

    if hero_lane is not None and hero_lane.node_keys:
        hero_node = graph.nodes.get(hero_lane.node_keys[0])
        if hero_node is not None:
            hero_node.x = hero_lane.x + ((hero_lane.width - hero_node.width) / 2.0)
            hero_node.y = hero_center_y - (NODE_HEIGHT / 2.0)
            apply_lane_metadata(hero_node, hero_lane, 0)
            ordered_nodes.append(hero_node)

    for lane in lanes:
        if lane.key == "lane:focus:center":
            continue

        lane_nodes = _lane_nodes_in_order(graph, lane)
        if not lane_nodes:
            continue

        gap = _lane_vertical_gap(lane)
        block_height = _lane_content_height(lane)

        if lane.role == "context":
            start_y = max(
                float(TOP_MARGIN + LANE_HEADER_TO_CONTENT_GAP + 12.0),
                (hero_center_y - (block_height / 2.0)) + FOCUS_CONTEXT_VERTICAL_OFFSET,
            )
        else:
            start_y = max(
                float(TOP_MARGIN + LANE_HEADER_TO_CONTENT_GAP),
                hero_center_y - (block_height / 2.0),
            )

        for index_in_lane, node in enumerate(lane_nodes):
            node.x = lane.x + LANE_BASE_PADDING_X
            node.y = start_y + (index_in_lane * (NODE_HEIGHT + gap))

            apply_lane_metadata(node, lane, index_in_lane)
            ordered_nodes.append(node)

    return ordered_nodes


def position_nodes_in_lanes(
    graph: DependencyGraph,
    lanes: list[LayoutLane],
    state: AnalysisState,
) -> list[DependencyNode]:
    """
    Posiciona nodos en sus carriles.

    - Vista module/package: columnas legibles con respiro.
    - Vista focus: staging centrado en el héroe.
    """
    if state.view == "focus":
        nodes = _position_nodes_focus_view(graph, lanes)
    else:
        nodes = _position_nodes_regular_view(graph, lanes)

    return sorted(
        nodes,
        key=lambda node: (
            int(node.metadata.get("visual_priority", 0)),
            float(node.metadata.get("layout_lane_x", 0.0)),
            node.y,
            node.label.lower(),
        ),
        reverse=False,
    )


def compute_layout_width(lanes: list[LayoutLane]) -> int:
    if not lanes:
        return DEFAULT_LAYOUT_WIDTH

    right_edge = max((lane.x + lane.width for lane in lanes), default=float(LEFT_MARGIN))
    return int(max(DEFAULT_LAYOUT_WIDTH, right_edge + RIGHT_MARGIN))


def compute_layout_height(nodes: Iterable[DependencyNode]) -> int:
    node_list = list(nodes)
    if not node_list:
        return DEFAULT_LAYOUT_HEIGHT

    bottom = max((node.y + NODE_HEIGHT for node in node_list), default=float(TOP_MARGIN))
    return int(max(DEFAULT_LAYOUT_HEIGHT, bottom + BOTTOM_MARGIN))


def _reset_layout_metadata(graph: DependencyGraph) -> None:
    layout_keys = {
        "layout_lane_key",
        "layout_lane_label",
        "layout_lane_x",
        "layout_lane_width",
        "layout_index_in_lane",
        "layout_lane_role",
        "layout_lane_density",
        "layout_lane_spacing_mode",
        "layout_lane_visual_emphasis",
        "visual_role",
        "visual_priority",
        "focus_relation",
    }

    for node in graph.nodes.values():
        for key in layout_keys:
            node.metadata.pop(key, None)
        node.x = 0.0
        node.y = 0.0


def layout_dependency_graph(
    graph: DependencyGraph,
    state: AnalysisState,
    notify: Callable[[str, str], None],
) -> LayoutResult:
    """
    Pipeline principal de layout.

    Produce:
    - nodos con x/y/width
    - carriles/columnas
    - tamaño recomendado del SVG
    """
    notify("Preparando layout del grafo...", f"{len(graph.nodes)} nodos")

    if not graph.nodes:
        return LayoutResult(
            nodes=[],
            lanes=[],
            width=DEFAULT_LAYOUT_WIDTH,
            height=DEFAULT_LAYOUT_HEIGHT,
        )

    _reset_layout_metadata(graph)
    graph.finalize_metrics()

    focus_key = ""
    if state.view == "focus":
        focus_key = resolve_focus_node_key(graph, state.focus_target)

    for node in graph.nodes.values():
        prepare_node_width(node)

    notify("Ordenando carriles...", state.view)
    lanes = choose_lanes_for_view(graph, state, focus_key)
    if not lanes:
        return LayoutResult(
            nodes=[],
            lanes=[],
            width=DEFAULT_LAYOUT_WIDTH,
            height=DEFAULT_LAYOUT_HEIGHT,
        )

    notify("Afinando orden interno...", f"{len(lanes)} carriles")
    _refine_lane_node_order(graph, lanes)

    _annotate_semantic_metadata(graph, lanes, state, focus_key)
    _boost_node_widths_for_semantics(graph)

    notify("Distribuyendo columnas...", f"{len(lanes)} carriles")
    position_lanes_horizontally(graph, lanes, state)
    annotate_lane_statistics(graph, lanes)

    notify("Posicionando nodos...", f"{len(graph.nodes)} nodos visibles")
    nodes = position_nodes_in_lanes(graph, lanes, state)

    width = compute_layout_width(lanes)
    height = compute_layout_height(nodes)

    return LayoutResult(
        nodes=nodes,
        lanes=lanes,
        width=width,
        height=height,
    )
def _hier_visible_dependency_maps(
    graph: DependencyGraph,
    visible_keys: set[str],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    parents: dict[str, set[str]] = {key: set() for key in visible_keys}
    children: dict[str, set[str]] = {key: set() for key in visible_keys}

    for edge in graph.iter_edges_sorted():
        if edge.source not in visible_keys or edge.target not in visible_keys:
            continue
        if edge.source == edge.target:
            continue

        parent_key = edge.target
        child_key = edge.source

        parents.setdefault(child_key, set()).add(parent_key)
        children.setdefault(parent_key, set()).add(child_key)

    return parents, children


def _hier_root_nodes(
    nodes: list[DependencyNode],
    parents: dict[str, set[str]],
    children: dict[str, set[str]],
) -> list[DependencyNode]:
    roots = [node for node in nodes if not parents.get(node.key)]
    if roots:
        return sorted(
            roots,
            key=lambda node: (
                -int(node.inbound),
                int(node.outbound),
                -len(children.get(node.key, set())),
                node.group.lower(),
                node.label.lower(),
            ),
        )

    return sorted(
        nodes,
        key=lambda node: (
            -int(node.inbound - node.outbound),
            -len(children.get(node.key, set())),
            node.group.lower(),
            node.label.lower(),
        ),
    )


def _hier_assign_levels(
    nodes: list[DependencyNode],
    parents: dict[str, set[str]],
    children: dict[str, set[str]],
) -> dict[str, int]:
    visible_keys = {node.key for node in nodes}
    indegree: dict[str, int] = {
        key: len(parents.get(key, set()))
        for key in visible_keys
    }
    levels: dict[str, int] = {}

    queue: list[str] = [node.key for node in _hier_root_nodes(nodes, parents, children)]
    if not queue and nodes:
        queue = [nodes[0].key]

    for key in queue:
        levels[key] = 0

    cursor = 0
    while cursor < len(queue):
        current = queue[cursor]
        cursor += 1
        current_level = levels.get(current, 0)

        for child in sorted(children.get(current, set())):
            next_level = current_level + 1
            if next_level > levels.get(child, -1):
                levels[child] = next_level

            indegree[child] = max(0, indegree.get(child, 0) - 1)
            if indegree[child] == 0 and child not in queue:
                queue.append(child)

    unresolved = [node for node in nodes if node.key not in levels]
    if unresolved:
        ordered_unresolved = sorted(
            unresolved,
            key=lambda node: (
                -int(node.inbound),
                int(node.outbound),
                node.group.lower(),
                node.label.lower(),
            ),
        )
        for node in ordered_unresolved:
            parent_levels = [
                levels[parent_key]
                for parent_key in parents.get(node.key, set())
                if parent_key in levels
            ]
            levels[node.key] = (max(parent_levels) + 1) if parent_levels else 0

        for _ in range(max(2, len(nodes))):
            changed = False
            for parent_key, child_keys in children.items():
                parent_level = levels.get(parent_key, 0)
                for child_key in child_keys:
                    wanted = parent_level + 1
                    if wanted > levels.get(child_key, 0):
                        levels[child_key] = wanted
                        changed = True
            if not changed:
                break

    if levels:
        min_level = min(levels.values())
        if min_level != 0:
            for key in list(levels.keys()):
                levels[key] = max(0, levels[key] - min_level)

    return levels


def _hier_group_nodes_by_level(
    nodes: list[DependencyNode],
    levels: dict[str, int],
) -> dict[int, list[DependencyNode]]:
    grouped: dict[int, list[DependencyNode]] = {}
    for node in nodes:
        grouped.setdefault(levels.get(node.key, 0), []).append(node)
    return grouped


def _hier_order_rows(
    grouped: dict[int, list[DependencyNode]],
    parents: dict[str, set[str]],
    children: dict[str, set[str]],
) -> list[tuple[int, list[DependencyNode]]]:
    ordered_rows: list[tuple[int, list[DependencyNode]]] = []
    previous_order: dict[str, float] = {}

    for level in sorted(grouped):
        row_nodes = list(grouped[level])

        def sort_key(node: DependencyNode) -> tuple[float, int, int, str, str]:
            parent_positions = [
                previous_order[parent_key]
                for parent_key in parents.get(node.key, set())
                if parent_key in previous_order
            ]
            bary = (sum(parent_positions) / len(parent_positions)) if parent_positions else 999999.0
            return (
                bary,
                -len(children.get(node.key, set())),
                -int(node.inbound),
                node.group.lower(),
                node.label.lower(),
            )

        row_nodes.sort(key=sort_key)

        current_order: dict[str, float] = {}
        for index, node in enumerate(row_nodes):
            current_order[node.key] = float(index)

        previous_order = current_order
        ordered_rows.append((level, row_nodes))

    return ordered_rows


def _hier_chunk_rows(
    ordered_rows: list[tuple[int, list[DependencyNode]]],
    *,
    max_nodes_per_row: int = 8,
    max_row_width_hint: float = 1680.0,
    gap_x: float = 56.0,
) -> list[tuple[int, list[DependencyNode]]]:
    final_rows: list[tuple[int, list[DependencyNode]]] = []

    for level, row_nodes in ordered_rows:
        current: list[DependencyNode] = []
        current_width = 0.0

        for node in row_nodes:
            node_width = float(max(NODE_MIN_WIDTH, node.width or NODE_MIN_WIDTH))
            proposed = node_width if not current else (current_width + gap_x + node_width)

            if current and (len(current) >= max_nodes_per_row or proposed > max_row_width_hint):
                final_rows.append((level, current))
                current = [node]
                current_width = node_width
            else:
                current.append(node)
                current_width = proposed

        if current:
            final_rows.append((level, current))

    return final_rows


def relayout_dependency_graph_as_layered_hierarchy(
    graph: DependencyGraph,
    state: AnalysisState,
    layout: LayoutResult,
    notify: Callable[[str, str], None],
) -> LayoutResult:
    """
    Reacomoda el grafo visible como jerarquÃ­a por capas:
    - dependencias/fundaciones arriba
    - consumidores abajo
    - sin columnas verticales tipo lane
    - inspirado en mapas conceptuales por filas
    """
    if not layout.nodes:
        return layout

    notify("Relayout jerÃ¡rquico...", f"{len(layout.nodes)} nodos")

    nodes = list(layout.nodes)
    visible_keys = {node.key for node in nodes}
    parents, children = _hier_visible_dependency_maps(graph, visible_keys)
    levels = _hier_assign_levels(nodes, parents, children)
    grouped = _hier_group_nodes_by_level(nodes, levels)
    ordered_rows = _hier_order_rows(grouped, parents, children)
    chunked_rows = _hier_chunk_rows(ordered_rows)

    if not chunked_rows:
        return layout

    horizontal_gap = 56.0
    top_y = float(TOP_MARGIN + 34.0)

    row_widths: list[float] = []
    max_row_width = 0.0
    for _, row_nodes in chunked_rows:
        row_width = sum(float(max(NODE_MIN_WIDTH, node.width or NODE_MIN_WIDTH)) for node in row_nodes)
        if len(row_nodes) > 1:
            row_width += horizontal_gap * (len(row_nodes) - 1)
        row_widths.append(row_width)
        max_row_width = max(max_row_width, row_width)

    content_width = int(
        max(
            DEFAULT_LAYOUT_WIDTH,
            max_row_width + LEFT_MARGIN + RIGHT_MARGIN + 180.0,
        )
    )

    y = top_y
    positioned: list[DependencyNode] = []

    for row_index, (level, row_nodes) in enumerate(chunked_rows):
        row_width = row_widths[row_index]
        start_x = max(float(LEFT_MARGIN), (content_width - row_width) / 2.0)
        x = start_x

        for index_in_row, node in enumerate(row_nodes):
            node.width = float(max(NODE_MIN_WIDTH, node.width or NODE_MIN_WIDTH))
            node.x = x
            node.y = y

            node.metadata["layout_lane_key"] = f"hier:{level}"
            node.metadata["layout_lane_label"] = f"Nivel {level + 1}"
            node.metadata["layout_lane_x"] = start_x
            node.metadata["layout_lane_width"] = row_width
            node.metadata["layout_index_in_lane"] = index_in_row
            node.metadata["layout_lane_role"] = "hierarchy"
            node.metadata["layout_lane_density"] = "layered"
            node.metadata["layout_lane_spacing_mode"] = "layered"
            node.metadata["layout_lane_visual_emphasis"] = max(0.80, 1.0 - (level * 0.05))
            node.metadata["visual_priority"] = level

            positioned.append(node)
            x += node.width + horizontal_gap

        current_level = level
        next_level = chunked_rows[row_index + 1][0] if row_index + 1 < len(chunked_rows) else None
        if next_level == current_level:
            y += NODE_HEIGHT + 74.0
        else:
            y += NODE_HEIGHT + 132.0

    height = int(max(DEFAULT_LAYOUT_HEIGHT, y + BOTTOM_MARGIN + 24.0))

    positioned.sort(key=lambda node: (node.y, node.x, node.label.lower()))

    return LayoutResult(
        nodes=positioned,
        lanes=[],
        width=content_width,
        height=height,
    )

# ============================================================

# 09. TEMAS VISUALES
# Fuente unica de verdad para temas SVG
# ============================================================

_THEME_TOKEN_FAMILIES: tuple[str, ...] = (
    "surfaces",
    "text",
    "accents",
    "borders",
    "ambient",
)

_NODE_PRESET_KEYS: tuple[str, ...] = (
    "package",
    "module",
    "external",
    "note",
    "focus_hero",
    "focus_inbound",
    "focus_outbound",
    "focus_mixed",
    "context_muted",
    "hub_accent",
)

_EDGE_PRESET_KEYS: tuple[str, ...] = (
    "default",
    "muted",
    "focus_inbound",
    "focus_outbound",
    "self_loop",
    "cross_lane",
    "intra_lane",
)

_LANE_PRESET_KEYS: tuple[str, ...] = (
    "standard",
    "focus_center",
    "focus_side",
    "issue_lane",
    "external_lane",
)

_PANEL_PRESET_KEYS: tuple[str, ...] = (
    "header",
    "legend",
    "footer",
    "warning",
)

_BADGE_PRESET_KEYS: tuple[str, ...] = (
    "inbound",
    "outbound",
    "hub",
    "island",
)

_MARKER_PRESET_KEYS: tuple[str, ...] = (
    "default_arrow",
    "subtle_arrow",
    "focus_arrow",
)

_EFFECT_PRESET_KEYS: tuple[str, ...] = (
    "glow_intensity",
    "shadow_intensity",
    "border_emphasis",
    "shine_intensity",
)

_GRADIENT_IDS: dict[str, str] = {
    "background": "bgGrad",
    "lane_header": "laneHeaderGrad",
    "package": "packageNodeGrad",
    "module": "moduleNodeGrad",
    "external": "externalNodeGrad",
    "note": "noteNodeGrad",
    "focus_hero": "focusHeroNodeGrad",
    "focus_inbound": "focusInboundNodeGrad",
    "focus_outbound": "focusOutboundNodeGrad",
    "focus_mixed": "focusMixedNodeGrad",
    "context_muted": "contextMutedNodeGrad",
    "hub_accent": "hubAccentNodeGrad",
}

_RADIAL_IDS: dict[str, str] = {
    "halo_a": "haloA",
    "halo_b": "haloB",
}

_PATTERN_IDS: dict[str, str] = {
    "grid": "gridPattern",
}

_FILTER_IDS: dict[str, str] = {
    "node_shadow": "nodeShadow",
    "edge_blur": "edgeBlur",
    "header_glow": "headerGlow",
}

_MARKER_IDS: dict[str, str] = {
    "default_arrow": "arrowHead",
    "subtle_arrow": "subtleArrowHead",
    "focus_arrow": "focusArrowHead",
}


@dataclass(slots=True)
class ThemeBundle:
    id: str
    label: str
    svg_defs: str
    is_default: bool = False
    tokens: dict[str, dict[str, Any]] = field(default_factory=dict)
    node_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    edge_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    lane_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    panel_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    badge_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    marker_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    effect_presets: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.id = clean_text(self.id).lower() or DEFAULT_THEME_ID
        self.label = clean_text(self.label) or self.id.title()
        self.svg_defs = self.svg_defs or ""
        self.tokens = _deep_copy_value(self.tokens)
        self.node_presets = _deep_copy_value(self.node_presets)
        self.edge_presets = _deep_copy_value(self.edge_presets)
        self.lane_presets = _deep_copy_value(self.lane_presets)
        self.panel_presets = _deep_copy_value(self.panel_presets)
        self.badge_presets = _deep_copy_value(self.badge_presets)
        self.marker_presets = _deep_copy_value(self.marker_presets)
        self.effect_presets = _deep_copy_value(self.effect_presets)



@dataclass(frozen=True, slots=True)
class ThemeManifest:
    id: str
    label: str
    dropdown_label: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    is_default: bool = False
    bundle_index: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", clean_text(self.id).lower() or DEFAULT_THEME_ID)
        label = clean_text(self.label) or self.id.title()
        object.__setattr__(self, "label", label)
        dropdown_label = clean_text(self.dropdown_label) or label
        object.__setattr__(self, "dropdown_label", dropdown_label)
        aliases = tuple(
            alias
            for alias in dict.fromkeys(clean_text(item) for item in self.aliases if clean_text(item))
        )
        object.__setattr__(self, "aliases", aliases)
        object.__setattr__(self, "is_default", bool(self.is_default))
        object.__setattr__(self, "bundle_index", int(self.bundle_index))


@dataclass(slots=True)
class ThemeRenderContract:
    theme_id: str
    label: str
    svg_defs: str
    is_dark: bool = True
    tokens: dict[str, Any] = field(default_factory=dict)
    node_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    edge_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    lane_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    panel_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    badge_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    marker_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    effect_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    state_tokens: dict[str, dict[str, Any]] = field(default_factory=dict)
    component_tokens: dict[str, dict[str, Any]] = field(default_factory=dict)
    manifest: ThemeManifest | None = None
    raw_bundle: ThemeBundle | None = None

    def __post_init__(self) -> None:
        self.theme_id = clean_text(self.theme_id).lower() or DEFAULT_THEME_ID
        self.label = clean_text(self.label) or self.theme_id.title()
        self.svg_defs = self.svg_defs or ""
        self.is_dark = bool(self.is_dark)
        self.tokens = _deep_copy_value(self.tokens)
        self.node_presets = _deep_copy_value(self.node_presets)
        self.edge_presets = _deep_copy_value(self.edge_presets)
        self.lane_presets = _deep_copy_value(self.lane_presets)
        self.panel_presets = _deep_copy_value(self.panel_presets)
        self.badge_presets = _deep_copy_value(self.badge_presets)
        self.marker_presets = _deep_copy_value(self.marker_presets)
        self.effect_presets = _deep_copy_value(self.effect_presets)
        self.state_tokens = _deep_copy_value(self.state_tokens)
        self.component_tokens = _deep_copy_value(self.component_tokens)


def _deep_copy_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _deep_copy_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_deep_copy_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_deep_copy_value(item) for item in value)
    return value


def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = _deep_copy_value(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = _deep_copy_value(value)
    return merged


def _css_name(value: str) -> str:
    return clean_text(value).replace("_", "-").replace(" ", "-").strip("-")


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _fmt_float(value: Any, default: float = 0.0) -> str:
    return f"{_safe_float(value, default):.2f}".rstrip("0").rstrip(".")


def _gradient_ref(gradient_id: str) -> str:
    return f"url(#{gradient_id})"



def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    text = clean_text(value).lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return (127, 127, 127)
    try:
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
    except Exception:
        return (127, 127, 127)


def _mix_hex(a: str, b: str, ratio: float) -> str:
    ratio = _clamp(ratio, 0.0, 1.0)
    ar, ag, ab = _hex_to_rgb(a)
    br, bg, bb = _hex_to_rgb(b)
    rr = int(round((ar * (1.0 - ratio)) + (br * ratio)))
    rg = int(round((ag * (1.0 - ratio)) + (bg * ratio)))
    rb = int(round((ab * (1.0 - ratio)) + (bb * ratio)))
    return f"#{rr:02x}{rg:02x}{rb:02x}"


def _with_alpha(hex_color: str, opacity: float) -> str:
    opacity = _clamp(opacity, 0.0, 1.0)
    r, g, b = _hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {opacity:.3f})"


def _coerce_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _build_theme_tokens(seed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base_tokens: dict[str, dict[str, Any]] = {
        "surfaces": {
            "canvas_start": "#030712",
            "canvas_mid": "#0b1224",
            "canvas_end": "#111827",
            "header_band": "#0f172a",
            "panel": "#0f172a",
            "panel_alt": "#13213a",
            "panel_soft": "#0b1326",
            "legend_panel": "#0f172a",
            "warning_panel": "#20140a",
            "lane_header_start": "#0f172a",
            "lane_header_end": "#13213a",
            "node_package_start": "#102c52",
            "node_package_end": "#0a1e3f",
            "node_module_start": "#0d3325",
            "node_module_end": "#08271c",
            "node_external_start": "#33245a",
            "node_external_end": "#25173f",
            "node_note_start": "#4c2f08",
            "node_note_end": "#3b2408",
            "node_focus_hero_start": "#123864",
            "node_focus_hero_end": "#0c244a",
            "node_focus_inbound_start": "#0d3353",
            "node_focus_inbound_end": "#082843",
            "node_focus_outbound_start": "#113925",
            "node_focus_outbound_end": "#0a2b1b",
            "node_focus_mixed_start": "#18315f",
            "node_focus_mixed_end": "#102543",
            "node_context_muted_start": "#172031",
            "node_context_muted_end": "#121a29",
            "node_hub_accent_start": "#4a3408",
            "node_hub_accent_end": "#332308",
        },
        "text": {
            "title": "#ecfeff",
            "body": "#e2e8f0",
            "muted": "#93c5fd",
            "soft": "#94a3b8",
            "code": "#cbd5e1",
            "warning": "#fbbf24",
            "inverse": "#ffffff",
            "badge_dark": "#04111f",
            "badge_light": "#ffffff",
        },
        "accents": {
            "primary": "#38bdf8",
            "secondary": "#60a5fa",
            "tertiary": "#a855f7",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "focus": "#7dd3fc",
            "hub": "#f59e0b",
        },
        "borders": {
            "subtle": "#1d3557",
            "panel": "#1e3a5f",
            "lane": "#1d3557",
            "strong": "#60a5fa",
            "focus": "#7dd3fc",
            "muted": "#475569",
            "node_package": "#60a5fa",
            "node_module": "#4ade80",
            "node_external": "#c084fc",
            "node_note": "#fbbf24",
            "warning": "#fbbf24",
        },
        "ambient": {
            "grid": "#38bdf8",
            "grid_opacity": 0.08,
            "grid_size": 28,
            "grid_stroke_width": 0.9,
            "halo_a_color": "#22d3ee",
            "halo_a_secondary": "#2563eb",
            "halo_a_opacity": 0.22,
            "halo_a_fade_opacity": 0.10,
            "halo_b_color": "#a855f7",
            "halo_b_opacity": 0.18,
            "header_glow": "#38bdf8",
        },
    }

    return _merge_dicts(base_tokens, seed)


def _build_effect_presets(seed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base_effects: dict[str, dict[str, Any]] = {
        "glow_intensity": {
            "ambient": 0.16,
            "edge": 0.10,
            "focus": 0.22,
            "header": 0.15,
        },
        "shadow_intensity": {
            "node": 0.55,
            "panel": 0.18,
            "soft": 0.08,
        },
        "border_emphasis": {
            "standard": 1.00,
            "strong": 1.25,
            "focus": 1.52,
            "hub": 1.35,
        },
        "shine_intensity": {
            "standard": 0.10,
            "focus": 0.16,
            "panel": 0.08,
        },
    }

    return _merge_dicts(base_effects, seed)


def _node_preset(
    *,
    key: str,
    gradient_id: str,
    stroke: str,
    label_fill: str,
    subtitle_fill: str,
    border_width: float,
    shine_opacity: float,
    semantic_role: str,
    emphasis: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "css_class": f"node-{_css_name(key)}",
        "semantic_role": semantic_role,
        "gradient_id": gradient_id,
        "fill": _gradient_ref(gradient_id),
        "stroke": stroke,
        "label_fill": label_fill,
        "subtitle_fill": subtitle_fill,
        "border_width": border_width,
        "radius": 12,
        "shine_opacity": shine_opacity,
        "emphasis": emphasis,
    }


def _build_node_presets(
    tokens: dict[str, dict[str, Any]],
    effects: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    surfaces = tokens["surfaces"]
    text = tokens["text"]
    borders = tokens["borders"]
    accents = tokens["accents"]

    standard_border = 1.55 * _safe_float(effects["border_emphasis"].get("standard"), 1.0)
    strong_border = 1.55 * _safe_float(effects["border_emphasis"].get("strong"), 1.25)
    focus_border = 1.55 * _safe_float(effects["border_emphasis"].get("focus"), 1.52)
    hub_border = 1.55 * _safe_float(effects["border_emphasis"].get("hub"), 1.35)
    shine_standard = _safe_float(effects["shine_intensity"].get("standard"), 0.10)
    shine_focus = _safe_float(effects["shine_intensity"].get("focus"), 0.16)

    return {
        "package": _node_preset(
            key="package",
            gradient_id=_GRADIENT_IDS["package"],
            stroke=borders["node_package"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=standard_border,
            shine_opacity=shine_standard,
            semantic_role="package",
            emphasis="standard",
        ),
        "module": _node_preset(
            key="module",
            gradient_id=_GRADIENT_IDS["module"],
            stroke=borders["node_module"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=standard_border,
            shine_opacity=shine_standard,
            semantic_role="module",
            emphasis="standard",
        ),
        "external": _node_preset(
            key="external",
            gradient_id=_GRADIENT_IDS["external"],
            stroke=borders["node_external"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=standard_border,
            shine_opacity=shine_standard,
            semantic_role="external",
            emphasis="standard",
        ),
        "note": _node_preset(
            key="note",
            gradient_id=_GRADIENT_IDS["note"],
            stroke=borders["node_note"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=standard_border,
            shine_opacity=shine_standard,
            semantic_role="note",
            emphasis="warning",
        ),
        "focus_hero": _node_preset(
            key="focus_hero",
            gradient_id=_GRADIENT_IDS["focus_hero"],
            stroke=borders["focus"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=focus_border,
            shine_opacity=shine_focus,
            semantic_role="focus_hero",
            emphasis="focus",
        ),
        "focus_inbound": _node_preset(
            key="focus_inbound",
            gradient_id=_GRADIENT_IDS["focus_inbound"],
            stroke=accents["secondary"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=strong_border,
            shine_opacity=shine_standard,
            semantic_role="focus_inbound",
            emphasis="supporting",
        ),
        "focus_outbound": _node_preset(
            key="focus_outbound",
            gradient_id=_GRADIENT_IDS["focus_outbound"],
            stroke=accents["success"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=strong_border,
            shine_opacity=shine_standard,
            semantic_role="focus_outbound",
            emphasis="supporting",
        ),
        "focus_mixed": _node_preset(
            key="focus_mixed",
            gradient_id=_GRADIENT_IDS["focus_mixed"],
            stroke=accents["tertiary"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=strong_border,
            shine_opacity=shine_standard,
            semantic_role="focus_mixed",
            emphasis="supporting",
        ),
        "context_muted": _node_preset(
            key="context_muted",
            gradient_id=_GRADIENT_IDS["context_muted"],
            stroke=borders["muted"],
            label_fill=text["body"],
            subtitle_fill=text["soft"],
            border_width=standard_border,
            shine_opacity=max(0.04, shine_standard * 0.6),
            semantic_role="context_muted",
            emphasis="muted",
        ),
        "hub_accent": _node_preset(
            key="hub_accent",
            gradient_id=_GRADIENT_IDS["hub_accent"],
            stroke=accents["hub"],
            label_fill=text["body"],
            subtitle_fill=text["muted"],
            border_width=hub_border,
            shine_opacity=shine_focus,
            semantic_role="hub_accent",
            emphasis="strong",
        ),
    }


def _edge_preset(
    *,
    key: str,
    stroke: str,
    glow: str,
    opacity: float,
    glow_opacity: float,
    base_width: float,
    glow_width: float,
    marker_key: str,
) -> dict[str, Any]:
    marker_id = _MARKER_IDS.get(marker_key, _MARKER_IDS["default_arrow"])
    return {
        "key": key,
        "css_class": f"edge-{_css_name(key)}",
        "stroke": stroke,
        "glow": glow,
        "opacity": opacity,
        "glow_opacity": glow_opacity,
        "base_width": base_width,
        "glow_width": glow_width,
        "marker": f"url(#{marker_id})",
        "marker_key": marker_key,
        "marker_id": marker_id,
    }


def _build_edge_presets(
    tokens: dict[str, dict[str, Any]],
    effects: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    accents = tokens["accents"]
    text = tokens["text"]
    ambient = tokens["ambient"]
    glow_base = _safe_float(effects["glow_intensity"].get("edge"), 0.10)
    glow_focus = _safe_float(effects["glow_intensity"].get("focus"), 0.22)

    return {
        "default": _edge_preset(
            key="default",
            stroke=accents["focus"],
            glow=accents["primary"],
            opacity=0.68,
            glow_opacity=glow_base,
            base_width=1.8,
            glow_width=7.2,
            marker_key="default_arrow",
        ),
        "muted": _edge_preset(
            key="muted",
            stroke=text["soft"],
            glow=text["soft"],
            opacity=0.34,
            glow_opacity=max(0.04, glow_base * 0.65),
            base_width=1.35,
            glow_width=4.8,
            marker_key="subtle_arrow",
        ),
        "focus_inbound": _edge_preset(
            key="focus_inbound",
            stroke=accents["secondary"],
            glow=accents["primary"],
            opacity=0.82,
            glow_opacity=glow_focus,
            base_width=2.05,
            glow_width=8.2,
            marker_key="focus_arrow",
        ),
        "focus_outbound": _edge_preset(
            key="focus_outbound",
            stroke=accents["success"],
            glow=accents["success"],
            opacity=0.82,
            glow_opacity=glow_focus,
            base_width=2.05,
            glow_width=8.2,
            marker_key="focus_arrow",
        ),
        "self_loop": _edge_preset(
            key="self_loop",
            stroke=accents["warning"],
            glow=accents["warning"],
            opacity=0.74,
            glow_opacity=max(0.06, glow_focus * 0.85),
            base_width=1.95,
            glow_width=7.6,
            marker_key="default_arrow",
        ),
        "cross_lane": _edge_preset(
            key="cross_lane",
            stroke=accents["focus"],
            glow=ambient["halo_a_color"],
            opacity=0.74,
            glow_opacity=glow_base,
            base_width=1.9,
            glow_width=7.4,
            marker_key="default_arrow",
        ),
        "intra_lane": _edge_preset(
            key="intra_lane",
            stroke=text["muted"],
            glow=text["muted"],
            opacity=0.54,
            glow_opacity=max(0.04, glow_base * 0.75),
            base_width=1.55,
            glow_width=5.6,
            marker_key="subtle_arrow",
        ),
    }


def _build_lane_presets(
    tokens: dict[str, dict[str, Any]],
    effects: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    surfaces = tokens["surfaces"]
    text = tokens["text"]
    accents = tokens["accents"]
    borders = tokens["borders"]
    glow_header = _safe_float(effects["glow_intensity"].get("header"), 0.15)

    return {
        "standard": {
            "key": "standard",
            "css_class": "lane-standard",
            "band_fill": _gradient_ref(_GRADIENT_IDS["lane_header"]),
            "band_stroke": borders["lane"],
            "band_opacity": 0.20,
            "title_fill": text["title"],
            "meta_fill": text["soft"],
            "header_fill": surfaces["lane_header_start"],
            "header_glow_opacity": glow_header,
        },
        "focus_center": {
            "key": "focus_center",
            "css_class": "lane-focus-center",
            "band_fill": _gradient_ref(_GRADIENT_IDS["lane_header"]),
            "band_stroke": borders["focus"],
            "band_opacity": 0.28,
            "title_fill": text["title"],
            "meta_fill": text["muted"],
            "header_fill": surfaces["lane_header_end"],
            "header_glow_opacity": glow_header + 0.05,
        },
        "focus_side": {
            "key": "focus_side",
            "css_class": "lane-focus-side",
            "band_fill": surfaces["panel_soft"],
            "band_stroke": accents["secondary"],
            "band_opacity": 0.18,
            "title_fill": text["body"],
            "meta_fill": text["soft"],
            "header_fill": surfaces["panel_alt"],
            "header_glow_opacity": glow_header,
        },
        "issue_lane": {
            "key": "issue_lane",
            "css_class": "lane-issue",
            "band_fill": surfaces["warning_panel"],
            "band_stroke": borders["warning"],
            "band_opacity": 0.22,
            "title_fill": text["warning"],
            "meta_fill": text["soft"],
            "header_fill": surfaces["warning_panel"],
            "header_glow_opacity": glow_header,
        },
        "external_lane": {
            "key": "external_lane",
            "css_class": "lane-external",
            "band_fill": surfaces["panel_alt"],
            "band_stroke": borders["node_external"],
            "band_opacity": 0.18,
            "title_fill": text["body"],
            "meta_fill": text["soft"],
            "header_fill": surfaces["panel_alt"],
            "header_glow_opacity": glow_header,
        },
    }


def _build_panel_presets(tokens: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    surfaces = tokens["surfaces"]
    text = tokens["text"]
    borders = tokens["borders"]
    ambient = tokens["ambient"]

    return {
        "header": {
            "key": "header",
            "css_class": "panel-header",
            "fill": surfaces["header_band"],
            "stroke": borders["panel"],
            "text_fill": text["body"],
            "meta_fill": text["soft"],
            "fill_opacity": 0.54,
            "glow": ambient["header_glow"],
        },
        "legend": {
            "key": "legend",
            "css_class": "panel-legend",
            "fill": surfaces["legend_panel"],
            "stroke": borders["panel"],
            "text_fill": text["body"],
            "meta_fill": text["soft"],
            "fill_opacity": 0.72,
            "glow": ambient["header_glow"],
        },
        "footer": {
            "key": "footer",
            "css_class": "panel-footer",
            "fill": surfaces["panel_soft"],
            "stroke": borders["subtle"],
            "text_fill": text["soft"],
            "meta_fill": text["soft"],
            "fill_opacity": 1.0,
            "glow": ambient["header_glow"],
        },
        "warning": {
            "key": "warning",
            "css_class": "panel-warning",
            "fill": surfaces["warning_panel"],
            "stroke": borders["warning"],
            "text_fill": text["warning"],
            "meta_fill": text["soft"],
            "fill_opacity": 0.82,
            "glow": ambient["header_glow"],
        },
    }


def _build_badge_presets(tokens: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    text = tokens["text"]
    accents = tokens["accents"]

    return {
        "inbound": {
            "key": "inbound",
            "fill": accents["secondary"],
            "text_fill": text["badge_dark"],
        },
        "outbound": {
            "key": "outbound",
            "fill": accents["success"],
            "text_fill": text["badge_dark"],
        },
        "hub": {
            "key": "hub",
            "fill": accents["hub"],
            "text_fill": text["badge_dark"],
        },
        "island": {
            "key": "island",
            "fill": accents["tertiary"],
            "text_fill": text["badge_light"],
        },
    }


def _build_marker_presets(
    tokens: dict[str, dict[str, Any]],
    effects: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    accents = tokens["accents"]
    text = tokens["text"]
    glow_focus = _safe_float(effects["glow_intensity"].get("focus"), 0.22)

    return {
        "default_arrow": {
            "key": "default_arrow",
            "svg_id": _MARKER_IDS["default_arrow"],
            "fill": accents["focus"],
            "opacity": 0.92,
        },
        "subtle_arrow": {
            "key": "subtle_arrow",
            "svg_id": _MARKER_IDS["subtle_arrow"],
            "fill": text["soft"],
            "opacity": 0.86,
        },
        "focus_arrow": {
            "key": "focus_arrow",
            "svg_id": _MARKER_IDS["focus_arrow"],
            "fill": accents["secondary"],
            "opacity": min(1.0, glow_focus + 0.75),
        },
    }


def _build_gradients(bundle: ThemeBundle) -> str:
    tokens = bundle.tokens
    surfaces = tokens["surfaces"]
    ambient = tokens["ambient"]

    gradient_specs = [
        (
            _GRADIENT_IDS["background"],
            [
                ("0%", surfaces["canvas_start"]),
                ("45%", surfaces["canvas_mid"]),
                ("100%", surfaces["canvas_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["lane_header"],
            [
                ("0%", surfaces["lane_header_start"]),
                ("100%", surfaces["lane_header_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["package"],
            [
                ("0%", surfaces["node_package_start"]),
                ("100%", surfaces["node_package_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["module"],
            [
                ("0%", surfaces["node_module_start"]),
                ("100%", surfaces["node_module_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["external"],
            [
                ("0%", surfaces["node_external_start"]),
                ("100%", surfaces["node_external_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["note"],
            [
                ("0%", surfaces["node_note_start"]),
                ("100%", surfaces["node_note_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["focus_hero"],
            [
                ("0%", surfaces["node_focus_hero_start"]),
                ("100%", surfaces["node_focus_hero_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["focus_inbound"],
            [
                ("0%", surfaces["node_focus_inbound_start"]),
                ("100%", surfaces["node_focus_inbound_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["focus_outbound"],
            [
                ("0%", surfaces["node_focus_outbound_start"]),
                ("100%", surfaces["node_focus_outbound_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["focus_mixed"],
            [
                ("0%", surfaces["node_focus_mixed_start"]),
                ("100%", surfaces["node_focus_mixed_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["context_muted"],
            [
                ("0%", surfaces["node_context_muted_start"]),
                ("100%", surfaces["node_context_muted_end"]),
            ],
        ),
        (
            _GRADIENT_IDS["hub_accent"],
            [
                ("0%", surfaces["node_hub_accent_start"]),
                ("100%", surfaces["node_hub_accent_end"]),
            ],
        ),
    ]

    gradients_markup = []
    for gradient_id, stops in gradient_specs:
        stop_markup = "\n".join(
            f'        <stop offset="{offset}" stop-color="{color}" />'
            for offset, color in stops
        )
        gradients_markup.append(
            f"""
      <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="100%">
{stop_markup}
      </linearGradient>
            """.rstrip()
        )

    radial_specs = [
        (
            _RADIAL_IDS["halo_a"],
            ambient["halo_a_color"],
            ambient["halo_a_secondary"],
            ambient["halo_a_opacity"],
            ambient["halo_a_fade_opacity"],
        ),
        (
            _RADIAL_IDS["halo_b"],
            ambient["halo_b_color"],
            ambient["halo_b_color"],
            ambient["halo_b_opacity"],
            0.0,
        ),
    ]

    for radial_id, primary, secondary, opacity_a, opacity_b in radial_specs:
        gradients_markup.append(
            f"""
      <radialGradient id="{radial_id}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="{primary}" stop-opacity="{_fmt_float(opacity_a)}" />
        <stop offset="38%" stop-color="{secondary}" stop-opacity="{_fmt_float(max(0.01, opacity_b + 0.02))}" />
        <stop offset="100%" stop-color="{secondary}" stop-opacity="{_fmt_float(opacity_b)}" />
      </radialGradient>
            """.rstrip()
        )

    return "\n".join(gradients_markup)


def _build_grid_pattern(bundle: ThemeBundle) -> str:
    ambient = bundle.tokens["ambient"]
    size = max(8, int(_safe_float(ambient.get("grid_size"), 28)))
    stroke_width = _fmt_float(ambient.get("grid_stroke_width"), 0.9)
    return f"""
      <pattern id="{_PATTERN_IDS['grid']}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">
        <path d="M {size} 0 L 0 0 0 {size}" fill="none" stroke="{ambient['grid']}" stroke-width="{stroke_width}" opacity="{_fmt_float(ambient['grid_opacity'], 0.08)}" />
      </pattern>
    """.rstrip()


def _build_filters(bundle: ThemeBundle) -> str:
    effects = bundle.effect_presets
    ambient = bundle.tokens["ambient"]

    node_shadow = _safe_float(effects["shadow_intensity"].get("node"), 0.55)
    panel_shadow = _safe_float(effects["shadow_intensity"].get("panel"), 0.18)
    edge_blur = max(0.6, 3.0 + (_safe_float(effects["glow_intensity"].get("edge"), 0.10) * 14.0))

    return f"""
      <filter id="{_FILTER_IDS['node_shadow']}" x="-30%" y="-30%" width="160%" height="170%">
        <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#020617" flood-opacity="{_fmt_float(node_shadow, 0.55)}" />
      </filter>
      <filter id="{_FILTER_IDS['edge_blur']}" x="-35%" y="-35%" width="170%" height="170%">
        <feGaussianBlur stdDeviation="{_fmt_float(edge_blur, 4.4)}" />
      </filter>
      <filter id="{_FILTER_IDS['header_glow']}" x="-40%" y="-40%" width="180%" height="180%">
        <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="{ambient['header_glow']}" flood-opacity="{_fmt_float(panel_shadow, 0.18)}" />
      </filter>
    """.rstrip()


def _build_markers(bundle: ThemeBundle) -> str:
    markers_markup: list[str] = []
    for key in _MARKER_PRESET_KEYS:
        marker = bundle.marker_presets[key]
        svg_id = marker["svg_id"]
        opacity = _fmt_float(marker.get("opacity", 0.9), 0.9)
        fill = marker["fill"]
        if key == "focus_arrow":
            width = 13
            height = 13
            ref_x = 12
            path_d = "M0,0 L13,6.5 L0,13 z"
        elif key == "subtle_arrow":
            width = 11
            height = 11
            ref_x = 10
            path_d = "M0,0 L11,5.5 L0,11 z"
        else:
            width = 12
            height = 12
            ref_x = 11
            path_d = "M0,0 L12,6 L0,12 z"

        markers_markup.append(
            f"""
      <marker id="{svg_id}" viewBox="0 0 {width} {height}" refX="{ref_x}" refY="{height / 2:.1f}" markerWidth="{width}" markerHeight="{height}" orient="auto-start-reverse">
        <path d="{path_d}" fill="{fill}" fill-opacity="{opacity}" />
      </marker>
            """.rstrip()
        )

    return "\n".join(markers_markup)


def _build_theme_css(bundle: ThemeBundle) -> str:
    tokens = bundle.tokens
    node_presets = bundle.node_presets
    edge_presets = bundle.edge_presets
    lane_presets = bundle.lane_presets
    panel_presets = bundle.panel_presets
    badge_presets = bundle.badge_presets
    effects = bundle.effect_presets

    text = tokens["text"]
    accents = tokens["accents"]
    surfaces = tokens["surfaces"]
    ambient = tokens["ambient"]

    package = node_presets["package"]
    module = node_presets["module"]
    external = node_presets["external"]
    note = node_presets["note"]
    focus_hero = node_presets["focus_hero"]
    focus_inbound = node_presets["focus_inbound"]
    focus_outbound = node_presets["focus_outbound"]
    focus_mixed = node_presets["focus_mixed"]
    context_muted = node_presets["context_muted"]
    hub_accent = node_presets["hub_accent"]

    edge_default = edge_presets["default"]
    edge_muted = edge_presets["muted"]
    edge_focus_inbound = edge_presets["focus_inbound"]
    edge_focus_outbound = edge_presets["focus_outbound"]
    edge_self_loop = edge_presets["self_loop"]
    edge_cross_lane = edge_presets["cross_lane"]
    edge_intra_lane = edge_presets["intra_lane"]

    lane_standard = lane_presets["standard"]
    lane_focus_center = lane_presets["focus_center"]
    lane_focus_side = lane_presets["focus_side"]
    lane_issue = lane_presets["issue_lane"]
    lane_external = lane_presets["external_lane"]

    panel_header = panel_presets["header"]
    panel_legend = panel_presets["legend"]
    panel_warning = panel_presets["warning"]
    panel_footer = panel_presets["footer"]

    badge_inbound = badge_presets["inbound"]
    badge_outbound = badge_presets["outbound"]
    badge_hub = badge_presets["hub"]
    badge_island = badge_presets["island"]

    shine_standard = _safe_float(effects["shine_intensity"].get("standard"), 0.10)
    shine_focus = _safe_float(effects["shine_intensity"].get("focus"), 0.16)

    return f"""
        .svg-root {{ background: {surfaces["canvas_mid"]}; color: {text["body"]}; }}

        .svg-title {{ font: 700 26px 'Segoe UI Variable Text', 'Segoe UI', Arial, sans-serif; fill: {text["title"]}; letter-spacing: 0.25px; }}
        .svg-subtitle {{ font: 500 12px 'Segoe UI', Arial, sans-serif; fill: {text["soft"]}; }}
        .svg-meta {{ font: 600 11px 'Segoe UI', Arial, sans-serif; fill: {text["muted"]}; letter-spacing: 0.35px; text-transform: uppercase; }}
        .svg-footer {{ font: 500 10.5px 'Segoe UI', Arial, sans-serif; fill: {text["soft"]}; }}

        .lane-band {{ stroke-width: 1.0; }}
        .lane-standard {{ fill: {lane_standard["band_fill"]}; fill-opacity: {_fmt_float(lane_standard["band_opacity"], 0.20)}; stroke: {lane_standard["band_stroke"]}; }}
        .lane-focus-center {{ fill: {lane_focus_center["band_fill"]}; fill-opacity: {_fmt_float(lane_focus_center["band_opacity"], 0.28)}; stroke: {lane_focus_center["band_stroke"]}; }}
        .lane-focus-side {{ fill: {lane_focus_side["band_fill"]}; fill-opacity: {_fmt_float(lane_focus_side["band_opacity"], 0.18)}; stroke: {lane_focus_side["band_stroke"]}; }}
        .lane-issue {{ fill: {lane_issue["band_fill"]}; fill-opacity: {_fmt_float(lane_issue["band_opacity"], 0.22)}; stroke: {lane_issue["band_stroke"]}; }}
        .lane-external {{ fill: {lane_external["band_fill"]}; fill-opacity: {_fmt_float(lane_external["band_opacity"], 0.18)}; stroke: {lane_external["band_stroke"]}; }}

        .laneHeaderText {{ font: 700 12px 'Segoe UI', Arial, sans-serif; fill: {text["title"]}; }}
        .laneMetaText {{ font: 600 10px 'Segoe UI', Arial, sans-serif; fill: {text["soft"]}; }}

        .edge {{ fill: none; stroke-linecap: round; stroke-linejoin: round; }}
        .edgeGlow {{ fill: none; filter: url(#{_FILTER_IDS["edge_blur"]}); stroke-linecap: round; stroke-linejoin: round; }}

        .edge-default {{ stroke: {edge_default["stroke"]}; marker-end: {edge_default["marker"]}; opacity: {_fmt_float(edge_default["opacity"], 0.68)}; }}
        .edge-default-glow {{ stroke: {edge_default["glow"]}; opacity: {_fmt_float(edge_default["glow_opacity"], 0.10)}; }}

        .edge-muted {{ stroke: {edge_muted["stroke"]}; marker-end: {edge_muted["marker"]}; opacity: {_fmt_float(edge_muted["opacity"], 0.34)}; }}
        .edge-muted-glow {{ stroke: {edge_muted["glow"]}; opacity: {_fmt_float(edge_muted["glow_opacity"], 0.06)}; }}

        .edge-focus-inbound {{ stroke: {edge_focus_inbound["stroke"]}; marker-end: {edge_focus_inbound["marker"]}; opacity: {_fmt_float(edge_focus_inbound["opacity"], 0.82)}; }}
        .edge-focus-inbound-glow {{ stroke: {edge_focus_inbound["glow"]}; opacity: {_fmt_float(edge_focus_inbound["glow_opacity"], 0.22)}; }}

        .edge-focus-outbound {{ stroke: {edge_focus_outbound["stroke"]}; marker-end: {edge_focus_outbound["marker"]}; opacity: {_fmt_float(edge_focus_outbound["opacity"], 0.82)}; }}
        .edge-focus-outbound-glow {{ stroke: {edge_focus_outbound["glow"]}; opacity: {_fmt_float(edge_focus_outbound["glow_opacity"], 0.22)}; }}

        .edge-self-loop {{ stroke: {edge_self_loop["stroke"]}; marker-end: {edge_self_loop["marker"]}; opacity: {_fmt_float(edge_self_loop["opacity"], 0.74)}; }}
        .edge-self-loop-glow {{ stroke: {edge_self_loop["glow"]}; opacity: {_fmt_float(edge_self_loop["glow_opacity"], 0.18)}; }}

        .edge-cross-lane {{ stroke: {edge_cross_lane["stroke"]}; marker-end: {edge_cross_lane["marker"]}; opacity: {_fmt_float(edge_cross_lane["opacity"], 0.74)}; }}
        .edge-cross-lane-glow {{ stroke: {edge_cross_lane["glow"]}; opacity: {_fmt_float(edge_cross_lane["glow_opacity"], 0.10)}; }}

        .edge-intra-lane {{ stroke: {edge_intra_lane["stroke"]}; marker-end: {edge_intra_lane["marker"]}; opacity: {_fmt_float(edge_intra_lane["opacity"], 0.54)}; }}
        .edge-intra-lane-glow {{ stroke: {edge_intra_lane["glow"]}; opacity: {_fmt_float(edge_intra_lane["glow_opacity"], 0.08)}; }}

        .node {{ transition: transform 140ms ease-out; transform-origin: center; }}
        .node:hover {{ transform: translateY(-1.4px); }}

        .nodeBody {{ stroke-width: {_fmt_float(package["border_width"], 1.55)}; }}
        .node-package .nodeBody {{ fill: {package["fill"]}; stroke: {package["stroke"]}; }}
        .node-module .nodeBody {{ fill: {module["fill"]}; stroke: {module["stroke"]}; }}
        .node-external .nodeBody {{ fill: {external["fill"]}; stroke: {external["stroke"]}; }}
        .node-note .nodeBody {{ fill: {note["fill"]}; stroke: {note["stroke"]}; }}

        .node-focus-hero .nodeBody {{ fill: {focus_hero["fill"]}; stroke: {focus_hero["stroke"]}; stroke-width: {_fmt_float(focus_hero["border_width"], 2.35)}; }}
        .node-focus-inbound .nodeBody {{ fill: {focus_inbound["fill"]}; stroke: {focus_inbound["stroke"]}; stroke-width: {_fmt_float(focus_inbound["border_width"], 1.95)}; }}
        .node-focus-outbound .nodeBody {{ fill: {focus_outbound["fill"]}; stroke: {focus_outbound["stroke"]}; stroke-width: {_fmt_float(focus_outbound["border_width"], 1.95)}; }}
        .node-focus-mixed .nodeBody {{ fill: {focus_mixed["fill"]}; stroke: {focus_mixed["stroke"]}; stroke-width: {_fmt_float(focus_mixed["border_width"], 1.95)}; }}
        .node-context-muted .nodeBody {{ fill: {context_muted["fill"]}; stroke: {context_muted["stroke"]}; stroke-width: {_fmt_float(context_muted["border_width"], 1.55)}; }}
        .node-hub-accent .nodeBody {{ fill: {hub_accent["fill"]}; stroke: {hub_accent["stroke"]}; stroke-width: {_fmt_float(hub_accent["border_width"], 2.05)}; }}

        .nodeShine {{ fill: #ffffff; opacity: {_fmt_float(shine_standard, 0.10)}; }}
        .nodeLabel {{ font: 700 13px 'Segoe UI Variable Text', 'Segoe UI', Arial, sans-serif; fill: {text["body"]}; }}
        .nodeSubLabel {{ font: 600 10.5px 'Segoe UI', Arial, sans-serif; fill: {text["muted"]}; }}
        .nodeIcon {{ font-size: 14px; opacity: 0.98; }}

        .node-island .nodeBody {{ stroke-dasharray: 5 4; }}
        .node-hub .nodeBody {{ stroke-width: {_fmt_float(hub_accent["border_width"], 1.95)}; }}
        .node-focus-hero .nodeShine {{ opacity: {_fmt_float(shine_focus, 0.16)}; }}

        .badgeBox {{ stroke-width: 0; }}
        .badgeInbound {{ fill: {badge_inbound["fill"]}; }}
        .badgeOutbound {{ fill: {badge_outbound["fill"]}; }}
             .badgeStateHub {{ fill: {badge_hub["fill"]}; }}
        .badgeStateIsland {{ fill: {badge_island["fill"]}; }}
        .badgeTextDark {{ font: 700 10px 'Segoe UI', Arial, sans-serif; fill: {text["badge_dark"]}; letter-spacing: 0.25px; }}
        .badgeTextLight {{ font: 700 10px 'Segoe UI', Arial, sans-serif; fill: {text["badge_light"]}; letter-spacing: 0.25px; }}

        .legendPanel {{ fill: {panel_legend["fill"]}; fill-opacity: {_fmt_float(panel_legend["fill_opacity"], 0.72)}; stroke: {panel_legend["stroke"]}; stroke-width: 1.15; }}
        .legendTitle {{ font: 700 12px 'Segoe UI', Arial, sans-serif; fill: {panel_legend["text_fill"]}; }}
        .legendLabel {{ font: 600 11.2px 'Segoe UI', Arial, sans-serif; fill: {panel_legend["text_fill"]}; }}
        .legendValue {{ font: 700 11.2px 'Segoe UI', Arial, sans-serif; fill: {text["title"]}; }}
        .legendHint {{ font: 600 10px 'Segoe UI', Arial, sans-serif; fill: {panel_legend["meta_fill"]}; }}

        .legendChipPackage {{ fill: {package["stroke"]}; }}
        .legendChipModule {{ fill: {module["stroke"]}; }}
        .legendChipExternal {{ fill: {external["stroke"]}; }}
        .legendChipWarning {{ fill: {note["stroke"]}; }}

        .footer {{ font: 500 10.5px 'Segoe UI', Arial, sans-serif; fill: {panel_footer["text_fill"]}; }}

        .panel-header {{ fill: {panel_header["fill"]}; fill-opacity: {_fmt_float(panel_header["fill_opacity"], 0.54)}; stroke: {panel_header["stroke"]}; stroke-width: 1.05; }}
        .panel-legend {{ fill: {panel_legend["fill"]}; fill-opacity: {_fmt_float(panel_legend["fill_opacity"], 0.72)}; stroke: {panel_legend["stroke"]}; stroke-width: 1.15; }}
        .panel-warning {{ fill: {panel_warning["fill"]}; fill-opacity: {_fmt_float(panel_warning["fill_opacity"], 0.82)}; stroke: {panel_warning["stroke"]}; stroke-width: 1.0; }}
        .panel-footer {{ fill: {panel_footer["fill"]}; fill-opacity: {_fmt_float(panel_footer["fill_opacity"], 1.0)}; stroke: {panel_footer["stroke"]}; stroke-width: 0.0; }}
    """.strip()


def _build_theme_svg_defs(bundle: ThemeBundle) -> str:
    gradients = _build_gradients(bundle)
    grid_pattern = _build_grid_pattern(bundle)
    filters = _build_filters(bundle)
    markers = _build_markers(bundle)
    css = _build_theme_css(bundle)

    return f"""
    <defs>
      {gradients}
      {grid_pattern}
      {filters}
      {markers}
      <style>
{css}
      </style>
    </defs>
    """.strip()


def _build_semantic_theme(
    *,
    theme_id: str,
    label: str,
    token_overrides: dict[str, Any] | None = None,
    effect_overrides: dict[str, Any] | None = None,
    is_default: bool = False,
) -> ThemeBundle:
    tokens = _build_theme_tokens(token_overrides or {})
    effects = _build_effect_presets(effect_overrides or {})

    bundle = ThemeBundle(
        id=theme_id,
        label=label,
        svg_defs="",
        is_default=is_default,
        tokens=tokens,
        node_presets={},
        edge_presets={},
        lane_presets={},
        panel_presets={},
        badge_presets={},
        marker_presets={},
        effect_presets=effects,
    )

    bundle.node_presets = _build_node_presets(bundle.tokens, bundle.effect_presets)
    bundle.edge_presets = _build_edge_presets(bundle.tokens, bundle.effect_presets)
    bundle.lane_presets = _build_lane_presets(bundle.tokens, bundle.effect_presets)
    bundle.panel_presets = _build_panel_presets(bundle.tokens)
    bundle.badge_presets = _build_badge_presets(bundle.tokens)
    bundle.marker_presets = _build_marker_presets(bundle.tokens, bundle.effect_presets)
    bundle.svg_defs = _build_theme_svg_defs(bundle)
    return bundle


def theme_dark() -> ThemeBundle:
    return _build_semantic_theme(
        theme_id="dark",
        label="Dark",
    )


def theme_silver_frost_cyan() -> ThemeBundle:
    return _build_semantic_theme(
        theme_id="silver_frost_cyan",
        label="Silver Frost Cyan",
        is_default=True,
        token_overrides={
            "surfaces": {
                "canvas_start": "#050913",
                "canvas_mid": "#0d1520",
                "canvas_end": "#172332",
                "header_band": "#182231",
                "panel": "#17202c",
                "panel_alt": "#1c2734",
                "panel_soft": "#111923",
                "legend_panel": "#16212c",
                "warning_panel": "#2a241d",
                "lane_header_start": "#1d2a39",
                "lane_header_end": "#182330",
                "node_package_start": "#213244",
                "node_package_end": "#182534",
                "node_module_start": "#1d2b39",
                "node_module_end": "#162230",
                "node_external_start": "#202b3c",
                "node_external_end": "#182231",
                "node_note_start": "#2f2a22",
                "node_note_end": "#241f18",
                "node_focus_hero_start": "#263748",
                "node_focus_hero_end": "#1a2735",
                "node_focus_inbound_start": "#203246",
                "node_focus_inbound_end": "#172536",
                "node_focus_outbound_start": "#1d2e3e",
                "node_focus_outbound_end": "#15212d",
                "node_focus_mixed_start": "#223042",
                "node_focus_mixed_end": "#182433",
                "node_context_muted_start": "#17202b",
                "node_context_muted_end": "#111821",
                "node_hub_accent_start": "#2a3949",
                "node_hub_accent_end": "#1d2936",
            },
            "text": {
                "title": "#f4fbff",
                "body": "#d8e6f2",
                "muted": "#a8bdd1",
                "soft": "#91a8be",
                "code": "#bed0e2",
                "warning": "#d7c19f",
                "inverse": "#ffffff",
                "badge_dark": "#08111a",
                "badge_light": "#ffffff",
            },
            "accents": {
                "primary": "#8feeff",
                "secondary": "#b7f6ff",
                "tertiary": "#ccd9ff",
                "success": "#7fdbef",
                "warning": "#c5ac84",
                "danger": "#bda8a1",
                "focus": "#8cefff",
                "hub": "#b7f6ff",
            },
            "borders": {
                "subtle": "#415366",
                "panel": "#566b81",
                "lane": "#4d6075",
                "strong": "#8cefff",
                "focus": "#8cefff",
                "muted": "#5f7388",
                "node_package": "#93d8ee",
                "node_module": "#83d7ed",
                "node_external": "#b6cff8",
                "node_note": "#b9a37f",
                "warning": "#b9a37f",
            },
            "ambient": {
                "grid": "#dceafb",
                "grid_opacity": 0.05,
                "grid_size": 32,
                "grid_stroke_width": 0.8,
                "halo_a_color": "#9af3ff",
                "halo_a_secondary": "#d8edff",
                "halo_a_opacity": 0.15,
                "halo_a_fade_opacity": 0.04,
                "halo_b_color": "#ffffff",
                "halo_b_opacity": 0.09,
                "header_glow": "#92efff",
            },
        },
        effect_overrides={
            "glow_intensity": {
                "ambient": 0.10,
                "edge": 0.08,
                "focus": 0.18,
                "header": 0.10,
            },
            "shadow_intensity": {
                "node": 0.22,
                "panel": 0.16,
                "soft": 0.08,
            },
            "border_emphasis": {
                "standard": 1.08,
                "strong": 1.24,
                "focus": 1.62,
                "hub": 1.34,
            },
            "shine_intensity": {
                "standard": 0.16,
                "focus": 0.22,
                "panel": 0.10,
            },
        },
    )


def theme_light() -> ThemeBundle:
    return _build_semantic_theme(
        theme_id="light",
        label="Light",
        token_overrides={
            "surfaces": {
                "canvas_start": "#f8fbff",
                "canvas_mid": "#f1f7ff",
                "canvas_end": "#eef2ff",
                "header_band": "#ffffff",
                "panel": "#ffffff",
                "panel_alt": "#eef6ff",
                "panel_soft": "#f7fbff",
                "legend_panel": "#ffffff",
                "warning_panel": "#fff7ed",
                "lane_header_start": "#ffffff",
                "lane_header_end": "#eef6ff",
                "node_package_start": "#e0f2fe",
                "node_package_end": "#dbeafe",
                "node_module_start": "#dcfce7",
                "node_module_end": "#bbf7d0",
                "node_external_start": "#f3e8ff",
                "node_external_end": "#e9d5ff",
                "node_note_start": "#fef9c3",
                "node_note_end": "#fde68a",
                "node_focus_hero_start": "#eef4ff",
                "node_focus_hero_end": "#dbeafe",
                "node_focus_inbound_start": "#e0f2fe",
                "node_focus_inbound_end": "#bae6fd",
                "node_focus_outbound_start": "#dcfce7",
                "node_focus_outbound_end": "#bbf7d0",
                "node_focus_mixed_start": "#ede9fe",
                "node_focus_mixed_end": "#ddd6fe",
                "node_context_muted_start": "#f1f5f9",
                "node_context_muted_end": "#e2e8f0",
                "node_hub_accent_start": "#fef3c7",
                "node_hub_accent_end": "#fde68a",
            },
            "text": {
                "title": "#0f172a",
                "body": "#334155",
                "muted": "#475569",
                "soft": "#64748b",
                "code": "#475569",
                "warning": "#b45309",
                "inverse": "#ffffff",
                "badge_dark": "#ffffff",
                "badge_light": "#ffffff",
            },
            "accents": {
                "primary": "#2563eb",
                "secondary": "#60a5fa",
                "tertiary": "#7c3aed",
                "success": "#16a34a",
                "warning": "#d97706",
                "danger": "#dc2626",
                "focus": "#2563eb",
                "hub": "#d97706",
            },
            "borders": {
                "subtle": "#dbe4f0",
                "panel": "#cbd5e1",
                "lane": "#dbeafe",
                "strong": "#60a5fa",
                "focus": "#2563eb",
                "muted": "#94a3b8",
                "node_package": "#1d4ed8",
                "node_module": "#15803d",
                "node_external": "#9333ea",
                "node_note": "#d97706",
                "warning": "#d97706",
            },
            "ambient": {
                "grid": "#cbd5e1",
                "grid_opacity": 0.20,
                "grid_size": 28,
                "grid_stroke_width": 0.9,
                "halo_a_color": "#60a5fa",
                "halo_a_secondary": "#93c5fd",
                "halo_a_opacity": 0.22,
                "halo_a_fade_opacity": 0.08,
                "halo_b_color": "#22d3ee",
                "halo_b_opacity": 0.16,
                "header_glow": "#60a5fa",
            },
        },
        effect_overrides={
            "glow_intensity": {
                "ambient": 0.10,
                "edge": 0.08,
                "focus": 0.12,
                "header": 0.06,
            },
            "shadow_intensity": {
                "node": 0.13,
                "panel": 0.10,
                "soft": 0.05,
            },
            "border_emphasis": {
                "standard": 1.05,
                "strong": 1.25,
                "focus": 1.52,
                "hub": 1.35,
            },
            "shine_intensity": {
                "standard": 0.24,
                "focus": 0.16,
                "panel": 0.08,
            },
        },
    )


def theme_obsidian_liquid_glass() -> ThemeBundle:
    return _build_semantic_theme(
        theme_id="obsidian_liquid_glass",
        label="Obsidian Liquid Glass",
        token_overrides={
            "surfaces": {
                "canvas_start": "#04060b",
                "canvas_mid": "#0a1020",
                "canvas_end": "#111827",
                "header_band": "#0b1120",
                "panel": "#0c1424",
                "panel_alt": "#101a2e",
                "panel_soft": "#0a1220",
                "legend_panel": "#0d1526",
                "warning_panel": "#22170f",
                "lane_header_start": "#10192d",
                "lane_header_end": "#18233b",
                "node_package_start": "#15253d",
                "node_package_end": "#0d1628",
                "node_module_start": "#10231d",
                "node_module_end": "#0b1715",
                "node_external_start": "#1b1730",
                "node_external_end": "#120f23",
                "node_note_start": "#2a2114",
                "node_note_end": "#1f180f",
                "node_focus_hero_start": "#18263d",
                "node_focus_hero_end": "#0f1a2d",
                "node_focus_inbound_start": "#12263a",
                "node_focus_inbound_end": "#0d1929",
                "node_focus_outbound_start": "#10261d",
                "node_focus_outbound_end": "#0b1714",
                "node_focus_mixed_start": "#211836",
                "node_focus_mixed_end": "#141126",
                "node_context_muted_start": "#151b27",
                "node_context_muted_end": "#0f141f",
                "node_hub_accent_start": "#2a2e3f",
                "node_hub_accent_end": "#191d2c",
            },
            "text": {
                "title": "#f5f7fb",
                "body": "#dbe5f2",
                "muted": "#97a8bc",
                "soft": "#6f8298",
                "code": "#c8d7ea",
                "warning": "#f6c177",
                "inverse": "#06101d",
                "badge_dark": "#06101d",
                "badge_light": "#f8fbff",
            },
            "accents": {
                "primary": "#79c6ff",
                "secondary": "#9ed8ff",
                "tertiary": "#bca7ff",
                "success": "#67d6a3",
                "warning": "#f2c078",
                "danger": "#ff8f8f",
                "focus": "#8ed7ff",
                "hub": "#d8deff",
            },
            "borders": {
                "subtle": "#273347",
                "panel": "#31405c",
                "lane": "#25324a",
                "strong": "#79c6ff",
                "focus": "#9ed8ff",
                "muted": "#55677c",
                "node_package": "#7fcfff",
                "node_module": "#79d8b0",
                "node_external": "#c2b6ff",
                "node_note": "#f2c078",
                "warning": "#f2c078",
            },
            "ambient": {
                "grid": "#8ecbff",
                "grid_opacity": 0.06,
                "grid_size": 28,
                "grid_stroke_width": 0.85,
                "halo_a_color": "#9ed8ff",
                "halo_a_secondary": "#79c6ff",
                "halo_a_opacity": 0.14,
                "halo_a_fade_opacity": 0.05,
                "halo_b_color": "#bca7ff",
                "halo_b_opacity": 0.10,
                "header_glow": "#dce8ff",
            },
        },
        effect_overrides={
            "glow_intensity": {
                "ambient": 0.08,
                "edge": 0.06,
                "focus": 0.14,
                "header": 0.08,
            },
            "shadow_intensity": {
                "node": 0.28,
                "panel": 0.16,
                "soft": 0.07,
            },
            "border_emphasis": {
                "standard": 1.08,
                "strong": 1.28,
                "focus": 1.56,
                "hub": 1.32,
            },
            "shine_intensity": {
                "standard": 0.18,
                "focus": 0.22,
                "panel": 0.12,
            },
        },
    )

def collect_theme_bundles() -> list[ThemeBundle]:
    bundles: list[ThemeBundle] = [
        theme_silver_frost_cyan(),
        theme_dark(),
        theme_light(),
        theme_obsidian_liquid_glass(),
    ]

    deduped: list[ThemeBundle] = []
    seen_ids: set[str] = set()
    for bundle in bundles:
        if not isinstance(bundle, ThemeBundle):
            continue
        theme_id = clean_text(bundle.id).lower() or DEFAULT_THEME_ID
        if theme_id in seen_ids:
            continue
        bundle.id = theme_id
        bundle.label = clean_text(bundle.label) or theme_id.title()
        seen_ids.add(theme_id)
        deduped.append(bundle)

    if not deduped:
        deduped = [theme_dark()]

    if not any(bundle.is_default for bundle in deduped):
        deduped[0].is_default = True

    return deduped


def build_theme_registry(theme_bundles: list[ThemeBundle]) -> dict[str, ThemeBundle]:
    registry: dict[str, ThemeBundle] = {}
    for bundle in theme_bundles:
        registry[clean_text(bundle.id).lower()] = bundle
    return registry


def _theme_lookup_keys(value: Any) -> tuple[str, ...]:
    cleaned = clean_text(value)
    if not cleaned:
        return tuple()

    lowered = cleaned.lower()
    slug = lowered.replace("_", "-").replace(" ", "-")
    spaced = lowered.replace("_", " ").replace("-", " ")
    compact = "".join(ch for ch in lowered if ch.isalnum())
    title_spaced = clean_text(cleaned.replace("_", " ").replace("-", " ")).title()

    ordered = dict.fromkeys(
        item
        for item in (
            cleaned,
            lowered,
            slug,
            spaced,
            compact,
            title_spaced,
            title_spaced.lower(),
        )
        if item
    )
    return tuple(ordered.keys())


def _build_theme_manifests(theme_bundles: list[ThemeBundle]) -> tuple[ThemeManifest, ...]:
    manifests: list[ThemeManifest] = []
    for index, bundle in enumerate(theme_bundles):
        theme_id = clean_text(bundle.id).lower() or DEFAULT_THEME_ID
        label = clean_text(bundle.label) or theme_id.title()
        dropdown_label = label
        aliases = list(_theme_lookup_keys(theme_id))
        aliases.extend(_theme_lookup_keys(label))
        aliases.extend(_theme_lookup_keys(dropdown_label))
        manifests.append(
            ThemeManifest(
                id=theme_id,
                label=label,
                dropdown_label=dropdown_label,
                aliases=tuple(aliases),
                is_default=bool(bundle.is_default),
                bundle_index=index,
            )
        )

    if not manifests:
        fallback = theme_dark()
        return (
            ThemeManifest(
                id=fallback.id,
                label=fallback.label,
                dropdown_label=fallback.label,
                aliases=_theme_lookup_keys(fallback.id) + _theme_lookup_keys(fallback.label),
                is_default=True,
                bundle_index=0,
            ),
        )

    if not any(item.is_default for item in manifests):
        first = manifests[0]
        manifests[0] = ThemeManifest(
            id=first.id,
            label=first.label,
            dropdown_label=first.dropdown_label,
            aliases=first.aliases,
            is_default=True,
            bundle_index=first.bundle_index,
        )

    return tuple(manifests)


def build_theme_label_to_id(theme_bundles: list[ThemeBundle]) -> dict[str, str]:
    return {
        manifest.dropdown_label: manifest.id
        for manifest in _build_theme_manifests(theme_bundles)
    }


def build_theme_id_to_label(theme_bundles: list[ThemeBundle]) -> dict[str, str]:
    return {
        manifest.id: manifest.dropdown_label
        for manifest in _build_theme_manifests(theme_bundles)
    }


def get_default_theme_id(theme_bundles: list[ThemeBundle]) -> str:
    for bundle in theme_bundles:
        if bundle.is_default:
            return clean_text(bundle.id).lower()
    if theme_bundles:
        return clean_text(theme_bundles[0].id).lower()
    return DEFAULT_THEME_ID


def _build_theme_alias_to_id(manifests: Iterable[ThemeManifest]) -> dict[str, str]:
    alias_to_id: dict[str, str] = {}
    for manifest in manifests:
        for alias in manifest.aliases:
            for key in _theme_lookup_keys(alias):
                alias_to_id.setdefault(key, manifest.id)
    return alias_to_id


def _is_dark_theme(theme_id: str) -> bool:
    lowered = clean_text(theme_id).lower()
    return lowered not in {"light", "paper", "white"}


def _bundle_section(bundle: ThemeBundle, section: str) -> dict[str, Any]:
    return _coerce_dict(_coerce_dict(bundle.tokens).get(section))


def _bundle_render_tokens(bundle: ThemeBundle) -> dict[str, Any]:
    dark = _is_dark_theme(bundle.id)
    surfaces = _bundle_section(bundle, "surfaces")
    text = _bundle_section(bundle, "text")
    accents = _bundle_section(bundle, "accents")
    borders = _bundle_section(bundle, "borders")
    ambient = _bundle_section(bundle, "ambient")

    package_fill = _mix_hex(
        str(surfaces.get("node_package_start", "#0f2238" if dark else "#e6f2ff")),
        str(surfaces.get("node_package_end", "#0a1e3f" if dark else "#dbeafe")),
        0.45,
    )
    module_fill = _mix_hex(
        str(surfaces.get("node_module_start", "#0d1d18" if dark else "#eafbf1")),
        str(surfaces.get("node_module_end", "#08271c" if dark else "#bbf7d0")),
        0.45,
    )
    external_fill = _mix_hex(
        str(surfaces.get("node_external_start", "#211a34" if dark else "#f2ebff")),
        str(surfaces.get("node_external_end", "#25173f" if dark else "#e9d5ff")),
        0.45,
    )
    note_fill = _mix_hex(
        str(surfaces.get("node_note_start", "#2e2512" if dark else "#fff6db")),
        str(surfaces.get("node_note_end", "#3b2408" if dark else "#fde68a")),
        0.42,
    )
    muted_fill = _mix_hex(
        str(surfaces.get("node_context_muted_start", "#101823" if dark else "#f4f7fb")),
        str(surfaces.get("node_context_muted_end", "#121a29" if dark else "#e2e8f0")),
        0.50,
    )

    return {
        "canvas_bg": str(surfaces.get("canvas_mid", surfaces.get("canvas_start", "#07101c" if dark else "#f4f8ff"))),
        "canvas_grid": str(ambient.get("grid", "#6ea8ff" if dark else "#7c9bc2")),
        "canvas_grid_opacity": _safe_float(ambient.get("grid_opacity"), 0.055 if dark else 0.10),
        "halo_a": str(ambient.get("halo_a_color", "#22d3ee" if dark else "#60a5fa")),
        "halo_b": str(ambient.get("halo_b_color", "#8b5cf6")),
        "header_fill": str(surfaces.get("header_band", surfaces.get("panel", "#0a1426" if dark else "#ffffff"))),
        "header_stroke": str(borders.get("panel", "#223556" if dark else "#d5e2f4")),
        "header_title": str(text.get("title", "#f5fbff" if dark else "#102033")),
        "header_text": str(text.get("body", "#b8c8df" if dark else "#30445b")),
        "header_meta": str(text.get("soft", "#8fa4c2" if dark else "#5c738f")),
        "footer_text": str(text.get("soft", "#8ba0bd" if dark else "#5e738e")),
        "legend_fill": str(surfaces.get("legend_panel", surfaces.get("panel", "#0c1424" if dark else "#ffffff"))),
        "legend_stroke": str(borders.get("panel", "#223556" if dark else "#d5e2f4")),
        "shadow": str(surfaces.get("canvas_start", "#020617" if dark else "#0f172a")),
        "focus": str(accents.get("focus", accents.get("primary", "#7dd3fc" if dark else "#2563eb"))),
        "focus_warm": str(accents.get("tertiary", "#c084fc" if dark else "#8b5cf6")),
        "package_fill": package_fill,
        "package_stroke": str(borders.get("node_package", accents.get("secondary", "#67b5ff" if dark else "#3f8fff"))),
        "package_accent": str(accents.get("primary", "#8ed1ff" if dark else "#5ca7ff")),
        "module_fill": module_fill,
        "module_stroke": str(borders.get("node_module", accents.get("success", "#4fd89a" if dark else "#25b46a"))),
        "module_accent": str(accents.get("success", "#7cfcc0" if dark else "#52d890")),
        "external_fill": external_fill,
        "external_stroke": str(borders.get("node_external", accents.get("tertiary", "#c39cff" if dark else "#9b6df4"))),
        "external_accent": str(accents.get("tertiary", "#ddc0ff" if dark else "#b79aff")),
        "note_fill": note_fill,
        "note_stroke": str(borders.get("node_note", accents.get("warning", "#f5c76a" if dark else "#d9972d"))),
        "note_accent": str(accents.get("warning", "#ffe29a" if dark else "#f0bb55")),
        "muted_fill": muted_fill,
        "muted_stroke": str(borders.get("muted", "#5a6c87" if dark else "#b5c3d8")),
        "muted_text": str(text.get("muted", "#97a9c0" if dark else "#6b7f97")),
        "muted_subtext": str(text.get("soft", "#70839c" if dark else "#7b8ea4")),
        "text_main": str(text.get("body", "#edf5ff" if dark else "#102033")),
        "text_soft": str(text.get("soft", "#9cb2cf" if dark else "#586f8b")),
        "chip_dark": str(surfaces.get("canvas_start", "#07101c" if dark else "#102033")),
        "chip_light": str(text.get("inverse", "#f8fbff" if dark else "#ffffff")),
        "badge_in": str(accents.get("primary", "#6ec8ff" if dark else "#2d82ff")),
        "badge_out": str(accents.get("success", "#6fe0a2" if dark else "#24b96c")),
        "badge_text_dark": str(text.get("badge_dark", "#07101c" if dark else "#ffffff")),
        "lane_fill": str(surfaces.get("panel_soft", "#0a1324" if dark else "#ffffff")),
        "lane_stroke": str(borders.get("lane", "#213552" if dark else "#d7e2f1")),
        "lane_header_fill": _mix_hex(
            str(surfaces.get("lane_header_start", surfaces.get("header_band", "#0f1a2e" if dark else "#ffffff"))),
            str(surfaces.get("lane_header_end", surfaces.get("panel_alt", "#13213a" if dark else "#eef6ff"))),
            0.50,
        ),
        "lane_header_text": str(text.get("body", "#eaf2ff" if dark else "#102033")),
        "lane_meta_text": str(text.get("soft", "#8ca2bf" if dark else "#5b728d")),
        "warning_fill": str(surfaces.get("warning_panel", "#2b1b0a" if dark else "#fff3d8")),
        "warning_stroke": str(borders.get("warning", accents.get("warning", "#f4b85d" if dark else "#d9972d"))),
        "warning_text": str(text.get("warning", "#ffdba6" if dark else "#7f4d00")),
        "footer_fill": str(surfaces.get("panel_soft", "#0a1322" if dark else "#ffffff")),
        "footer_stroke": str(borders.get("panel", "#20324e" if dark else "#d7e2f1")),
    }


def _render_effects(bundle: ThemeBundle, dark: bool) -> dict[str, float]:
    effect_presets = _coerce_dict(bundle.effect_presets)
    glow = _coerce_dict(effect_presets.get("glow_intensity"))
    shine = _coerce_dict(effect_presets.get("shine_intensity"))
    border = _coerce_dict(effect_presets.get("border_emphasis"))
    shadow = _coerce_dict(effect_presets.get("shadow_intensity"))
    return {
        "glow_edge": _safe_float(glow.get("edge"), 0.10 if dark else 0.08),
        "glow_focus": _safe_float(glow.get("focus"), 0.20 if dark else 0.10),
        "shine_standard": _safe_float(shine.get("standard"), 0.08 if dark else 0.18),
        "shine_focus": _safe_float(shine.get("focus"), 0.12 if dark else 0.16),
        "border_standard": 1.55 * _safe_float(border.get("standard"), 1.0),
        "border_strong": 1.55 * _safe_float(border.get("strong"), 1.25),
        "border_focus": 1.55 * _safe_float(border.get("focus"), 1.52),
        "border_hub": 1.55 * _safe_float(border.get("hub"), 1.35),
        "shadow_node": _safe_float(shadow.get("node"), 0.55 if dark else 0.13),
    }



def _build_state_tokens(tokens: dict[str, Any], dark: bool) -> dict[str, dict[str, Any]]:
    focus_border = _with_alpha(tokens["focus"], 0.72 if dark else 0.78)
    hover_border = _with_alpha(tokens["focus"], 0.26 if dark else 0.34)
    selection_bg = tokens["focus"]
    selection_fg = tokens["chip_light"]

    primary_base = tokens["focus"]
    secondary_base = _mix_hex(tokens["header_fill"], tokens["canvas_bg"], 0.30 if dark else 0.08)
    success_base = tokens["badge_out"]
    danger_base = _mix_hex(tokens["warning_fill"], tokens["header_fill"], 0.34 if dark else 0.16)

    return {
        "surface": {
            "hover_fill": _mix_hex(tokens["legend_fill"], tokens["focus"], 0.06 if dark else 0.04),
            "active_fill": _mix_hex(tokens["legend_fill"], tokens["focus"], 0.10 if dark else 0.06),
        },
        "input": {
            "hover_border": hover_border,
            "focus_border": focus_border,
            "focus_bg": _mix_hex(tokens["canvas_bg"], tokens["header_fill"], 0.12 if dark else 0.05),
            "active_border": _with_alpha(tokens["focus"], 0.62 if dark else 0.66),
            "active_bg": _mix_hex(tokens["canvas_bg"], tokens["focus"], 0.06 if dark else 0.04),
            "disabled_fg": _with_alpha(tokens["muted_text"], 0.82),
            "disabled_bg": _mix_hex(tokens["canvas_bg"], tokens["legend_fill"], 0.10 if dark else 0.04),
            "disabled_border": _with_alpha(tokens["legend_stroke"], 0.08 if dark else 0.20),
            "selection_bg": selection_bg,
            "selection_fg": selection_fg,
        },
        "button_primary": {
            "hover_bg": _mix_hex(primary_base, tokens["chip_light"], 0.10 if dark else 0.12),
            "pressed_bg": _mix_hex(primary_base, tokens["chip_dark"], 0.16 if dark else 0.10),
            "focus_border": focus_border,
        },
        "button_secondary": {
            "hover_bg": _mix_hex(secondary_base, tokens["focus"], 0.10 if dark else 0.06),
            "pressed_bg": _mix_hex(secondary_base, tokens["focus"], 0.18 if dark else 0.10),
            "focus_border": focus_border,
        },
        "button_success": {
            "hover_bg": _mix_hex(success_base, tokens["chip_light"], 0.08 if dark else 0.10),
            "pressed_bg": _mix_hex(success_base, tokens["chip_dark"], 0.18 if dark else 0.10),
            "focus_border": _with_alpha(tokens["badge_out"], 0.46 if dark else 0.52),
        },
        "button_danger": {
            "hover_bg": _mix_hex(danger_base, tokens["warning_stroke"], 0.10 if dark else 0.08),
            "pressed_bg": _mix_hex(danger_base, tokens["warning_stroke"], 0.18 if dark else 0.10),
            "focus_border": _with_alpha(tokens["warning_stroke"], 0.46 if dark else 0.52),
        },
        "disabled": {
            "fg": _with_alpha(tokens["muted_text"], 0.84),
            "bg": _mix_hex(tokens["header_fill"], tokens["canvas_bg"], 0.18 if dark else 0.08),
            "border": _with_alpha(tokens["legend_stroke"], 0.06 if dark else 0.18),
        },
        "selection": {
            "bg": selection_bg,
            "fg": selection_fg,
        },
        "progress": {
            "chunk": tokens["focus"],
        },
    }


def _build_component_tokens(tokens: dict[str, Any], state_tokens: dict[str, dict[str, Any]], dark: bool) -> dict[str, dict[str, Any]]:
    return {
        "spacing": {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20, "2xl": 24},
        "radius": {"sm": 10, "md": 12, "lg": 16, "xl": 22},
        "elevation": {"card_alpha": 0.28 if dark else 0.14, "shell_alpha": 0.82 if dark else 0.26, "button_alpha": 0.38 if dark else 0.18},
        "card": {"radius": 16, "border_alpha": 0.18 if dark else 0.40},
        "chip": {"radius": 11, "padding_y": 6, "padding_x": 10, "font_size": 11},
        "input": {"radius": 12, "padding_y": 10, "padding_x": 12, "font_size": 12, "dropdown_width": 26, "arrow_size": 6},
        "button": {"radius": 12, "padding_y": 10, "padding_x": 16, "font_size": 12, "min_height": 18},
        "progress": {"height": 16, "radius": 10, "chunk_radius": 9},
    }


def _default_render_contract(bundle: ThemeBundle, manifest: ThemeManifest | None) -> ThemeRenderContract:
    dark = _is_dark_theme(bundle.id)
    tokens = _bundle_render_tokens(bundle)
    fx = _render_effects(bundle, dark)
    state_tokens = _build_state_tokens(tokens, dark)
    component_tokens = _build_component_tokens(tokens, state_tokens, dark)

    chip_base = tokens["chip_dark" if dark else "chip_light"]

    node_presets = {
        "package": {
            "fill": tokens["package_fill"],
            "stroke": tokens["package_stroke"],
            "text": tokens["text_main"],
            "subtext": tokens["text_soft"],
            "accent": tokens["package_accent"],
            "chip_fill": _mix_hex(tokens["package_stroke"], chip_base, 0.15 if dark else 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": tokens["badge_in"],
            "badge_out_fill": tokens["badge_out"],
            "badge_text": tokens["badge_text_dark"],
            "glow": tokens["package_stroke"],
            "glow_opacity": 0.14 if dark else 0.06,
            "border_width": fx["border_standard"],
            "shine_opacity": fx["shine_standard"],
            "accent_bar": True,
        },
        "module": {
            "fill": tokens["module_fill"],
            "stroke": tokens["module_stroke"],
            "text": tokens["text_main"],
            "subtext": tokens["text_soft"],
            "accent": tokens["module_accent"],
            "chip_fill": _mix_hex(tokens["module_stroke"], chip_base, 0.16 if dark else 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": tokens["badge_in"],
            "badge_out_fill": tokens["badge_out"],
            "badge_text": tokens["badge_text_dark"],
            "glow": tokens["module_stroke"],
            "glow_opacity": 0.10 if dark else 0.05,
            "border_width": fx["border_standard"],
            "shine_opacity": max(0.06 if dark else 0.14, fx["shine_standard"]),
            "accent_bar": True,
        },
        "external": {
            "fill": tokens["external_fill"],
            "stroke": tokens["external_stroke"],
            "text": tokens["text_main"],
            "subtext": tokens["text_soft"],
            "accent": tokens["external_accent"],
            "chip_fill": _mix_hex(tokens["external_stroke"], chip_base, 0.14 if dark else 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": _mix_hex(tokens["badge_in"], tokens["external_stroke"], 0.25),
            "badge_out_fill": _mix_hex(tokens["badge_out"], tokens["external_stroke"], 0.20),
            "badge_text": tokens["badge_text_dark"],
            "glow": tokens["external_stroke"],
            "glow_opacity": 0.10 if dark else 0.05,
            "border_width": fx["border_standard"],
            "shine_opacity": max(0.06 if dark else 0.14, fx["shine_standard"]),
            "accent_bar": True,
        },
        "note": {
            "fill": tokens["note_fill"],
            "stroke": tokens["note_stroke"],
            "text": tokens["text_main"] if dark else tokens["header_title"],
            "subtext": tokens["text_soft"] if dark else tokens["header_text"],
            "accent": tokens["note_accent"],
            "chip_fill": _mix_hex(tokens["note_stroke"], chip_base, 0.14 if dark else 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": _mix_hex(tokens["note_stroke"], tokens["badge_in"], 0.18),
            "badge_out_fill": _mix_hex(tokens["note_stroke"], tokens["badge_out"], 0.18),
            "badge_text": tokens["badge_text_dark"],
            "glow": tokens["note_stroke"],
            "glow_opacity": 0.08 if dark else 0.04,
            "border_width": fx["border_standard"],
            "shine_opacity": max(0.06 if dark else 0.16, fx["shine_standard"]),
            "accent_bar": True,
        },
        "focus_hero": {
            "fill": _mix_hex(tokens["package_fill"], tokens["focus"], 0.18 if dark else 0.16),
            "stroke": tokens["focus"],
            "text": tokens["text_main"] if dark else tokens["header_title"],
            "subtext": tokens["text_soft"] if dark else tokens["header_text"],
            "accent": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.22),
            "chip_fill": _mix_hex(tokens["focus"], chip_base, 0.16 if dark else 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": tokens["focus"],
            "badge_out_fill": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.28),
            "badge_text": tokens["badge_text_dark"],
            "glow": tokens["focus"],
            "glow_opacity": 0.20 if dark else 0.10,
            "border_width": fx["border_focus"],
            "shine_opacity": fx["shine_focus"],
            "accent_bar": True,
        },
        "focus_inbound": {
            "fill": _mix_hex(tokens["module_fill"], tokens["focus"], 0.12 if dark else 0.10),
            "stroke": tokens["focus"],
            "text": tokens["text_main"],
            "subtext": tokens["text_soft"],
            "accent": tokens["focus"],
            "chip_fill": _mix_hex(tokens["focus"], chip_base, 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": tokens["focus"],
            "badge_out_fill": tokens["badge_out"],
            "badge_text": tokens["badge_text_dark"],
            "glow": tokens["focus"],
            "glow_opacity": 0.18 if dark else 0.09,
            "border_width": fx["border_strong"],
            "shine_opacity": max(0.06 if dark else 0.15, fx["shine_standard"]),
            "accent_bar": True,
        },
        "focus_outbound": {
            "fill": _mix_hex(tokens["module_fill"], tokens["focus_warm"], 0.10 if dark else 0.09),
            "stroke": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.44),
            "text": tokens["text_main"],
            "subtext": tokens["text_soft"],
            "accent": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.44),
            "chip_fill": _mix_hex(tokens["focus_warm"], chip_base, 0.16 if dark else 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": tokens["badge_in"],
            "badge_out_fill": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.44),
            "badge_text": tokens["badge_text_dark"],
            "glow": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.44),
            "glow_opacity": 0.18 if dark else 0.09,
            "border_width": fx["border_strong"],
            "shine_opacity": max(0.06 if dark else 0.15, fx["shine_standard"]),
            "accent_bar": True,
        },
        "focus_mixed": {
            "fill": _mix_hex(tokens["module_fill"], tokens["focus_warm"], 0.14 if dark else 0.12),
            "stroke": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.52),
            "text": tokens["text_main"],
            "subtext": tokens["text_soft"],
            "accent": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.58),
            "chip_fill": _mix_hex(_mix_hex(tokens["focus"], tokens["focus_warm"], 0.55), chip_base, 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": tokens["focus"],
            "badge_out_fill": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.52),
            "badge_text": tokens["badge_text_dark"],
            "glow": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.52),
            "glow_opacity": 0.18 if dark else 0.09,
            "border_width": fx["border_strong"],
            "shine_opacity": max(0.06 if dark else 0.15, fx["shine_standard"]),
            "accent_bar": True,
        },
        "context_muted": {
            "fill": tokens["muted_fill"],
            "stroke": tokens["muted_stroke"],
            "text": tokens["muted_text"],
            "subtext": tokens["muted_subtext"],
            "accent": tokens["muted_stroke"],
            "chip_fill": _mix_hex(tokens["muted_stroke"], chip_base, 0.12 if dark else 0.18),
            "chip_text": tokens["muted_text"],
            "badge_in_fill": _mix_hex(tokens["muted_stroke"], tokens["badge_in"], 0.10),
            "badge_out_fill": _mix_hex(tokens["muted_stroke"], tokens["badge_out"], 0.10),
            "badge_text": tokens["badge_text_dark"] if dark else tokens["chip_light"],
            "glow": tokens["muted_stroke"],
            "glow_opacity": 0.06 if dark else 0.03,
            "border_width": fx["border_standard"],
            "shine_opacity": max(0.04, fx["shine_standard"] * 0.6),
            "accent_bar": False,
        },
        "hub_accent": {
            "fill": _mix_hex(tokens["module_fill"], tokens["package_fill"], 0.30),
            "stroke": _mix_hex(tokens["package_stroke"], tokens["module_stroke"], 0.48),
            "text": tokens["text_main"],
            "subtext": tokens["text_soft"],
            "accent": _mix_hex(tokens["package_accent"], tokens["module_accent"], 0.40),
            "chip_fill": _mix_hex(tokens["package_stroke"], chip_base, 0.16 if dark else 0.18),
            "chip_text": tokens["text_main"] if dark else tokens["header_title"],
            "badge_in_fill": tokens["badge_in"],
            "badge_out_fill": tokens["badge_out"],
            "badge_text": tokens["badge_text_dark"],
            "glow": _mix_hex(tokens["package_stroke"], tokens["focus_warm"], 0.20),
            "glow_opacity": 0.14 if dark else 0.06,
            "border_width": fx["border_hub"],
            "shine_opacity": fx["shine_focus"],
            "accent_bar": True,
        },
    }

    edge_presets = {
        "default": {
            "stroke": tokens["focus"],
            "marker_fill": tokens["focus"],
            "width": 1.8,
            "opacity": 0.68 if dark else 0.72,
            "glow": tokens["focus"],
            "glow_opacity": fx["glow_edge"],
            "glow_width": 5.2,
            "curve_bias": 0.34,
            "layer": 2,
            "marker_id": "arrow_default",
        },
        "muted": {
            "stroke": tokens["muted_stroke"],
            "marker_fill": tokens["muted_stroke"],
            "width": 1.25,
            "opacity": 0.24 if dark else 0.34,
            "glow": tokens["muted_stroke"],
            "glow_opacity": max(0.02, fx["glow_edge"] * 0.40),
            "glow_width": 3.6,
            "dasharray": "5 7",
            "curve_bias": 0.30,
            "layer": 1,
            "marker_id": "arrow_muted",
        },
        "focus_inbound": {
            "stroke": tokens["focus"],
            "marker_fill": tokens["focus"],
            "width": 2.2,
            "opacity": 0.86 if dark else 0.82,
            "glow": tokens["focus"],
            "glow_opacity": fx["glow_focus"],
            "glow_width": 6.6,
            "curve_bias": 0.38,
            "layer": 3,
            "marker_id": "arrow_focus_in",
        },
        "focus_outbound": {
            "stroke": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.42),
            "marker_fill": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.42),
            "width": 2.15,
            "opacity": 0.82 if dark else 0.78,
            "glow": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.42),
            "glow_opacity": max(0.08, fx["glow_focus"] * 0.90),
            "glow_width": 6.2,
            "curve_bias": 0.38,
            "layer": 3,
            "marker_id": "arrow_focus_out",
        },
        "self_loop": {
            "stroke": _mix_hex(tokens["package_stroke"], tokens["focus_warm"], 0.26),
            "marker_fill": _mix_hex(tokens["package_stroke"], tokens["focus_warm"], 0.26),
            "width": 1.65,
            "opacity": 0.48 if dark else 0.56,
            "glow": _mix_hex(tokens["package_stroke"], tokens["focus_warm"], 0.26),
            "glow_opacity": max(0.04, fx["glow_focus"] * 0.40),
            "glow_width": 5.0,
            "dasharray": "4 4",
            "curve_bias": 0.42,
            "layer": 2,
            "marker_id": "arrow_default",
        },
        "cross_lane": {
            "stroke": _mix_hex(tokens["focus"], tokens["package_stroke"], 0.28),
            "marker_fill": _mix_hex(tokens["focus"], tokens["package_stroke"], 0.28),
            "width": 1.8,
            "opacity": 0.60 if dark else 0.66,
            "glow": _mix_hex(tokens["focus"], tokens["package_stroke"], 0.24),
            "glow_opacity": max(0.04, fx["glow_edge"] * 0.70),
            "glow_width": 5.6,
            "curve_bias": 0.37,
            "layer": 2,
            "marker_id": "arrow_default",
        },
        "intra_lane": {
            "stroke": _mix_hex(tokens["module_stroke"], tokens["focus"], 0.18),
            "marker_fill": _mix_hex(tokens["module_stroke"], tokens["focus"], 0.18),
            "width": 1.45,
            "opacity": 0.42 if dark else 0.52,
            "glow": _mix_hex(tokens["module_stroke"], tokens["focus"], 0.18),
            "glow_opacity": max(0.03, fx["glow_edge"] * 0.55),
            "glow_width": 4.4,
            "curve_bias": 0.30,
            "layer": 2,
            "marker_id": "arrow_default",
        },
    }

    lane_presets = {
        "default": {
            "fill": tokens["lane_fill"],
            "stroke": tokens["lane_stroke"],
            "header_fill": tokens["lane_header_fill"],
            "header_text": tokens["lane_header_text"],
            "meta_text": tokens["lane_meta_text"],
            "accent": tokens["focus"],
            "fill_opacity": 0.32 if dark else 0.74,
            "stroke_opacity": 0.78 if dark else 0.84,
            "header_fill_opacity": 0.94 if dark else 0.96,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.0,
            "accent_opacity": 0.14 if dark else 0.08,
        },
        "focus_center_lane": {
            "fill": _mix_hex(tokens["lane_fill"], tokens["focus"], 0.10 if dark else 0.06),
            "stroke": tokens["focus"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["focus"], 0.12 if dark else 0.08),
            "header_text": tokens["header_title"],
            "meta_text": tokens["header_text"],
            "accent": _mix_hex(tokens["focus"], tokens["focus_warm"], 0.20),
            "fill_opacity": 0.42 if dark else 0.82,
            "stroke_opacity": 0.92,
            "header_fill_opacity": 0.98,
            "radius": 20.0,
            "header_radius": 15.0,
            "border_width": 1.35,
            "accent_opacity": 0.24 if dark else 0.10,
            "label_capsule_fill": _mix_hex(tokens["focus"], chip_base, 0.18),
            "label_capsule_text": tokens["text_main"] if dark else tokens["header_title"],
        },
        "side_lane": {
            "fill": tokens["lane_fill"],
            "stroke": tokens["lane_stroke"],
            "header_fill": tokens["lane_header_fill"],
            "header_text": tokens["lane_header_text"],
            "meta_text": tokens["lane_meta_text"],
            "accent": tokens["module_accent"],
            "fill_opacity": 0.28 if dark else 0.70,
            "stroke_opacity": 0.70 if dark else 0.82,
            "header_fill_opacity": 0.92,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.0,
            "accent_opacity": 0.12 if dark else 0.06,
        },
        "issue_lane": {
            "fill": _mix_hex(tokens["lane_fill"], tokens["note_fill"], 0.18 if dark else 0.12),
            "stroke": tokens["note_stroke"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["note_fill"], 0.26 if dark else 0.14),
            "header_text": tokens["header_title"] if dark else tokens["warning_text"],
            "meta_text": tokens["warning_text"] if not dark else tokens["note_accent"],
            "accent": tokens["note_accent"],
            "fill_opacity": 0.36 if dark else 0.84,
            "stroke_opacity": 0.80,
            "header_fill_opacity": 0.96,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.10,
            "accent_opacity": 0.18 if dark else 0.09,
        },
        "external_lane": {
            "fill": _mix_hex(tokens["lane_fill"], tokens["external_fill"], 0.20 if dark else 0.10),
            "stroke": tokens["external_stroke"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["external_fill"], 0.24 if dark else 0.12),
            "header_text": tokens["header_title"],
            "meta_text": tokens["header_text"],
            "accent": tokens["external_accent"],
            "fill_opacity": 0.34 if dark else 0.78,
            "stroke_opacity": 0.76,
            "header_fill_opacity": 0.95,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.05,
            "accent_opacity": 0.16 if dark else 0.08,
        },
    }

    panel_presets = {
        "header": {
            "fill": tokens["header_fill"],
            "stroke": tokens["header_stroke"],
            "title": tokens["header_title"],
            "text": tokens["header_text"],
            "meta": tokens["header_meta"],
            "accent": tokens["focus"],
            "fill_opacity": 0.74 if dark else 0.88,
            "stroke_opacity": 0.90,
            "radius": 18.0,
            "border_width": 1.0,
        },
        "legend": {
            "fill": tokens["legend_fill"],
            "stroke": tokens["legend_stroke"],
            "title": tokens["header_title"],
            "text": tokens["header_text"],
            "meta": tokens["header_meta"],
            "accent": tokens["focus"],
            "fill_opacity": 0.76 if dark else 0.92,
            "stroke_opacity": 0.92,
            "radius": 16.0,
            "border_width": 1.0,
        },
        "warning": {
            "fill": tokens["warning_fill"],
            "stroke": tokens["warning_stroke"],
            "title": tokens["warning_text"],
            "text": tokens["warning_text"],
            "meta": tokens["warning_text"],
            "accent": tokens["note_accent"],
            "fill_opacity": 0.94 if dark else 0.96,
            "stroke_opacity": 0.96,
            "radius": 14.0,
            "border_width": 1.05,
        },
        "footer": {
            "fill": tokens["footer_fill"],
            "stroke": tokens["footer_stroke"],
            "title": tokens["footer_text"],
            "text": tokens["footer_text"],
            "meta": tokens["footer_text"],
            "accent": tokens["focus"],
            "fill_opacity": 0.46 if dark else 0.82,
            "stroke_opacity": 0.72,
            "radius": 12.0,
            "border_width": 1.0,
        },
    }

    badge_presets = {
        "inbound": {"fill": tokens["badge_in"], "text_fill": tokens["badge_text_dark"]},
        "outbound": {"fill": tokens["badge_out"], "text_fill": tokens["badge_text_dark"]},
        "hub": {"fill": tokens["note_accent"], "text_fill": tokens["chip_light"]},
        "island": {"fill": tokens["muted_stroke"], "text_fill": tokens["chip_light"]},
    }

    marker_presets = {
        "default_arrow": {"svg_id": "arrowHead", "fill": edge_presets["default"]["marker_fill"], "opacity": 0.95},
        "subtle_arrow": {"svg_id": "subtleArrowHead", "fill": edge_presets["muted"]["marker_fill"], "opacity": 0.75},
        "focus_arrow": {"svg_id": "focusArrowHead", "fill": edge_presets["focus_inbound"]["marker_fill"], "opacity": 0.98},
    }

    return ThemeRenderContract(
        theme_id=bundle.id,
        label=bundle.label,
        svg_defs=bundle.svg_defs,
        is_dark=dark,
        tokens=tokens,
        node_presets=node_presets,
        edge_presets=edge_presets,
        lane_presets=lane_presets,
        panel_presets=panel_presets,
        badge_presets=badge_presets,
        marker_presets=marker_presets,
        effect_presets=_deep_copy_value(bundle.effect_presets),
        state_tokens=state_tokens,
        component_tokens=component_tokens,
        manifest=manifest,
        raw_bundle=bundle,
    )


def _map_bundle_node_overrides(bundle: ThemeBundle) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    badge_in = _coerce_dict(bundle.badge_presets).get("inbound", {})
    badge_out = _coerce_dict(bundle.badge_presets).get("outbound", {})
    for key, source in _coerce_dict(bundle.node_presets).items():
        source_dict = _coerce_dict(source)
        if not source_dict:
            continue
        mapped[key] = {
            "fill": source_dict.get("fill"),
            "stroke": source_dict.get("stroke"),
            "text": source_dict.get("label_fill"),
            "subtext": source_dict.get("subtitle_fill"),
            "accent": source_dict.get("stroke"),
            "badge_in_fill": _coerce_dict(badge_in).get("fill"),
            "badge_out_fill": _coerce_dict(badge_out).get("fill"),
            "badge_text": _coerce_dict(badge_in).get("text_fill"),
            "glow": source_dict.get("stroke"),
            "border_width": source_dict.get("border_width"),
            "shine_opacity": source_dict.get("shine_opacity"),
        }
    return mapped


def _map_bundle_edge_overrides(bundle: ThemeBundle) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    marker_id_aliases = {
        "default_arrow": "arrowHead",
        "subtle_arrow": "subtleArrowHead",
        "focus_arrow": "focusArrowHead",
    }
    for key, source in _coerce_dict(bundle.edge_presets).items():
        source_dict = _coerce_dict(source)
        if not source_dict:
            continue
        marker_key = clean_text(source_dict.get("marker_key") or "")
        marker_id = clean_text(source_dict.get("marker_id") or marker_id_aliases.get(marker_key, ""))
        mapped[key] = {
            "stroke": source_dict.get("stroke"),
            "marker_fill": source_dict.get("stroke"),
            "width": source_dict.get("base_width"),
            "opacity": source_dict.get("opacity"),
            "glow": source_dict.get("glow"),
            "glow_opacity": source_dict.get("glow_opacity"),
            "glow_width": source_dict.get("glow_width"),
            "marker_id": marker_id,
        }
    return mapped


def _map_bundle_lane_overrides(bundle: ThemeBundle) -> dict[str, dict[str, Any]]:
    key_aliases = {
        "standard": "default",
        "focus_center": "focus_center_lane",
        "focus_side": "side_lane",
        "issue_lane": "issue_lane",
        "external_lane": "external_lane",
    }
    mapped: dict[str, dict[str, Any]] = {}
    for key, source in _coerce_dict(bundle.lane_presets).items():
        source_dict = _coerce_dict(source)
        mapped_key = key_aliases.get(key, key)
        if not source_dict:
            continue
        mapped[mapped_key] = {
            "fill": source_dict.get("band_fill"),
            "stroke": source_dict.get("band_stroke"),
            "header_fill": source_dict.get("header_fill"),
            "header_text": source_dict.get("title_fill"),
            "meta_text": source_dict.get("meta_fill"),
            "accent": source_dict.get("band_stroke"),
            "fill_opacity": source_dict.get("band_opacity"),
        }
    return mapped


def _map_bundle_panel_overrides(bundle: ThemeBundle) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for key, source in _coerce_dict(bundle.panel_presets).items():
        source_dict = _coerce_dict(source)
        if not source_dict:
            continue
        mapped[key] = {
            "fill": source_dict.get("fill"),
            "stroke": source_dict.get("stroke"),
            "title": source_dict.get("text_fill"),
            "text": source_dict.get("text_fill"),
            "meta": source_dict.get("meta_fill"),
            "accent": source_dict.get("glow") or source_dict.get("stroke"),
            "fill_opacity": source_dict.get("fill_opacity"),
        }
    return mapped


def _map_bundle_badge_overrides(bundle: ThemeBundle) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for key, source in _coerce_dict(bundle.badge_presets).items():
        source_dict = _coerce_dict(source)
        if not source_dict:
            continue
        mapped[key] = {
            "fill": source_dict.get("fill"),
            "text_fill": source_dict.get("text_fill"),
        }
    return mapped


def _map_bundle_marker_overrides(bundle: ThemeBundle) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for key, source in _coerce_dict(bundle.marker_presets).items():
        source_dict = _coerce_dict(source)
        if not source_dict:
            continue
        mapped[key] = {
            "svg_id": source_dict.get("svg_id"),
            "fill": source_dict.get("fill"),
            "opacity": source_dict.get("opacity"),
        }
    return mapped


def _build_render_contract(bundle: ThemeBundle, manifest: ThemeManifest | None = None) -> ThemeRenderContract:
    base = _default_render_contract(bundle, manifest)
    return ThemeRenderContract(

        theme_id=base.theme_id,
        label=base.label,
        svg_defs=bundle.svg_defs or base.svg_defs,
        is_dark=base.is_dark,
        tokens=base.tokens,
        node_presets=_merge_dicts(base.node_presets, _map_bundle_node_overrides(bundle)),
        edge_presets=_merge_dicts(base.edge_presets, _map_bundle_edge_overrides(bundle)),
        lane_presets=_merge_dicts(base.lane_presets, _map_bundle_lane_overrides(bundle)),
        panel_presets=_merge_dicts(base.panel_presets, _map_bundle_panel_overrides(bundle)),
        badge_presets=_merge_dicts(base.badge_presets, _map_bundle_badge_overrides(bundle)),
        marker_presets=_merge_dicts(base.marker_presets, _map_bundle_marker_overrides(bundle)),
        effect_presets=_deep_copy_value(bundle.effect_presets),
        state_tokens=base.state_tokens,
        component_tokens=base.component_tokens,
        manifest=manifest,
        raw_bundle=bundle,
    )


def _build_render_registry(
    theme_bundles: Iterable[ThemeBundle],
    manifest_by_id: dict[str, ThemeManifest],
) -> dict[str, ThemeRenderContract]:
    registry: dict[str, ThemeRenderContract] = {}
    for bundle in theme_bundles:
        theme_id = clean_text(bundle.id).lower()
        if not theme_id:
            continue
        registry[theme_id] = _build_render_contract(bundle, manifest_by_id.get(theme_id))
    return registry


def normalize_theme(theme: str) -> str:
    for key in _theme_lookup_keys(theme):
        resolved = _THEME_ALIAS_TO_ID.get(key)
        if resolved:
            return resolved
    return DEFAULT_THEME


def resolve_theme_bundle(theme_id: str) -> ThemeBundle:
    normalized = normalize_theme(theme_id)

    bundle = THEME_REGISTRY.get(normalized)
    if bundle is not None:
        return bundle

    bundle = THEME_REGISTRY.get(DEFAULT_THEME)
    if bundle is not None:
        return bundle

    if THEME_BUNDLES:
        return THEME_BUNDLES[0]

    return theme_dark()


def resolve_render_theme(theme_id: str) -> ThemeRenderContract:
    normalized = normalize_theme(theme_id)

    contract = _THEME_RENDER_REGISTRY.get(normalized)
    if contract is not None:
        return contract

    fallback_id = normalize_theme(DEFAULT_THEME)
    contract = _THEME_RENDER_REGISTRY.get(fallback_id)
    if contract is not None:
        return contract

    bundle = resolve_theme_bundle(theme_id)
    manifest = _THEME_MANIFEST_BY_ID.get(clean_text(bundle.id).lower())
    return _build_render_contract(bundle, manifest)


# PATCH_MINIMO_FALTANTES_MOD09_V2

def _qss_vertical_gradient(top: str, bottom: str) -> str:
    return (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
        f"stop:0 {top}, stop:0.55 {top}, stop:1 {bottom})"
    )


def _qss_horizontal_gradient(left: str, right: str) -> str:
    return (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        f"stop:0 {left}, stop:1 {right})"
    )


def build_app_stylesheet(theme_id: str) -> str:
    render = resolve_render_theme(theme_id)
    t = render.tokens
    dark = render.is_dark
    silver_theme = _is_silver_theme_id(theme_id)

    dialog_bg = "transparent"
    shell_top = _with_alpha(_mix_hex(t["header_fill"], t["legend_fill"], 0.42 if dark else 0.16), 0.80 if dark else 0.90 if silver_theme else 0.94)
    shell_bottom = _with_alpha(_mix_hex(t["canvas_bg"], t["header_fill"], 0.26 if dark else 0.08), 0.72 if dark else 0.82 if silver_theme else 0.90)
    shell_border = _with_alpha(_mix_hex(t["focus"], t["legend_stroke"], 0.24 if dark else 0.10), 0.24 if dark else 0.42)
    shell_glow = _with_alpha("#ffffff", 0.07 if dark else 0.12)
    shell_rim = _with_alpha(t["focus"], 0.20 if dark else 0.22)

    hero_top = _with_alpha(_mix_hex(t["focus"], t["header_fill"], 0.14 if dark else 0.04), 0.30 if dark else 0.78)
    hero_bottom = _with_alpha(_mix_hex(t["legend_fill"], t["canvas_bg"], 0.18 if dark else 0.05), 0.78 if dark else 0.92)
    hero_border = _with_alpha(t["focus"], 0.30 if dark else 0.36)

    card_top = _with_alpha(_mix_hex(t["legend_fill"], t["header_fill"], 0.12 if dark else 0.04), 0.66 if dark else 0.78 if silver_theme else 0.92)
    card_bottom = _with_alpha(_mix_hex(t["canvas_bg"], t["legend_fill"], 0.20 if dark else 0.05), 0.56 if dark else 0.70 if silver_theme else 0.88)
    muted_top = _with_alpha(_mix_hex(t["canvas_bg"], t["legend_fill"], 0.26 if dark else 0.06), 0.48 if dark else 0.66 if silver_theme else 0.84)
    muted_bottom = _with_alpha(_mix_hex(t["canvas_bg"], t["header_fill"], 0.18 if dark else 0.05), 0.42 if dark else 0.62 if silver_theme else 0.80)
    footer_top = _with_alpha(_mix_hex(t["header_fill"], t["canvas_bg"], 0.18 if dark else 0.06), 0.50 if dark else 0.70 if silver_theme else 0.86)
    footer_bottom = _with_alpha(_mix_hex(t["canvas_bg"], t["legend_fill"], 0.18 if dark else 0.06), 0.40 if dark else 0.62 if silver_theme else 0.82)
    card_border = _with_alpha(t["legend_stroke"], 0.24 if dark else 0.42)
    muted_border = _with_alpha(t["header_stroke"], 0.18 if dark else 0.30)
    line = _with_alpha(t["header_stroke"], 0.12 if dark else 0.22)
    line_glow = _with_alpha(t["focus"], 0.26 if dark else 0.18)

    title = t["header_title"]
    subtitle = _mix_hex(t["header_meta"], t["text_soft"], 0.18)
    section = t["header_title"]
    field = _mix_hex(t["focus"], t["chip_light"], 0.74 if dark else 0.26)
    eyebrow = _mix_hex(t["focus"], t["header_meta"], 0.42 if dark else 0.26)
    hint = t["footer_text"]
    value = t["text_main"]
    mono = t["text_soft"]
    chrome_title = _mix_hex(t["header_title"], t["text_main"], 0.24 if dark else 0.12)
    chrome_icon = _mix_hex(t["focus"], t["chip_light"], 0.56 if dark else 0.24)
    chrome_bg_top = _with_alpha(_mix_hex(t["header_fill"], t["canvas_bg"], 0.26 if dark else 0.06), 0.72 if dark else 0.90)
    chrome_bg_bottom = _with_alpha(_mix_hex(t["legend_fill"], t["canvas_bg"], 0.20 if dark else 0.04), 0.54 if dark else 0.82)
    chrome_border = _with_alpha(t["legend_stroke"], 0.20 if dark else 0.30)
    chrome_button_fg = _mix_hex(t["text_main"], t["chip_light"], 0.18 if dark else 0.10)
    chrome_button_bg = _with_alpha(_mix_hex(t["canvas_bg"], t["legend_fill"], 0.20 if dark else 0.06), 0.62 if dark else 0.86)
    chrome_button_border = _with_alpha(t["header_stroke"], 0.18 if dark else 0.30)
    chrome_button_hover = _with_alpha(t["focus"], 0.18 if dark else 0.14)
    chrome_close_hover = _with_alpha(t["warning_fill"], 0.28 if dark else 0.24)
    chrome_close_border = _with_alpha(t["warning_stroke"], 0.36 if dark else 0.38)

    neutral_chip_text = t["text_soft"] if dark else _mix_hex(t["header_text"], t["text_main"], 0.34 if silver_theme else 0.16)
    neutral_chip_bg = _with_alpha(_mix_hex(t["legend_fill"], t["canvas_bg"], 0.24 if dark else 0.08), 0.36 if dark else 0.82)
    neutral_chip_border = _with_alpha(t["muted_stroke"], 0.18 if dark else 0.28)
    good_chip_text = _mix_hex(t["badge_out"], t["chip_light"], 0.72 if dark else 0.40)
    good_chip_bg = _with_alpha(t["badge_out"], 0.12 if dark else 0.18)
    good_chip_border = _with_alpha(t["badge_out"], 0.24 if dark else 0.32)
    warn_chip_text = _mix_hex(t["warning_stroke"], t["chip_light"], 0.70 if dark else 0.24)
    warn_chip_bg = _with_alpha(t["warning_stroke"], 0.12 if dark else 0.18)
    warn_chip_border = _with_alpha(t["warning_stroke"], 0.24 if dark else 0.32)
    accent_chip_text = _mix_hex(t["focus"], t["chip_light"], 0.78 if dark else 0.30)
    accent_chip_bg = _with_alpha(t["focus"], 0.13 if dark else 0.16)
    accent_chip_border = _with_alpha(t["focus"], 0.28 if dark else 0.34)

    input_bg = _with_alpha(_mix_hex(t["canvas_bg"], t["legend_fill"], 0.18 if dark else 0.04), 0.72 if dark else 0.90)
    input_fg = value
    input_border = _with_alpha(t["legend_stroke"], 0.18 if dark else 0.34)
    input_hover = _with_alpha(t["focus"], 0.46 if dark else 0.54)
    input_focus = _with_alpha(t["focus"], 0.84 if dark else 0.82)
    input_focus_bg = _with_alpha(_mix_hex(t["canvas_bg"], t["header_fill"], 0.16 if dark else 0.06), 0.78 if dark else 0.92)
    input_disabled_fg = _with_alpha(t["muted_text"], 0.82)
    input_disabled_bg = _with_alpha(_mix_hex(t["canvas_bg"], t["legend_fill"], 0.12 if dark else 0.04), 0.40 if dark else 0.72)
    input_disabled_border = _with_alpha(t["legend_stroke"], 0.08 if dark else 0.20)
    dropdown_bg = _with_alpha(_mix_hex(t["legend_fill"], t["canvas_bg"], 0.10 if dark else 0.03), 0.92 if dark else 0.96)
    selection_bg = t["focus"]
    selection_fg = t["chip_light"]

    primary_top = _mix_hex(t["focus"], t["chip_light"], 0.04 if dark else 0.12)
    primary_bottom = _mix_hex(t["focus"], t["canvas_bg"], 0.12 if dark else 0.04)
    primary_border = _with_alpha(t["focus"], 0.36 if dark else 0.40)
    primary_hover_top = _mix_hex(t["focus"], t["chip_light"], 0.10 if dark else 0.16)
    primary_hover_bottom = _mix_hex(t["focus"], t["chip_light"], 0.04 if dark else 0.10)

    secondary_top = _with_alpha(_mix_hex(t["header_fill"], t["legend_fill"], 0.16 if dark else 0.06), 0.78 if dark else 0.92)
    secondary_bottom = _with_alpha(_mix_hex(t["canvas_bg"], t["header_fill"], 0.18 if dark else 0.05), 0.62 if dark else 0.86)
    secondary_border = _with_alpha(t["legend_stroke"], 0.16 if dark else 0.30)
    secondary_hover_top = _with_alpha(_mix_hex(t["focus"], t["legend_fill"], 0.10 if dark else 0.05), 0.82 if dark else 0.94)
    secondary_hover_bottom = _with_alpha(_mix_hex(t["focus"], t["canvas_bg"], 0.10 if dark else 0.04), 0.68 if dark else 0.88)

    success_top = _mix_hex(t["badge_out"], t["chip_light"], 0.06 if dark else 0.12)
    success_bottom = _mix_hex(t["badge_out"], t["canvas_bg"], 0.16 if dark else 0.04)
    success_border = _with_alpha(t["badge_out"], 0.28 if dark else 0.32)
    success_hover_top = _mix_hex(t["badge_out"], t["chip_light"], 0.12 if dark else 0.18)
    success_hover_bottom = _mix_hex(t["badge_out"], t["chip_light"], 0.04 if dark else 0.10)

    danger_top = _with_alpha(_mix_hex(t["warning_fill"], t["header_fill"], 0.20 if dark else 0.10), 0.80 if dark else 0.92)
    danger_bottom = _with_alpha(_mix_hex(t["warning_fill"], t["canvas_bg"], 0.26 if dark else 0.08), 0.68 if dark else 0.86)
    danger_border = _with_alpha(t["warning_stroke"], 0.22 if dark else 0.30)
    danger_hover_top = _with_alpha(_mix_hex(t["warning_fill"], t["warning_stroke"], 0.12 if dark else 0.08), 0.84 if dark else 0.94)
    danger_hover_bottom = _with_alpha(_mix_hex(t["warning_fill"], t["warning_stroke"], 0.20 if dark else 0.12), 0.72 if dark else 0.90)

    disabled_bg = _with_alpha(_mix_hex(t["header_fill"], t["canvas_bg"], 0.18 if dark else 0.08), 0.42 if dark else 0.76)
    disabled_fg = _with_alpha(t["muted_text"], 0.84)
    disabled_border = _with_alpha(t["legend_stroke"], 0.06 if dark else 0.18)

    progress_bg = _with_alpha(_mix_hex(t["canvas_bg"], t["legend_fill"], 0.18 if dark else 0.06), 0.70 if dark else 0.92)
    progress_border = _with_alpha(t["legend_stroke"], 0.18 if dark else 0.32)
    progress_text = value
    progress_chunk_top = _mix_hex(t["focus"], t["chip_light"], 0.10 if dark else 0.22)
    progress_chunk_bottom = _mix_hex(t["focus"], t["canvas_bg"], 0.14 if dark else 0.08)

    tooltip_bg = _with_alpha(_mix_hex(t["header_fill"], t["canvas_bg"], 0.14 if dark else 0.05), 0.94 if dark else 0.98)
    tooltip_border = _with_alpha(t["focus"], 0.22 if dark else 0.28)

    if silver_theme:
        shell_top = _with_alpha("#eef6ff", 0.08)
        shell_bottom = _with_alpha("#94a8c1", 0.04)
        shell_border = _with_alpha("#eef8ff", 0.24)
        shell_glow = _with_alpha("#ffffff", 0.04)
        shell_rim = _with_alpha(t["focus"], 0.42)

        hero_top = _with_alpha("#eef7ff", 0.10)
        hero_bottom = _with_alpha(t["focus"], 0.06)
        hero_border = _with_alpha(t["focus"], 0.44)

        card_top = _with_alpha("#edf6ff", 0.09)
        card_bottom = _with_alpha("#a4b5ca", 0.05)
        muted_top = _with_alpha("#e6f1fb", 0.10)
        muted_bottom = _with_alpha("#9cb0c8", 0.06)
        footer_top = _with_alpha("#eef6ff", 0.10)
        footer_bottom = _with_alpha("#9caec5", 0.06)
        card_border = _with_alpha("#eaf6ff", 0.18)
        muted_border = _with_alpha("#eaf6ff", 0.15)
        line = _with_alpha("#d8e7f6", 0.14)
        line_glow = _with_alpha(t["focus"], 0.22)

        title = "#f5fbff"
        subtitle = "#c1d0df"
        section = "#edf6ff"
        field = "#95eeff"
        eyebrow = "#7fc8df"
        hint = "#98adc2"
        value = "#e0edf9"
        mono = "#b8cade"
        chrome_title = "#dce8f3"
        chrome_icon = "#86e9ff"
        chrome_bg_top = _with_alpha("#edf6ff", 0.06)
        chrome_bg_bottom = _with_alpha("#95aac3", 0.04)
        chrome_border = _with_alpha("#eef8ff", 0.10)
        chrome_button_fg = "#ebf4ff"
        chrome_button_bg = _with_alpha("#0c1520", 0.44)
        chrome_button_border = _with_alpha("#eef8ff", 0.08)
        chrome_button_hover = _with_alpha(t["focus"], 0.16)
        chrome_close_hover = _with_alpha(t["focus"], 0.18)
        chrome_close_border = _with_alpha(t["focus"], 0.26)

        neutral_chip_text = "#d7e6f3"
        neutral_chip_bg = _with_alpha("#0c1520", 0.34)
        neutral_chip_border = _with_alpha("#eef8ff", 0.12)
        good_chip_text = "#d7f3fa"
        good_chip_bg = _with_alpha(t["badge_out"], 0.12)
        good_chip_border = _with_alpha(t["badge_out"], 0.28)
        warn_chip_text = "#f0e5d4"
        warn_chip_bg = _with_alpha(t["warning_stroke"], 0.12)
        warn_chip_border = _with_alpha(t["warning_stroke"], 0.26)
        accent_chip_text = "#ecfbff"
        accent_chip_bg = _with_alpha(t["focus"], 0.14)
        accent_chip_border = _with_alpha(t["focus"], 0.34)

        input_bg = _with_alpha("#0a1320", 0.56)
        input_fg = "#eff8ff"
        input_border = _with_alpha("#e7f5ff", 0.14)
        input_hover = _with_alpha(t["focus"], 0.52)
        input_focus = _with_alpha(t["focus"], 0.84)
        input_focus_bg = _with_alpha("#0e1824", 0.68)
        input_disabled_fg = _with_alpha("#9db0c4", 0.76)
        input_disabled_bg = _with_alpha("#0b121c", 0.28)
        input_disabled_border = _with_alpha("#e7f5ff", 0.06)
        dropdown_bg = _with_alpha("#0f1825", 0.96)
        selection_bg = t["focus"]
        selection_fg = "#08111a"

        primary_top = _mix_hex(t["focus"], "#ffffff", 0.20)
        primary_bottom = _mix_hex(t["focus"], "#74dcef", 0.08)
        primary_border = _with_alpha(t["focus"], 0.40)
        primary_hover_top = _mix_hex(t["focus"], "#ffffff", 0.28)
        primary_hover_bottom = _mix_hex(t["focus"], "#8cefff", 0.18)

        secondary_top = _with_alpha("#edf6ff", 0.10)
        secondary_bottom = _with_alpha("#95aac1", 0.05)
        secondary_border = _with_alpha("#eef8ff", 0.14)
        secondary_hover_top = _with_alpha("#edf6ff", 0.14)
        secondary_hover_bottom = _with_alpha(t["focus"], 0.07)

        success_top = primary_top
        success_bottom = primary_bottom
        success_border = _with_alpha(t["focus"], 0.30)
        success_hover_top = primary_hover_top
        success_hover_bottom = primary_hover_bottom

        danger_top = _with_alpha("#f2f6fb", 0.10)
        danger_bottom = _with_alpha("#a6b4c3", 0.06)
        danger_border = _with_alpha("#eef8ff", 0.14)
        danger_hover_top = _with_alpha("#f2f6fb", 0.14)
        danger_hover_bottom = _with_alpha(t["focus"], 0.05)

        disabled_bg = _with_alpha("#0d141d", 0.22)
        disabled_fg = _with_alpha("#9fb4c7", 0.64)
        disabled_border = _with_alpha("#e7f5ff", 0.06)

        progress_bg = _with_alpha("#0c1520", 0.44)
        progress_border = _with_alpha("#eef8ff", 0.12)
        progress_text = "#e4f0fb"
        progress_chunk_top = _mix_hex(t["focus"], "#ffffff", 0.18)
        progress_chunk_bottom = _mix_hex(t["focus"], "#6dd9ee", 0.06)

        tooltip_bg = _with_alpha("#0f1825", 0.94)
        tooltip_border = _with_alpha(t["focus"], 0.24)

    return f"""
    QDialog,
    QMessageBox {{
        background: {dialog_bg};
        color: {value};
    }}

    QWidget#GlassStage,
    QWidget#GlassContent {{
        background: transparent;
    }}

    QFrame#Shell {{
        background: {_qss_vertical_gradient(shell_top, shell_bottom)};
        border: 0px solid transparent;
        border-radius: 28px;
    }}

    QFrame#Shell:hover {{
        border: 0px solid transparent;
    }}

    QFrame#Shell[variant="progress"] {{
        border-radius: 26px;
    }}

    QFrame#WindowChrome {{
        background: {_qss_vertical_gradient(chrome_bg_top, chrome_bg_bottom)};
        border: 1px solid {chrome_border};
        border-radius: 12px;
    }}

    QFrame[card="hero"] {{
        background: {_qss_vertical_gradient(hero_top, hero_bottom)};
        border: 1px solid {hero_border};
        border-radius: 22px;
    }}

    QFrame[card="true"] {{
        background: {_qss_vertical_gradient(card_top, card_bottom)};
        border: 1px solid {card_border};
        border-radius: 18px;
    }}

    QFrame[card="muted"] {{
        background: {_qss_vertical_gradient(muted_top, muted_bottom)};
        border: 1px solid {muted_border};
        border-radius: 18px;
    }}

    QFrame[card="footer"] {{
        background: {_qss_vertical_gradient(footer_top, footer_bottom)};
        border: 1px solid {muted_border};
        border-radius: 18px;
    }}

    QFrame[hoverable="true"][hover="true"] {{
        border: 1px solid {input_hover};
    }}

    QFrame#Line {{
        background: {_qss_horizontal_gradient(line_glow, line)};
        min-height: 1px;
        max-height: 1px;
        border-radius: 1px;
        border: none;
    }}

    QLabel[role="title"] {{
        color: {title};
        font-size: 28px;
        font-weight: 760;
        letter-spacing: 0.25px;
    }}

    QLabel[role="eyebrow"] {{
        color: {eyebrow};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }}

    QLabel[role="window_title"] {{
        color: {chrome_title};
        font-size: 12px;
        font-weight: 740;
        letter-spacing: 0.25px;
    }}

    QLabel[role="window_icon"] {{
        color: {chrome_icon};
        font-size: 11px;
        font-weight: 700;
    }}

    QLabel[role="subtitle"] {{
        color: {subtitle};
        font-size: 12px;
        line-height: 1.35em;
    }}

    QLabel[role="section"] {{
        color: {section};
        font-size: 15px;
        font-weight: 720;
    }}

    QLabel[role="field"] {{
        color: {field};
        font-size: 11px;
        font-weight: 720;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }}

    QLabel[role="hint"] {{
        color: {hint};
        font-size: 11px;
        line-height: 1.35em;
    }}

    QLabel[role="value"] {{
        color: {value};
        font-size: 12px;
    }}

    QLabel[role="mono"] {{
        color: {mono};
        font-size: 12px;
        font-family: "Consolas", "Cascadia Code", monospace;
    }}

    QLabel[chip="true"] {{
        border-radius: 12px;
        padding: 7px 11px;
        font-size: 11px;
        font-weight: 760;
        letter-spacing: 0.4px;
    }}

    QLabel[chip="true"][tone="neutral"] {{
        color: {neutral_chip_text};
        background: {neutral_chip_bg};
        border: 1px solid {neutral_chip_border};
    }}

    QLabel[chip="true"][tone="good"] {{
        color: {good_chip_text};
        background: {good_chip_bg};
        border: 1px solid {good_chip_border};
    }}

    QLabel[chip="true"][tone="warn"] {{
        color: {warn_chip_text};
        background: {warn_chip_bg};
        border: 1px solid {warn_chip_border};
    }}

    QLabel[chip="true"][tone="accent"] {{
        color: {accent_chip_text};
        background: {accent_chip_bg};
        border: 1px solid {accent_chip_border};
    }}

    QLineEdit,
    QComboBox,
    QMessageBox QLineEdit {{
        background: {input_bg};
        color: {input_fg};
        border: 1px solid {input_border};
        border-radius: 14px;
        padding: 10px 12px;
        font-size: 12px;
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
    }}

    QLineEdit:hover,
    QComboBox:hover,
    QMessageBox QLineEdit:hover {{
        border: 1px solid {input_hover};
    }}

    QLineEdit:focus,
    QComboBox:focus,
    QMessageBox QLineEdit:focus {{
        border: 1px solid {input_focus};
        background: {input_focus_bg};
    }}

    QLineEdit:disabled,
    QComboBox:disabled,
    QMessageBox QLineEdit:disabled {{
        color: {input_disabled_fg};
        background: {input_disabled_bg};
        border: 1px solid {input_disabled_border};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 28px;
        background: transparent;
    }}

    QComboBox::down-arrow {{
        image: none;
        width: 0px;
        height: 0px;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid {field};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background: {dropdown_bg};
        color: {value};
        border: 1px solid {card_border};
        border-radius: 12px;
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
        outline: none;
        padding: 4px;
    }}

    QPushButton,
    QMessageBox QPushButton {{
        min-height: 18px;
        border-radius: 14px;
        padding: 10px 16px;
        font-size: 12px;
        font-weight: 760;
        outline: none;
        color: {value};
        background: {_qss_vertical_gradient(secondary_top, secondary_bottom)};
        border: 1px solid {secondary_border};
    }}

    QPushButton:hover,
    QMessageBox QPushButton:hover {{
        background: {_qss_vertical_gradient(secondary_hover_top, secondary_hover_bottom)};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="primary"],
    QMessageBox QPushButton[variant="primary"] {{
        color: {selection_fg};
        background: {_qss_vertical_gradient(primary_top, primary_bottom)};
        border: 1px solid {primary_border};
    }}

    QPushButton[variant="primary"]:hover,
    QMessageBox QPushButton[variant="primary"]:hover {{
        background: {_qss_vertical_gradient(primary_hover_top, primary_hover_bottom)};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="secondary"] {{
        color: {value};
        background: {_qss_vertical_gradient(secondary_top, secondary_bottom)};
        border: 1px solid {secondary_border};
    }}

    QPushButton[variant="secondary"]:hover {{
        background: {_qss_vertical_gradient(secondary_hover_top, secondary_hover_bottom)};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="success"] {{
        color: {selection_fg};
        background: {_qss_vertical_gradient(success_top, success_bottom)};
        border: 1px solid {success_border};
    }}

    QPushButton[variant="success"]:hover {{
        background: {_qss_vertical_gradient(success_hover_top, success_hover_bottom)};
        border: 1px solid {good_chip_border};
    }}

    QPushButton[variant="danger"],
    QMessageBox QPushButton[variant="danger"] {{
        color: {value};
        background: {_qss_vertical_gradient(danger_top, danger_bottom)};
        border: 1px solid {danger_border};
    }}

    QPushButton[variant="danger"]:hover,
    QMessageBox QPushButton[variant="danger"]:hover {{
        background: {_qss_vertical_gradient(danger_hover_top, danger_hover_bottom)};
        border: 1px solid {warn_chip_border};
    }}

    QPushButton:disabled,
    QMessageBox QPushButton:disabled {{
        color: {disabled_fg};
        background: {disabled_bg};
        border: 1px solid {disabled_border};
    }}

    QPushButton[chrome="true"] {{
        min-width: 30px;
        max-width: 30px;
        min-height: 22px;
        max-height: 22px;
        border-radius: 8px;
        padding: 0px;
        font-size: 11px;
        font-weight: 760;
        color: {chrome_button_fg};
        background: {chrome_button_bg};
        border: 1px solid {chrome_button_border};
    }}

    QPushButton[chrome="true"]:hover {{
        background: {chrome_button_hover};
        border: 1px solid {input_hover};
    }}

    QPushButton[chrome="true"]:pressed {{
        background: {_with_alpha(t["focus"], 0.28 if dark else 0.22)};
        border: 1px solid {input_focus};
    }}

    QPushButton[chrome="true"][chrome_kind="close"]:hover {{
        background: {chrome_close_hover};
        border: 1px solid {chrome_close_border};
    }}

    QLineEdit[readOnly="true"],
    QLabel[role="mono"] {{
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
    }}

    QFrame[card="hero"] QLabel[role="subtitle"] {{
        color: {subtitle};
    }}

    QFrame[card="muted"] QLabel[role="value"],
    QFrame[card="muted"] QLabel[role="mono"],
    QFrame[card="muted"] QLabel[role="hint"] {{
        color: {mono};
    }}

    QProgressBar {{
        min-height: 18px;
        border-radius: 11px;
        background: {progress_bg};
        border: 1px solid {progress_border};
        text-align: center;
        color: {progress_text};
        font-size: 11px;
        font-weight: 760;
        padding: 2px;
    }}

    QProgressBar::chunk {{
        border-radius: 9px;
        background: {_qss_vertical_gradient(progress_chunk_top, progress_chunk_bottom)};
        margin: 1px;
    }}

    QToolTip {{
        background: {tooltip_bg};
        color: {value};
        border: 1px solid {tooltip_border};
        border-radius: 10px;
        padding: 6px 8px;
    }}
    """.strip()


THEME_BUNDLES: list[ThemeBundle] = collect_theme_bundles()
THEME_REGISTRY: dict[str, ThemeBundle] = build_theme_registry(THEME_BUNDLES)
_THEME_MANIFESTS: tuple[ThemeManifest, ...] = _build_theme_manifests(THEME_BUNDLES)
_THEME_MANIFEST_BY_ID: dict[str, ThemeManifest] = {manifest.id: manifest for manifest in _THEME_MANIFESTS}
_THEME_ALIAS_TO_ID: dict[str, str] = _build_theme_alias_to_id(_THEME_MANIFESTS)
THEME_LABEL_TO_ID: dict[str, str] = {manifest.dropdown_label: manifest.id for manifest in _THEME_MANIFESTS}
THEME_ID_TO_LABEL: dict[str, str] = {manifest.id: manifest.dropdown_label for manifest in _THEME_MANIFESTS}
THEME_DROPDOWN_LABELS: list[str] = [manifest.dropdown_label for manifest in _THEME_MANIFESTS]
DEFAULT_THEME: str = next((manifest.id for manifest in _THEME_MANIFESTS if manifest.is_default), get_default_theme_id(THEME_BUNDLES))
VALID_THEMES: tuple[str, ...] = tuple(THEME_REGISTRY.keys())
_THEME_RENDER_REGISTRY: dict[str, ThemeRenderContract] = _build_render_registry(THEME_BUNDLES, _THEME_MANIFEST_BY_ID)


__all__ = [
    "ThemeBundle",
    "ThemeManifest",
    "ThemeRenderContract",
    "THEME_BUNDLES",
    "THEME_REGISTRY",
    "THEME_LABEL_TO_ID",
    "THEME_ID_TO_LABEL",
    "THEME_DROPDOWN_LABELS",
    "DEFAULT_THEME",
    "VALID_THEMES",
    "normalize_theme",
    "resolve_theme_bundle",
    "resolve_render_theme",
    "build_app_stylesheet",
]

# 10. RENDER SVG
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional
import html


# ----------------------------
# Semantic visual models
# ----------------------------

@dataclass(slots=True)
class NodeVisualPreset:
    fill: str
    stroke: str
    text: str
    subtext: str
    accent: str
    chip_fill: str
    chip_text: str
    badge_in_fill: str
    badge_out_fill: str
    badge_text: str
    glow: str = ""
    glow_opacity: float = 0.0
    fill_opacity: float = 1.0
    stroke_opacity: float = 1.0
    border_width: float = 1.6
    radius: float = 16.0
    shine_opacity: float = 0.10
    text_weight: int = 700
    muted: bool = False
    dim_opacity: float = 1.0
    scale: float = 1.0
    label_size: float = 13.0
    subtitle_size: float = 10.6
    chip_border: str = ""
    chip_border_opacity: float = 0.0
    dasharray: str = ""
    accent_bar: bool = True
    halo: bool = False
    ring: bool = False


@dataclass(slots=True)
class EdgeVisualPreset:
    stroke: str
    marker_fill: str
    width: float
    opacity: float
    glow: str = ""
    glow_opacity: float = 0.0
    glow_width: float = 0.0
    dasharray: str = ""
    curve_bias: float = 0.34
    layer: int = 2
    marker_id: str = "arrow_default"


@dataclass(slots=True)
class LaneVisualPreset:
    fill: str
    stroke: str
    header_fill: str
    header_text: str
    meta_text: str
    accent: str
    fill_opacity: float = 0.34
    stroke_opacity: float = 0.80
    header_fill_opacity: float = 0.95
    radius: float = 18.0
    header_radius: float = 14.0
    border_width: float = 1.0
    accent_opacity: float = 0.20
    label_capsule_fill: str = ""
    label_capsule_text: str = ""


@dataclass(slots=True)
class PanelVisualPreset:
    fill: str
    stroke: str
    title: str
    text: str
    meta: str
    accent: str
    fill_opacity: float = 0.76
    stroke_opacity: float = 0.90
    radius: float = 16.0
    border_width: float = 1.0


@dataclass(slots=True)
class SemanticTheme:
    theme_id: str
    label: str
    tokens: dict[str, Any] = field(default_factory=dict)
    node_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    edge_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    lane_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    panel_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    badge_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    marker_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    effect_presets: dict[str, dict[str, Any]] = field(default_factory=dict)
    svg_defs: str = ""
    is_dark: bool = True
    raw_contract: Any = None


@dataclass(slots=True)
class ResolvedNodeVisual:
    node: DependencyNode
    role: str
    preset: NodeVisualPreset
    x: float
    y: float
    width: float
    height: float
    label: str
    subtitle: str
    chip_label: str
    chip_kind: str
    icon: str
    emphasis: float
    layer: int


@dataclass(slots=True)
class ResolvedEdgeVisual:
    edge: DependencyEdge
    role: str
    preset: EdgeVisualPreset
    path_d: str
    tooltip: str
    layer: int
    emphasis: float
    forensic_id: str = ""
    source_label: str = ""
    target_label: str = ""
    forensic_summary: str = ""
    forensic_evidence: tuple[str, ...] = field(default_factory=tuple)
    overlay_x: float = 0.0
    overlay_y: float = 0.0


@dataclass(slots=True)
class ResolvedLaneVisual:
    lane: LayoutLane
    role: str
    preset: LaneVisualPreset


# ----------------------------
# Basic helpers
# ----------------------------

def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).strip()


def _safe_short(value: Any, limit: int) -> str:
    text = _clean_text(value)
    if len(text) <= limit:
        return text
    if limit <= 1:
        return "…"
    return text[: limit - 1] + "…"


def _text_limit_for_width(
    pixel_width: float,
    font_size: float,
    *,
    min_chars: int = 6,
    max_chars: int = 260,
) -> int:
    usable = max(0.0, float(pixel_width))
    estimated_char_px = max(4.8, float(font_size) * 0.58)
    limit = int(usable / estimated_char_px)
    return max(min_chars, min(max_chars, limit))


def _escape(value: Any) -> str:
    return html.escape(str(value or ""))


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _deep_merge(base: dict[str, Any], extra: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not extra:
        return dict(base)

    result: dict[str, Any] = dict(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _get_bundle_attr(bundle: Any, name: str, default: Any) -> Any:
    if isinstance(bundle, dict):
        value = bundle.get(name, default)
        return default if value is None else value
    try:
        value = getattr(bundle, name)
    except Exception:
        return default
    return default if value is None else value


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _parse_marker_ref(value: Any) -> tuple[str, str]:
    text = _clean_text(value)
    if text.startswith("url(#") and text.endswith(")"):
        svg_id = text[5:-1]
        marker_key = svg_id
        if svg_id == "arrowHead":
            marker_key = "default_arrow"
        elif svg_id == "subtleArrowHead":
            marker_key = "subtle_arrow"
        elif svg_id == "focusArrowHead":
            marker_key = "focus_arrow"
        return marker_key, svg_id
    return ("", "")


def _theme_manifest(source: Any) -> dict[str, Any]:
    manifest = _get_bundle_attr(source, "manifest", {})
    if isinstance(manifest, dict):
        return manifest
    if manifest is None:
        return {}
    result: dict[str, Any] = {}
    for key in ("id", "theme_id", "label", "is_default", "is_dark"):
        try:
            value = getattr(manifest, key)
        except Exception:
            continue
        if value is not None:
            result[key] = value
    return result


def _theme_identity(source: Any, requested_theme_id: str) -> tuple[str, str]:
    manifest = _theme_manifest(source)
    theme_id = (
        _clean_text(manifest.get("theme_id"))
        or _clean_text(manifest.get("id"))
        or _clean_text(_get_bundle_attr(source, "theme_id", ""))
        or _clean_text(_get_bundle_attr(source, "id", ""))
        or _clean_text(requested_theme_id)
        or "dark"
    ).lower()
    label = (
        _clean_text(manifest.get("label"))
        or _clean_text(_get_bundle_attr(source, "label", ""))
        or theme_id.title()
    )
    return theme_id, label


def _color_luminance(value: Any) -> float:
    r, g, b = _hex_to_rgb(str(value or ""))
    return ((0.2126 * r) + (0.7152 * g) + (0.0722 * b)) / 255.0


def _detect_dark_theme(theme_id: str, tokens: dict[str, Any], source: Any) -> bool:
    manifest = _theme_manifest(source)
    if "is_dark" in manifest:
        return bool(manifest["is_dark"])
    direct = _get_bundle_attr(source, "is_dark", None)
    if isinstance(direct, bool):
        return direct

    canvas = (
        _clean_text(tokens.get("canvas_bg", ""))
        or _clean_text(tokens.get("header_fill", ""))
        or _clean_text(tokens.get("legend_fill", ""))
    )
    if canvas:
        return _color_luminance(canvas) < 0.54

    lowered = _clean_text(theme_id).lower()
    return lowered not in {"light", "paper", "white"}


def _flatten_family_tokens(
    source: Any,
    theme_id: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    direct_tokens = _mapping(_get_bundle_attr(source, "tokens", {}))
    families = {
        "surfaces": _mapping(direct_tokens.get("surfaces")),
        "text": _mapping(direct_tokens.get("text")),
        "accents": _mapping(direct_tokens.get("accents")),
        "borders": _mapping(direct_tokens.get("borders")),
        "ambient": _mapping(direct_tokens.get("ambient")),
    }

    surfaces = families["surfaces"]
    text = families["text"]
    accents = families["accents"]
    borders = families["borders"]
    ambient = families["ambient"]

    canvas_bg = (
        surfaces.get("canvas_mid")
        or surfaces.get("canvas_start")
        or surfaces.get("panel_soft")
        or surfaces.get("panel")
        or "#07101c"
    )
    dark_guess = _clean_text(theme_id).lower() not in {"light", "paper", "white"}

    flat = {
        "canvas_bg": canvas_bg,
        "canvas_grid": ambient.get("grid", accents.get("primary", "#6ea8ff")),
        "canvas_grid_opacity": ambient.get("grid_opacity", 0.08),
        "grid_size": ambient.get("grid_size", 28),
        "grid_stroke_width": ambient.get("grid_stroke_width", 0.9),
        "halo_a": ambient.get("halo_a_color", accents.get("primary", "#22d3ee")),
        "halo_a_opacity": ambient.get("halo_a_opacity", 0.18 if dark_guess else 0.10),
        "halo_b": ambient.get("halo_b_color", accents.get("tertiary", "#8b5cf6")),
        "halo_b_opacity": ambient.get("halo_b_opacity", 0.13 if dark_guess else 0.08),
        "header_fill": surfaces.get("header_band", surfaces.get("panel", "#0a1426")),
        "header_stroke": borders.get("panel", borders.get("strong", "#223556")),
        "header_title": text.get("title", text.get("body", "#f5fbff")),
        "header_text": text.get("body", text.get("muted", "#b8c8df")),
        "header_meta": text.get("muted", text.get("soft", "#8fa4c2")),
        "footer_text": text.get("soft", text.get("muted", "#8ba0bd")),
        "legend_fill": surfaces.get("legend_panel", surfaces.get("panel", "#0c1424")),
        "legend_stroke": borders.get("panel", borders.get("lane", "#223556")),
        "shadow": ambient.get("shadow", "#020617"),
        "focus": accents.get("focus", accents.get("primary", "#7dd3fc")),
        "focus_warm": accents.get("tertiary", accents.get("secondary", "#c084fc")),
        "package_fill": surfaces.get("node_package_start", surfaces.get("panel_alt", "#0f2238")),
        "package_fill_alt": surfaces.get("node_package_end", surfaces.get("panel", "#102c52")),
        "package_stroke": borders.get("node_package", borders.get("strong", "#67b5ff")),
        "package_accent": accents.get("primary", borders.get("node_package", "#8ed1ff")),
        "module_fill": surfaces.get("node_module_start", surfaces.get("panel_soft", "#0d1d18")),
        "module_fill_alt": surfaces.get("node_module_end", surfaces.get("panel", "#08271c")),
        "module_stroke": borders.get("node_module", accents.get("success", "#4fd89a")),
        "module_accent": accents.get("success", borders.get("node_module", "#7cfcc0")),
        "external_fill": surfaces.get("node_external_start", surfaces.get("panel_alt", "#211a34")),
        "external_fill_alt": surfaces.get("node_external_end", surfaces.get("panel", "#25173f")),
        "external_stroke": borders.get("node_external", accents.get("tertiary", "#c39cff")),
        "external_accent": accents.get("tertiary", borders.get("node_external", "#ddc0ff")),
        "note_fill": surfaces.get("node_note_start", surfaces.get("warning_panel", "#2e2512")),
        "note_fill_alt": surfaces.get("node_note_end", surfaces.get("warning_panel", "#3b2408")),
        "note_stroke": borders.get("node_note", accents.get("warning", "#f5c76a")),
        "note_accent": accents.get("warning", borders.get("warning", "#ffe29a")),
        "muted_fill": surfaces.get("node_context_muted_start", surfaces.get("panel_soft", "#101823")),
        "muted_fill_alt": surfaces.get("node_context_muted_end", surfaces.get("panel", "#121a29")),
        "muted_stroke": borders.get("muted", "#5a6c87"),
        "muted_text": text.get("muted", text.get("soft", "#97a9c0")),
        "muted_subtext": text.get("soft", text.get("muted", "#70839c")),
        "text_main": text.get("body", text.get("title", "#edf5ff")),
        "text_soft": text.get("soft", text.get("muted", "#9cb2cf")),
        "chip_dark": surfaces.get("panel_soft", canvas_bg),
        "chip_light": text.get("badge_light", "#ffffff"),
        "badge_in": accents.get("primary", "#6ec8ff"),
        "badge_out": accents.get("success", "#6fe0a2"),
        "badge_hub": accents.get("hub", accents.get("warning", "#f59e0b")),
        "badge_island": accents.get("danger", "#ef4444"),
        "badge_text_dark": text.get("badge_dark", "#07101c"),
        "badge_text_light": text.get("badge_light", "#ffffff"),
        "lane_fill": surfaces.get("panel_soft", surfaces.get("panel", "#0a1324")),
        "lane_stroke": borders.get("lane", borders.get("panel", "#213552")),
        "lane_header_fill": surfaces.get("lane_header_start", surfaces.get("header_band", "#0f1a2e")),
        "lane_header_fill_alt": surfaces.get("lane_header_end", surfaces.get("panel_alt", "#13213a")),
        "lane_header_text": text.get("body", text.get("title", "#eaf2ff")),
        "lane_meta_text": text.get("soft", text.get("muted", "#8ca2bf")),
        "warning_fill": surfaces.get("warning_panel", "#2b1b0a"),
        "warning_stroke": borders.get("warning", accents.get("warning", "#f4b85d")),
        "warning_text": text.get("warning", accents.get("warning", "#ffdba6")),
        "footer_fill": surfaces.get("panel", surfaces.get("panel_soft", "#0a1322")),
        "footer_stroke": borders.get("panel", borders.get("lane", "#20324e")),
    }
    return flat, families


def _theme_effects(source: Any) -> dict[str, dict[str, Any]]:
    effects = _mapping(_get_bundle_attr(source, "effect_presets", {}))
    return {
        "glow_intensity": _mapping(effects.get("glow_intensity")),
        "shadow_intensity": _mapping(effects.get("shadow_intensity")),
        "border_emphasis": _mapping(effects.get("border_emphasis")),
        "shine_intensity": _mapping(effects.get("shine_intensity")),
    }


def _theme_badges(source: Any, tokens: dict[str, Any]) -> dict[str, dict[str, Any]]:
    badges = _mapping(_get_bundle_attr(source, "badge_presets", {}))

    badge_in = tokens.get("badge_in") or tokens.get("focus") or "#6ec8ff"
    badge_out = tokens.get("badge_out") or tokens.get("focus_warm") or "#6fe0a2"
    badge_hub = (
        tokens.get("badge_hub")
        or tokens.get("warning_stroke")
        or tokens.get("focus")
        or "#f59e0b"
    )
    badge_island = tokens.get("badge_island") or tokens.get("note_stroke") or "#ef4444"
    badge_text_dark = tokens.get("badge_text_dark") or tokens.get("text_main") or "#07101c"
    badge_text_light = tokens.get("badge_text_light") or tokens.get("chip_light") or "#ffffff"

    resolved: dict[str, dict[str, Any]] = {
        "inbound": {
            "fill": badge_in,
            "text_fill": badge_text_dark,
        },
        "outbound": {
            "fill": badge_out,
            "text_fill": badge_text_dark,
        },
        "hub": {
            "fill": badge_hub,
            "text_fill": badge_text_light,
        },
        "island": {
            "fill": badge_island,
            "text_fill": badge_text_light,
        },
    }

    for key, value in badges.items():
        if not isinstance(value, dict):
            continue

        current = dict(resolved.get(key, {}))
        fill = value.get("fill", current.get("fill", badge_in))
        text_fill = value.get("text_fill", current.get("text_fill", badge_text_dark))

        resolved[key] = {
            "fill": fill,
            "text_fill": text_fill,
        }

    return resolved
def _theme_markers(source: Any, tokens: dict[str, Any], effects: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    markers = _mapping(_get_bundle_attr(source, "marker_presets", {}))
    glow_base = _num(effects["glow_intensity"].get("edge", 0.10), 0.10)
    glow_focus = _num(effects["glow_intensity"].get("focus", 0.22), 0.22)

    defaults: dict[str, dict[str, Any]] = {
        "default_arrow": {
            "svg_id": "arrow_default",
            "fill": tokens["focus"],
            "opacity": min(1.0, 0.85 + glow_base),
            "marker_width": 12,
            "marker_height": 12,
            "ref_x": 10,
            "ref_y": 6,
        },
        "subtle_arrow": {
            "svg_id": "arrow_muted",
            "fill": tokens["muted_text"],
            "opacity": 0.78,
            "marker_width": 11,
            "marker_height": 11,
            "ref_x": 9,
            "ref_y": 5.5,
        },
        "focus_arrow": {
            "svg_id": "arrow_focus_in",
            "fill": tokens["focus"],
            "opacity": min(1.0, 0.88 + (glow_focus * 0.4)),
            "marker_width": 14,
            "marker_height": 14,
            "ref_x": 11.5,
            "ref_y": 7,
        },
    }

    resolved = {key: dict(value) for key, value in defaults.items()}
    for key, value in markers.items():
        if not isinstance(value, dict):
            continue
        current = dict(resolved.get(key, {}))
        current.update(value)
        current["svg_id"] = _clean_text(current.get("svg_id")) or current.get("id") or defaults.get(key, {}).get("svg_id", key)
        current["fill"] = _clean_text(current.get("fill")) or defaults.get(key, {}).get("fill", tokens["focus"])
        current["opacity"] = _num(current.get("opacity", defaults.get(key, {}).get("opacity", 0.9)), 0.9)
        current["marker_width"] = _num(current.get("marker_width", defaults.get(key, {}).get("marker_width", 12)), 12)
        current["marker_height"] = _num(current.get("marker_height", defaults.get(key, {}).get("marker_height", 12)), 12)
        current["ref_x"] = _num(current.get("ref_x", defaults.get(key, {}).get("ref_x", 10)), 10)
        current["ref_y"] = _num(current.get("ref_y", defaults.get(key, {}).get("ref_y", 6)), 6)
        resolved[key] = current

    if "focus_arrow" in resolved and "arrow_focus_out" not in {resolved["focus_arrow"]["svg_id"], resolved["default_arrow"]["svg_id"]}:
        focus_marker = dict(resolved["focus_arrow"])
        focus_marker["svg_id"] = "arrow_focus_out"
        resolved["focus_arrow_out"] = focus_marker

    return resolved


def _base_node_presets(tokens: dict[str, Any], effects: dict[str, dict[str, Any]], dark: bool) -> dict[str, dict[str, Any]]:
    border_std = max(1.35, 1.55 * _num(effects["border_emphasis"].get("standard", 1.0), 1.0))
    border_strong = max(border_std, 1.55 * _num(effects["border_emphasis"].get("strong", 1.25), 1.25))
    border_focus = max(border_strong, 1.55 * _num(effects["border_emphasis"].get("focus", 1.52), 1.52))
    border_hub = max(border_strong, 1.55 * _num(effects["border_emphasis"].get("hub", 1.35), 1.35))
    shine_std = _num(effects["shine_intensity"].get("standard", 0.10), 0.10)
    shine_focus = _num(effects["shine_intensity"].get("focus", 0.16), 0.16)

    def node(
        *,
        fill: str,
        stroke: str,
        accent: str,
        glow_opacity: float,
        border_width: float,
        shine_opacity: float,
        text: str | None = None,
        subtext: str | None = None,
        chip_fill: str | None = None,
        chip_text: str | None = None,
        badge_in_fill: str | None = None,
        badge_out_fill: str | None = None,
        badge_text: str | None = None,
        radius: float = 16.0,
        scale: float = 1.0,
        label_size: float = 13.0,
        subtitle_size: float = 10.6,
        muted: bool = False,
        dim_opacity: float = 1.0,
        dasharray: str = "",
        accent_bar: bool = True,
        halo: bool = False,
        ring: bool = False,
    ) -> dict[str, Any]:
        fill_base = tokens["canvas_bg"] if dark else tokens["chip_light"]
        chip = chip_fill or _mix_hex(stroke, fill_base, 0.26 if dark else 0.12)
        return {
            "fill": fill,
            "stroke": stroke,
            "text": text or tokens["text_main"],
            "subtext": subtext or tokens["text_soft"],
            "accent": accent,
            "chip_fill": chip,
            "chip_text": chip_text or (tokens["header_title"] if not muted else tokens["muted_text"]),
            "badge_in_fill": badge_in_fill or tokens["badge_in"],
            "badge_out_fill": badge_out_fill or tokens["badge_out"],
            "badge_text": badge_text or tokens["badge_text_dark"],
            "glow": accent or stroke,
            "glow_opacity": glow_opacity,
            "fill_opacity": 0.90 if muted else 1.0,
            "stroke_opacity": 0.92 if muted else 1.0,
            "border_width": border_width,
            "radius": radius,
            "shine_opacity": shine_opacity,
            "text_weight": 700,
            "muted": muted,
            "dim_opacity": dim_opacity,
            "scale": scale,
            "label_size": label_size,
            "subtitle_size": subtitle_size,
            "chip_border": stroke,
            "chip_border_opacity": 0.12 if (muted or halo or ring) else 0.0,
            "dasharray": dasharray,
            "accent_bar": accent_bar,
            "halo": halo,
            "ring": ring,
        }

    return {
        "package": node(
            fill=tokens["package_fill"],
            stroke=tokens["package_stroke"],
            accent=tokens["package_accent"],
            glow_opacity=0.14 if dark else 0.06,
            border_width=border_std,
            shine_opacity=shine_std,
        ),
        "module": node(
            fill=tokens["module_fill"],
            stroke=tokens["module_stroke"],
            accent=tokens["module_accent"],
            glow_opacity=0.10 if dark else 0.05,
            border_width=border_std,
            shine_opacity=shine_std,
            radius=14.0,
        ),
        "external": node(
            fill=tokens["external_fill"],
            stroke=tokens["external_stroke"],
            accent=tokens["external_accent"],
            glow_opacity=0.09 if dark else 0.05,
            border_width=border_std,
            shine_opacity=shine_std,
            dasharray="7 5",
        ),
        "note": node(
            fill=tokens["note_fill"],
            stroke=tokens["note_stroke"],
            accent=tokens["note_accent"],
            glow_opacity=0.08 if dark else 0.04,
            border_width=border_std,
            shine_opacity=max(0.05, shine_std * 0.9),
            accent_bar=False,
            label_size=12.8,
            subtitle_size=10.4,
        ),
        "focus_hero": node(
            fill=_mix_hex(tokens["package_fill"], tokens["focus"], 0.18 if dark else 0.16),
            stroke=tokens["focus"],
            accent=_mix_hex(tokens["focus"], tokens["focus_warm"], 0.22),
            glow_opacity=0.24 if dark else 0.11,
            border_width=border_focus,
            shine_opacity=shine_focus,
            scale=1.12,
            label_size=14.2,
            subtitle_size=10.8,
            halo=True,
            ring=True,
        ),
        "focus_inbound": node(
            fill=_mix_hex(tokens["module_fill"], tokens["focus"], 0.12 if dark else 0.10),
            stroke=tokens["focus"],
            accent=tokens["focus"],
            glow_opacity=0.14 if dark else 0.07,
            border_width=border_strong,
            shine_opacity=shine_std,
        ),
        "focus_outbound": node(
            fill=_mix_hex(tokens["module_fill"], tokens["focus_warm"], 0.10 if dark else 0.09),
            stroke=_mix_hex(tokens["focus"], tokens["focus_warm"], 0.44),
            accent=_mix_hex(tokens["focus"], tokens["focus_warm"], 0.44),
            glow_opacity=0.14 if dark else 0.07,
            border_width=border_strong,
            shine_opacity=shine_std,
        ),
        "focus_mixed": node(
            fill=_mix_hex(tokens["external_fill"], tokens["focus"], 0.10 if dark else 0.09),
            stroke=tokens["focus_warm"],
            accent=tokens["focus_warm"],
            glow_opacity=0.14 if dark else 0.07,
            border_width=border_strong,
            shine_opacity=shine_std,
        ),
        "context_muted": node(
            fill=tokens["muted_fill"],
            stroke=tokens["muted_stroke"],
            accent=tokens["muted_stroke"],
            glow_opacity=0.02 if dark else 0.01,
            border_width=border_std,
            shine_opacity=max(0.04, shine_std * 0.6),
            text=tokens["muted_text"],
            subtext=tokens["muted_subtext"],
            muted=True,
            dim_opacity=0.82,
            accent_bar=False,
        ),
           "hub_accent": node(
            fill=_mix_hex(
                tokens["package_fill"],
                tokens.get("badge_hub") or tokens.get("warning_stroke") or tokens.get("focus") or "#f59e0b",
                0.16 if dark else 0.12,
            ),
            stroke=tokens.get("badge_hub") or tokens.get("warning_stroke") or tokens.get("focus") or "#f59e0b",
            accent=tokens.get("badge_hub") or tokens.get("warning_stroke") or tokens.get("focus") or "#f59e0b",
            glow_opacity=0.16 if dark else 0.08,
            border_width=border_hub,
            shine_opacity=shine_focus,
            halo=True,
        ),
    }


def _base_edge_presets(tokens: dict[str, Any], effects: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    glow_base = _num(effects["glow_intensity"].get("edge", 0.10), 0.10)
    glow_focus = _num(effects["glow_intensity"].get("focus", 0.22), 0.22)
    return {
        "default": {
            "stroke": tokens["focus"],
            "marker_fill": tokens["focus"],
            "width": 1.8,
            "opacity": 0.68,
            "glow": tokens["focus"],
            "glow_opacity": glow_base,
            "glow_width": 7.2,
            "dasharray": "",
            "curve_bias": 0.34,
            "layer": 2,
            "marker_id": "arrow_default",
        },
        "muted": {
            "stroke": tokens["muted_text"],
            "marker_fill": tokens["muted_text"],
            "width": 1.35,
            "opacity": 0.34,
            "glow": tokens["muted_text"],
            "glow_opacity": max(0.04, glow_base * 0.65),
            "glow_width": 4.8,
            "dasharray": "7 5",
            "curve_bias": 0.30,
            "layer": 1,
            "marker_id": "arrow_muted",
        },
        "focus_inbound": {
            "stroke": _mix_hex(tokens["focus"], tokens["package_stroke"], 0.28),
            "marker_fill": tokens["focus"],
            "width": 2.05,
            "opacity": 0.82,
            "glow": tokens["focus"],
            "glow_opacity": glow_focus,
            "glow_width": 8.2,
            "dasharray": "",
            "curve_bias": 0.36,
            "layer": 2,
            "marker_id": "arrow_focus_in",
        },
        "focus_outbound": {
            "stroke": tokens["badge_out"],
            "marker_fill": tokens["badge_out"],
            "width": 2.05,
            "opacity": 0.82,
            "glow": tokens["badge_out"],
            "glow_opacity": glow_focus,
            "glow_width": 8.2,
            "dasharray": "",
            "curve_bias": 0.36,
            "layer": 2,
            "marker_id": "arrow_focus_out",
        },
        "self_loop": {
            "stroke": tokens["note_accent"],
            "marker_fill": tokens["note_accent"],
            "width": 1.95,
            "opacity": 0.74,
            "glow": tokens["note_accent"],
            "glow_opacity": max(0.06, glow_focus * 0.85),
            "glow_width": 7.6,
            "dasharray": "",
            "curve_bias": 0.42,
            "layer": 2,
            "marker_id": "arrow_default",
        },
        "cross_lane": {
            "stroke": tokens["focus"],
            "marker_fill": tokens["focus"],
            "width": 1.9,
            "opacity": 0.74,
            "glow": tokens["focus"],
            "glow_opacity": glow_base,
            "glow_width": 7.4,
            "dasharray": "",
            "curve_bias": 0.34,
            "layer": 2,
            "marker_id": "arrow_default",
        },
        "intra_lane": {
            "stroke": tokens["muted_text"],
            "marker_fill": tokens["muted_text"],
            "width": 1.55,
            "opacity": 0.54,
            "glow": tokens["muted_text"],
            "glow_opacity": max(0.04, glow_base * 0.75),
            "glow_width": 5.6,
            "dasharray": "5 4",
            "curve_bias": 0.26,
            "layer": 1,
            "marker_id": "arrow_muted",
        },
    }


def _base_lane_presets(tokens: dict[str, Any], dark: bool) -> dict[str, dict[str, Any]]:
    return {
        "default": {
            "fill": tokens["lane_fill"],
            "stroke": tokens["lane_stroke"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["lane_header_fill_alt"], 0.30),
            "header_text": tokens["lane_header_text"],
            "meta_text": tokens["lane_meta_text"],
            "accent": tokens["focus"],
            "fill_opacity": 0.34 if dark else 0.78,
            "stroke_opacity": 0.80,
            "header_fill_opacity": 0.95,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.0,
            "accent_opacity": 0.18 if dark else 0.08,
        },
        "focus_center_lane": {
            "fill": _mix_hex(tokens["lane_fill"], tokens["focus"], 0.08 if dark else 0.06),
            "stroke": tokens["focus"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["focus"], 0.12 if dark else 0.08),
            "header_text": tokens["header_title"],
            "meta_text": tokens["focus"],
            "accent": tokens["focus"],
            "fill_opacity": 0.42 if dark else 0.84,
            "stroke_opacity": 0.92,
            "header_fill_opacity": 0.98,
            "radius": 20.0,
            "header_radius": 15.0,
            "border_width": 1.35,
            "accent_opacity": 0.24 if dark else 0.10,
            "label_capsule_fill": _mix_hex(tokens["focus"], tokens["chip_dark"] if dark else tokens["chip_light"], 0.18),
            "label_capsule_text": tokens["header_title"],
        },
        "side_lane": {
            "fill": tokens["lane_fill"],
            "stroke": tokens["lane_stroke"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["lane_header_fill_alt"], 0.24),
            "header_text": tokens["lane_header_text"],
            "meta_text": tokens["lane_meta_text"],
            "accent": tokens["module_accent"],
            "fill_opacity": 0.28 if dark else 0.72,
            "stroke_opacity": 0.74,
            "header_fill_opacity": 0.92,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.0,
            "accent_opacity": 0.12 if dark else 0.06,
        },
        "issue_lane": {
            "fill": _mix_hex(tokens["lane_fill"], tokens["warning_fill"], 0.18 if dark else 0.12),
            "stroke": tokens["warning_stroke"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["warning_fill"], 0.22 if dark else 0.14),
            "header_text": tokens["warning_text"] if not dark else tokens["header_title"],
            "meta_text": tokens["warning_text"],
            "accent": tokens["note_accent"],
            "fill_opacity": 0.36 if dark else 0.84,
            "stroke_opacity": 0.80,
            "header_fill_opacity": 0.96,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.08,
            "accent_opacity": 0.18 if dark else 0.09,
        },
        "external_lane": {
            "fill": _mix_hex(tokens["lane_fill"], tokens["external_fill"], 0.20 if dark else 0.10),
            "stroke": tokens["external_stroke"],
            "header_fill": _mix_hex(tokens["lane_header_fill"], tokens["external_fill"], 0.24 if dark else 0.12),
            "header_text": tokens["header_title"],
            "meta_text": tokens["header_text"],
            "accent": tokens["external_accent"],
            "fill_opacity": 0.34 if dark else 0.78,
            "stroke_opacity": 0.76,
            "header_fill_opacity": 0.95,
            "radius": 18.0,
            "header_radius": 14.0,
            "border_width": 1.05,
            "accent_opacity": 0.16 if dark else 0.08,
        },
    }


def _base_panel_presets(tokens: dict[str, Any], dark: bool) -> dict[str, dict[str, Any]]:
    return {
        "header": {
            "fill": tokens["header_fill"],
            "stroke": tokens["header_stroke"],
            "title": tokens["header_title"],
            "text": tokens["header_text"],
            "meta": tokens["header_meta"],
            "accent": tokens["focus"],
            "fill_opacity": 0.74 if dark else 0.90,
            "stroke_opacity": 0.90,
            "radius": 18.0,
            "border_width": 1.0,
        },
        "legend": {
            "fill": tokens["legend_fill"],
            "stroke": tokens["legend_stroke"],
            "title": tokens["header_title"],
            "text": tokens["header_text"],
            "meta": tokens["header_meta"],
            "accent": tokens["focus"],
            "fill_opacity": 0.76 if dark else 0.92,
            "stroke_opacity": 0.92,
            "radius": 16.0,
            "border_width": 1.0,
        },
        "warning": {
            "fill": tokens["warning_fill"],
            "stroke": tokens["warning_stroke"],
            "title": tokens["warning_text"],
            "text": tokens["warning_text"],
            "meta": tokens["warning_text"],
            "accent": tokens["note_accent"],
            "fill_opacity": 0.94 if dark else 0.96,
            "stroke_opacity": 0.96,
            "radius": 14.0,
            "border_width": 1.05,
        },
        "footer": {
            "fill": tokens["footer_fill"],
            "stroke": tokens["footer_stroke"],
            "title": tokens["footer_text"],
            "text": tokens["footer_text"],
            "meta": tokens["footer_text"],
            "accent": tokens["focus"],
            "fill_opacity": 0.46 if dark else 0.82,
            "stroke_opacity": 0.72,
            "radius": 12.0,
            "border_width": 1.0,
        },
    }


def _coerce_node_presets(
    source: Any,
    tokens: dict[str, Any],
    effects: dict[str, dict[str, Any]],
    badges: dict[str, dict[str, Any]],
    dark: bool,
) -> dict[str, dict[str, Any]]:
    presets = _mapping(_get_bundle_attr(source, "node_presets", {}))
    resolved: dict[str, dict[str, Any]] = {}

    for key, value in presets.items():
        if not isinstance(value, dict):
            continue
        data = dict(value)
        fill = _clean_text(data.get("fill"))
        gradient_id = _clean_text(data.get("gradient_id"))
        if not fill and gradient_id:
            fill = f"url(#{gradient_id})"

        stroke = _clean_text(data.get("stroke")) or tokens.get(f"{key}_stroke", tokens["focus"])
        semantic_role = _clean_text(data.get("semantic_role", key)) or key
        emphasis = _clean_text(data.get("emphasis", semantic_role))
        muted = semantic_role == "context_muted" or emphasis == "muted"

        chip_base = tokens["chip_dark"] if dark else tokens["chip_light"]
        chip_fill = _clean_text(data.get("chip_fill")) or _mix_hex(stroke, chip_base, 0.24 if dark else 0.12)
        chip_text = _clean_text(data.get("chip_text")) or (tokens["header_title"] if not muted else tokens["muted_text"])
        badge_text = (
            _clean_text(data.get("badge_text"))
            or badges.get("inbound", {}).get("text_fill")
            or tokens["badge_text_dark"]
        )
        glow_opacity = _num(
            data.get(
                "glow_opacity",
                0.24 if semantic_role == "focus_hero" else 0.14 if semantic_role.startswith("focus_") else 0.08,
            ),
            0.08,
        )

        resolved[key] = {
            "fill": fill or _mix_hex(tokens["canvas_bg"], stroke, 0.14 if dark else 0.08),
            "stroke": stroke,
            "text": _clean_text(data.get("text")) or _clean_text(data.get("label_fill")) or tokens["text_main"],
            "subtext": _clean_text(data.get("subtext")) or _clean_text(data.get("subtitle_fill")) or tokens["text_soft"],
            "accent": _clean_text(data.get("accent")) or stroke,
            "chip_fill": chip_fill,
            "chip_text": chip_text,
            "badge_in_fill": _clean_text(data.get("badge_in_fill")) or badges.get("inbound", {}).get("fill", tokens["badge_in"]),
            "badge_out_fill": _clean_text(data.get("badge_out_fill")) or badges.get("outbound", {}).get("fill", tokens["badge_out"]),
            "badge_text": badge_text,
            "glow": _clean_text(data.get("glow")) or stroke,
            "glow_opacity": glow_opacity,
            "fill_opacity": _num(data.get("fill_opacity", 0.90 if muted else 1.0), 1.0),
            "stroke_opacity": _num(data.get("stroke_opacity", 0.92 if muted else 1.0), 1.0),
            "border_width": _num(data.get("border_width", 1.6), 1.6),
            "radius": _num(data.get("radius", 16.0), 16.0),
            "shine_opacity": _num(data.get("shine_opacity", effects["shine_intensity"].get("standard", 0.10)), 0.10),
            "text_weight": _int(data.get("text_weight", 700), 700),
            "muted": muted or bool(data.get("muted", False)),
            "dim_opacity": _num(data.get("dim_opacity", 0.82 if muted else 1.0), 1.0),
            "scale": _num(data.get("scale", 1.12 if semantic_role == "focus_hero" else 1.0), 1.0),
            "label_size": _num(data.get("label_size", 14.2 if semantic_role == "focus_hero" else 13.0), 13.0),
            "subtitle_size": _num(data.get("subtitle_size", 10.8 if semantic_role == "focus_hero" else 10.6), 10.6),
            "chip_border": _clean_text(data.get("chip_border")) or stroke,
            "chip_border_opacity": _num(data.get("chip_border_opacity", 0.12 if muted else 0.0), 0.0),
            "dasharray": _clean_text(data.get("dasharray")) or ("7 5" if semantic_role == "external" else ""),
            "accent_bar": bool(data.get("accent_bar", semantic_role != "note" and semantic_role != "context_muted")),
            "halo": bool(data.get("halo", semantic_role in {"focus_hero", "hub_accent"})),
            "ring": bool(data.get("ring", semantic_role == "focus_hero")),
        }

    return resolved


def _coerce_edge_presets(
    source: Any,
    tokens: dict[str, Any],
    markers: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    presets = _mapping(_get_bundle_attr(source, "edge_presets", {}))
    resolved: dict[str, dict[str, Any]] = {}

    for key, value in presets.items():
        if not isinstance(value, dict):
            continue
        data = dict(value)
        marker_key = _clean_text(data.get("marker_key"))
        marker_svg_id = _clean_text(data.get("marker_id"))
        parsed_key, parsed_svg_id = _parse_marker_ref(data.get("marker"))
        if not marker_key:
            marker_key = parsed_key
        if not marker_svg_id:
            marker_svg_id = parsed_svg_id

        marker = markers.get(marker_key) or {}
        stroke = _clean_text(data.get("stroke")) or tokens["focus"]
        marker_fill = _clean_text(data.get("marker_fill")) or _clean_text(marker.get("fill")) or stroke

        resolved[key] = {
            "stroke": stroke,
            "marker_fill": marker_fill,
            "width": _num(data.get("width", data.get("base_width", 1.7)), 1.7),
            "opacity": _num(data.get("opacity", 0.56), 0.56),
            "glow": _clean_text(data.get("glow")) or stroke,
            "glow_opacity": _num(data.get("glow_opacity", 0.0), 0.0),
            "glow_width": _num(data.get("glow_width", 6.0), 6.0),
            "dasharray": _clean_text(data.get("dasharray")),
            "curve_bias": _num(data.get("curve_bias", 0.34), 0.34),
            "layer": _int(data.get("layer", 2), 2),
            "marker_id": marker_svg_id or _clean_text(marker.get("svg_id")) or "arrow_default",
        }

    return resolved


def _coerce_lane_presets(
    source: Any,
    tokens: dict[str, Any],
    dark: bool,
) -> dict[str, dict[str, Any]]:
    presets = _mapping(_get_bundle_attr(source, "lane_presets", {}))
    resolved: dict[str, dict[str, Any]] = {}
    for key, value in presets.items():
        if not isinstance(value, dict):
            continue
        data = dict(value)
        accent = (
            _clean_text(data.get("accent"))
            or _clean_text(data.get("band_stroke"))
            or tokens["focus"]
        )
        resolved[key] = {
            "fill": _clean_text(data.get("fill")) or _clean_text(data.get("band_fill")) or tokens["lane_fill"],
            "stroke": _clean_text(data.get("stroke")) or _clean_text(data.get("band_stroke")) or tokens["lane_stroke"],
            "header_fill": _clean_text(data.get("header_fill")) or _mix_hex(tokens["lane_header_fill"], tokens["lane_header_fill_alt"], 0.24),
            "header_text": _clean_text(data.get("header_text")) or _clean_text(data.get("title_fill")) or tokens["lane_header_text"],
            "meta_text": _clean_text(data.get("meta_text")) or _clean_text(data.get("meta_fill")) or tokens["lane_meta_text"],
            "accent": accent,
            "fill_opacity": _num(data.get("fill_opacity", data.get("band_opacity", 0.34 if dark else 0.78)), 0.34),
            "stroke_opacity": _num(data.get("stroke_opacity", 0.80), 0.80),
            "header_fill_opacity": _num(data.get("header_fill_opacity", 0.95), 0.95),
            "radius": _num(data.get("radius", 18.0), 18.0),
            "header_radius": _num(data.get("header_radius", 14.0), 14.0),
            "border_width": _num(data.get("border_width", 1.0), 1.0),
            "accent_opacity": _num(data.get("accent_opacity", 0.20 if dark else 0.08), 0.20),
            "label_capsule_fill": _clean_text(data.get("label_capsule_fill")),
            "label_capsule_text": _clean_text(data.get("label_capsule_text")),
        }
    return resolved


def _coerce_panel_presets(
    source: Any,
    tokens: dict[str, Any],
    dark: bool,
) -> dict[str, dict[str, Any]]:
    presets = _mapping(_get_bundle_attr(source, "panel_presets", {}))
    resolved: dict[str, dict[str, Any]] = {}
    for key, value in presets.items():
        if not isinstance(value, dict):
            continue
        data = dict(value)
        text_fill = _clean_text(data.get("text")) or _clean_text(data.get("title")) or _clean_text(data.get("text_fill"))
        meta_fill = _clean_text(data.get("meta")) or _clean_text(data.get("meta_fill")) or tokens["header_meta"]
        accent = _clean_text(data.get("accent")) or _clean_text(data.get("glow")) or tokens["focus"]
        resolved[key] = {
            "fill": _clean_text(data.get("fill")) or tokens["legend_fill"],
            "stroke": _clean_text(data.get("stroke")) or tokens["legend_stroke"],
            "title": text_fill or tokens["header_title"],
            "text": _clean_text(data.get("text")) or text_fill or tokens["header_text"],
            "meta": meta_fill,
            "accent": accent,
            "fill_opacity": _num(data.get("fill_opacity", 0.76 if dark else 0.92), 0.76),
            "stroke_opacity": _num(data.get("stroke_opacity", 0.90), 0.90),
            "radius": _num(data.get("radius", 16.0), 16.0),
            "border_width": _num(data.get("border_width", 1.0), 1.0),
        }
    return resolved


def _resolve_semantic_theme(source: Any, requested_theme_id: str) -> SemanticTheme:
    theme_id, label = _theme_identity(source, requested_theme_id)
    tokens, token_families = _flatten_family_tokens(source, theme_id)
    dark = _detect_dark_theme(theme_id, tokens, source)
    effects = _theme_effects(source)
    badges = _theme_badges(source, tokens)
    markers = _theme_markers(source, tokens, effects)

    base_node_presets = _base_node_presets(tokens, effects, dark)
    base_edge_presets = _base_edge_presets(tokens, effects)
    base_lane_presets = _base_lane_presets(tokens, dark)
    base_panel_presets = _base_panel_presets(tokens, dark)

    node_presets = _deep_merge(base_node_presets, _coerce_node_presets(source, tokens, effects, badges, dark))
    edge_presets = _deep_merge(base_edge_presets, _coerce_edge_presets(source, tokens, markers))
    lane_presets = _deep_merge(base_lane_presets, _coerce_lane_presets(source, tokens, dark))
    panel_presets = _deep_merge(base_panel_presets, _coerce_panel_presets(source, tokens, dark))

    svg_defs = str(_get_bundle_attr(source, "svg_defs", ""))

    semantic = SemanticTheme(
        theme_id=theme_id,
        label=label,
        tokens=tokens,
        node_presets=node_presets,
        edge_presets=edge_presets,
        lane_presets=lane_presets,
        panel_presets=panel_presets,
        badge_presets=badges,
        marker_presets=markers,
        effect_presets=effects,
        svg_defs=svg_defs,
        is_dark=dark,
        raw_contract=source,
    )
    return semantic


# ----------------------------
# Semantic role resolution
# ----------------------------

def _find_focus_key(graph: DependencyGraph, layout: LayoutResult, state: AnalysisState) -> str:
    explicit = _clean_text(state.focus_target)
    if explicit:
        direct = [explicit, f"module:{explicit}", f"package:{explicit}"]
        for key in direct:
            if key in graph.nodes:
                return key
        for node in graph.nodes.values():
            module_name = _clean_text(node.metadata.get("module_name", ""))
            root_group = _clean_text(node.metadata.get("root_group", ""))
            if explicit in {node.key, node.label, module_name, root_group}:
                return node.key

    for node in layout.nodes:
        lane_key = _clean_text(node.metadata.get("layout_lane_key", ""))
        if lane_key == "lane:focus:center":
            return node.key

    ranked = sorted(
        graph.nodes.values(),
        key=lambda n: (
            -int(n.inbound + n.outbound),
            -int(n.inbound),
            -int(n.outbound),
            _clean_text(n.label).lower(),
        ),
    )
    return ranked[0].key if ranked else ""


def _infer_focus_relation(node: DependencyNode, focus_key: str, graph: DependencyGraph) -> str:
    explicit = _clean_text(node.metadata.get("focus_relation", ""))
    if explicit:
        return explicit

    if not focus_key or focus_key not in graph.nodes:
        return ""

    if node.key == focus_key:
        return "hero"

    inbound = False
    outbound = False
    for edge in graph.edges.values():
        if edge.source == node.key and edge.target == focus_key:
            inbound = True
        if edge.source == focus_key and edge.target == node.key:
            outbound = True
        if inbound and outbound:
            return "mixed"

    if inbound:
        return "inbound"
    if outbound:
        return "outbound"
    return "context"


def _resolve_node_role(
    node: DependencyNode,
    graph: DependencyGraph,
    layout: LayoutResult,
    state: AnalysisState,
    focus_key: str,
) -> str:
    explicit_role = _clean_text(node.metadata.get("visual_role", ""))
    if explicit_role:
        return explicit_role

    if state.view == "focus":
        relation = _infer_focus_relation(node, focus_key, graph)
        if relation == "hero":
            return "focus_hero"
        if relation == "inbound":
            return "focus_inbound"
        if relation == "outbound":
            return "focus_outbound"
        if relation == "mixed":
            return "focus_mixed"
        if relation == "context":
            return "context_muted"

    if node.kind == "external":
        return "external"
    if node.kind == "note":
        return "note"
    if node.kind == "package":
        return "package"
    if node.is_hub:
        return "hub_accent"
    return "module"


def _node_role_chip(role: str, node: DependencyNode, state: AnalysisState) -> tuple[str, str]:
    if role == "focus_hero":
        return ("FOCUS", "focus")
    if role == "focus_inbound":
        return ("INBOUND", "focus")
    if role == "focus_outbound":
        return ("OUTBOUND", "focus")
    if role == "focus_mixed":
        return ("MIXED", "focus")
    if role == "context_muted":
        return ("CONTEXT", "muted")
    if node.kind == "external":
        return ("EXTERNAL", "external")
    if node.kind == "note":
        level = _clean_text(node.metadata.get("issue_level", "")).upper() or "NOTE"
        return (level[:10], "note")
    if node.is_hub:
        return ("HUB", "hub")
    if state.view == "package" and node.kind == "package":
        return ("PACKAGE", "package")
    return ("", "")


def _resolve_node_preset(theme: SemanticTheme, role: str, node: DependencyNode, state: AnalysisState) -> NodeVisualPreset:
    base_key = role if role in theme.node_presets else (
        "note" if node.kind == "note" else
        "external" if node.kind == "external" else
        "package" if node.kind == "package" else
        "module"
    )
    data = dict(theme.node_presets.get(base_key, theme.node_presets["module"]))

    if state.view == "package" and node.kind == "package" and role not in {"focus_hero", "context_muted"}:
        data["scale"] = max(1.02, _num(data.get("scale", 1.0), 1.0))
        data["border_width"] = max(1.8, _num(data.get("border_width", 1.6), 1.6))
        data["shine_opacity"] = max(_num(data.get("shine_opacity", 0.08), 0.08), 0.08)

    if state.view == "module" and node.kind == "module" and role == "module":
        data["radius"] = 14.0
        data["fill_opacity"] = min(1.0, _num(data.get("fill_opacity", 1.0), 1.0))
        data["glow_opacity"] = min(_num(data.get("glow_opacity", 0.0), 0.0), 0.08)

    if node.kind == "external" and role not in {"context_muted"}:
        data["dasharray"] = data.get("dasharray") or "7 5"
        data["fill_opacity"] = min(_num(data.get("fill_opacity", 0.92), 0.92), 0.92)

    if node.kind == "note":
        data["radius"] = max(14.0, _num(data.get("radius", 16.0), 16.0))
        data["label_size"] = min(13.0, _num(data.get("label_size", 13.0), 13.0))
        data["subtitle_size"] = min(10.4, _num(data.get("subtitle_size", 10.6), 10.6))

    if node.is_hub and role not in {"focus_hero", "focus_inbound", "focus_outbound", "focus_mixed", "context_muted"}:
        data["border_width"] = max(2.0, _num(data.get("border_width", 1.6), 1.6))
        data["halo"] = bool(data.get("halo", False))
        data["glow_opacity"] = max(_num(data.get("glow_opacity", 0.0), 0.0), 0.10)

    return NodeVisualPreset(
        fill=str(data["fill"]),
        stroke=str(data["stroke"]),
        text=str(data["text"]),
        subtext=str(data["subtext"]),
        accent=str(data["accent"]),
        chip_fill=str(data["chip_fill"]),
        chip_text=str(data["chip_text"]),
        badge_in_fill=str(data["badge_in_fill"]),
        badge_out_fill=str(data["badge_out_fill"]),
        badge_text=str(data["badge_text"]),
        glow=str(data.get("glow", "")),
        glow_opacity=_num(data.get("glow_opacity", 0.0), 0.0),
        fill_opacity=_num(data.get("fill_opacity", 1.0), 1.0),
        stroke_opacity=_num(data.get("stroke_opacity", 1.0), 1.0),
        border_width=_num(data.get("border_width", 1.6), 1.6),
        radius=_num(data.get("radius", 16.0), 16.0),
        shine_opacity=_num(data.get("shine_opacity", 0.10), 0.10),
        text_weight=_int(data.get("text_weight", 700), 700),
        muted=bool(data.get("muted", False)),
        dim_opacity=_num(data.get("dim_opacity", 1.0), 1.0),
        scale=_num(data.get("scale", 1.0), 1.0),
        label_size=_num(data.get("label_size", 13.0), 13.0),
        subtitle_size=_num(data.get("subtitle_size", 10.6), 10.6),
        chip_border=str(data.get("chip_border", "")),
        chip_border_opacity=_num(data.get("chip_border_opacity", 0.0), 0.0),
        dasharray=str(data.get("dasharray", "")),
        accent_bar=bool(data.get("accent_bar", True)),
        halo=bool(data.get("halo", False)),
        ring=bool(data.get("ring", False)),
    )


def _resolve_lane_role(lane: LayoutLane, state: AnalysisState) -> str:
    explicit_role = _clean_text(getattr(lane, "role", "")).lower().replace(" ", "_")
    role_aliases = {
        "focus_center": "focus_center_lane",
        "focus_center_lane": "focus_center_lane",
        "focus_side": "side_lane",
        "focus_side_lane": "side_lane",
        "context": "side_lane",
        "group": "default",
        "core": "default",
        "issue": "issue_lane",
        "issues": "issue_lane",
        "warning": "issue_lane",
        "issue_lane": "issue_lane",
        "external": "external_lane",
        "external_lane": "external_lane",
        "standard": "default",
        "default": "default",
    }
    if explicit_role in role_aliases:
        return role_aliases[explicit_role]

    key = _clean_text(lane.key).lower()
    label = _clean_text(lane.label).lower()

    if state.view == "focus":
        if key == "lane:focus:center":
            return "focus_center_lane"
        if "issue" in label or "warning" in label:
            return "issue_lane"
        if "external" in label:
            return "external_lane"
        return "side_lane"

    if "[issues]" in key or "issue" in label or "warning" in label:
        return "issue_lane"
    if "[external]" in key or "external" in label:
        return "external_lane"
    return "default"


def _resolve_lane_preset(theme: SemanticTheme, role: str, lane: Optional[LayoutLane] = None) -> LaneVisualPreset:
    data = dict(theme.lane_presets.get(role, theme.lane_presets["default"]))

    emphasis = _num(getattr(lane, "visual_emphasis", 1.0), 1.0) if lane is not None else 1.0
    density = _clean_text(getattr(lane, "density", "")).lower() if lane is not None else ""
    spacing_mode = _clean_text(getattr(lane, "spacing_mode", "")).lower() if lane is not None else ""

    if emphasis > 1.0:
        data["border_width"] = _num(data.get("border_width", 1.0), 1.0) * min(1.55, 0.88 + (emphasis * 0.32))
        data["accent_opacity"] = min(0.42, _num(data.get("accent_opacity", 0.20), 0.20) * min(1.8, 0.90 + (emphasis * 0.45)))
        data["stroke_opacity"] = min(1.0, _num(data.get("stroke_opacity", 0.80), 0.80) + min(0.18, (emphasis - 1.0) * 0.22))

    if density in {"dense", "tight"}:
        data["fill_opacity"] = min(0.94, _num(data.get("fill_opacity", 0.34), 0.34) + 0.05)
        data["header_fill_opacity"] = min(1.0, _num(data.get("header_fill_opacity", 0.95), 0.95) + 0.02)

    if spacing_mode in {"relaxed", "wide"}:
        data["accent_opacity"] = max(0.04, _num(data.get("accent_opacity", 0.20), 0.20) * 0.88)

    return LaneVisualPreset(
        fill=str(data["fill"]),
        stroke=str(data["stroke"]),
        header_fill=str(data["header_fill"]),
        header_text=str(data["header_text"]),
        meta_text=str(data["meta_text"]),
        accent=str(data["accent"]),
        fill_opacity=_num(data.get("fill_opacity", 0.34), 0.34),
        stroke_opacity=_num(data.get("stroke_opacity", 0.80), 0.80),
        header_fill_opacity=_num(data.get("header_fill_opacity", 0.95), 0.95),
        radius=_num(data.get("radius", 18.0), 18.0),
        header_radius=_num(data.get("header_radius", 14.0), 14.0),
        border_width=_num(data.get("border_width", 1.0), 1.0),
        accent_opacity=_num(data.get("accent_opacity", 0.20), 0.20),
        label_capsule_fill=str(data.get("label_capsule_fill", "")),
        label_capsule_text=str(data.get("label_capsule_text", "")),
    )


def _resolve_panel_preset(theme: SemanticTheme, role: str) -> PanelVisualPreset:
    data = dict(theme.panel_presets.get(role, theme.panel_presets["legend"]))
    return PanelVisualPreset(
        fill=str(data["fill"]),
        stroke=str(data["stroke"]),
        title=str(data["title"]),
        text=str(data["text"]),
        meta=str(data["meta"]),
        accent=str(data["accent"]),
        fill_opacity=_num(data.get("fill_opacity", 0.76), 0.76),
        stroke_opacity=_num(data.get("stroke_opacity", 0.90), 0.90),
        radius=_num(data.get("radius", 16.0), 16.0),
        border_width=_num(data.get("border_width", 1.0), 1.0),
    )


def _resolve_edge_role(
    edge: DependencyEdge,
    graph: DependencyGraph,
    state: AnalysisState,
    focus_key: str,
) -> str:
    if edge.source == edge.target:
        return "self_loop"

    source = graph.nodes.get(edge.source)
    target = graph.nodes.get(edge.target)
    if source is None or target is None:
        return "default"

    source_lane = _clean_text(source.metadata.get("layout_lane_key", ""))
    target_lane = _clean_text(target.metadata.get("layout_lane_key", ""))
    same_lane = bool(source_lane and source_lane == target_lane)

    if state.view == "focus" and focus_key:
        if edge.target == focus_key:
            return "focus_inbound"
        if edge.source == focus_key:
            return "focus_outbound"

        relation_source = _infer_focus_relation(source, focus_key, graph)
        relation_target = _infer_focus_relation(target, focus_key, graph)
        if relation_source == "context" and relation_target == "context":
            return "muted"

    if same_lane:
        return "intra_lane"

    return "cross_lane"


def _edge_width_from_weight(base_width: float, weight: int, role: str) -> float:
    weight = max(1, int(weight))
    width = base_width + min(1.30, (weight - 1) * 0.18)
    if role in {"focus_inbound", "focus_outbound"}:
        width += min(0.40, (weight - 1) * 0.05)
    return width


def _resolve_edge_preset(theme: SemanticTheme, role: str, edge: DependencyEdge) -> EdgeVisualPreset:
    data = dict(theme.edge_presets.get(role, theme.edge_presets["default"]))
    width = _edge_width_from_weight(_num(data.get("width", 1.7), 1.7), edge.weight, role)
    glow_width = max(width + 3.0, _num(data.get("glow_width", width + 3.0), width + 3.0))
    opacity = _num(data.get("opacity", 0.56), 0.56)
    if edge.weight > 1:
        opacity = min(0.96, opacity + min(0.18, (edge.weight - 1) * 0.03))
    return EdgeVisualPreset(
        stroke=str(data["stroke"]),
        marker_fill=str(data.get("marker_fill", data["stroke"])),
        width=width,
        opacity=opacity,
        glow=str(data.get("glow", "")),
        glow_opacity=_num(data.get("glow_opacity", 0.0), 0.0),
        glow_width=glow_width,
        dasharray=str(data.get("dasharray", "")),
        curve_bias=_num(data.get("curve_bias", 0.34), 0.34),
        layer=_int(data.get("layer", 2), 2),
        marker_id=str(data.get("marker_id", "arrow_default")),
    )


# ----------------------------
# Labels, subtitles, icons
# ----------------------------




def _format_count(value: Any) -> str:
    try:
        n = int(value)
    except Exception:
        return "0"

    sign = "-" if n < 0 else ""
    n = abs(n)

    if n >= 1_000_000:
        text = f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        text = f"{n / 1_000:.1f}k"
    else:
        text = str(n)

    if text.endswith(".0M") or text.endswith(".0k"):
        text = text.replace(".0M", "M").replace(".0k", "k")

    return f"{sign}{text}"


def _node_label(node: DependencyNode) -> str:
    if node.kind == "note":
        msg = _clean_text(node.metadata.get("full_message", ""))
        return _safe_short(msg or node.label or "(note)", LABEL_LIMIT)
    return _safe_short(node.label or "(sin nombre)", LABEL_LIMIT)


def _node_subtitle(node: DependencyNode, state: AnalysisState) -> str:
    if node.kind == "module":
        rel = _clean_text(node.metadata.get("relative_path", ""))
        if rel:
            return _safe_short(rel, 42)
        module_name = _clean_text(node.metadata.get("module_name", ""))
        return _safe_short(module_name, 42)
    if node.kind == "package":
        root = _clean_text(node.metadata.get("root_group", node.group))
        if state.view == "package":
            return f"in {_format_count(node.inbound)} • out {_format_count(node.outbound)}"
        return _safe_short(root, 30)
    if node.kind == "external":
        return "boundary system"
    if node.kind == "note":
        issue_path = _clean_text(node.metadata.get("issue_path", node.path))
        return _safe_short(issue_path or "observación", 42)
    return ""


def _node_icon(node: DependencyNode, role: str, state: AnalysisState) -> str:
    if role == "focus_hero":
        return "◆"
    if node.kind == "package":
        return "▣"
    if node.kind == "module":
        return "◫" if state.view == "module" else "▪"
    if node.kind == "external":
        return "◎"
    if node.kind == "note":
        return "!"
    return "•"


def _node_tooltip(node: DependencyNode, role: str) -> str:
    parts = [
        f"label={_clean_text(node.label)}",
        f"kind={_clean_text(node.kind)}",
        f"role={role}",
        f"in={int(node.inbound)}",
        f"out={int(node.outbound)}",
    ]
    module_name = _clean_text(node.metadata.get("module_name", ""))
    relative_path = _clean_text(node.metadata.get("relative_path", ""))
    full_message = _clean_text(node.metadata.get("full_message", ""))
    lane_label = _clean_text(node.metadata.get("layout_lane_label", ""))
    if module_name:
        parts.append(f"module={module_name}")
    if lane_label:
        parts.append(f"lane={lane_label}")
    if relative_path:
        parts.append(relative_path)
    elif node.path:
        parts.append(_clean_text(node.path))
    if full_message and full_message != _clean_text(node.label):
        parts.append(full_message)
    return " | ".join(parts)


def _edge_evidence_lines(
    edge: DependencyEdge,
    *,
    limit: int = EDGE_FORENSIC_EVIDENCE_LIMIT,
) -> tuple[str, ...]:
    cleaned: list[str] = []
    for item in sorted(edge.evidence):
        text = _clean_text(item)
        if text:
            cleaned.append(text)

    if not cleaned:
        return ("sin evidencia textual capturada",)

    return tuple(cleaned[: max(1, int(limit))])


def _edge_forensic_id(edge: DependencyEdge, source_label: str, target_label: str) -> str:
    left = _clean_text(source_label or edge.source).lower().replace(" ", "_")
    right = _clean_text(target_label or edge.target).lower().replace(" ", "_")
    return _safe_short(f"{left}__to__{right}", 96)


def _edge_forensic_summary(
    edge: DependencyEdge,
    *,
    source_label: str,
    target_label: str,
    role: str,
) -> str:
    evidence = _edge_evidence_lines(edge, limit=3)
    head = evidence[0] if evidence else "sin evidencia textual capturada"
    return (
        f"{source_label} -> {target_label} | "
        f"role={role} | weight={int(edge.weight)} | "
        f"evidence={len(_edge_evidence_lines(edge))} | "
        f"first={head}"
    )


def _edge_tooltip(edge: DependencyEdge, graph: DependencyGraph, role: str) -> str:
    source = graph.nodes.get(edge.source)
    target = graph.nodes.get(edge.target)
    source_label = _clean_text(source.label if source else edge.source)
    target_label = _clean_text(target.label if target else edge.target)
    forensic_id = _edge_forensic_id(edge, source_label, target_label)
    evidence = _edge_evidence_lines(edge, limit=6)
    base = (
        f"{source_label} -> {target_label} | "
        f"role={role} | weight={int(edge.weight)} | forensic={forensic_id}"
    )
    if evidence:
        base += " | " + " | ".join(_clean_text(item) for item in evidence)
    return base


# ----------------------------
# Geometry helpers
# ----------------------------

def _node_center_y(node: DependencyNode) -> float:
    return float(node.y) + (NODE_HEIGHT / 2.0)


def _node_center_x(visual: ResolvedNodeVisual) -> float:
    return float(visual.x) + (visual.width / 2.0)


def _resolved_node_box(node: DependencyNode, preset: NodeVisualPreset) -> tuple[float, float, float, float]:
    width = float(node.width)
    height = float(NODE_HEIGHT)

    if preset.scale > 1.0:
        extra_w = (width * (preset.scale - 1.0))
        extra_h = (height * (preset.scale - 1.0))
        x = float(node.x) - (extra_w / 2.0)
        y = float(node.y) - (extra_h / 2.0)
        width += extra_w
        height += extra_h
    else:
        x = float(node.x)
        y = float(node.y)

    if preset.ring:
        x -= 2.0
        y -= 2.0
        width += 4.0
        height += 4.0

    return (x, y, width, height)


def _node_anchor_points(source: DependencyNode, target: DependencyNode) -> tuple[float, float, float, float]:
    y1 = _node_center_y(source)
    y2 = _node_center_y(target)

    lane_x_a = _num(source.metadata.get("layout_lane_x", source.x), source.x)
    lane_x_b = _num(target.metadata.get("layout_lane_x", target.x), target.x)

    if lane_x_b > lane_x_a:
        return (float(source.x + source.width), y1, float(target.x), y2)
    if lane_x_b < lane_x_a:
        return (float(source.x), y1, float(target.x + target.width), y2)

    return (float(source.x + source.width), y1, float(target.x + target.width), y2)


def _self_edge_path(node: DependencyNode, preset: EdgeVisualPreset) -> str:
    x = float(node.x + node.width)
    y = _node_center_y(node)
    loop_out = 56.0 + (preset.width * 3.0)
    loop_up = 24.0
    loop_down = 28.0
    return (
        f"M{x:.1f},{y:.1f} "
        f"C{x + loop_out:.1f},{y - loop_up:.1f} "
        f"{x + loop_out:.1f},{y + loop_down:.1f} "
        f"{x:.1f},{y + 7.0:.1f}"
    )


def _edge_path(source: DependencyNode, target: DependencyNode, preset: EdgeVisualPreset) -> str:
    if source.key == target.key:
        return _self_edge_path(source, preset)

    x1, y1, x2, y2 = _node_anchor_points(source, target)
    lane_x_a = _num(source.metadata.get("layout_lane_x", source.x), source.x)
    lane_x_b = _num(target.metadata.get("layout_lane_x", target.x), target.x)

    if lane_x_a == lane_x_b:
        bend = max(84.0, abs(y2 - y1) * (0.26 + preset.curve_bias))
        cx1 = x1 + bend
        cx2 = x2 + bend
        return f"M{x1:.1f},{y1:.1f} C{cx1:.1f},{y1:.1f} {cx2:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"

    bend = max(34.0, abs(x2 - x1) * preset.curve_bias)
    cx1 = x1 + bend if x2 >= x1 else x1 - bend
    cx2 = x2 - bend if x2 >= x1 else x2 + bend
    return f"M{x1:.1f},{y1:.1f} C{cx1:.1f},{y1:.1f} {cx2:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"


# ----------------------------
# Ordering and emphasis
# ----------------------------

def _node_emphasis(role: str, node: DependencyNode, state: AnalysisState) -> float:
    if role == "focus_hero":
        return 10.0
    if role == "focus_mixed":
        return 8.0
    if role in {"focus_inbound", "focus_outbound"}:
        return 7.2
    if role == "hub_accent":
        return 6.2
    if node.kind == "package" and state.view == "package":
        return 5.8
    if node.kind == "module":
        return 5.0
    if node.kind == "external":
        return 4.0
    if node.kind == "note":
        return 3.8
    if role == "context_muted":
        return 2.4
    return 4.6


def _node_layer(role: str, node: DependencyNode) -> int:
    if role == "focus_hero":
        return 5
    if role in {"focus_mixed", "focus_inbound", "focus_outbound"}:
        return 4
    if node.kind in {"note", "external"}:
        return 3
    return 2


def _edge_emphasis(role: str, edge: DependencyEdge) -> float:
    base = float(edge.weight)
    if role == "focus_inbound":
        return 9.0 + base
    if role == "focus_outbound":
        return 8.8 + base
    if role == "self_loop":
        return 4.6 + (base * 0.2)
    if role == "cross_lane":
        return 5.2 + (base * 0.3)
    if role == "intra_lane":
        return 4.0 + (base * 0.2)
    if role == "muted":
        return 1.8 + (base * 0.1)
    return 4.5 + (base * 0.2)


def _resolve_node_visuals(
    graph: DependencyGraph,
    layout: LayoutResult,
    state: AnalysisState,
    theme: SemanticTheme,
) -> list[ResolvedNodeVisual]:
    focus_key = _find_focus_key(graph, layout, state)
    visuals: list[ResolvedNodeVisual] = []

    for node in layout.nodes:
        role = _resolve_node_role(node, graph, layout, state, focus_key)
        preset = _resolve_node_preset(theme, role, node, state)
        x, y, width, height = _resolved_node_box(node, preset)
        chip_label, chip_kind = _node_role_chip(role, node, state)
        visuals.append(
            ResolvedNodeVisual(
                node=node,
                role=role,
                preset=preset,
                x=x,
                y=y,
                width=width,
                height=height,
                label=_node_label(node),
                subtitle=_node_subtitle(node, state),
                chip_label=chip_label,
                chip_kind=chip_kind,
                icon=_node_icon(node, role, state),
                emphasis=_node_emphasis(role, node, state),
                layer=_node_layer(role, node),
            )
        )

    visuals.sort(key=lambda item: (item.layer, item.emphasis, item.y, item.x))
    return visuals


def _resolve_edge_visuals(
    graph: DependencyGraph,
    layout: LayoutResult,
    state: AnalysisState,
    theme: SemanticTheme,
) -> list[ResolvedEdgeVisual]:
    focus_key = _find_focus_key(graph, layout, state)
    visible_keys = {node.key for node in layout.nodes}
    visuals: list[ResolvedEdgeVisual] = []

    for edge in graph.iter_edges_sorted():
        if edge.source not in visible_keys or edge.target not in visible_keys:
            continue

        source = graph.nodes.get(edge.source)
        target = graph.nodes.get(edge.target)
        if source is None or target is None:
            continue

        role = _resolve_edge_role(edge, graph, state, focus_key)
        preset = _resolve_edge_preset(theme, role, edge)
        x1, y1, x2, y2 = _node_anchor_points(source, target)
        source_label = _clean_text(source.label or edge.source)
        target_label = _clean_text(target.label or edge.target)
        forensic_evidence = _edge_evidence_lines(edge)
        forensic_id = _edge_forensic_id(edge, source_label, target_label)

        visuals.append(
            ResolvedEdgeVisual(
                edge=edge,
                role=role,
                preset=preset,
                path_d=_edge_path(source, target, preset),
                tooltip=_edge_tooltip(edge, graph, role),
                layer=preset.layer,
                emphasis=_edge_emphasis(role, edge),
                forensic_id=forensic_id,
                source_label=source_label,
                target_label=target_label,
                forensic_summary=_edge_forensic_summary(
                    edge,
                    source_label=source_label,
                    target_label=target_label,
                    role=role,
                ),
                forensic_evidence=forensic_evidence,
                overlay_x=((x1 + x2) / 2.0),
                overlay_y=((y1 + y2) / 2.0),
            )
        )

    visuals.sort(key=lambda item: (item.layer, item.emphasis))
    return visuals


def _resolve_lane_visuals(

    layout: LayoutResult,
    state: AnalysisState,
    theme: SemanticTheme,
) -> list[ResolvedLaneVisual]:
    visuals: list[ResolvedLaneVisual] = []
    for lane in layout.lanes:
        role = _resolve_lane_role(lane, state)
        visuals.append(
            ResolvedLaneVisual(
                lane=lane,
                role=role,
                preset=_resolve_lane_preset(theme, role, lane),
            )
        )
    return visuals


# ----------------------------
# SVG defs and style helpers
# ----------------------------

def _build_semantic_defs(theme: SemanticTheme, width: int, height: int) -> str:
    t = theme.tokens
    dark = bool(theme.is_dark)
    grid_color = _clean_text(t.get("canvas_grid")) or "#6ea8ff"
    grid_opacity = _num(t.get("canvas_grid_opacity", 0.06), 0.06)
    grid_size = _num(t.get("grid_size", 28), 28)
    grid_stroke_width = _num(t.get("grid_stroke_width", 1.0), 1.0)
    shadow = _clean_text(t.get("shadow")) or "#020617"

    default_marker = dict(theme.marker_presets.get("default_arrow", {}))
    subtle_marker = dict(theme.marker_presets.get("subtle_arrow", {}))
    focus_marker = dict(theme.marker_presets.get("focus_arrow", {}))
    focus_out_marker = dict(theme.marker_presets.get("focus_arrow_out", focus_marker))

    def marker_markup(marker: dict[str, Any], fallback_id: str, fallback_fill: str) -> str:
        svg_id = _clean_text(marker.get("svg_id")) or fallback_id
        fill = _clean_text(marker.get("fill")) or fallback_fill
        opacity = _num(marker.get("opacity", 0.9), 0.9)
        marker_width = _num(marker.get("marker_width", 12), 12)
        marker_height = _num(marker.get("marker_height", 12), 12)
        ref_x = _num(marker.get("ref_x", 10), 10)
        ref_y = _num(marker.get("ref_y", 6), 6)
        return (
            f'<marker id="{_escape(svg_id)}" markerWidth="{marker_width:.2f}" markerHeight="{marker_height:.2f}" '
            f'refX="{ref_x:.2f}" refY="{ref_y:.2f}" orient="auto" markerUnits="strokeWidth">'
            f'<path d="M0,0 L12,6 L0,12 z" fill="{_escape(fill)}" opacity="{opacity:.3f}" />'
            f"</marker>"
        )

    return f"""
    <defs>
      <linearGradient id="semanticCanvasGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="{_escape(_mix_hex(t['canvas_bg'], '#000000' if dark else '#ffffff', 0.02 if dark else 0.00))}" />
        <stop offset="58%" stop-color="{_escape(t['canvas_bg'])}" />
        <stop offset="100%" stop-color="{_escape(_mix_hex(t['canvas_bg'], '#163356' if dark else '#dfeaf8', 0.10 if dark else 0.04))}" />
      </linearGradient>

      <radialGradient id="semanticHaloA" cx="0.18" cy="0.06" r="0.95">
        <stop offset="0%" stop-color="{_escape(_clean_text(t.get('halo_a')) or t['focus'])}" stop-opacity="{_num(t.get('halo_a_opacity', 0.18 if dark else 0.10), 0.18):.3f}" />
        <stop offset="100%" stop-color="{_escape(_clean_text(t.get('halo_a')) or t['focus'])}" stop-opacity="0" />
      </radialGradient>

      <radialGradient id="semanticHaloB" cx="0.86" cy="0.14" r="0.70">
        <stop offset="0%" stop-color="{_escape(_clean_text(t.get('halo_b')) or t['focus_warm'])}" stop-opacity="{_num(t.get('halo_b_opacity', 0.13 if dark else 0.08), 0.13):.3f}" />
        <stop offset="100%" stop-color="{_escape(_clean_text(t.get('halo_b')) or t['focus_warm'])}" stop-opacity="0" />
      </radialGradient>

      <pattern id="semanticGrid" width="{grid_size:.2f}" height="{grid_size:.2f}" patternUnits="userSpaceOnUse">
        <path d="M{grid_size:.2f} 0 L0 0 0 {grid_size:.2f}" fill="none" stroke="{_escape(grid_color)}" stroke-width="{grid_stroke_width:.2f}" opacity="{grid_opacity:.3f}" />
      </pattern>

      <filter id="shadowSoft" x="-30%" y="-30%" width="180%" height="220%">
        <feDropShadow dx="0" dy="10" stdDeviation="9" flood-color="{_escape(shadow)}" flood-opacity="{0.36 if dark else 0.16}" />
      </filter>

      <filter id="shadowNode" x="-35%" y="-40%" width="200%" height="240%">
        <feDropShadow dx="0" dy="14" stdDeviation="11" flood-color="{_escape(shadow)}" flood-opacity="{0.44 if dark else 0.14}" />
      </filter>

      <filter id="glowStrong" x="-40%" y="-40%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="6.0" />
      </filter>

      <filter id="glowSoft" x="-35%" y="-35%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3.2" />
      </filter>

      <filter id="laneGlow" x="-30%" y="-20%" width="180%" height="160%">
        <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="{_escape(t['focus'])}" flood-opacity="{0.08 if dark else 0.04}" />
      </filter>

      {marker_markup(default_marker, 'arrow_default', theme.edge_presets['default']['marker_fill'])}
      {marker_markup(subtle_marker, 'arrow_muted', theme.edge_presets['muted']['marker_fill'])}
      {marker_markup(focus_marker, 'arrow_focus_in', theme.edge_presets['focus_inbound']['marker_fill'])}
      {marker_markup(focus_out_marker, 'arrow_focus_out', theme.edge_presets['focus_outbound']['marker_fill'])}

      <style>
        .svg-title {{
          font: 700 31px 'Segoe UI Variable Display', 'Segoe UI', Arial, sans-serif;
          fill: {_escape(t['header_title'])};
          letter-spacing: 0.2px;
        }}
        .svg-subtitle {{
          font: 600 13px 'Segoe UI Variable Text', 'Segoe UI', Arial, sans-serif;
          fill: {_escape(t['header_text'])};
        }}
        .svg-meta {{
          font: 500 11.5px 'Consolas', 'Cascadia Mono', monospace;
          fill: {_escape(t['header_meta'])};
        }}
        .svg-footer {{
          font: 500 10.5px 'Segoe UI', Arial, sans-serif;
          fill: {_escape(t['footer_text'])};
        }}
        .lane-title {{
          font: 700 12px 'Segoe UI', Arial, sans-serif;
          letter-spacing: 0.25px;
        }}
        .lane-meta {{
          font: 600 10px 'Segoe UI', Arial, sans-serif;
        }}
        .node-label {{
          font-family: 'Segoe UI Variable Text', 'Segoe UI', Arial, sans-serif;
        }}
        .node-subtitle {{
          font-family: 'Segoe UI', Arial, sans-serif;
        }}
        .node-icon {{
          font: 700 12px 'Segoe UI', Arial, sans-serif;
        }}
        .chip-text {{
          font: 700 9.4px 'Segoe UI', Arial, sans-serif;
          letter-spacing: 0.45px;
        }}
        .badge-text {{
          font: 700 9.6px 'Segoe UI', Arial, sans-serif;
          letter-spacing: 0.18px;
        }}
        .panel-title {{
          font: 700 12.2px 'Segoe UI', Arial, sans-serif;
        }}
        .panel-text {{
          font: 600 11px 'Segoe UI', Arial, sans-serif;
        }}
        .panel-meta {{
          font: 500 10px 'Segoe UI', Arial, sans-serif;
        }}

        .edgeGroup .edge-hit {{
          fill: none;
          stroke: transparent;
          stroke-width: 18;
          pointer-events: stroke;
        }}
        .edgeGroup .edge-arrow-core {{
          opacity: 0.0;
          transition: opacity 120ms ease;
        }}
        .edgeGroup .edge-glow-core {{
          opacity: 0.0;
          transition: opacity 120ms ease;
        }}
        .edgeGroup .edge-forensic-card {{
          opacity: 0.0;
          pointer-events: none;
          transition: opacity 120ms ease;
        }}
        .edgeGroup:hover .edge-arrow-core,
        .edgeGroup:hover .edge-glow-core,
        .edgeGroup:hover .edge-forensic-card {{
          opacity: 1.0;
        }}
        .edge-forensic-title {{
          font: 700 10.2px 'Segoe UI', Arial, sans-serif;
          fill: {_escape(t['header_title'])};
        }}
        .edge-forensic-text {{
          font: 600 9.2px 'Consolas', 'Cascadia Mono', monospace;
          fill: {_escape(t['header_text'])};
        }}
        .edge-forensic-meta {{
          font: 500 8.6px 'Segoe UI', Arial, sans-serif;
          fill: {_escape(t['header_meta'])};
        }}
      </style>
    </defs>
    """


# ----------------------------
# Drawing helpers
# ----------------------------

def _badge_width(text: str) -> float:
    return max(30.0, 14.0 + (6.4 * len(text)))


def _chip_width(text: str) -> float:
    return max(46.0, 18.0 + (6.6 * len(text)))


def _lane_capsule_label(resolved: ResolvedLaneVisual) -> str:
    lane = resolved.lane
    role = resolved.role
    density = _clean_text(getattr(lane, "density", "")).lower()
    spacing_mode = _clean_text(getattr(lane, "spacing_mode", "")).lower()

    if resolved.preset.label_capsule_fill and resolved.preset.label_capsule_text:
        if role == "focus_center_lane":



            return "CENTER"
        if role == "issue_lane":
            return "ISSUE"
        if role == "external_lane":
            return "EXT"

    if density in {"dense", "tight"}:
        return "DENSE"
    if spacing_mode in {"relaxed", "wide"}:
        return "RELAX"
    return ""


def _lane_meta_text(lane: LayoutLane) -> str:
    base = f"{lane.node_count} nodos • in {lane.inbound_sum} • out {lane.outbound_sum}"
    density = _clean_text(getattr(lane, "density", "")).lower()
    spacing_mode = _clean_text(getattr(lane, "spacing_mode", "")).lower()

    tags: list[str] = []
    if density and density not in {"regular", "normal"}:
        tags.append(density)
    if spacing_mode and spacing_mode not in {"regular", "normal"}:
        tags.append(spacing_mode)

    if tags:
        base += " • " + " / ".join(tag.upper()[:8] for tag in tags)
    return base


def _draw_lane(resolved: ResolvedLaneVisual, canvas_height: int) -> str:
    lane = resolved.lane
    p = resolved.preset

    lane_top = TOP_MARGIN - 22.0
    header_y = TOP_MARGIN - 14.0
    header_h = 40.0
    body_y = header_y + header_h + 8.0
    body_h = max(86.0, canvas_height - body_y - BOTTOM_MARGIN + 18.0)

    title_limit = _text_limit_for_width(lane.width - 42.0, 12.0, min_chars=10, max_chars=80)
    meta_limit = _text_limit_for_width(lane.width - 42.0, 10.0, min_chars=14, max_chars=110)
    lane_title = _safe_short(lane.label, title_limit)
    meta = _safe_short(_lane_meta_text(lane), meta_limit)
    capsule = ""
    capsule_label = _lane_capsule_label(resolved)
    if capsule_label:
        cap_w = _chip_width(capsule_label)
        capsule_fill = p.label_capsule_fill or _mix_hex(p.accent, p.fill, 0.18)
        capsule_text = p.label_capsule_text or p.header_text
        capsule = (
            f'<g transform="translate({lane.x + lane.width - cap_w - 12:.1f},{header_y + 8:.1f})">'
            f'<rect x="0" y="0" width="{cap_w:.1f}" height="18" rx="9" ry="9" '
            f'fill="{_escape(capsule_fill)}" opacity="0.98" />'
            f'<text class="chip-text" x="{cap_w / 2:.1f}" y="12.4" text-anchor="middle" '
            f'fill="{_escape(capsule_text)}">{_escape(capsule_label)}</text>'
            f'</g>'
        )

    accent_x = lane.x + 8.0
    accent_y = lane_top + 10.0
    accent_h = body_h + 36.0

    return f"""
    <g class="laneGroup">
      <rect x="{lane.x:.1f}" y="{lane_top:.1f}" width="{lane.width:.1f}" height="{body_h + 58.0:.1f}" rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}"
            filter="url(#laneGlow)" />
      <rect x="{accent_x:.1f}" y="{accent_y:.1f}" width="3.5" height="{accent_h:.1f}" rx="2" ry="2"
            fill="{_escape(p.accent)}" opacity="{p.accent_opacity:.3f}" />
      <rect x="{lane.x + 8.0:.1f}" y="{header_y:.1f}" width="{lane.width - 16.0:.1f}" height="{header_h:.1f}" rx="{p.header_radius:.1f}" ry="{p.header_radius:.1f}"
            fill="{_escape(p.header_fill)}" fill-opacity="{p.header_fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{min(1.0, p.stroke_opacity + 0.08):.3f}" stroke-width="0.9" />
      <text class="lane-title" x="{lane.x + 18.0:.1f}" y="{header_y + 16.0:.1f}" fill="{_escape(p.header_text)}">{_escape(lane_title)}</text>
      <text class="lane-meta" x="{lane.x + 18.0:.1f}" y="{header_y + 31.0:.1f}" fill="{_escape(p.meta_text)}">{_escape(meta)}</text>
      {capsule}
    </g>
    """


def _draw_edge(resolved: ResolvedEdgeVisual) -> str:
    p = resolved.preset
    dash = f' stroke-dasharray="{_escape(p.dasharray)}"' if p.dasharray else ""
    edge_dom_id = safe_slug(resolved.forensic_id or f"{resolved.edge.source}_{resolved.edge.target}")
    evidence_lines = list(resolved.forensic_evidence[:4])
    while len(evidence_lines) < 4:
        evidence_lines.append("")

    glow = ""
    if p.glow and p.glow_opacity > 0.0:
        glow = (
            f'<path class="edge-glow-core" d="{resolved.path_d}" fill="none" stroke="{_escape(p.glow)}" '
            f'stroke-opacity="{p.glow_opacity:.3f}" stroke-width="{p.glow_width:.2f}" '
            f'stroke-linecap="round" filter="url(#glowSoft)"{dash} />'
        )

    card_w = 272.0
    line_count = 2 + len([item for item in evidence_lines if item.strip()])
    card_h = 28.0 + (line_count * 12.0)
    card_x = max(LEFT_MARGIN, resolved.overlay_x - (card_w / 2.0))
    card_y = max(TOP_MARGIN - 6.0, resolved.overlay_y - card_h - 12.0)

    forensic_card = ""
    if ENABLE_EDGE_FORENSICS:
        evidence_markup: list[str] = []
        y = card_y + 34.0
        if evidence_lines and evidence_lines[0].strip():
            for item in evidence_lines:
                if not item.strip():
                    continue
                evidence_markup.append(
                    f'<text class="edge-forensic-text" x="{card_x + 10.0:.1f}" y="{y:.1f}">â€¢ {_escape(_safe_short(item, 72))}</text>'
                )
                y += 12.0

        forensic_card = f"""
      <g class="edge-forensic-card">
        <rect x="{card_x:.1f}" y="{card_y:.1f}" width="{card_w:.1f}" height="{card_h:.1f}"
              rx="12" ry="12"
              fill="#070c16" fill-opacity="0.94"
              stroke="{_escape(p.stroke)}" stroke-opacity="0.70" stroke-width="1.0" />
        <text class="edge-forensic-title" x="{card_x + 10.0:.1f}" y="{card_y + 16.0:.1f}">{_escape(_safe_short(resolved.source_label + ' -> ' + resolved.target_label, 40))}</text>
        <text class="edge-forensic-meta" x="{card_x + 10.0:.1f}" y="{card_y + 28.0:.1f}">{_escape(_safe_short(resolved.forensic_summary, 82))}</text>
        {''.join(evidence_markup)}
      </g>
"""

    return f"""
    <g class="edgeGroup" id="edge_{_escape(edge_dom_id)}"
       data-edge-id="{_escape(resolved.forensic_id)}"
       data-source="{_escape(resolved.source_label)}"
       data-target="{_escape(resolved.target_label)}"
       data-role="{_escape(resolved.role)}"
       data-weight="{int(resolved.edge.weight)}"
       data-evidence-count="{len(resolved.forensic_evidence)}">
      <title>{_escape(resolved.tooltip)}</title>
      <desc>{_escape(resolved.forensic_summary)}</desc>
      <path class="edge-hit" d="{resolved.path_d}" />
      {glow}
      <path class="edge-arrow-core" d="{resolved.path_d}" fill="none"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.opacity:.3f}"
            stroke-width="{p.width:.2f}" stroke-linecap="round"
            marker-end="url(#{_escape(p.marker_id)})"{dash} />
      {forensic_card}
    </g>
    """


def _draw_role_chip(visual: ResolvedNodeVisual) -> str:
    if not visual.chip_label:
        return ""

    p = visual.preset
    chip_w = _chip_width(visual.chip_label)
    chip_h = 18.0
    chip_x = visual.x + 12.0
    chip_y = visual.y - 9.0

    border = ""
    if p.chip_border and p.chip_border_opacity > 0.0:
        border = (
            f' stroke="{_escape(p.chip_border)}" '
            f'stroke-opacity="{p.chip_border_opacity:.3f}" stroke-width="0.8"'
        )

    return (
        f'<g class="nodeChip">'
        f'<rect x="{chip_x:.1f}" y="{chip_y:.1f}" width="{chip_w:.1f}" height="{chip_h:.1f}" '
        f'rx="9" ry="9" fill="{_escape(p.chip_fill)}" opacity="0.98"{border} />'
        f'<text class="chip-text" x="{chip_x + chip_w / 2:.1f}" y="{chip_y + 12.2:.1f}" '
        f'text-anchor="middle" fill="{_escape(p.chip_text)}">{_escape(visual.chip_label)}</text>'
        f'</g>'
    )


def _draw_badges(visual: ResolvedNodeVisual) -> str:
    node = visual.node
    if node.kind == "note":
        return ""

    p = visual.preset
    badges: list[tuple[str, str]] = [
        (f"↙ {_format_count(node.inbound)}", p.badge_in_fill),
        (f"↗ {_format_count(node.outbound)}", p.badge_out_fill),
    ]

    if node.is_hub and visual.role not in {"focus_hero"}:
        badges.append(("H", _mix_hex(p.accent, p.stroke, 0.28)))
    elif node.is_island and visual.role == "context_muted":
        badges.append(("0", _mix_hex(p.stroke, "#ef4444", 0.22)))

    cursor_x = visual.x + visual.width - 12.0
    y = visual.y + 11.0
    parts: list[str] = []

    for text, fill in reversed(badges):
        w = _badge_width(text)
        x = cursor_x - w
        parts.append(
            f'<g class="nodeBadge">'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="16.5" rx="8.2" ry="8.2" '
            f'fill="{_escape(fill)}" opacity="0.96" />'
            f'<text class="badge-text" x="{x + w / 2:.1f}" y="{y + 11.4:.1f}" text-anchor="middle" '
            f'fill="{_escape(p.badge_text)}">{_escape(text)}</text>'
            f'</g>'
        )
        cursor_x = x - 6.0

    return "".join(parts)


def _draw_node(visual: ResolvedNodeVisual) -> str:
    p = visual.preset
    node = visual.node

    opacity = p.dim_opacity if p.muted else 1.0
    title = _node_tooltip(node, visual.role)
    icon_x = visual.x + 14.0
    label_x = visual.x + 32.0
    label_y = visual.y + (23.0 if visual.subtitle else 26.0)
    subtitle_y = visual.y + 37.5
    text_lane_width = max(52.0, visual.width - 72.0)
    label_limit = _text_limit_for_width(text_lane_width, p.label_size, min_chars=8, max_chars=90)
    subtitle_limit = _text_limit_for_width(text_lane_width, p.subtitle_size, min_chars=10, max_chars=100)
    label_text = _safe_short(visual.label, label_limit)
    subtitle_text = _safe_short(visual.subtitle, subtitle_limit) if visual.subtitle else ""

    glow = ""
    if p.glow and p.glow_opacity > 0.0:
        glow = (
            f'<rect x="{visual.x - 1.0:.1f}" y="{visual.y - 1.0:.1f}" width="{visual.width + 2.0:.1f}" height="{visual.height + 2.0:.1f}" '
            f'rx="{p.radius + 1.0:.1f}" ry="{p.radius + 1.0:.1f}" fill="none" '
            f'stroke="{_escape(p.glow)}" stroke-opacity="{p.glow_opacity:.3f}" stroke-width="{max(4.0, p.border_width * 3.8):.2f}" '
            f'filter="url(#glowStrong)" />'
        )

    halo = ""
    if p.halo:
        cx = _node_center_x(visual)
        cy = visual.y + (visual.height / 2.0)
        rx = max(42.0, visual.width * 0.56)
        ry = max(24.0, visual.height * 0.88)
        halo = (
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{_escape(p.glow or p.accent)}" opacity="{min(0.18, p.glow_opacity + 0.04):.3f}" filter="url(#glowStrong)" />'
        )

    ring = ""
    if p.ring:
        ring = (
            f'<rect x="{visual.x - 5.0:.1f}" y="{visual.y - 5.0:.1f}" width="{visual.width + 10.0:.1f}" height="{visual.height + 10.0:.1f}" '
            f'rx="{p.radius + 4.0:.1f}" ry="{p.radius + 4.0:.1f}" fill="none" '
            f'stroke="{_escape(p.accent)}" stroke-opacity="0.28" stroke-width="1.1" />'
        )

    shine_h = max(10.0, visual.height * 0.46)
    shine = (
        f'<rect x="{visual.x + 1.2:.1f}" y="{visual.y + 1.2:.1f}" width="{max(1.0, visual.width - 2.4):.1f}" height="{shine_h:.1f}" '
        f'rx="{max(8.0, p.radius - 1.0):.1f}" ry="{max(8.0, p.radius - 1.0):.1f}" fill="#ffffff" opacity="{p.shine_opacity:.3f}" />'
    )

    accent_bar = ""
    if p.accent_bar:
        accent_bar = (
            f'<rect x="{visual.x + 9.0:.1f}" y="{visual.y + 9.0:.1f}" width="3.8" height="{visual.height - 18.0:.1f}" '
            f'rx="2" ry="2" fill="{_escape(p.accent)}" opacity="0.95" />'
        )

    dash = f' stroke-dasharray="{_escape(p.dasharray)}"' if p.dasharray else ""
    subtitle = ""
    if subtitle_text:
        subtitle = (
            f'<text class="node-subtitle" x="{label_x:.1f}" y="{subtitle_y:.1f}" '
            f'font-size="{p.subtitle_size:.1f}" font-weight="600" fill="{_escape(p.subtext)}">{_escape(subtitle_text)}</text>'
        )

    return f"""
    <g class="nodeGroup" opacity="{opacity:.3f}">
      <title>{_escape(title)}</title>
      {halo}
      {ring}
      {glow}
      <g filter="url(#shadowNode)">
        <rect x="{visual.x:.1f}" y="{visual.y:.1f}" width="{visual.width:.1f}" height="{visual.height:.1f}"
              rx="{p.radius:.1f}" ry="{p.radius:.1f}"
              fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
              stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}"{dash} />
        {shine}
        {accent_bar}
      </g>
      {_draw_role_chip(visual)}
      {_draw_badges(visual)}
      <text class="node-icon" x="{icon_x:.1f}" y="{label_y:.1f}" fill="{_escape(p.accent)}">{_escape(visual.icon)}</text>
      <text class="node-label" x="{label_x:.1f}" y="{label_y:.1f}"
            font-size="{p.label_size:.1f}" font-weight="{p.text_weight}" fill="{_escape(p.text)}">{_escape(label_text)}</text>
      {subtitle}
    </g>
    """


# ----------------------------
# Panels, header, legend, footer
# ----------------------------

def _count_nodes_by_kind(graph: DependencyGraph) -> dict[str, int]:
    counts = {"package": 0, "module": 0, "external": 0, "note": 0}
    for node in graph.nodes.values():
        counts[node.kind] = counts.get(node.kind, 0) + 1
    return counts


def _view_identity_text(state: AnalysisState) -> tuple[str, str]:
    if state.view == "package":
        return ("Package View", "macro • calm • executive")
    if state.view == "module":
        return ("Module View", "technical • breathable • controlled")
    return ("Focus View", "hero-driven • staged • premium")


def _graph_title(state: AnalysisState) -> str:
    root = _clean_text(state.project_root or state.selected_path)
    if root:
        try:
            return f"Dependency Graph · {Path(root).name}"
        except Exception:
            return f"Dependency Graph · {root}"
    return "Dependency Graph"


def _graph_subtitle(state: AnalysisState, graph: DependencyGraph) -> str:
    primary, identity = _view_identity_text(state)
    parts = [
        primary,
        identity,
        f"preset {state.visibility_preset}",
        f"{len(graph.nodes)} nodos",
        f"{len(graph.edges)} relaciones",
    ]
    if state.view == "focus":
        parts.append(f"foco {_clean_text(state.focus_target) or '(auto)'}")
    if state.visible_external_bucket_count > 0:
        parts.append(f"externos {state.visible_external_bucket_count}")
    if graph.issues:
        parts.append(f"issues {len(graph.issues)}")
    return " • ".join(parts)


def _graph_path_line(state: AnalysisState) -> str:
    path_value = _clean_text(state.project_root or state.selected_path)
    return _safe_short(path_value, 130)


def _draw_header(width: int, state: AnalysisState, graph: DependencyGraph, theme: SemanticTheme) -> str:
    p = _resolve_panel_preset(theme, "header")
    primary, identity = _view_identity_text(state)
    title = _graph_title(state)
    subtitle = _graph_subtitle(state, graph)
    path_line = _graph_path_line(state)

    header_x = LEFT_MARGIN - 8.0
    header_y = 18.0
    header_w = width - (LEFT_MARGIN * 2) - 18.0
    header_h = 96.0

    identity_w = _chip_width(primary) + 44.0
    identity_x = header_x + header_w - identity_w - 16.0
    identity_y = header_y + 16.0
    title_limit = _text_limit_for_width(header_w - identity_w - 54.0, 31.0, min_chars=14, max_chars=120)
    subtitle_limit = _text_limit_for_width(header_w - 30.0, 13.0, min_chars=20, max_chars=240)
    path_limit = _text_limit_for_width(header_w - 30.0, 11.5, min_chars=20, max_chars=220)
    identity_limit = _text_limit_for_width(identity_w + 12.0, 10.0, min_chars=10, max_chars=44)
    title_text = _safe_short(title, title_limit)
    subtitle_text = _safe_short(subtitle, subtitle_limit)
    path_text = _safe_short(path_line, path_limit)
    identity_text = _safe_short(identity, identity_limit)

    return f"""
    <g class="headerPanel">
      <rect x="{header_x:.1f}" y="{header_y:.1f}" width="{header_w:.1f}" height="{header_h:.1f}"
            rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}"
            filter="url(#shadowSoft)" />
      <rect x="{header_x + 12.0:.1f}" y="{header_y + 12.0:.1f}" width="4.0" height="{header_h - 24.0:.1f}"
            rx="2" ry="2" fill="{_escape(p.accent)}" opacity="0.84" />
      <text class="svg-title" x="{LEFT_MARGIN + 10.0:.1f}" y="{header_y + 38.0:.1f}">{_escape(title_text)}</text>
      <text class="svg-subtitle" x="{LEFT_MARGIN + 10.0:.1f}" y="{header_y + 58.0:.1f}">{_escape(subtitle_text)}</text>
      <text class="svg-meta" x="{LEFT_MARGIN + 10.0:.1f}" y="{header_y + 78.0:.1f}">{_escape(path_text)}</text>

      <g transform="translate({identity_x:.1f},{identity_y:.1f})">
        <rect x="0" y="0" width="{identity_w:.1f}" height="26" rx="13" ry="13"
              fill="{_escape(_mix_hex(p.accent, p.fill, 0.20))}" opacity="0.92" />
        <circle cx="16" cy="13" r="4.2" fill="{_escape(p.accent)}" />
        <text class="chip-text" x="{identity_w / 2 + 8.0:.1f}" y="16.0" text-anchor="middle"
              fill="{_escape(p.title)}">{_escape(primary.upper())}</text>
      </g>
      <text class="panel-meta" x="{identity_x + identity_w:.1f}" y="{identity_y + 40.0:.1f}" text-anchor="end" fill="{_escape(p.meta)}">{_escape(identity_text)}</text>
    </g>
    """


def _draw_warning_panel(width: int, state: AnalysisState, theme: SemanticTheme) -> str:
    if not state.truncated or not _clean_text(state.limit_reason):
        return ""

    p = _resolve_panel_preset(theme, "warning")
    text = _safe_short(state.limit_reason, 120)
    x = LEFT_MARGIN
    y = 120.0
    w = min(620.0, max(320.0, 18.0 + (len(text) * 7.0)))
    h = 30.0

    return f"""
    <g class="warningPanel">
      <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"
            rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}" />
      <circle cx="{x + 14.0:.1f}" cy="{y + 15.0:.1f}" r="4.0" fill="{_escape(p.accent)}" />
      <text class="panel-text" x="{x + 28.0:.1f}" y="{y + 19.0:.1f}" fill="{_escape(p.text)}">{_escape(text)}</text>
    </g>
    """


def _draw_legend(
    width: int,
    graph: DependencyGraph,
    state: AnalysisState,
    theme: SemanticTheme,
    *,
    x: Optional[float] = None,
    y: float = 28.0,
    w: float = 286.0,
) -> tuple[str, float]:
    p = _resolve_panel_preset(theme, "legend")
    counts = _count_nodes_by_kind(graph)
    if x is None:
        x = max(LEFT_MARGIN + 12.0, width - 324.0)
    h = 176.0

    hint = "sin issues relevantes"
    if state.truncated and _clean_text(state.limit_reason):
        hint = _safe_short(state.limit_reason, 34)
    elif graph.issues:
        hint = f"issues visibles {len(graph.issues)}"

    items = [
        ("package", "paquetes", counts.get("package", 0), theme.node_presets["package"]["stroke"]),
        ("module", "módulos", counts.get("module", 0), theme.node_presets["module"]["stroke"]),
        ("external", "externos", counts.get("external", 0), theme.node_presets["external"]["stroke"]),
        ("note", "notas", counts.get("note", 0), theme.node_presets["note"]["stroke"]),
    ]

    rows: list[str] = []
    y_cursor = 44.0
    for _, label, value, color in items:
        rows.append(
            f'<circle cx="18" cy="{y_cursor - 4.0:.1f}" r="5" fill="{_escape(color)}" />'
            f'<text class="panel-text" x="32" y="{y_cursor:.1f}" fill="{_escape(p.text)}">{_escape(label)}</text>'
            f'<text class="panel-text" x="{w - 16.0:.1f}" y="{y_cursor:.1f}" text-anchor="end" fill="{_escape(p.title)}">{value}</text>'
        )
        y_cursor += 22.0

    rows.append(
        f'<text class="panel-text" x="14" y="{y_cursor + 4.0:.1f}" fill="{_escape(p.text)}">relaciones</text>'
        f'<text class="panel-text" x="{w - 16.0:.1f}" y="{y_cursor + 4.0:.1f}" text-anchor="end" fill="{_escape(p.title)}">{len(graph.edges)}</text>'
    )
    y_cursor += 24.0
    rows.append(
        f'<text class="panel-text" x="14" y="{y_cursor + 4.0:.1f}" fill="{_escape(p.text)}">vista</text>'
        f'<text class="panel-text" x="{w - 16.0:.1f}" y="{y_cursor + 4.0:.1f}" text-anchor="end" fill="{_escape(p.title)}">{_escape(state.view)}</text>'
    )
    y_cursor += 24.0
    rows.append(
        f'<text class="panel-meta" x="14" y="{y_cursor + 2.0:.1f}" fill="{_escape(p.meta)}">{_escape(hint)}</text>'
    )

    clip_id = f"legendClip_{int(x)}_{int(y)}"
    return (
        f"""
    <g class="legendPanel">
      <defs>
        <clipPath id="{clip_id}">
          <rect x="{x + 18.0:.1f}" y="{y + 12.0:.1f}" width="{w - 36.0:.1f}" height="{h - 22.0:.1f}" />
        </clipPath>
      </defs>
      <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"
            rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}"
            filter="url(#shadowSoft)" />
      <rect x="{x + 14.0:.1f}" y="{y + 14.0:.1f}" width="3.6" height="{h - 28.0:.1f}" rx="2" ry="2"
            fill="{_escape(p.accent)}" opacity="0.70" />
      <g transform="translate({x + 18.0:.1f},{y + 12.0:.1f})" clip-path="url(#{clip_id})">
        <text class="panel-title" x="10" y="10" fill="{_escape(p.title)}">Resumen</text>
        {''.join(rows)}
      </g>
    </g>
    """,
        h,
    )


def _draw_visibility_panel(
    width: int,
    state: AnalysisState,
    theme: SemanticTheme,
    *,
    x: Optional[float] = None,
    y: float = 214.0,
    w: float = 286.0,
) -> tuple[str, float]:
    show_panel = (
        state.visibility_preset != "raw"
        or state.external_roots_total > 0
        or state.hidden_issue_count > 0
    )
    if not show_panel:
        return ("", 0.0)

    p = _resolve_panel_preset(theme, "legend")
    if x is None:
        x = max(LEFT_MARGIN + 12.0, width - 324.0)

    top_roots = ", ".join(state.external_top_roots[:3]) if state.external_top_roots else "sin dominantes"
    visible_buckets = ", ".join(state.visible_external_bucket_labels[:3]) if state.visible_external_bucket_labels else "ninguno"
    if state.visibility_preset == "raw":
        external_mode = "inline"
    elif state.visible_external_bucket_count > 0:
        external_mode = "bucket inline"
    else:
        external_mode = "fuera del canvas"
    issue_mode = "inline" if should_surface_issue_notes(state) else "panel/footer"

    lines = [
        ("preset", state.visibility_preset),
        ("externos", f"{state.external_import_total} refs • {state.external_roots_total} roots • {external_mode}"),
        ("top externos", top_roots),
        ("buckets visibles", visible_buckets),
        ("issues", f"{state.hidden_issue_count} fuera del canvas • {issue_mode}"),
    ]

    h = 34.0 + (len(lines) * 22.0) + 10.0
    value_limit = _text_limit_for_width(w - 120.0, 11.0, min_chars=12, max_chars=48)
    clip_id = f"visibilityClip_{int(x)}_{int(y)}"
    rows: list[str] = []
    y_cursor = 40.0
    for label, value in lines:
        rows.append(
            f'<text class="panel-text" x="14" y="{y_cursor:.1f}" fill="{_escape(p.text)}">{_escape(label)}</text>'
            f'<text class="panel-text" x="{w - 16.0:.1f}" y="{y_cursor:.1f}" text-anchor="end" fill="{_escape(p.title)}">{_escape(_safe_short(value, value_limit))}</text>'
        )
        y_cursor += 22.0

    return (
        f"""
    <g class="visibilityPanel">
      <defs>
        <clipPath id="{clip_id}">
          <rect x="{x + 18.0:.1f}" y="{y + 12.0:.1f}" width="{w - 36.0:.1f}" height="{h - 22.0:.1f}" />
        </clipPath>
      </defs>
      <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"
            rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}"
            filter="url(#shadowSoft)" />
      <rect x="{x + 14.0:.1f}" y="{y + 14.0:.1f}" width="3.6" height="{h - 28.0:.1f}" rx="2" ry="2"
            fill="{_escape(p.accent)}" opacity="0.70" />
      <g transform="translate({x + 18.0:.1f},{y + 12.0:.1f})" clip-path="url(#{clip_id})">
        <text class="panel-title" x="10" y="10" fill="{_escape(p.title)}">Surface Control</text>
        {''.join(rows)}
      </g>
    </g>
    """,
        h,
    )


def _build_state_summary(state: AnalysisState) -> str:
    parts = [
        f"{state.source_files_seen} fuentes",
        f"{state.parsed_files} parseados",
        f"{state.total_nodes} nodos",
        f"{state.total_edges} relaciones",
        f"vista {state.view}",
        f"tema {state.theme}",
    ]
    if state.truncated:
        parts.append("análisis truncado")
    return " • ".join(parts)


def _draw_footer(width: int, height: int, state: AnalysisState, theme: SemanticTheme) -> str:
    p = _resolve_panel_preset(theme, "footer")
    summary = _build_state_summary(state)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    x = LEFT_MARGIN - 2.0
    y = height - 36.0
    w = width - (LEFT_MARGIN * 2) + 4.0
    h = 22.0

    return f"""
    <g class="footerPanel">
      <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"
            rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}" />
      <text class="svg-footer" x="{LEFT_MARGIN + 10.0:.1f}" y="{y + 14.5:.1f}">{_escape(_safe_short(summary, 130))}</text>
      <text class="svg-footer" x="{width - RIGHT_MARGIN:.1f}" y="{y + 14.5:.1f}" text-anchor="end">{_escape('Generado: ' + generated_at)}</text>
    </g>
    """


# ----------------------------
# Layer draw orchestration
# ----------------------------

def _draw_lanes(lanes: list[ResolvedLaneVisual], height: int) -> str:
    return "".join(_draw_lane(item, height) for item in lanes)


def _draw_edges(edges: list[ResolvedEdgeVisual]) -> str:
    return "".join(_draw_edge(item) for item in edges)


def _draw_nodes(nodes: list[ResolvedNodeVisual]) -> str:
    ordered = sorted(nodes, key=lambda item: (item.layer, item.emphasis, item.y, item.x))
    return "".join(_draw_node(item) for item in ordered)


def _empty_state_svg(width: int, height: int, theme: SemanticTheme, state: AnalysisState) -> str:
    p = _resolve_panel_preset(theme, "legend")
    cx = width / 2.0
    cy = max(220.0, height / 2.0)

    return f"""
    <g class="emptyState">
      <circle cx="{cx:.1f}" cy="{cy - 20.0:.1f}" r="28" fill="{_escape(_mix_hex(p.accent, p.fill, 0.30))}" opacity="0.40" />
      <text class="svg-title" x="{cx:.1f}" y="{cy + 4.0:.1f}" text-anchor="middle" font-size="24">No hay elementos visibles</text>
      <text class="svg-subtitle" x="{cx:.1f}" y="{cy + 28.0:.1f}" text-anchor="middle">La vista {_escape(state.view)} no produjo nodos renderizables.</text>
    </g>
    """


# ----------------------------
# Public API
# ----------------------------

def render_svg(
    graph: DependencyGraph,
    layout: LayoutResult,
    state: AnalysisState,
    notify: Callable[[str, str], None],
) -> str:
    notify("Resolviendo tema visual...", state.theme)

    resolver = globals().get("resolve_render_theme")
    if callable(resolver):
        theme_source = resolver(state.theme)
    else:
        theme_source = resolve_theme_bundle(state.theme)

    semantic_theme = _resolve_semantic_theme(theme_source, state.theme)

    content_width = max(1080, int(layout.width or 1080))
    sidebar_width = 332
    width = content_width + sidebar_width
    height = max(360, int(layout.height or 360))

    notify("Resolviendo semántica visual...", f"{len(layout.nodes)} nodos • {len(graph.edges)} edges")
    resolved_lanes = _resolve_lane_visuals(layout, state, semantic_theme)
    resolved_edges = _resolve_edge_visuals(graph, layout, state, semantic_theme)
    resolved_nodes = _resolve_node_visuals(graph, layout, state, semantic_theme)

    notify("Dibujando carriles...", f"{len(resolved_lanes)} carriles")
    lanes_markup = _draw_lanes(resolved_lanes, height)

    notify("Dibujando conexiones...", f"{len(resolved_edges)} relaciones")
    edges_markup = _draw_edges(resolved_edges)

    notify("Pintando nodos...", f"{len(resolved_nodes)} nodos visibles")
    nodes_markup = _draw_nodes(resolved_nodes)

    sidebar_x = content_width + 18.0
    header_markup = _draw_header(content_width, state, graph, semantic_theme)
    legend_markup, legend_h = _draw_legend(width, graph, state, semantic_theme, x=sidebar_x, y=28.0, w=286.0)
    visibility_markup, _ = _draw_visibility_panel(
        width,
        state,
        semantic_theme,
        x=sidebar_x,
        y=28.0 + legend_h + 12.0,
        w=286.0,
    )
    warning_markup = _draw_warning_panel(content_width, state, semantic_theme)
    footer_markup = _draw_footer(content_width, height, state, semantic_theme)

    empty_markup = ""
    if not layout.nodes:
        empty_markup = _empty_state_svg(width, height, semantic_theme, state)

    canvas_bg = _clean_text(semantic_theme.tokens.get("canvas_bg")) or "#0b1224"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="xMinYMin meet" style="display:block;width:100%;height:auto;background:{_escape(canvas_bg)};">
  {semantic_theme.svg_defs}
  {_build_semantic_defs(semantic_theme, width, height)}

  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#semanticCanvasGrad)" />
  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#semanticGrid)" />
  <circle cx="{int(width * 0.16)}" cy="{int(height * 0.08)}" r="{int(max(width, height) * 0.62)}" fill="url(#semanticHaloA)" />
  <circle cx="{int(width * 0.86)}" cy="{int(height * 0.16)}" r="{int(max(width, height) * 0.36)}" fill="url(#semanticHaloB)" />

  {header_markup}
  {legend_markup}
  {visibility_markup}
  {warning_markup}

  <g id="lanesLayer">{lanes_markup}</g>
  <g id="edgesLayer">{edges_markup}</g>
  <g id="nodesLayer">{nodes_markup}</g>

  {empty_markup}
  {footer_markup}
</svg>
"""


# ============================================================
# 10.B VISUAL CONTROL LAYER (SIDECAR)
# ============================================================

VisualSurfaceKind = Literal[
    "qt_ui",
    "qt_backdrop",
    "svg_theme",
    "svg_panel",
    "svg_render",
    "pipeline",
    "guide",
]

VisualRelationKind = Literal[
    "drives",
    "styles",
    "renders",
    "exports",
    "points_to",
    "owns",
]

VISUAL_CONTROL_OUTPUT_PREFIX = "visual_control_map"
VISUAL_CONTROL_NOTE_GROUP = "visual_guide"
VISUAL_CONTROL_MODULE_NAMESPACE = "visual"


@dataclass(slots=True)
class VisualTargetRef:
    symbol: str
    kind: str = "function"
    path_hint: str = "code-atlas.py"
    note: str = ""


@dataclass(slots=True)
class VisualControlSpec:
    key: str
    label: str
    group: str
    surface_kind: VisualSurfaceKind
    description: str
    why: str
    how_to_change: str
    targets: list[VisualTargetRef] = field(default_factory=list)
    tips: list[str] = field(default_factory=list)
    tags: tuple[str, ...] = field(default_factory=tuple)
    priority: int = 50


@dataclass(slots=True)
class VisualControlEdgeSpec:
    source: str
    target: str
    label: str
    relation: VisualRelationKind = "drives"
    weight: int = 1


@dataclass(slots=True)
class VisualControlArtifactPaths:
    svg_path: Path
    markdown_path: Path
    json_path: Path
    forensics_json_path: Path


@dataclass(slots=True)
class VisualControlExportResult:
    paths: VisualControlArtifactPaths
    graph: Any
    state: Any
    registry: dict[str, VisualControlSpec]
    forensics_summary: dict[str, Any] = field(default_factory=dict)


def _vc_clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).strip()


def _vc_safe_slug(value: Any) -> str:
    text = _vc_clean_text(value)
    if not text:
        return "graph"

    forbidden = '<>:"/\\|?*'
    safe = "".join(ch if ch not in forbidden else "_" for ch in text)
    safe = safe.replace(" ", "_").strip("._")
    return safe or "graph"


def _vc_date_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _vc_notify(notify: Optional[Callable[[str, str], None]], title: str, detail: str = "") -> None:
    if callable(notify):
        notify(title, detail)


def _vc_output_dir(selected_path: str) -> Path:
    resolver = globals().get("resolve_output_dir")
    if callable(resolver):
        return Path(resolver(selected_path))

    base = Path(selected_path).expanduser().resolve()
    if base.is_file():
        base = base.parent
    return base / "_dependency_graphs"


def _vc_ensure_output_dir(path: Path) -> None:
    ensure = globals().get("ensure_output_dir")
    if callable(ensure):
        ensure(path)
        return
    path.mkdir(parents=True, exist_ok=True)


def _vc_module_key(spec_key: str) -> str:
    maker = globals().get("make_module_key")
    dotted = f"{VISUAL_CONTROL_MODULE_NAMESPACE}.{spec_key}"
    if callable(maker):
        return maker(dotted)
    return f"module:{dotted}"


def _vc_note_key(name: str) -> str:
    return f"note:{VISUAL_CONTROL_NOTE_GROUP}:{_vc_safe_slug(name)}"


def _vc_group_label(group: str) -> str:
    return group.replace("_", " ").strip().title()


def build_visual_control_specs() -> dict[str, VisualControlSpec]:
    specs: list[VisualControlSpec] = [
        VisualControlSpec(
            key="qt_shadow_blur",
            label="Qt Blur / Shadow",
            group="ui_qt",
            surface_kind="qt_ui",
            description="Controla el blur, offset, alpha y color de sombras para cards, botones, shells y paneles Qt.",
            why="Si quieres que una pieza se vea más suave, más elevada o más pesada visualmente, aquí es donde realmente se mueve la aguja.",
            how_to_change="Ajusta blur, x_offset, y_offset, alpha y color en apply_shadow(...). Luego revisa dónde lo invocan header, form_card, preview_card, footer, hero, body y create_button(...).",
            targets=[
                VisualTargetRef("apply_shadow", "function", note="Motor principal de sombra Qt"),
                VisualTargetRef("create_button", "function", note="Aplica shadow por variante de botón"),
            ],
            tips=[
                "Más blur y menos alpha = sombra más premium y más difusa.",
                "Más y_offset con blur medio = sensación de elevación.",
                "Si el botón se siente muy pesado, baja alpha antes de bajar blur.",
            ],
            tags=("blur", "shadow", "elevation", "qt"),
            priority=100,
        ),
        VisualControlSpec(
            key="qt_stylesheet_shell",
            label="Qt Panel / Shell Styles",
            group="ui_qt",
            surface_kind="qt_ui",
            description="Define bordes, radius, rellenos, gradientes y acabados visuales de shell, cards, footer y chrome en PySide.",
            why="Si quieres tocar marco, fondo, radio de esquinas o lectura visual de un panel Qt, esta es la mesa de mezclas correcta.",
            how_to_change="Edita build_app_stylesheet(theme_id). Si el cambio es global, empieza ahí; si es local, luego afina el QFrame o property correspondiente en _build_ui().",
            targets=[
                VisualTargetRef("build_app_stylesheet", "function", note="Catálogo CSS de la UI PySide"),
                VisualTargetRef("app_stylesheet", "function", note="Une base compartida + overrides locales"),
            ],
            tips=[
                "Para cambiar paneles Qt, toca primero CSS y luego el layout solo si de plano hace falta.",
                "Si quieres diferenciar hero/card/footer, usa sus properties card=hero|true|footer|muted.",
            ],
            tags=("panel", "frame", "radius", "border", "qt", "stylesheet"),
            priority=98,
        ),
        VisualControlSpec(
            key="qt_selector_progress_layout",
            label="Qt Selector / Progress Assembly",
            group="ui_qt",
            surface_kind="qt_ui",
            description="Ensamble real de header, form_card, preview_card, footer, hero, body y chips dentro de SelectorDialog y ProgressUI.",
            why="Si preguntas '¿ese panel cuál es?', la respuesta vive aquí, no en el theme y no en el render SVG.",
            how_to_change="Ubica el widget exacto en SelectorDialog._build_ui(), SelectorDialog._build_form_panel(), SelectorDialog._build_preview_panel() o ProgressUI._build_ui().",
            targets=[
                VisualTargetRef("SelectorDialog._build_ui", "method", note="Shell principal y cards del selector"),
                VisualTargetRef("SelectorDialog._build_form_panel", "method", note="Panel izquierdo / opciones"),
                VisualTargetRef("SelectorDialog._build_preview_panel", "method", note="Panel derecho / preview"),
                VisualTargetRef("ProgressUI._build_ui", "method", note="Consola de progreso"),
            ],
            tips=[
                "Si quieres mover o renombrar paneles Qt, empieza aquí.",
                "Si el panel correcto ya está ubicado, luego te vas a stylesheet o apply_shadow según el tipo de ajuste.",
            ],
            tags=("selector", "progress", "panel", "widget", "qt"),
            priority=95,
        ),
        VisualControlSpec(
            key="qt_hover_and_dividers",
            label="Qt Hover / Dividers / Micro-UX",
            group="ui_qt",
            surface_kind="qt_ui",
            description="Controla hover de cards, repolish y separadores visuales secundarios en la UI PySide.",
            why="Sirve cuando el look general ya está bien, pero quieres afinar la respuesta al mouse y el micro-ritmo visual.",
            how_to_change="Ajusta enable_card_hover(...), _HoverCardFilter y make_separator(). Si el widget necesita reaccionar más o menos, este es el corredor correcto.",
            targets=[
                VisualTargetRef("enable_card_hover", "function"),
                VisualTargetRef("_HoverCardFilter", "class"),
                VisualTargetRef("make_separator", "function"),
                VisualTargetRef("repolish", "function"),
            ],
            tips=[
                "Hover excesivo rompe elegancia antes que ayudar.",
                "Los separadores ayudan más por contraste que por grosor.",
            ],
            tags=("hover", "divider", "separator", "micro ux", "qt"),
            priority=72,
        ),
        VisualControlSpec(
            key="qt_window_chrome",
            label="Qt Window Chrome / Resize",
            group="ui_qt",
            surface_kind="qt_ui",
            description="Barra de ventana, drag, maximize/restore y esquinas de resize para diálogos frameless.",
            why="Cuando quieres tocar controles de ventana o sensación de app flotante, esto no vive en el backdrop ni en el stylesheet normal del panel.",
            how_to_change="Edita WindowChromeBar, FramelessResizeController y _FramelessResizeCorner. Ahí vive el comportamiento del marco vivo.",
            targets=[
                VisualTargetRef("WindowChromeBar", "class"),
                VisualTargetRef("FramelessResizeController", "class"),
                VisualTargetRef("_FramelessResizeCorner", "class"),
            ],
            tips=[
                "Si solo quieres color o fondo del chrome, ve primero a build_app_stylesheet().",
                "Si quieres comportamiento, ve a estas clases, no al theme.",
            ],
            tags=("window", "chrome", "resize", "frameless", "qt"),
            priority=68,
        ),
        VisualControlSpec(
            key="qt_backdrop_palette",
            label="Glass Backdrop Palette",
            group="qt_backdrop",
            surface_kind="qt_backdrop",
            description="Paleta, mezclas, halos y decisión de variante selector/progress para el fondo glass de PySide.",
            why="Si el mood del backdrop se siente demasiado frío, saturado o plano, aquí nace esa atmósfera.",
            how_to_change="Modifica _glass_palette(...), _qcolor_from_value(...) y _is_silver_theme_id(...). Este bloque define el lenguaje cromático del backdrop.",
            targets=[
                VisualTargetRef("_glass_palette", "function"),
                VisualTargetRef("_qcolor_from_value", "function"),
                VisualTargetRef("_is_silver_theme_id", "function"),
            ],
            tips=[
                "Si quieres cambio global del backdrop, toca paleta antes que paintEvent().",
                "Los halos y sheens nacen aquí, no en build_app_stylesheet().",
            ],
            tags=("backdrop", "glass", "palette", "halo", "qt"),
            priority=92,
        ),
        VisualControlSpec(
            key="qt_backdrop_painter",
            label="Glass Backdrop Painter",
            group="qt_backdrop",
            surface_kind="qt_backdrop",
            description="Motor de dibujo del fondo glass: orbs, stars, spark flashes, sheen, vignette y campos de plata.",
            why="Si quieres mover brillo, partículas, trayectorias o densidad del fondo, éste es el taller correcto.",
            how_to_change="Ajusta FrostedGlassBackdrop.paintEvent(...) y sus helpers _orb_specs, _paint_stars, _paint_spark_flashes, _paint_silver_field y bandas asociadas.",
            targets=[
                VisualTargetRef("FrostedGlassBackdrop.paintEvent", "method"),
                VisualTargetRef("FrostedGlassBackdrop._orb_specs", "method"),
                VisualTargetRef("FrostedGlassBackdrop._paint_stars", "method"),
                VisualTargetRef("FrostedGlassBackdrop._paint_spark_flashes", "method"),
                VisualTargetRef("FrostedGlassBackdrop._paint_silver_field", "method"),
            ],
            tips=[
                "Color = paleta. Movimiento y densidad = painter.",
                "Si algo parpadea demasiado, suele estar aquí y no en el theme SVG.",
            ],
            tags=("backdrop", "particles", "stars", "glass", "qt"),
            priority=94,
        ),
        VisualControlSpec(
            key="svg_theme_root",
            label="SVG Theme Root",
            group="svg_theme",
            surface_kind="svg_theme",
            description="Raíz del contrato visual semántico del SVG. De aquí nacen presets de nodos, edges, lanes, panels, badges, markers y defs.",
            why="Si el cambio es global y semántico, no se corrige parche por parche: se baja aquí y se propaga bonito.",
            how_to_change="Empieza por _build_semantic_theme(...), ThemeBundle y resolve_render_theme(...). Este bloque decide qué bundle manda en render.",
            targets=[
                VisualTargetRef("ThemeBundle", "class"),
                VisualTargetRef("_build_semantic_theme", "function"),
                VisualTargetRef("resolve_render_theme", "function"),
            ],
            tips=[
                "Tema completo = aquí. Ajuste puntual de panel SVG = _build_panel_presets().",
                "No metas reglas de tema Qt aquí; esto gobierna el SVG semántico.",
            ],
            tags=("theme", "bundle", "svg", "semantic"),
            priority=100,
        ),
        VisualControlSpec(
            key="svg_panel_presets",
            label="SVG Panel Presets",
            group="svg_theme",
            surface_kind="svg_panel",
            description="Preset de header, legend, footer y warning del SVG con fill, stroke, text_fill, meta_fill, opacity y glow.",
            why="Si la pregunta es 'quiero ese panel del SVG diferente', esta es la respuesta más directa.",
            how_to_change="Edita _build_panel_presets(tokens). Cambia fill/stroke/text_fill/meta_fill/fill_opacity según el panel que quieras afinar.",
            targets=[
                VisualTargetRef("_build_panel_presets", "function"),
            ],
            tips=[
                "Panel de SVG no es igual a panel de Qt. No cruces cables.",
                "Header/legend/footer/warning salen de este catálogo.",
            ],
            tags=("svg", "panel", "legend", "header", "footer", "warning"),
            priority=97,
        ),
        VisualControlSpec(
            key="svg_filters",
            label="SVG Filters / Glow",
            group="svg_theme",
            surface_kind="svg_theme",
            description="Define glow, edge blur y node shadow del SVG mediante filters y preset intensities.",
            why="Si quieres blur, glow o shadow del artefacto SVG final, aquí vive la perilla real.",
            how_to_change="Ajusta _build_filters(bundle) y sus intensidades derivadas de effect_presets. Este bloque transforma presets en filtros SVG reales.",
            targets=[
                VisualTargetRef("_build_filters", "function"),
            ],
            tips=[
                "Blur del SVG no pasa por apply_shadow().",
                "Si el SVG está muy neón, baja glow_intensity o stdDeviation aquí.",
            ],
            tags=("svg", "filter", "glow", "blur", "shadow"),
            priority=99,
        ),
        VisualControlSpec(
            key="svg_theme_defs",
            label="SVG Theme Defs",
            group="svg_theme",
            surface_kind="svg_theme",
            description="Empaqueta gradients, grid pattern, filters, markers y CSS final en el bloque <defs> del SVG temático.",
            why="Si un asset visual del theme no aparece en render, suele faltarle camino por aquí.",
            how_to_change="Edita _build_theme_svg_defs(bundle) y revisa _build_gradients, _build_grid_pattern, _build_filters, _build_markers y _build_theme_css.",
            targets=[
                VisualTargetRef("_build_theme_svg_defs", "function"),
                VisualTargetRef("_build_gradients", "function"),
                VisualTargetRef("_build_grid_pattern", "function"),
                VisualTargetRef("_build_markers", "function"),
                VisualTargetRef("_build_theme_css", "function"),
            ],
            tips=[
                "Si el preset existe pero no se ve, sigue la cadena hasta defs.",
            ],
            tags=("svg", "defs", "gradient", "marker", "css"),
            priority=91,
        ),
        VisualControlSpec(
            key="svg_header_legend_footer",
            label="SVG Panels Drawn",
            group="svg_render",
            surface_kind="svg_panel",
            description="Dibujo concreto de header, warning panel, legend, visibility panel y footer del SVG final.",
            why="Aquí se decide geometría real, copy, tamaños y composición de paneles ya en pantalla.",
            how_to_change="Toca _draw_header(...), _draw_warning_panel(...), _draw_legend(...), _draw_visibility_panel(...) y _draw_footer(...).",
            targets=[
                VisualTargetRef("_draw_header", "function"),
                VisualTargetRef("_draw_warning_panel", "function"),
                VisualTargetRef("_draw_legend", "function"),
                VisualTargetRef("_draw_visibility_panel", "function"),
                VisualTargetRef("_draw_footer", "function"),
            ],
            tips=[
                "Preset define color. Draw decide tamaño, copy y posición.",
            ],
            tags=("svg", "header", "legend", "footer", "panel"),
            priority=96,
        ),
        VisualControlSpec(
            key="svg_nodes",
            label="SVG Nodes Composition",
            group="svg_render",
            surface_kind="svg_render",
            description="Resuelve la semántica visual de nodos y los dibuja con icono, label, subtitle, badges, chips y layers.",
            why="Si quieres que 'el cuadrito' cambie de carácter, densidad o composición interna, este bloque manda.",
            how_to_change="Modifica _resolve_node_visuals(...), _draw_nodes(...), _draw_single_node(...), _draw_role_chip(...) y _draw_badges(...).",
            targets=[
                VisualTargetRef("_resolve_node_visuals", "function"),
                VisualTargetRef("_draw_nodes", "function"),
                VisualTargetRef("_draw_single_node", "function"),
                VisualTargetRef("_draw_role_chip", "function"),
                VisualTargetRef("_draw_badges", "function"),
            ],
            tips=[
                "Color/preset del nodo nace en theme. La anatomía visual del nodo vive aquí.",
            ],
            tags=("svg", "nodes", "badges", "chips", "labels"),
            priority=97,
        ),
        VisualControlSpec(
            key="svg_edges",
            label="SVG Edges Composition",
            group="svg_render",
            surface_kind="svg_render",
            description="Calcula y dibuja caminos, capas, tooltip, evidencia y acentos visuales de las relaciones del SVG.",
            why="Si quieres líneas más tensas, suaves, prominentes o trazables a nivel forense, aquí está el telar.",
            how_to_change="Edita _resolve_edge_visuals(...), _draw_edges(...), _draw_edge(...) y los presets que estos consumen.",
            targets=[
                VisualTargetRef("_resolve_edge_visuals", "function"),
                VisualTargetRef("_draw_edges", "function"),
                VisualTargetRef("_draw_edge", "function", note="Aquí vive el hover forense y la tarjeta de evidencia"),
            ],
            tips=[
                "Si solo quieres glow de edge, revisa _build_filters(). Si quieres forma, layering y evidencia visual, ven acá.",
            ],
            tags=("svg", "edges", "relations", "paths", "forensics"),
            priority=90,
        ),
        VisualControlSpec(
            key="svg_lanes",
            label="SVG Lanes Composition",
            group="svg_render",
            surface_kind="svg_render",
            description="Resuelve y dibuja carriles, headers de lane y bandas de contexto dentro del SVG final.",
            why="Si la pregunta es 'ese bloque vertical dónde se controla', la respuesta está aquí.",
            how_to_change="Edita _resolve_lane_visuals(...), _draw_lanes(...) y presets de lanes en el theme.",
            targets=[
                VisualTargetRef("_resolve_lane_visuals", "function"),
                VisualTargetRef("_draw_lanes", "function"),
            ],
            tips=[
                "Layout decide distribución. draw_lanes decide presencia visual del carril.",
            ],
            tags=("svg", "lanes", "bands", "columns"),
            priority=88,
        ),
        VisualControlSpec(
            key="svg_orchestrator",
            label="SVG Render Orchestrator",
            group="svg_render",
            surface_kind="svg_render",
            description="Orquesta tema, capas, ancho/alto, fondo, header, legend, warning, lanes, edges, nodes y footer para producir el SVG final.",
            why="Si quieres entender dónde entra todo al horno final, esta función es la cocina completa.",
            how_to_change="Usa render_svg(...) como punto de verdad para todo el render. Aquí se enchufan theme, defs, draw functions y canvas global.",
            targets=[
                VisualTargetRef("render_svg", "function"),
            ],
            tips=[
                "Cuando el cambio ya toca composición final o sidebars, entra por render_svg(...).",
            ],
            tags=("svg", "render", "orchestrator", "canvas"),
            priority=100,
        ),
        VisualControlSpec(
            key="pipeline_output",
            label="Pipeline Output",
            group="pipeline",
            surface_kind="pipeline",
            description="Punto donde el pipeline calcula layout, renderiza el SVG y escribe el archivo final en disco.",
            why="Es el mejor punto para colgar una capa nueva sin reventar discovery ni el layout original.",
            how_to_change="Hook recomendado: después de layout_dependency_graph(...) y antes o después de write_svg(...), según quieras sidecar o híbrido. También puedes exportar una guía paralela desde main().",
            targets=[
                VisualTargetRef("layout_dependency_graph", "function"),
                VisualTargetRef("write_svg", "function"),
                VisualTargetRef("main", "function"),
            ],
            tips=[
                "Si quieres añadir una capa nueva sin tocar demasiado, este es el injerto más limpio.",
            ],
            tags=("pipeline", "output", "layout", "write", "hook"),
            priority=100,
        ),
        VisualControlSpec(
            key="visual_sidecar_exports",
            label="Visual Guide Sidecar Exports",
            group="pipeline",
            surface_kind="guide",
            description="Exporta sidecar SVG + JSON + Markdown con el mapa de control visual, sin tocar el análisis de dependencias real.",
            why="Es la forma limpia de añadir la capa nueva: paralela, auditable y fácil de apagar o encender.",
            how_to_change="Usa export_visual_control_sidecar(...) y cuélgalo después del write_svg(...) principal o detrás de un flag. Así no invades el core.",
            targets=[
                VisualTargetRef("export_visual_control_sidecar", "function", note="Nueva API recomendada"),
                VisualTargetRef("render_visual_control_markdown", "function", note="Nueva guía Markdown"),
                VisualTargetRef("render_visual_control_svg_markup", "function", note="Nuevo render sidecar SVG"),
            ],
            tips=[
                "Sidecar separado = menos riesgo y más claridad.",
            ],
            tags=("sidecar", "markdown", "json", "svg", "guide"),
            priority=100,
        ),
    ]
    return {spec.key: spec for spec in specs}


def build_visual_control_edges() -> list[VisualControlEdgeSpec]:
    return [
        VisualControlEdgeSpec("qt_stylesheet_shell", "qt_selector_progress_layout", "styles"),
        VisualControlEdgeSpec("qt_shadow_blur", "qt_selector_progress_layout", "shadows"),
        VisualControlEdgeSpec("qt_hover_and_dividers", "qt_selector_progress_layout", "micro-ux"),
        VisualControlEdgeSpec("qt_window_chrome", "qt_selector_progress_layout", "wraps"),
        VisualControlEdgeSpec("qt_backdrop_palette", "qt_backdrop_painter", "feeds"),
        VisualControlEdgeSpec("qt_backdrop_painter", "qt_selector_progress_layout", "backdrops"),
        VisualControlEdgeSpec("svg_theme_root", "svg_panel_presets", "builds"),
        VisualControlEdgeSpec("svg_theme_root", "svg_filters", "builds"),
        VisualControlEdgeSpec("svg_theme_root", "svg_theme_defs", "packages"),
        VisualControlEdgeSpec("svg_theme_root", "svg_nodes", "styles"),
        VisualControlEdgeSpec("svg_theme_root", "svg_edges", "styles"),
        VisualControlEdgeSpec("svg_theme_root", "svg_lanes", "styles"),
        VisualControlEdgeSpec("svg_panel_presets", "svg_header_legend_footer", "skins"),
        VisualControlEdgeSpec("svg_filters", "svg_theme_defs", "injects"),
        VisualControlEdgeSpec("svg_theme_defs", "svg_orchestrator", "mounts defs"),
        VisualControlEdgeSpec("svg_nodes", "svg_orchestrator", "renders nodes"),
        VisualControlEdgeSpec("svg_edges", "svg_orchestrator", "renders edges"),
        VisualControlEdgeSpec("svg_lanes", "svg_orchestrator", "renders lanes"),
        VisualControlEdgeSpec("svg_header_legend_footer", "svg_orchestrator", "renders panels"),
        VisualControlEdgeSpec("pipeline_output", "visual_sidecar_exports", "hosts sidecar"),
        VisualControlEdgeSpec("svg_orchestrator", "visual_sidecar_exports", "reused by"),
        VisualControlEdgeSpec("pipeline_output", "svg_orchestrator", "calls"),
    ]


def build_visual_control_mermaid() -> str:
    specs = build_visual_control_specs()
    edges = build_visual_control_edges()

    groups: dict[str, list[VisualControlSpec]] = {}
    for spec in specs.values():
        groups.setdefault(spec.group, []).append(spec)

    lines = ["graph TD"]
    for group_name, items in groups.items():
        lines.append(f"  subgraph {group_name}[{_vc_group_label(group_name)}]")
        for spec in sorted(items, key=lambda item: (-item.priority, item.label.lower())):
            lines.append(f"    {spec.key}[\"{spec.label}\"]")
        lines.append("  end")

    for edge in edges:
        lines.append(f"  {edge.source} -->|{edge.label}| {edge.target}")

    return "\n".join(lines)


def _visual_control_note_specs() -> list[tuple[str, str]]:
    return [
        ("Guía • blur/sombra → apply_shadow / create_button", "Si quieres blur o sombra Qt, empieza por apply_shadow(...) y luego revisa dónde se invoca."),
        ("Guía • marco/fondo Qt → build_app_stylesheet", "Si quieres tocar marco, borde, radius o background de panel Qt, empieza por build_app_stylesheet(...)."),
        ("Guía • backdrop glass → _glass_palette / FrostedGlassBackdrop", "Paleta del backdrop en _glass_palette(...); movimiento y partículas en FrostedGlassBackdrop."),
        ("Guía • glow/blur SVG → _build_filters", "Glow, blur y shadow del SVG viven en _build_filters(...), no en apply_shadow(...)."),
        ("Guía • panel SVG → _build_panel_presets / _draw_header|legend|footer", "Preset define skin; draw define geometría y copy."),
        ("Guía • tema completo → _build_semantic_theme", "Si el cambio es global y semántico, baja a _build_semantic_theme(...)."),
    ]


def build_visual_control_dependency_graph(*, include_notes: bool = True) -> Any:
    graph_cls = globals().get("DependencyGraph")
    if graph_cls is None:
        raise RuntimeError("DependencyGraph no está disponible. Esta capa debe vivir dentro de code-atlas.py o importar su core.")

    graph = graph_cls()
    specs = build_visual_control_specs()

    for spec in specs.values():
        targets_summary = ", ".join(target.symbol for target in spec.targets)
        graph.upsert_node(
            key=_vc_module_key(spec.key),
            label=spec.label,
            path=targets_summary or spec.group,
            kind="module",
            group=spec.group,
            metadata={
                "module_name": f"{VISUAL_CONTROL_MODULE_NAMESPACE}.{spec.key}",
                "relative_path": targets_summary,
                "root_group": spec.group,
                "visual_control": True,
                "visual_key": spec.key,
                "visual_description": spec.description,
                "visual_why": spec.why,
                "visual_how_to_change": spec.how_to_change,
                "visual_targets": [
                    {
                        "symbol": target.symbol,
                        "kind": target.kind,
                        "path_hint": target.path_hint,
                        "note": target.note,
                    }
                    for target in spec.targets
                ],
                "visual_tips": list(spec.tips),
                "visual_tags": list(spec.tags),
                "visual_priority": spec.priority,
            },
        )

    for edge in build_visual_control_edges():
        graph.add_edge(
            _vc_module_key(edge.source),
            _vc_module_key(edge.target),
            kind="import",
            evidence=edge.label,
        )

    if include_notes:
        for index, (title, message) in enumerate(_visual_control_note_specs(), start=1):
            graph.upsert_node(
                key=_vc_note_key(f"guide_{index}"),
                label=title,
                path="visual control guide",
                kind="note",
                group=VISUAL_CONTROL_NOTE_GROUP,
                metadata={
                    "full_message": message,
                    "issue_level": "info",
                    "issue_code": f"visual_guide_{index}",
                    "issue_path": "visual-control",
                    "root_group": VISUAL_CONTROL_NOTE_GROUP,
                },
            )

    graph.finalize_metrics()
    return graph


def build_visual_control_state(
    *,
    selected_path: str,
    theme_id: str,
    view: GraphView = "module",
    focus_target: str = "",
) -> Any:
    state_cls = globals().get("AnalysisState")
    if state_cls is None:
        raise RuntimeError("AnalysisState no está disponible. Esta capa debe vivir dentro de code-atlas.py o importar su core.")

    root_resolver = globals().get("derive_project_root")
    project_root = selected_path
    if callable(root_resolver):
        try:
            project_root = str(root_resolver(selected_path))
        except Exception:
            project_root = selected_path

    state = state_cls(
        selected_path=str(selected_path),
        project_root=str(project_root),
        theme=_vc_clean_text(theme_id) or "silver_frost_cyan",
        view=view,
        focus_target=_vc_clean_text(focus_target),
        visibility_preset="raw",
    )
    return state


def _visual_control_file_stem(selected_path: str, theme_id: str) -> str:
    base_name = Path(selected_path).expanduser().name if _vc_clean_text(selected_path) else "workspace"
    base_name = _vc_safe_slug(base_name or "workspace")
    theme_part = _vc_safe_slug(theme_id or "theme")
    return f"{VISUAL_CONTROL_OUTPUT_PREFIX}_{base_name}_{theme_part}_{_vc_date_stamp()}"


def build_visual_control_output_paths(selected_path: str, theme_id: str) -> VisualControlArtifactPaths:
    out_dir = _vc_output_dir(selected_path)
    _vc_ensure_output_dir(out_dir)
    stem = _visual_control_file_stem(selected_path, theme_id)
    return VisualControlArtifactPaths(
        svg_path=out_dir / f"{stem}.svg",
        markdown_path=out_dir / f"{stem}.md",
        json_path=out_dir / f"{stem}.json",
        forensics_json_path=out_dir / f"{stem}.forensics.json",
    )


def build_visual_control_registry_payload(registry: dict[str, VisualControlSpec]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "forensics": {
            "enabled": bool(ENABLE_EDGE_FORENSICS),
            "scope": "svg_edges",
            "what_it_adds": [
                "edge forensic id",
                "hover card with evidence",
                "json export with source-target evidence",
                "svg data-* attributes per relation",
            ],
        },
        "controls": [
            {
                "key": spec.key,
                "label": spec.label,
                "group": spec.group,
                "surface_kind": spec.surface_kind,
                "description": spec.description,
                "why": spec.why,
                "how_to_change": spec.how_to_change,
                "targets": [
                    {
                        "symbol": target.symbol,
                        "kind": target.kind,
                        "path_hint": target.path_hint,
                        "note": target.note,
                    }
                    for target in spec.targets
                ],
                "tips": list(spec.tips),
                "tags": list(spec.tags),
                "priority": spec.priority,
            }
            for spec in sorted(registry.values(), key=lambda item: (-item.priority, item.group, item.label.lower()))
        ],
        "edges": [
            {
                "source": edge.source,
                "target": edge.target,
                "label": edge.label,
                "relation": edge.relation,
                "weight": edge.weight,
            }
            for edge in build_visual_control_edges()
        ],
    }


def write_visual_control_json(paths: VisualControlArtifactPaths, registry: dict[str, VisualControlSpec]) -> None:
    payload = build_visual_control_registry_payload(registry)
    paths.json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def build_edge_forensic_payload(graph: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    iter_edges = getattr(graph, "iter_edges_sorted", None)
    nodes = getattr(graph, "nodes", {}) or {}

    if not callable(iter_edges):
        return rows

    for edge in iter_edges():
        source = nodes.get(edge.source)
        target = nodes.get(edge.target)
        source_label = _clean_text(source.label if source else edge.source)
        target_label = _clean_text(target.label if target else edge.target)
        evidence = list(_edge_evidence_lines(edge, limit=EDGE_FORENSIC_EVIDENCE_LIMIT))

        rows.append(
            {
                "edge_id": _edge_forensic_id(edge, source_label, target_label),
                "source_key": edge.source,
                "target_key": edge.target,
                "source_label": source_label,
                "target_label": target_label,
                "kind": _clean_text(edge.kind),
                "weight": int(edge.weight),
                "evidence_count": len(tuple(sorted(edge.evidence))),
                "evidence": evidence,
                "summary": _edge_forensic_summary(
                    edge,
                    source_label=source_label,
                    target_label=target_label,
                    role="forensic",
                ),
            }
        )

    return rows


def write_visual_control_forensics_json(paths: VisualControlArtifactPaths, graph: Any) -> dict[str, Any]:
    edges = build_edge_forensic_payload(graph)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "edge_count": len(edges),
        "edges": edges,
    }
    paths.forensics_json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload


def _render_visual_control_summary_markdown(registry: dict[str, VisualControlSpec]) -> str:
    lines = [
        "| Key | Label | Grupo | Si quieres tocar... | Targets |",
        "| --- | --- | --- | --- | --- |",
    ]
    for spec in sorted(registry.values(), key=lambda item: (-item.priority, item.group, item.label.lower())):
        first_target = spec.targets[0].symbol if spec.targets else "-"
        lines.append(
            f"| `{spec.key}` | {spec.label} | `{spec.group}` | {spec.description} | `{first_target}` |"
        )
    return "\n".join(lines)


def _render_visual_control_detail_markdown(registry: dict[str, VisualControlSpec]) -> str:
    blocks: list[str] = []
    for spec in sorted(registry.values(), key=lambda item: (-item.priority, item.group, item.label.lower())):
        blocks.append(f"## {spec.label}")
        blocks.append("")
        blocks.append(f"**Grupo:** `{spec.group}`  ")
        blocks.append(f"**Surface kind:** `{spec.surface_kind}`  ")
        blocks.append(f"**Por qué existe:** {spec.why}")
        blocks.append("")
        blocks.append(f"**Qué controla:** {spec.description}")
        blocks.append("")
        blocks.append(f"**Cómo moverle:** {spec.how_to_change}")
        blocks.append("")
        blocks.append("**Targets reales:**")
        blocks.append("")
        for target in spec.targets:
            note = f" - {target.note}" if target.note else ""
            blocks.append(f"- `{target.symbol}` ({target.kind}){note}")
        if spec.tips:
            blocks.append("")
            blocks.append("**Tips:**")
            blocks.append("")
            for tip in spec.tips:
                blocks.append(f"- {tip}")
        if spec.tags:
            blocks.append("")
            tags_line = ", ".join(f"`{tag}`" for tag in spec.tags)
            blocks.append(f"**Tags:** {tags_line}")
        blocks.append("")
    return "\n".join(blocks).strip()


def render_visual_control_markdown(*, selected_path: str, theme_id: str) -> str:
    registry = build_visual_control_specs()
    mermaid = build_visual_control_mermaid()
    summary_table = _render_visual_control_summary_markdown(registry)
    details = _render_visual_control_detail_markdown(registry)

    return f"""# Visual Control Map Layer

## Qué es

Esta capa nueva **no toca el análisis de dependencias real**. Vive como sidecar y explica dónde modificar cada cosa visual del sistema.

Objetivo:

- saber **qué bloque tocar** si quieres cambiar blur, marco, panel, glow, backdrop o tema
- generar un **SVG lateral** usando el motor existente (`layout_dependency_graph(...)` + `render_svg(...)`)
- exponer un **trazador forense de relaciones** para saber por qué existe cada edge
- exportar **JSON + Markdown** para que Codex o cualquier otra herramienta lo pueda ensamblar sin destruir el core

## Estrategia de injerto

Hook recomendado:

1. corres el pipeline normal
2. generas el SVG real del grafo
3. llamas `export_visual_control_sidecar(...)`
4. te deja un sidecar con:
   - mapa visual en SVG
   - registry en JSON
   - guía en Markdown
   - forensics JSON por relación

Así la capa es **paralela**, **auditable** y fácil de apagar.

## Grafo conceptual

```mermaid
{mermaid}
```

## Tabla rápida

{summary_table}

## Detalle de controles

{details}
""".strip() + "\n"


def render_visual_control_svg_markup(
    *,
    selected_path: str,
    theme_id: str,
    notify: Optional[Callable[[str, str], None]] = None,
) -> tuple[str, Any, Any, dict[str, VisualControlSpec]]:
    registry = build_visual_control_specs()
    graph = build_visual_control_dependency_graph(include_notes=True)
    state = build_visual_control_state(
        selected_path=selected_path,
        theme_id=theme_id,
        view="module",
        focus_target="",
    )

    _vc_notify(notify, "Preparando sidecar visual...", f"{len(graph.nodes)} nodos")

    enrich = globals().get("enrich_graph_for_presentation")
    if callable(enrich):
        graph = enrich(graph, state)

    simplify = globals().get("simplify_visible_graph")
    if callable(simplify):
        graph = simplify(graph, state)

    ensure_visible = globals().get("_ensure_graph_has_visible_content")
    if callable(ensure_visible):
        graph = ensure_visible(graph, state)

    layout_fn = globals().get("layout_dependency_graph")
    render_fn = globals().get("render_svg")
    if not callable(layout_fn) or not callable(render_fn):
        raise RuntimeError("layout_dependency_graph(...) y render_svg(...) son obligatorios para el sidecar visual.")

    layout = layout_fn(graph, state, notify or (lambda *_args: None))
    svg_markup = render_fn(graph, layout, state, notify or (lambda *_args: None))
    return svg_markup, graph, state, registry


def export_visual_control_sidecar(
    *,
    selected_path: str,
    theme_id: str,
    notify: Optional[Callable[[str, str], None]] = None,
) -> VisualControlExportResult:
    paths = build_visual_control_output_paths(selected_path, theme_id)

    _vc_notify(notify, "Renderizando sidecar visual...", str(paths.svg_path))
    svg_markup, graph, state, registry = render_visual_control_svg_markup(
        selected_path=selected_path,
        theme_id=theme_id,
        notify=notify,
    )

    paths.svg_path.write_text(svg_markup, encoding="utf-8")
    _vc_notify(notify, "SVG visual guardado.", str(paths.svg_path))

    write_visual_control_json(paths, registry)
    _vc_notify(notify, "Registry visual guardado.", str(paths.json_path))

    forensic_payload = write_visual_control_forensics_json(paths, graph)
    _vc_notify(notify, "Forensics JSON guardado.", str(paths.forensics_json_path))

    markdown = render_visual_control_markdown(
        selected_path=selected_path,
        theme_id=theme_id,
    )
    paths.markdown_path.write_text(markdown, encoding="utf-8")
    _vc_notify(notify, "Markdown visual guardado.", str(paths.markdown_path))

    return VisualControlExportResult(
        paths=paths,
        graph=graph,
        state=state,
        registry=registry,
        forensics_summary={
            "edge_count": int(forensic_payload.get("edge_count", 0)),
            "path": str(paths.forensics_json_path),
        },
    )

# 11. ORQUESTACION PRINCIPAL
# ============================================================

import os
import traceback
from pathlib import Path
from typing import Callable, Literal, Optional


class _PipelineCancelled(Exception):
    pass


def _progress_parent(progress: object | None) -> QWidget | None:
    if progress is None:
        return None

    root = getattr(progress, "root", None)
    if isinstance(root, QWidget):
        return root

    if isinstance(progress, QWidget):
        return progress

    return None


def _call_progress_method(
    progress: object | None,
    method_names: tuple[str, ...],
    *args: object,
) -> bool:
    if progress is None:
        return False

    for method_name in method_names:
        method = getattr(progress, method_name, None)
        if not callable(method):
            continue

        try:
            method(*args)
            return True
        except TypeError:
            continue
        except Exception:
            return False

    return False


def _set_widget_text(owner: object | None, attr_name: str, text: str) -> None:
    if owner is None:
        return

    widget = getattr(owner, attr_name, None)
    setter = getattr(widget, "setText", None)
    if callable(setter):
        try:
            setter(text)
        except Exception:
            pass


def _refresh_progress(progress: object | None) -> None:
    if progress is None:
        return

    refresh = getattr(progress, "refresh", None)
    if callable(refresh):
        try:
            refresh()
            return
        except Exception:
            pass

    try:
        ensure_app().processEvents()
    except Exception:
        pass


def _set_progress_status(
    progress: object | None,
    status: str,
    detail: str = "",
) -> None:
    if progress is None:
        return

    if _call_progress_method(
        progress,
        ("set_status", "update_status", "show_status"),
        status,
        detail,
    ):
        return

    if _call_progress_method(
        progress,
        ("set_status", "update_status", "show_status"),
        status,
    ):
        if detail:
            _set_widget_text(progress, "detail_label", detail)
        _refresh_progress(progress)
        return

    _set_widget_text(progress, "status_label", status)
    _set_widget_text(progress, "detail_label", detail)
    _refresh_progress(progress)


def _set_progress_footer(
    progress: object | None,
    text: str,
) -> None:
    if progress is None:
        return
    _set_widget_text(progress, "footer_hint", text or "")
    _refresh_progress(progress)


def _finalize_progress(
    progress: object | None,
    status: str,
    detail: str = "",
) -> None:
    if progress is None:
        return

    if _call_progress_method(progress, ("finalize", "finish", "complete"), status, detail):
        return

    if _call_progress_method(progress, ("finalize", "finish", "complete"), status):
        if detail:
            _set_widget_text(progress, "detail_label", detail)
        _refresh_progress(progress)
        return

    _set_progress_status(progress, status, detail)

    progress_bar = getattr(progress, "progress", None)
    try:
        if progress_bar is not None:
            progress_bar.setRange(0, 1)
            progress_bar.setValue(1)
    except Exception:
        pass

    _set_widget_text(progress, "spinner_label", "✔ listo")
    _refresh_progress(progress)


def _wait_for_user_close(progress: object | None, detail: str = "") -> None:
    if progress is None:
        return

    if detail:
        _set_widget_text(progress, "detail_label", detail)
        _refresh_progress(progress)

    exec_method = getattr(progress, "exec", None)
    if callable(exec_method):
        try:
            exec_method()
            return
        except Exception:
            pass

    is_visible = getattr(progress, "isVisible", None)
    if not callable(is_visible):
        return

    while True:
        try:
            if not bool(is_visible()):
                break
        except Exception:
            break

        try:
            ensure_app().processEvents()
        except Exception:
            break

        time.sleep(0.05)


def _progress_was_cancelled(progress: object | None) -> bool:
    if progress is None:
        return False

    for attr_name in ("is_cancelled", "was_cancelled", "cancelled"):
        value = getattr(progress, attr_name, None)

        if callable(value):
            try:
                if bool(value()):
                    return True
            except Exception:
                continue
        elif isinstance(value, bool) and value:
            return True

    return False


def _make_progress_notifier(progress: object | None) -> Callable[[str, str], None]:
    def notify(status: str, detail: str = "") -> None:
        if _progress_was_cancelled(progress):
            raise _PipelineCancelled()

        _set_progress_status(progress, status, detail)

    return notify


def _make_tree_analysis_notifier(
    notify: Callable[[str, str], None],
) -> Callable[[str, str], None]:
    status_map = {
        "Construyendo catálogo de módulos...": "Detectando archivos fuente...",
        "Análisis de dependencias listo.": "Resolviendo archivos relevantes...",
        "Construyendo grafo final...": "Resolviendo archivos relevantes...",
        "Calculando layout...": "Construyendo tree...",
    }

    def tree_notify(status: str, detail: str = "") -> None:
        notify(status_map.get(status, status), detail)

    return tree_notify


def _resolve_selected_path(selection: SelectionResult) -> Path | None:
    selected = clean_text(selection.path or "")
    if not selected:
        return None

    selected_path = Path(selected).expanduser().resolve()
    if not selected_path.exists():
        raise FileNotFoundError(f"La ruta seleccionada no existe:\n\n{selected_path}")

    return selected_path


def _build_analysis_state(
    selection: SelectionResult,
    selected_path: Path,
    effective_focus_target: str,
) -> AnalysisState:
    return AnalysisState(
        selected_path=str(selected_path),
        project_root=str(derive_project_root(str(selected_path))),
        theme=normalize_theme(selection.theme),
        view=selection.view,
        focus_target=clean_text(effective_focus_target),
        visibility_preset=resolve_visibility_preset(selection.view),
    )


def _initial_progress_detail(selection: SelectionResult, selected_path: Path) -> str:
    chunks = [
        short_path(str(selected_path), 92),
        f"vista {selection.view}",
        f"preset {resolve_visibility_preset(selection.view)}",
        f"tema {normalize_theme(selection.theme)}",
    ]

    focus_target = clean_text(selection.focus_target)
    if selection.view == "focus":
        chunks.append(f"foco {focus_target or '(auto)'}")

    return " | ".join(chunks)


def _ensure_graph_has_visible_content(
    graph: DependencyGraph,
    state: AnalysisState,
) -> DependencyGraph:
    if graph.nodes:
        return graph

    graph.add_issue(
        "warning",
        "empty_graph",
        "El análisis terminó sin nodos visibles.",
        state.project_root,
    )
    graph.upsert_node(
        key="note:empty_graph",
        label="Sin nodos visibles",
        path=state.project_root,
        kind="note",
        group=ISSUE_NOTE_GROUP,
        metadata={
            "full_message": "El análisis terminó sin nodos visibles.",
            "issue_level": "warning",
            "issue_code": "empty_graph",
            "issue_path": state.project_root,
            "root_group": ISSUE_NOTE_GROUP,
        },
    )
    graph.finalize_metrics()
    state.total_nodes = len(graph.nodes)
    state.total_edges = len(graph.edges)
    return graph


def write_svg(
    svg_markup: str,
    output_path: Path,
    notify: Callable[[str, str], None],
) -> None:
    resolved_path = output_path.expanduser().resolve()
    ensure_output_dir(resolved_path.parent)

    notify("Guardando SVG...", str(resolved_path))
    resolved_path.write_text(svg_markup, encoding="utf-8")
    notify("SVG guardado.", str(resolved_path))


def write_tree_txt(
    tree_text: str,
    output_path: Path,
    notify: Callable[[str, str], None],
) -> None:
    resolved_path = output_path.expanduser().resolve()
    ensure_output_dir(resolved_path.parent)

    notify("Guardando tree .txt...", str(resolved_path))
    resolved_path.write_text(tree_text, encoding="utf-8")
    notify("Tree .txt guardado.", str(resolved_path))


def write_tree_html(
    html_markup: str,
    output_path: Path,
    notify: Callable[[str, str], None],
) -> None:
    resolved_path = output_path.expanduser().resolve()
    ensure_output_dir(resolved_path.parent)

    notify("Guardando HTML en F:\\trees...", str(resolved_path))
    resolved_path.write_text(html_markup, encoding="utf-8")
    notify("Tree HTML Premium guardado.", str(resolved_path))


def _ca_svg_attr(opening_tag: str, name: str) -> str:
    marker = f'{name}="'
    start = opening_tag.find(marker)
    if start < 0:
        return ""
    start += len(marker)
    end = opening_tag.find('"', start)
    if end < 0:
        return ""
    return opening_tag[start:end]


def _ca_extract_svg_shell(svg_markup: str) -> tuple[str, str]:
    start = svg_markup.find("<svg")
    if start < 0:
        return "", svg_markup

    open_end = svg_markup.find(">", start)
    close_start = svg_markup.rfind("</svg>")

    if open_end < 0 or close_start < 0 or close_start <= open_end:
        return "", svg_markup

    opening_tag = svg_markup[start : open_end + 1]
    body = svg_markup[open_end + 1 : close_start]
    return opening_tag, body


def _ca_split_defs_and_content(svg_body: str) -> tuple[str, str]:
    defs_start = svg_body.find("<defs")
    if defs_start < 0:
        return "", svg_body.strip()

    defs_open_end = svg_body.find(">", defs_start)
    defs_end = svg_body.find("</defs>", defs_open_end)

    if defs_open_end < 0 or defs_end < 0:
        return "", svg_body.strip()

    defs_markup = svg_body[defs_start : defs_end + len("</defs>")].strip()
    content_markup = (svg_body[:defs_start] + svg_body[defs_end + len("</defs>"):]).strip()
    return defs_markup, content_markup


def _ca_svg_canvas(opening_tag: str) -> tuple[int, int, str]:
    width_text = _ca_svg_attr(opening_tag, "width")
    height_text = _ca_svg_attr(opening_tag, "height")
    view_box = _ca_svg_attr(opening_tag, "viewBox")

    def _as_int(value: str, default: int) -> int:
        digits = "".join(ch for ch in str(value or "") if ch.isdigit())
        return int(digits) if digits else default

    width = _as_int(width_text, 1600)
    height = _as_int(height_text, 980)

    if not view_box:
        view_box = f"0 0 {width} {height}"

    return width, height, view_box


def _ca_premium_style() -> str:
    return """
<style><![CDATA[
  .caPremiumSvg {
    width: 100vw;
    height: 100vh;
    display: block;
    overflow: hidden;
    background:
      radial-gradient(circle at 14% 12%, rgba(170, 228, 255, 0.09), transparent 32%),
      radial-gradient(circle at 82% 18%, rgba(116, 220, 255, 0.10), transparent 26%),
      linear-gradient(180deg, rgba(4, 8, 16, 0.98), rgba(10, 18, 30, 1));
    user-select: none;
    -webkit-user-select: none;
  }

  #caViewport {
    cursor: grab;
  }

  .caPremiumSvg.is-panning #caViewport {
    cursor: grabbing;
  }

  #lanesLayer {
    opacity: 0.84;
  }

  #edgesLayer {
    opacity: 0.82;
  }

  #nodesLayer {
    opacity: 1.0;
  }

  .nodeGroup {
    cursor: pointer;
    transition: opacity 180ms ease, filter 180ms ease;
  }

  .nodeGroup.is-dim {
    opacity: 0.22 !important;
  }

  .nodeGroup.is-hot,
  .nodeGroup.is-focused {
    opacity: 1 !important;
  }

  .nodeGroup.is-focused .node-label,
  .nodeGroup.is-hot .node-label {
    letter-spacing: 0.12px;
  }

  .caHudTitle {
    font: 700 11px 'Segoe UI', Arial, sans-serif;
    fill: #eaf8ff;
    letter-spacing: 0.65px;
  }

  .caHudMeta {
    font: 600 9.6px 'Segoe UI', Arial, sans-serif;
    fill: rgba(234, 248, 255, 0.72);
    letter-spacing: 0.20px;
  }

  .caHudHint {
    font: 600 9.4px 'Segoe UI', Arial, sans-serif;
    fill: rgba(234, 248, 255, 0.66);
  }

  .caHudButton rect {
    fill: rgba(15, 25, 40, 0.88);
    stroke: rgba(146, 235, 255, 0.40);
    stroke-width: 1.0;
    rx: 12;
    ry: 12;
  }

  .caHudButton text {
    font: 700 10px 'Segoe UI', Arial, sans-serif;
    fill: #effbff;
    letter-spacing: 0.45px;
    text-anchor: middle;
    dominant-baseline: middle;
  }

  .caHudButton:hover rect {
    fill: rgba(20, 35, 54, 0.98);
    stroke: rgba(158, 242, 255, 0.72);
  }

  .caHudBadge {
    fill: rgba(255, 255, 255, 0.08);
    stroke: rgba(255, 255, 255, 0.10);
    stroke-width: 1.0;
  }

  .caViewportBackdrop {
    fill: rgba(5, 10, 18, 1.0);
  }
]]></style>
""".strip()


def _ca_premium_script() -> str:
    return """
<script><![CDATA[
(function () {
  const root = document.documentElement;
  const scene = document.getElementById('caScene');
  const hud = document.getElementById('caHud');
  const nodeGroups = Array.from(root.querySelectorAll('.nodeGroup'));
  if (!scene) { return; }

  let scale = 1;
  let tx = 0;
  let ty = 0;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  let lockedNode = null;

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function viewportSize() {
    const raw = (root.getAttribute('viewBox') || '0 0 1600 980').trim().split(/\\s+/).map(Number);
    return {
      w: raw[2] || 1600,
      h: raw[3] || 980
    };
  }

  function applyTransform() {
    scene.setAttribute('transform', `translate(${tx} ${ty}) scale(${scale})`);
  }

  function svgPoint(clientX, clientY) {
    const pt = root.createSVGPoint();
    pt.x = clientX;
    pt.y = clientY;
    return pt.matrixTransform(root.getScreenCTM().inverse());
  }

  function fitScene() {
    const box = scene.getBBox();
    if (!box || !box.width || !box.height) { return; }

    const size = viewportSize();
    const pad = Math.max(42, Math.min(size.w, size.h) * 0.05);

    scale = clamp(
      Math.min((size.w - (pad * 2)) / box.width, (size.h - (pad * 2)) / box.height),
      0.18,
      2.25
    );

    tx = ((size.w - (box.width * scale)) / 2) - (box.x * scale);
    ty = ((size.h - (box.height * scale)) / 2) - (box.y * scale);
    applyTransform();
  }

  function normalizeScene() {
    const box = scene.getBBox();
    if (!box || !box.width || !box.height) { return; }

    const size = viewportSize();
    const pad = Math.max(42, Math.min(size.w, size.h) * 0.05);
    const fitScale = Math.min(
      (size.w - (pad * 2)) / box.width,
      (size.h - (pad * 2)) / box.height
    );

    scale = clamp(fitScale * 8.0, 0.35, 12.0);
    tx = ((size.w - (box.width * scale)) / 2) - (box.x * scale);
    ty = ((size.h - (box.height * scale)) / 2) - (box.y * scale);
    applyTransform();
  }

  function clearFocus() {
    lockedNode = null;
    root.classList.remove('has-focus');
    nodeGroups.forEach((node) => {
      node.classList.remove('is-dim', 'is-hot', 'is-focused');
      node.removeAttribute('transform');
    });
  }

  function applyLockedFocus() {
    if (!lockedNode) {
      clearFocus();
      return;
    }

    root.classList.add('has-focus');
    nodeGroups.forEach((node) => {
      const active = node === lockedNode;
      node.classList.toggle('is-focused', active);
      node.classList.toggle('is-dim', !active);

      if (active) {
        node.setAttribute('transform', 'translate(0 -6)');
      } else {
        node.removeAttribute('transform');
      }
    });
  }

  nodeGroups.forEach((node) => {
    node.addEventListener('pointerenter', () => {
      if (lockedNode) { return; }
      node.classList.add('is-hot');
      node.setAttribute('transform', 'translate(0 -4)');
      nodeGroups.forEach((other) => {
        if (other !== node) {
          other.classList.add('is-dim');
        }
      });
    });

    node.addEventListener('pointerleave', () => {
      if (lockedNode) { return; }
      node.classList.remove('is-hot');
      node.removeAttribute('transform');
      nodeGroups.forEach((other) => other.classList.remove('is-dim'));
    });

    node.addEventListener('click', (event) => {
      event.stopPropagation();
      lockedNode = (lockedNode === node) ? null : node;
      applyLockedFocus();
    });
  });

  root.addEventListener('click', (event) => {
    if (hud && hud.contains(event.target)) {
      return;
    }
    clearFocus();
  });

  root.addEventListener('wheel', (event) => {
    if (hud && hud.contains(event.target)) {
      return;
    }

    event.preventDefault();

    const point = svgPoint(event.clientX, event.clientY);
    const px = (point.x - tx) / scale;
    const py = (point.y - ty) / scale;
    const factor = event.deltaY < 0 ? 1.26 : 0.78;
    const nextScale = clamp(scale * factor, 0.05, 32.0);

    tx = point.x - (px * nextScale);
    ty = point.y - (py * nextScale);
    scale = nextScale;
    applyTransform();
  }, { passive: false });

  root.addEventListener('pointerdown', (event) => {
    if (hud && hud.contains(event.target)) {
      return;
    }
    dragging = true;
    lastX = event.clientX;
    lastY = event.clientY;
    root.classList.add('is-panning');
  });

  window.addEventListener('pointermove', (event) => {
    if (!dragging) {
      return;
    }
    tx += event.clientX - lastX;
    ty += event.clientY - lastY;
    lastX = event.clientX;
    lastY = event.clientY;
    applyTransform();
  });

  window.addEventListener('pointerup', () => {
    dragging = false;
    root.classList.remove('is-panning');
  });

  root.addEventListener('dblclick', (event) => {
    if (hud && hud.contains(event.target)) {
      return;
    }
    clearFocus();
    fitScene();
  });

  Array.from(root.querySelectorAll('[data-ca-action]')).forEach((button) => {
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      const action = button.getAttribute('data-ca-action');

      if (action === 'fit') {
        clearFocus();
        fitScene();
        return;
      }

      if (action === 'one') {
        clearFocus();
        normalizeScene();
        return;
      }

      if (action === 'reset') {
        clearFocus();
        fitScene();
      }
    });
  });

  window.addEventListener('resize', () => {
    fitScene();
  });

  fitScene();
})();
]]></script>
""".strip()


def _ca_ultra_premium_style() -> str:
    return """
<style><![CDATA[
  @keyframes caEdgeFlow {
    from { stroke-dashoffset: 0; }
    to { stroke-dashoffset: -48; }
  }

  @keyframes caNodeFrameFlow {
    from { stroke-dashoffset: 0; }
    to { stroke-dashoffset: -38; }
  }

  @keyframes caNodePulse {
    0%, 100% { opacity: 0.82; }
    50% { opacity: 1.0; }
  }

  #edgesLayer > * {
    transition: opacity 180ms ease, filter 180ms ease;
  }

  #edgesLayer > *.is-dim {
    opacity: 0.06 !important;
    filter: saturate(0.55) blur(0.20px);
  }

  #edgesLayer > *.is-hidden {
    opacity: 0 !important;
    pointer-events: none !important;
  }

  #edgesLayer > *.is-hot {
    opacity: 1 !important;
    filter:
      brightness(1.18)
      saturate(1.24)
      drop-shadow(0 0 5px rgba(143, 238, 255, 0.30))
      drop-shadow(0 0 10px rgba(143, 238, 255, 0.16));
  }

  #edgesLayer .ca-edge-path,
  #edgesLayer > path {
    transition:
      opacity 180ms ease,
      stroke 180ms ease,
      stroke-width 180ms ease,
      filter 180ms ease;
  }

  #edgesLayer > *.is-hot .ca-edge-path,
  #edgesLayer > path.is-hot {
    stroke: rgba(168, 244, 255, 0.96) !important;
    stroke-width: 2.55px !important;
    stroke-linecap: round;
    stroke-dasharray: 12 10;
    animation: caEdgeFlow 1.45s linear infinite;
    filter:
      drop-shadow(0 0 4px rgba(143, 238, 255, 0.55))
      drop-shadow(0 0 9px rgba(143, 238, 255, 0.28));
  }

  #nodesLayer .nodeGroup {
    transition: opacity 180ms ease, filter 180ms ease;
  }

  #nodesLayer .nodeGroup.is-neighbor {
    opacity: 0.90 !important;
    filter: brightness(1.04) saturate(1.06);
  }

  #nodesLayer .nodeGroup rect {
    fill: rgba(8, 18, 28, 0.015) !important;
    fill-opacity: 0.06 !important;
    stroke-opacity: 0.56 !important;
  }

  #nodesLayer .nodeGroup > g[filter] > rect:first-child {
    fill: rgba(8, 18, 28, 0.01) !important;
    fill-opacity: 0.045 !important;
    stroke: rgba(156, 242, 255, 0.78) !important;
    stroke-width: 1.05px !important;
    rx: 18;
    ry: 18;
  }

  #nodesLayer .nodeGroup.is-hot > g[filter] > rect:first-child,
  #nodesLayer .nodeGroup.is-focused > g[filter] > rect:first-child {
    stroke: rgba(193, 249, 255, 0.98) !important;
    stroke-width: 1.35px !important;
    stroke-dasharray: 14 8;
    animation:
      caNodeFrameFlow 1.55s linear infinite,
      caNodePulse 1.65s ease-in-out infinite;
    filter:
      drop-shadow(0 0 5px rgba(143, 238, 255, 0.42))
      drop-shadow(0 0 12px rgba(143, 238, 255, 0.18));
  }

  #nodesLayer .nodeGroup.is-dim rect {
    stroke-opacity: 0.16 !important;
  }

  #nodesLayer .nodeGroup .node-label {
    fill: #f2fbff !important;
    font-weight: 700 !important;
    letter-spacing: 0.18px;
    filter:
      drop-shadow(0 0 4px rgba(143, 238, 255, 0.32))
      drop-shadow(0 0 8px rgba(143, 238, 255, 0.12));
  }

  #nodesLayer .nodeGroup .node-subtitle {
    fill: rgba(181, 229, 240, 0.92) !important;
    filter: drop-shadow(0 0 3px rgba(143, 238, 255, 0.14));
  }

  #nodesLayer .nodeGroup .node-icon {
    fill: rgba(148, 243, 255, 0.98) !important;
    filter: drop-shadow(0 0 5px rgba(143, 238, 255, 0.20));
  }

  #nodesLayer .nodeGroup.is-dim .node-label,
  #nodesLayer .nodeGroup.is-dim .node-subtitle,
  #nodesLayer .nodeGroup.is-dim .node-icon {
    opacity: 0.30 !important;
    filter: none !important;
  }
]]></style>
""".strip()


def _ca_ultra_premium_script() -> str:
    return """
<script><![CDATA[
(() => {
  const root = document.currentScript && document.currentScript.ownerSVGElement;
  if (!root) {
    return;
  }

  const nodesLayer = root.querySelector('#nodesLayer');
  const edgesLayer = root.querySelector('#edgesLayer');
  if (!nodesLayer || !edgesLayer) {
    return;
  }

  const nodeGroups = Array.from(nodesLayer.querySelectorAll('.nodeGroup'));
  const edgeGroups = Array.from(edgesLayer.children || []);

  const closestSafe = (node, selector) => {
    if (!node || typeof node.closest !== 'function') {
      return null;
    }
    return node.closest(selector);
  };

  const parseNodeLabel = (el) => {
    const titleText = ((el.querySelector('title') || {}).textContent || '').trim();
    const match = titleText.match(/(?:^|\\|)\\s*label=([^|]+)/i);
    if (match && match[1]) {
      return match[1].trim();
    }
    const labelText = ((el.querySelector('.node-label') || {}).textContent || '').trim();
    return labelText;
  };

  const parseEdgeEndpoints = (el) => {
    const titleText = ((el.querySelector('title') || {}).textContent || '').trim();
    const match = titleText.match(/^\\s*(.*?)\\s*->\\s*(.*?)\\s*(?:\\||$)/);
    if (!match) {
      return { source: '', target: '' };
    }
    return {
      source: (match[1] || '').trim(),
      target: (match[2] || '').trim(),
    };
  };

  const nodeLabelToElements = new Map();
  nodeGroups.forEach((el) => {
    const label = parseNodeLabel(el);
    if (!label) {
      return;
    }
    el.dataset.caNodeLabel = label;
    if (!nodeLabelToElements.has(label)) {
      nodeLabelToElements.set(label, []);
    }
    nodeLabelToElements.get(label).push(el);
  });

  const edgeRecords = edgeGroups.map((el) => {
    const ends = parseEdgeEndpoints(el);
    const nestedPaths = Array.from(el.querySelectorAll('path'));
    const paths = nestedPaths.length > 0 ? nestedPaths : (el.tagName && el.tagName.toLowerCase() === 'path' ? [el] : []);
    paths.forEach((path) => path.classList.add('ca-edge-path'));
    return {
      el,
      source: ends.source,
      target: ends.target,
      paths,
    };
  });

  const relatedEdges = new Map();
  const relatedLabels = new Map();

  const pushRelated = (label, edgeEl, otherLabel) => {
    if (!label) {
      return;
    }
    if (!relatedEdges.has(label)) {
      relatedEdges.set(label, new Set());
    }
    relatedEdges.get(label).add(edgeEl);

    if (otherLabel) {
      if (!relatedLabels.has(label)) {
        relatedLabels.set(label, new Set());
      }
      relatedLabels.get(label).add(otherLabel);
    }
  };

  edgeRecords.forEach((record) => {
    pushRelated(record.source, record.el, record.target);
    pushRelated(record.target, record.el, record.source);
  });

  let lockedLabel = '';

  const clearVisualState = () => {
    nodeGroups.forEach((el) => {
      el.classList.remove('is-hot', 'is-neighbor', 'is-dim');
    });
    edgeRecords.forEach((record) => {
      record.el.classList.remove('is-hot', 'is-dim', 'is-hidden');
      record.paths.forEach((path) => path.classList.remove('is-hot'));
    });
  };

  const applyRelationState = (label) => {
    const activeLabel = (label || '').trim();
    if (!activeLabel) {
      clearVisualState();
      return;
    }

    const hotEdges = relatedEdges.get(activeLabel) || new Set();
    const neighborLabels = relatedLabels.get(activeLabel) || new Set();

    nodeGroups.forEach((el) => {
      const nodeLabel = (el.dataset.caNodeLabel || '').trim();
      const isSelf = nodeLabel === activeLabel;
      const isNeighbor = neighborLabels.has(nodeLabel);

      el.classList.toggle('is-hot', isSelf);
      el.classList.toggle('is-neighbor', !isSelf && isNeighbor);
      el.classList.toggle('is-dim', !isSelf && !isNeighbor);
    });

    edgeRecords.forEach((record) => {
      const isHot = hotEdges.has(record.el);
      record.el.classList.toggle('is-hot', isHot);
      record.el.classList.toggle('is-dim', !isHot);
      record.paths.forEach((path) => path.classList.toggle('is-hot', isHot));
    });
  };

  nodeGroups.forEach((el) => {
    const label = (el.dataset.caNodeLabel || '').trim();
    if (!label) {
      return;
    }

    el.addEventListener('pointerenter', () => {
      applyRelationState(label);
    });

    el.addEventListener('pointerleave', () => {
      if (lockedLabel) {
        applyRelationState(lockedLabel);
        return;
      }
      clearVisualState();
    });

    el.addEventListener('click', (event) => {
      event.stopPropagation();
      lockedLabel = (lockedLabel === label) ? '' : label;
      if (lockedLabel) {
        applyRelationState(lockedLabel);
      } else {
        clearVisualState();
      }
    });
  });

  root.addEventListener('click', (event) => {
    if (closestSafe(event.target, '.nodeGroup') || closestSafe(event.target, '#caHud')) {
      return;
    }
    lockedLabel = '';
    clearVisualState();
  });
})();
]]></script>
""".strip()


def _ca_spectral_relation_style() -> str:
    return """
<style><![CDATA[
  #nodesLayer .nodeGroup {
    --ca-accent-rgb: 140, 239, 255;
    --ca-accent-soft-rgb: 232, 249, 255;
    --ca-accent-dim-rgb: 92, 182, 205;
  }

  #nodesLayer .nodeGroup > g[filter] > rect:first-child {
    fill: rgba(8, 18, 28, 0.010) !important;
    fill-opacity: 0.028 !important;
    stroke: rgba(var(--ca-accent-rgb), 0.44) !important;
    stroke-width: 0.96px !important;
  }

  #nodesLayer .nodeGroup .node-label {
    fill: rgba(var(--ca-accent-soft-rgb), 0.98) !important;
    filter:
      drop-shadow(0 0 4px rgba(var(--ca-accent-rgb), 0.24))
      drop-shadow(0 0 9px rgba(var(--ca-accent-rgb), 0.10));
  }

  #nodesLayer .nodeGroup .node-subtitle {
    fill: rgba(var(--ca-accent-soft-rgb), 0.74) !important;
    filter: drop-shadow(0 0 3px rgba(var(--ca-accent-rgb), 0.10));
  }

  #nodesLayer .nodeGroup .node-icon {
    fill: rgba(var(--ca-accent-rgb), 0.98) !important;
    filter:
      drop-shadow(0 0 4px rgba(var(--ca-accent-rgb), 0.18))
      drop-shadow(0 0 8px rgba(var(--ca-accent-rgb), 0.08));
  }

  #nodesLayer .nodeGroup.is-neighbor > g[filter] > rect:first-child {
    stroke: rgba(var(--ca-accent-rgb), 0.66) !important;
    stroke-width: 1.10px !important;
    filter:
      drop-shadow(0 0 4px rgba(var(--ca-accent-rgb), 0.18))
      drop-shadow(0 0 8px rgba(var(--ca-accent-rgb), 0.08));
  }

  #nodesLayer .nodeGroup.is-hot > g[filter] > rect:first-child,
  #nodesLayer .nodeGroup.is-focused > g[filter] > rect:first-child {
    stroke: rgba(var(--ca-accent-soft-rgb), 0.98) !important;
    stroke-width: 1.38px !important;
    stroke-dasharray: 14 8;
    animation:
      caNodeFrameFlow 1.55s linear infinite,
      caNodePulse 1.70s ease-in-out infinite;
    filter:
      drop-shadow(0 0 6px rgba(var(--ca-accent-rgb), 0.34))
      drop-shadow(0 0 14px rgba(var(--ca-accent-rgb), 0.15));
  }

  #nodesLayer .nodeGroup.is-dim > g[filter] > rect:first-child {
    stroke: rgba(var(--ca-accent-dim-rgb), 0.16) !important;
  }

  #nodesLayer .nodeGroup.is-dim .node-label,
  #nodesLayer .nodeGroup.is-dim .node-subtitle,
  #nodesLayer .nodeGroup.is-dim .node-icon {
    opacity: 0.28 !important;
    filter: none !important;
  }

  #edgesLayer > * {
    --ca-edge-rgb: 140, 239, 255;
    transition: opacity 180ms ease, filter 180ms ease;
  }

  #edgesLayer > *.is-dim {
    opacity: 0.025 !important;
    filter: saturate(0.42) blur(0.28px);
  }

  #edgesLayer > *.is-hot {
    opacity: 1 !important;
    filter:
      brightness(1.05)
      saturate(1.10)
      drop-shadow(0 0 3px rgba(var(--ca-edge-rgb), 0.12))
      drop-shadow(0 0 7px rgba(var(--ca-edge-rgb), 0.05));
  }

  #edgesLayer .ca-edge-path,
  #edgesLayer > path {
    transition:
      opacity 180ms ease,
      stroke 180ms ease,
      stroke-width 180ms ease,
      filter 180ms ease;
  }

  #edgesLayer > *.is-hot .ca-edge-path,
  #edgesLayer > path.is-hot {
    stroke: rgba(var(--ca-edge-rgb), 0.92) !important;
    stroke-width: 1.55px !important;
    stroke-linecap: round;
    stroke-dasharray: 8 12;
    animation: caEdgeFlow 2.05s linear infinite;
    filter:
      drop-shadow(0 0 2px rgba(var(--ca-edge-rgb), 0.14))
      drop-shadow(0 0 6px rgba(var(--ca-edge-rgb), 0.06));
  }
]]></style>
""".strip()


def _ca_spectral_relation_script() -> str:
    return """
<script><![CDATA[
(() => {
  const root = document.currentScript && document.currentScript.ownerSVGElement;
  if (!root) {
    return;
  }

  const scene = root.querySelector('#caScene');
  const nodesLayer = root.querySelector('#nodesLayer');
  const edgesLayer = root.querySelector('#edgesLayer');
  if (!scene || !nodesLayer || !edgesLayer) {
    return;
  }

  const nodeGroups = Array.from(nodesLayer.querySelectorAll('.nodeGroup'));
  const edgeGroups = Array.from(edgesLayer.children || []);

  const hslToRgb = (h, s, l) => {
    s /= 100;
    l /= 100;
    const k = (n) => (n + (h / 30)) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = (n) => l - (a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1))));
    return [
      Math.round(255 * f(0)),
      Math.round(255 * f(8)),
      Math.round(255 * f(4)),
    ];
  };

  const rgbText = (rgb) => rgb.join(', ');
  const rgbaFromText = (rgbTextValue, alpha) => `rgba(${rgbTextValue}, ${alpha})`;

  const closestSafe = (node, selector) => {
    if (!node || typeof node.closest !== 'function') {
      return null;
    }
    return node.closest(selector);
  };

  const parseNodeLabel = (el) => {
    const titleText = ((el.querySelector('title') || {}).textContent || '').trim();
    const match = titleText.match(/(?:^|\\|)\\s*label=([^|]+)/i);
    if (match && match[1]) {
      return match[1].trim();
    }
    const labelText = ((el.querySelector('.node-label') || {}).textContent || '').trim();
    return labelText;
  };

  const parseEdgeEndpoints = (el) => {
    const sourceAttr = (el.getAttribute('data-ca-source') || '').trim();
    const targetAttr = (el.getAttribute('data-ca-target') || '').trim();
    if (sourceAttr || targetAttr) {
      return { source: sourceAttr, target: targetAttr };
    }

    const titleText = ((el.querySelector('title') || {}).textContent || '').trim();
    const match = titleText.match(/^\\s*(.*?)\\s*->\\s*(.*?)\\s*(?:\\||$)/);
    if (!match) {
      return { source: '', target: '' };
    }
    return {
      source: (match[1] || '').trim(),
      target: (match[2] || '').trim(),
    };
  };

  const parseNodeCounts = (el) => {
    const values = Array.from(el.querySelectorAll('text'))
      .map((node) => (node.textContent || '').trim())
      .filter((text) => /^\\d+$/.test(text))
      .map((text) => Number(text));

    return {
      inbound: values.length > 0 ? values[0] : 0,
      outbound: values.length > 1 ? values[1] : 0,
    };
  };

  const sceneBox = scene.getBBox();
  const nodeLabelToElements = new Map();

  nodeGroups.forEach((el, index) => {
    const label = parseNodeLabel(el);
    if (!label) {
      return;
    }

    el.dataset.caNodeLabel = label;
    if (!nodeLabelToElements.has(label)) {
      nodeLabelToElements.set(label, []);
    }
    nodeLabelToElements.get(label).push(el);

    const counts = parseNodeCounts(el);
    const degree = (counts.inbound || 0) + (counts.outbound || 0);
    const box = el.getBBox();
    const normY = sceneBox.height > 0 ? Math.max(0, Math.min(1, (box.y - sceneBox.y) / sceneBox.height)) : 0;
    const isHub = degree >= 16 || el.classList.contains('node-hub');
    const isPackage = /package/i.test((el.querySelector('title') || {}).textContent || '');
    const isExternal = /external/i.test((el.querySelector('title') || {}).textContent || '');

    let hue = 194;
    let sat = 92;
    let light = 73;

    if (isHub) {
      hue = 34;
      sat = 96;
      light = 72;
    } else if (isPackage) {
      hue = 278;
      sat = 90;
      light = 76;
    } else if (isExternal) {
      hue = 332;
      sat = 88;
      light = 78;
    } else if (degree >= 10) {
      hue = 152;
      sat = 86;
      light = 74;
    } else {
      hue = 188 + Math.round(normY * 118.0);
      sat = 86 + Math.round((1.0 - normY) * 8.0);
      light = 72 + Math.round((degree > 4 ? 4 : degree) * 0.6);
    }

    const accent = hslToRgb(hue, sat, light);
    const soft = hslToRgb(hue, Math.max(66, sat - 14), Math.min(90, light + 11));
    const dim = hslToRgb(hue, Math.max(44, sat - 32), Math.max(54, light - 16));

    el.style.setProperty('--ca-accent-rgb', rgbText(accent));
    el.style.setProperty('--ca-accent-soft-rgb', rgbText(soft));
    el.style.setProperty('--ca-accent-dim-rgb', rgbText(dim));
    el.setAttribute('data-ca-degree', String(degree));
    el.setAttribute('data-ca-inbound', String(counts.inbound || 0));
    el.setAttribute('data-ca-outbound', String(counts.outbound || 0));
    el.setAttribute('data-ca-color-family', String(hue));
    el.setAttribute('data-ca-node-index', String(index));
  });

  const edgeRecords = edgeGroups.map((el) => {
    const ends = parseEdgeEndpoints(el);
    const nestedPaths = Array.from(el.querySelectorAll('path'));
    const paths = nestedPaths.length > 0 ? nestedPaths : (el.tagName && el.tagName.toLowerCase() === 'path' ? [el] : []);
    paths.forEach((path) => path.classList.add('ca-edge-path'));

    if (ends.source) {
      el.setAttribute('data-ca-source', ends.source);
    }
    if (ends.target) {
      el.setAttribute('data-ca-target', ends.target);
    }

    return {
      el,
      source: ends.source,
      target: ends.target,
      paths,
    };
  });

  const relatedEdges = new Map();
  const relatedLabels = new Map();

  const pushRelated = (label, edgeEl, otherLabel) => {
    if (!label) {
      return;
    }
    if (!relatedEdges.has(label)) {
      relatedEdges.set(label, new Set());
    }
    relatedEdges.get(label).add(edgeEl);

    if (otherLabel) {
      if (!relatedLabels.has(label)) {
        relatedLabels.set(label, new Set());
      }
      relatedLabels.get(label).add(otherLabel);
    }
  };

  edgeRecords.forEach((record) => {
    pushRelated(record.source, record.el, record.target);
    pushRelated(record.target, record.el, record.source);
  });

  const accentForLabel = (label) => {
    const group = (nodeLabelToElements.get(label) || [])[0];
    if (!group) {
      return '140, 239, 255';
    }
    return (group.style.getPropertyValue('--ca-accent-rgb') || '140, 239, 255').trim();
  };

  let lockedLabel = '';

  const clearVisualState = () => {
    nodeGroups.forEach((el) => {
      el.classList.remove('is-hot', 'is-neighbor', 'is-dim');
    });

    edgeRecords.forEach((record) => {
      record.el.classList.remove('is-hot', 'is-dim', 'is-hidden');
      record.el.style.removeProperty('--ca-edge-rgb');
      record.paths.forEach((path) => {
        path.classList.remove('is-hot');
        path.style.removeProperty('stroke');
        path.style.removeProperty('filter');
      });
    });
  };

  const applyRelationState = (label) => {
    const activeLabel = (label || '').trim();
    if (!activeLabel) {
      clearVisualState();
      return;
    }

    const hotEdges = relatedEdges.get(activeLabel) || new Set();
    const neighborLabels = relatedLabels.get(activeLabel) || new Set();
    const accent = accentForLabel(activeLabel);

    nodeGroups.forEach((el) => {
      const nodeLabel = (el.dataset.caNodeLabel || '').trim();
      const isSelf = nodeLabel === activeLabel;
      const isNeighbor = neighborLabels.has(nodeLabel);

      el.classList.toggle('is-hot', isSelf);
      el.classList.toggle('is-neighbor', !isSelf && isNeighbor);
      el.classList.toggle('is-dim', !isSelf && !isNeighbor);
    });

    edgeRecords.forEach((record) => {
      const isHot = hotEdges.has(record.el);
      record.el.classList.toggle('is-hot', isHot);
      record.el.classList.toggle('is-dim', !isHot);
      record.el.setAttribute('data-ca-source', record.source || '');
      record.el.setAttribute('data-ca-target', record.target || '');

      if (isHot) {
        record.el.style.setProperty('--ca-edge-rgb', accent);
      } else {
        record.el.style.removeProperty('--ca-edge-rgb');
      }

      record.paths.forEach((path) => {
        path.classList.toggle('is-hot', isHot);
        if (isHot) {
          path.style.stroke = rgbaFromText(accent, 0.98);
          path.style.filter =
            `drop-shadow(0 0 4px rgba(${accent}, 0.34)) ` +
            `drop-shadow(0 0 10px rgba(${accent}, 0.16))`;
        } else {
          path.style.removeProperty('stroke');
          path.style.removeProperty('filter');
        }
      });
    });
  };

  nodeGroups.forEach((el) => {
    const label = (el.dataset.caNodeLabel || '').trim();
    if (!label) {
      return;
    }

    el.addEventListener('pointerenter', () => {
      applyRelationState(label);
    });

    el.addEventListener('pointerleave', () => {
      if (lockedLabel) {
        applyRelationState(lockedLabel);
        return;
      }
      clearVisualState();
    });

    el.addEventListener('click', (event) => {
      event.stopPropagation();
      lockedLabel = (lockedLabel === label) ? '' : label;
      if (lockedLabel) {
        applyRelationState(lockedLabel);
      } else {
        clearVisualState();
      }
    });
  });

  root.addEventListener('click', (event) => {
    if (closestSafe(event.target, '.nodeGroup') || closestSafe(event.target, '#caHud')) {
      return;
    }
    lockedLabel = '';
    clearVisualState();
  });
})();
]]></script>
""".strip()


def _ca_glass_luxe_node_style() -> str:
    return """
<style><![CDATA[
  @keyframes caGlassNodePulse {
    0%, 100% {
      opacity: 0.84;
    }
    50% {
      opacity: 1.0;
    }
  }

  @keyframes caGlassNodeBlink {
    0%, 100% {
      stroke-opacity: 0.88;
    }
    50% {
      stroke-opacity: 0.58;
    }
  }

  #nodesLayer .nodeGroup {
    transition: opacity 180ms ease, filter 180ms ease;
  }

  #nodesLayer .nodeGroup rect {
    fill: transparent !important;
    fill-opacity: 0 !important;
  }

  #nodesLayer .nodeGroup > g[filter] > rect:first-child {
    fill: transparent !important;
    fill-opacity: 0 !important;
    stroke: rgba(var(--ca-accent-rgb, 160, 236, 255), 0.42) !important;
    stroke-width: 0.92px !important;
    filter:
      drop-shadow(0 0 3px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.12))
      drop-shadow(0 0 8px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.05));
  }

  #nodesLayer .nodeGroup .ca-glass-inner-border {
    fill: transparent !important;
    fill-opacity: 0 !important;
    stroke: rgba(var(--ca-accent-soft-rgb, 232, 248, 255), 0.24) !important;
    stroke-width: 0.72px !important;
    vector-effect: non-scaling-stroke;
    pointer-events: none;
    opacity: 0.84;
    filter:
      drop-shadow(0 0 2px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.08));
  }

  #nodesLayer .nodeGroup.is-dim > g[filter] > rect:first-child,
  #nodesLayer .nodeGroup.is-dim .ca-glass-inner-border {
    stroke-opacity: 0.12 !important;
    filter: none !important;
  }

  #nodesLayer .nodeGroup.is-neighbor > g[filter] > rect:first-child {
    stroke: rgba(var(--ca-accent-rgb, 160, 236, 255), 0.54) !important;
    stroke-width: 0.98px !important;
  }

  #nodesLayer .nodeGroup.is-neighbor .ca-glass-inner-border {
    stroke: rgba(var(--ca-accent-soft-rgb, 232, 248, 255), 0.30) !important;
    stroke-width: 0.74px !important;
  }

  #nodesLayer .nodeGroup.is-hot > g[filter] > rect:first-child,
  #nodesLayer .nodeGroup.is-focused > g[filter] > rect:first-child {
    stroke: rgba(var(--ca-accent-soft-rgb, 232, 248, 255), 0.92) !important;
    stroke-width: 1.08px !important;
    stroke-dasharray: 10 12;
    animation:
      caNodeFrameFlow 2.35s linear infinite,
      caGlassNodeBlink 2.8s ease-in-out infinite;
    filter:
      drop-shadow(0 0 4px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.18))
      drop-shadow(0 0 10px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.08));
  }

  #nodesLayer .nodeGroup.is-hot .ca-glass-inner-border,
  #nodesLayer .nodeGroup.is-focused .ca-glass-inner-border {
    stroke: rgba(var(--ca-accent-soft-rgb, 232, 248, 255), 0.48) !important;
    stroke-width: 0.82px !important;
    stroke-dasharray: 8 14;
    animation:
      caNodeFrameFlow 3.0s linear infinite reverse,
      caGlassNodePulse 3.4s ease-in-out infinite;
    filter:
      drop-shadow(0 0 3px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.12));
  }

  #nodesLayer .nodeGroup .node-label {
    fill: rgba(var(--ca-accent-soft-rgb, 236, 248, 255), 0.96) !important;
    font-weight: 700 !important;
    font-size: 17px !important;
    letter-spacing: 0.10px !important;
    filter:
      drop-shadow(0 0 2px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.10))
      drop-shadow(0 0 5px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.05));
  }

  #nodesLayer .nodeGroup .node-subtitle {
    fill: rgba(var(--ca-accent-soft-rgb, 236, 248, 255), 0.58) !important;
    font-size: 10.6px !important;
    letter-spacing: 0.04px !important;
    filter:
      drop-shadow(0 0 2px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.04));
  }

  #nodesLayer .nodeGroup .node-icon {
    fill: rgba(var(--ca-accent-rgb, 160, 236, 255), 0.92) !important;
    filter:
      drop-shadow(0 0 3px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.10));
  }

  #nodesLayer .nodeGroup.is-hot .node-label,
  #nodesLayer .nodeGroup.is-focused .node-label {
    filter:
      drop-shadow(0 0 3px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.16))
      drop-shadow(0 0 8px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.07));
  }

  #nodesLayer .nodeGroup.is-hot .node-subtitle,
  #nodesLayer .nodeGroup.is-focused .node-subtitle {
    filter:
      drop-shadow(0 0 2px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.08));
  }

  #nodesLayer .nodeGroup.is-dim .node-label,
  #nodesLayer .nodeGroup.is-dim .node-subtitle,
  #nodesLayer .nodeGroup.is-dim .node-icon {
    opacity: 0.24 !important;
    filter: none !important;
  }
]]></style>
""".strip()


def _ca_glass_luxe_node_script() -> str:
    return """
<script><![CDATA[
(() => {
  const root = document.currentScript && document.currentScript.ownerSVGElement;
  if (!root) {
    return;
  }

  const nodeGroups = Array.from(root.querySelectorAll('#nodesLayer .nodeGroup'));
  if (!nodeGroups.length) {
    return;
  }

  const toNum = (value, fallback = 0) => {
    const parsed = Number.parseFloat(String(value ?? '').trim());
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  nodeGroups.forEach((el) => {
    if (el.getAttribute('data-ca-glass-luxe') === '1') {
      return;
    }

    const mainRect =
      el.querySelector('g[filter] > rect:first-child') ||
      el.querySelector('rect');

    if (!mainRect) {
      return;
    }

    const innerRect = mainRect.cloneNode(false);
    const x = toNum(mainRect.getAttribute('x'), 0);
    const y = toNum(mainRect.getAttribute('y'), 0);
    const width = toNum(mainRect.getAttribute('width'), 0);
    const height = toNum(mainRect.getAttribute('height'), 0);
    const rx = toNum(mainRect.getAttribute('rx'), 18);
    const ry = toNum(mainRect.getAttribute('ry'), 18);

    if (width <= 18 || height <= 18) {
      return;
    }

    innerRect.setAttribute('class', 'ca-glass-inner-border');
    innerRect.setAttribute('x', String(x + 5.5));
    innerRect.setAttribute('y', String(y + 5.5));
    innerRect.setAttribute('width', String(Math.max(8, width - 11.0)));
    innerRect.setAttribute('height', String(Math.max(8, height - 11.0)));
    innerRect.setAttribute('rx', String(Math.max(6, rx - 5.0)));
    innerRect.setAttribute('ry', String(Math.max(6, ry - 5.0)));
    innerRect.setAttribute('fill', 'transparent');
    innerRect.setAttribute('fill-opacity', '0');
    innerRect.setAttribute('pointer-events', 'none');

    mainRect.insertAdjacentElement('afterend', innerRect);
    el.setAttribute('data-ca-glass-luxe', '1');
  });
})();
]]></script>
""".strip()


def _ca_edge_cleanup_luxe_style() -> str:
    return """
<style><![CDATA[
  .caPremiumSvg {
    background:
      radial-gradient(circle at 26% 24%, rgba(82, 214, 255, 0.045), transparent 24%),
      radial-gradient(circle at 73% 33%, rgba(121, 98, 255, 0.040), transparent 18%),
      linear-gradient(180deg, rgba(4, 8, 16, 0.99), rgba(7, 14, 24, 1));
  }

  .caViewportBackdrop {
    fill: rgba(4, 10, 18, 0.92) !important;
  }

  #edgesLayer {
    opacity: 0.96 !important;
  }

  #edgesLayer > * {
    --ca-edge-rgb: 140, 239, 255;
    opacity: 0.58 !important;
    transition:
      opacity 180ms ease,
      filter 180ms ease,
      transform 180ms ease;
  }

  #edgesLayer > *.is-dim {
    opacity: 0.06 !important;
    filter: blur(0.15px) saturate(0.62);
  }

  #edgesLayer > *.is-hot {
    opacity: 1 !important;
    filter:
      brightness(1.08)
      saturate(1.16)
      drop-shadow(0 0 3px rgba(var(--ca-edge-rgb), 0.18))
      drop-shadow(0 0 8px rgba(var(--ca-edge-rgb), 0.08));
  }

  #edgesLayer .ca-edge-path,
  #edgesLayer > path {
    fill: none !important;
    stroke: rgba(var(--ca-edge-rgb), 0.42) !important;
    stroke-width: 1.16px !important;
    stroke-linecap: round;
    stroke-linejoin: round;
    filter:
      drop-shadow(0 0 2px rgba(var(--ca-edge-rgb), 0.08));
  }

  #edgesLayer > *.is-hot .ca-edge-path,
  #edgesLayer > path.is-hot {
    stroke: rgba(var(--ca-edge-rgb), 0.96) !important;
    stroke-width: 1.42px !important;
    stroke-dasharray: 7 13;
    animation: caEdgeFlow 2.35s linear infinite;
    filter:
      drop-shadow(0 0 3px rgba(var(--ca-edge-rgb), 0.18))
      drop-shadow(0 0 7px rgba(var(--ca-edge-rgb), 0.07));
  }

  #nodesLayer .nodeGroup .node-label {
    filter:
      drop-shadow(0 0 2px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.08))
      drop-shadow(0 0 5px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.03)) !important;
  }

  #nodesLayer .nodeGroup .node-subtitle {
    filter:
      drop-shadow(0 0 1px rgba(var(--ca-accent-rgb, 160, 236, 255), 0.03)) !important;
  }
]]></style>
""".strip()


def _ca_edge_cleanup_luxe_script() -> str:
    return """
<script><![CDATA[
(() => {
  const root = document.currentScript && document.currentScript.ownerSVGElement;
  if (!root) {
    return;
  }

  const scene = root.querySelector('#caScene');
  const defs = root.querySelector('defs');
  const edgesLayer = root.querySelector('#edgesLayer');
  if (!scene || !defs || !edgesLayer) {
    return;
  }

  const edgeGroups = Array.from(edgesLayer.children || []);
  const palette = [
    '140, 239, 255',
    '88, 232, 156',
    '255, 173, 92',
    '218, 132, 255',
    '255, 118, 190'
  ];

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

  const hashText = (text) => {
    let hash = 0;
    const source = String(text || '');
    for (let i = 0; i < source.length; i += 1) {
      hash = ((hash << 5) - hash) + source.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash);
  };

  const parseViewBox = () => {
    const raw = (root.getAttribute('viewBox') || '0 0 1600 980')
      .trim()
      .split(/\\s+/)
      .map(Number);
    return {
      x: raw[0] || 0,
      y: raw[1] || 0,
      w: raw[2] || 1600,
      h: raw[3] || 980,
    };
  };

  const parseEdgeEndpoints = (el) => {
    const sourceAttr = (el.getAttribute('data-ca-source') || '').trim();
    const targetAttr = (el.getAttribute('data-ca-target') || '').trim();
    if (sourceAttr || targetAttr) {
      return { source: sourceAttr, target: targetAttr };
    }

    const titleText = ((el.querySelector('title') || {}).textContent || '').trim();
    const match = titleText.match(/^\\s*(.*?)\\s*->\\s*(.*?)\\s*(?:\\||$)/);
    if (!match) {
      return { source: '', target: '' };
    }
    return {
      source: (match[1] || '').trim(),
      target: (match[2] || '').trim(),
    };
  };

  const colorForEdge = (source, target) => {
    const index = hashText(`${source}->${target}`) % palette.length;
    return palette[index];
  };

  let markerCounter = 0;

  const restyleMarkerClone = (markerEl, rgbText) => {
    markerEl.setAttribute('markerWidth', '6.2');
    markerEl.setAttribute('markerHeight', '6.2');
    markerEl.setAttribute('refX', '5.2');
    markerEl.setAttribute('refY', '3.1');
    markerEl.setAttribute('overflow', 'visible');

    Array.from(markerEl.querySelectorAll('path, polygon, polyline')).forEach((shape) => {
      shape.setAttribute('fill', 'none');
      shape.setAttribute('stroke', `rgba(${rgbText}, 0.95)`);
      shape.setAttribute('stroke-width', '1.05');
      shape.setAttribute('stroke-linecap', 'round');
      shape.setAttribute('stroke-linejoin', 'round');
      shape.style.fill = 'none';
      shape.style.stroke = `rgba(${rgbText}, 0.95)`;
      shape.style.strokeWidth = '1.05px';
      shape.style.strokeLinecap = 'round';
      shape.style.strokeLinejoin = 'round';
      shape.style.opacity = '0.98';
    });
  };

  const cloneMarkerForPath = (pathEl, attrName, rgbText) => {
    const raw = (pathEl.getAttribute(attrName) || '').trim();
    const match = raw.match(/^url\\(#(.+)\\)$/);
    if (!match) {
      return;
    }

    const baseId = match[1];
    const original = root.querySelector(`#${CSS.escape(baseId)}`);
    if (!original) {
      return;
    }

    const cloned = original.cloneNode(true);
    const nextId = `${baseId}-ca-edge-${markerCounter++}`;
    cloned.setAttribute('id', nextId);
    restyleMarkerClone(cloned, rgbText);
    defs.appendChild(cloned);
    pathEl.setAttribute(attrName, `url(#${nextId})`);
  };

  const assignEdgeColor = (recordEl) => {
    const ends = parseEdgeEndpoints(recordEl);
    const rgbText = colorForEdge(ends.source, ends.target);
    recordEl.style.setProperty('--ca-edge-rgb', rgbText);

    Array.from(recordEl.querySelectorAll('path')).forEach((pathEl) => {
      pathEl.classList.add('ca-edge-path');
      pathEl.style.fill = 'none';
      pathEl.style.stroke = `rgba(${rgbText}, 0.42)`;
      pathEl.style.strokeWidth = '1.16px';
      pathEl.style.strokeLinecap = 'round';
      pathEl.style.strokeLinejoin = 'round';

      cloneMarkerForPath(pathEl, 'marker-start', rgbText);
      cloneMarkerForPath(pathEl, 'marker-end', rgbText);
    });
  };

  const tightenInitialViewport = () => {
    const box = scene.getBBox();
    if (!box || !box.width || !box.height) {
      return;
    }

    const view = parseViewBox();
    const padX = view.w * 0.07;
    const padY = view.h * 0.10;

    const scale = clamp(
      Math.min(
        (view.w - (padX * 2)) / box.width,
        (view.h - (padY * 2)) / box.height
      ) * 1.46,
      0.55,
      9.5
    );

    const tx = ((view.w - (box.width * scale)) / 2) - (box.x * scale);
    const ty = ((view.h * 0.46) - ((box.y + (box.height / 2)) * scale));

    scene.setAttribute('transform', `translate(${tx} ${ty}) scale(${scale})`);
  };

  edgeGroups.forEach(assignEdgeColor);

  requestAnimationFrame(() => {
    tightenInitialViewport();
  });
})();
]]></script>
""".strip()


def enhance_svg_markup_for_premium_viewer(
    svg_markup: str,
    *,
    state: AnalysisState,
) -> str:
    opening_tag, body = _ca_extract_svg_shell(svg_markup)
    if not opening_tag:
        return svg_markup

    width, height, view_box = _ca_svg_canvas(opening_tag)
    defs_markup, content_markup = _ca_split_defs_and_content(body)

    if not content_markup.strip():
        return svg_markup

    theme_label = html.escape(clean_text(getattr(state, "theme", "")).upper()[:24] or "THEME")
    view_label = html.escape(clean_text(getattr(state, "view", "")).upper() or "VIEW")
    aria_label = html.escape(f"Dependency Graph Premium Â· {clean_text(getattr(state, 'view', 'graph'))}")

    hud_x = max(24.0, float(width) - 328.0)

    hud_markup = f"""
<g id="caHud" transform="translate({hud_x:.1f}, 18)">
  <rect width="296" height="118" rx="18" ry="18" fill="rgba(8,14,24,0.86)" stroke="rgba(148,236,255,0.20)" stroke-width="1.0" />
  <text class="caHudTitle" x="18" y="24">INTERACTIVE VIEWER</text>
  <text class="caHudMeta" x="18" y="42">{theme_label} â€¢ {view_label}</text>

  <g class="caHudButton" data-ca-action="fit" transform="translate(18, 58)">
    <rect width="78" height="26" />
    <text x="39" y="13">FIT</text>
  </g>

  <g class="caHudButton" data-ca-action="one" transform="translate(108, 58)">
    <rect width="78" height="26" />
    <text x="39" y="13">100%</text>
  </g>

  <g class="caHudButton" data-ca-action="reset" transform="translate(198, 58)">
    <rect width="78" height="26" />
    <text x="39" y="13">RESET</text>
  </g>

  <rect class="caHudBadge" x="18" y="92" width="258" height="16" rx="8" ry="8" />
  <text class="caHudHint" x="28" y="103">drag pan â€¢ wheel zoom â€¢ click node focus â€¢ dblclick fit</text>
</g>
""".strip()

    rebuilt = f"""<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="{view_box}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{aria_label}" class="caPremiumSvg">
  {defs_markup}
  {_ca_premium_style()}
  {_ca_ultra_premium_style()}
  {_ca_spectral_relation_style()}
  {_ca_edge_cleanup_luxe_style()}
  <rect class="caViewportBackdrop" x="0" y="0" width="{width}" height="{height}" />
  <g id="caViewport">
    <g id="caScene">
      {content_markup}
    </g>
  </g>
  {hud_markup}
  {_ca_premium_script()}
  {_ca_ultra_premium_script()}
  {_ca_spectral_relation_script()}
  {_ca_edge_cleanup_luxe_script()}
</svg>"""
    return rebuilt


def destroy_progress_ui(progress: Optional[ProgressUI]) -> None:
    if progress is None:
        return

    try:
        close_method = getattr(progress, "close", None)
        if callable(close_method):
            close_method()
            return
    except Exception:
        pass

    root = getattr(progress, "root", None)
    try:
        if root is not None and hasattr(root, "close"):
            root.close()
            ensure_app().processEvents()
    except Exception:
        pass


def show_message_dialog(
    level: Literal["info", "error"],
    title: str,
    message: str,
    parent: QWidget | None = None,
    theme_id: str | None = None,
) -> None:
    ensure_app()

    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(message)
    box.setTextFormat(Qt.PlainText)
    box.setStandardButtons(QMessageBox.Ok)
    box.setIcon(QMessageBox.Information if level == "info" else QMessageBox.Critical)
    box.setStyleSheet(app_stylesheet(theme_id or DEFAULT_THEME))

    for button in box.buttons():
        button.setProperty("variant", "primary" if level == "info" else "danger")
        repolish(button)

    box.exec()


def open_output_location(path: Path) -> None:
    target = Path(path).expanduser()
    if target.is_file():
        target = target.parent

    if not target.exists():
        return

    target_str = str(target)

    try:
        if hasattr(os, "startfile"):
            os.startfile(target_str)  # type: ignore[attr-defined]
            return
    except Exception:
        pass

    try:
        import subprocess
        import sys

        if sys.platform == "darwin":
            subprocess.Popen(["open", target_str])
            return

        if os.name == "posix":
            subprocess.Popen(["xdg-open", target_str])
            return
    except Exception:
        pass


def build_success_message(
    *,
    output_path: Path,
    state: AnalysisState,
    graph: DependencyGraph,
    visual_sidecar: VisualControlExportResult | None = None,
) -> str:
    lines = [
        "SVG generado con éxito.",
        "",
        f"Archivo: {output_path}",
        f"Vista: {state.view} • Preset: {state.visibility_preset} • Tema: {state.theme}",
        f"Nodos: {len(graph.nodes)} • Relaciones: {len(graph.edges)}",
    ]

    if state.external_roots_total > 0:
        lines.append(
            f"Externos detectados: {state.external_import_total} refs • {state.external_roots_total} roots"
        )
    if state.visible_external_bucket_count > 0:
        lines.append(
            "Buckets externos visibles: "
            + ", ".join(state.visible_external_bucket_labels[:4])
        )

    if state.hidden_issue_count > 0:
        lines.append(f"Issues fuera del canvas: {state.hidden_issue_count}")

    if state.view == "focus":
        lines.append(f"Foco: {state.focus_target or '(auto)'}")

    if graph.issues:
        lines.append(f"Issues: {len(graph.issues)}")

    if state.truncated:
        lines.append("Aviso: el análisis fue truncado por límites de seguridad.")

    if visual_sidecar is not None:
        lines.extend(
            [
                (
                    "Sidecar visual: "
                    f"{visual_sidecar.paths.svg_path.name} | "
                    f"{visual_sidecar.paths.markdown_path.name} | "
                    f"{visual_sidecar.paths.json_path.name}"
                ),
                f"Mapa visual: {visual_sidecar.paths.svg_path}",
            ]
        )

    lines.extend(
        [
            "",
            "Se abrirá la carpeta de salida al cerrar esta ventana.",
        ]
    )
    return "\n".join(lines)


def build_success_footer_text(
    *,
    output_path: Path,
    state: AnalysisState,
    graph: DependencyGraph,
    visual_sidecar: VisualControlExportResult | None = None,
) -> str:
    lines = [
        f"Archivo: {short_path(str(output_path), 92)}",
        f"Vista: {state.view} • Preset: {state.visibility_preset} • Tema: {state.theme}",
        f"Nodos: {len(graph.nodes)} • Relaciones: {len(graph.edges)}",
    ]
    if state.external_roots_total > 0:
        lines.append(
            f"Externos detectados: {state.external_import_total} refs • {state.external_roots_total} roots"
        )
    if visual_sidecar is not None:
        lines.append(
            f"Sidecar visual: {short_path(str(visual_sidecar.paths.svg_path), 92)}"
        )
    lines.append("Cierra esta ventana para generar otro grafo. La carpeta de salida se abrirá al cerrar.")
    return "\n".join(lines)


def build_tree_success_message(
    *,
    output_path: Path,
    state: AnalysisState,
    graph: DependencyGraph,
    relevant_path_count: int,
) -> str:
    lines = [
        "Tree .txt generado con éxito.",
        "",
        f"Archivo: {output_path}",
        f"Vista: {state.view} • Preset: {state.visibility_preset} • Tema: {state.theme}",
        f"Archivos relevantes: {relevant_path_count}",
        f"Nodos: {len(graph.nodes)} • Relaciones: {len(graph.edges)}",
    ]

    if state.external_roots_total > 0:
        lines.append(
            f"Externos detectados: {state.external_import_total} refs • {state.external_roots_total} roots"
        )

    if state.hidden_issue_count > 0:
        lines.append(f"Issues fuera del tree visible: {state.hidden_issue_count}")

    if state.view == "focus":
        lines.append(f"Foco: {state.focus_target or '(auto)'}")

    if graph.issues:
        lines.append(f"Issues: {len(graph.issues)}")

    if state.truncated:
        lines.append("Aviso: el análisis fue truncado por límites de seguridad.")

    lines.extend(
        [
            "",
            "Se abrirá la carpeta de salida al cerrar esta ventana.",
        ]
    )
    return "\n".join(lines)


def build_tree_success_footer_text(
    *,
    output_path: Path,
    state: AnalysisState,
    graph: DependencyGraph,
    relevant_path_count: int,
) -> str:
    lines = [
        f"Archivo: {short_path(str(output_path), 92)}",
        f"Vista: {state.view} • Preset: {state.visibility_preset} • Tema: {state.theme}",
        f"Archivos relevantes: {relevant_path_count} • Nodos: {len(graph.nodes)} • Relaciones: {len(graph.edges)}",
    ]
    lines.append("Cierra esta ventana para generar otro tree. La carpeta de salida se abrirá al cerrar.")
    return "\n".join(lines)


def build_filesystem_tree_success_message(
    *,
    output_path: Path,
    state: AnalysisState,
    summary: FileTreeSummary,
    label: str,
) -> str:
    return "\n".join(
        [
            f"{label} generado con éxito.",
            "",
            f"Archivo: {output_path}",
            f"Project root: {state.project_root}",
            f"Total folders: {summary.total_folders}",
            f"Total files: {summary.total_files}",
            f"Total size: {format_size_bytes(summary.total_size_bytes)}",
            f"Max depth: {summary.max_depth}",
            f"Scanned: {summary.scanned_at}",
            "",
            "Se abrirá la carpeta de salida al cerrar esta ventana.",
        ]
    )


def build_filesystem_tree_success_footer_text(
    *,
    output_path: Path,
    summary: FileTreeSummary,
) -> str:
    return "\n".join(
        [
            f"Archivo: {short_path(str(output_path), 92)}",
            (
                f"Folders: {summary.total_folders} • Files: {summary.total_files} • "
                f"Size: {format_size_bytes(summary.total_size_bytes)} • Max depth: {summary.max_depth}"
            ),
            "Cierra esta ventana para generar otro reporte. La carpeta F:\\trees se abrirá al cerrar.",
        ]
    )


def main() -> int:
    progress: Optional[ProgressUI] = None
    selected_theme = DEFAULT_THEME

    try:
        ensure_app()
        while True:
            # 1. Elegir opciones
            selection = choose_options()
            selected_theme = normalize_theme(selection.theme)
            output_mode = _coerce_output_mode(selection.output_mode)

            # 2. Validar selección / ruta
            selected_path = _resolve_selected_path(selection)
            if selected_path is None:
                return 0

            # 3. Resolver foco efectivo
            effective_focus_target = resolve_effective_focus_target(
                selected_path=str(selected_path),
                view=selection.view,
                requested_focus_target=selection.focus_target,
            )

            # 4. Crear UI de progreso
            progress = ProgressUI(theme_id=selected_theme)
            notify = _make_progress_notifier(progress)
            analysis_notify = (
                _make_tree_analysis_notifier(notify)
                if output_mode == "tree"
                else notify
            )
            notify(
                "Preparando ejecución...",
                _initial_progress_detail(selection, selected_path),
            )

            # 5. Construir AnalysisState
            state = _build_analysis_state(selection, selected_path, effective_focus_target)
            if state.view == "focus":
                notify(
                    "Modo foco preparado.",
                    state.focus_target or "sin objetivo explícito, se elegirá por conectividad",
                )

            if output_mode in {"tree", "tree_html"}:
                project_root = Path(state.project_root)
                notify("Detectando filesystem...", str(project_root))
                notify("Escaneando carpetas y archivos...", str(project_root))
                file_tree_entries, file_tree_summary = collect_filesystem_tree_entries(project_root)
                notify(
                    "Calculando tamaños...",
                    (
                        f"{file_tree_summary.total_folders} folders | "
                        f"{file_tree_summary.total_files} files | "
                        f"{format_size_bytes(file_tree_summary.total_size_bytes)}"
                    ),
                )

                if output_mode == "tree_html":
                    notify(
                        "Construyendo Tree HTML Premium...",
                        f"{file_tree_summary.total_folders} folders | {file_tree_summary.total_files} files",
                    )
                    html_markup = build_premium_tree_html(
                        selected_path=state.selected_path,
                        project_root=project_root,
                        entries=file_tree_entries,
                        summary=file_tree_summary,
                    )
                    output_path = make_tree_html_output_path(
                        selected_path=state.selected_path,
                        view=state.view,
                        focus_target=state.focus_target,
                    )
                    write_tree_html(html_markup, output_path, notify)
                    output_label = "Tree HTML Premium"
                else:
                    notify(
                        "Construyendo tree...",
                        f"{file_tree_summary.total_folders} folders | {file_tree_summary.total_files} files",
                    )
                    tree_text = build_filesystem_tree_text(
                        selected_path=state.selected_path,
                        project_root=project_root,
                        entries=file_tree_entries,
                        summary=file_tree_summary,
                    )
                    output_path = make_tree_output_path(
                        selected_path=state.selected_path,
                        view=state.view,
                        focus_target=state.focus_target,
                    )
                    write_tree_txt(tree_text, output_path, notify)
                    output_label = "Tree .txt"

                notify("Validando salida...", str(output_path))
                if not output_path.exists() or output_path.stat().st_size <= 0:
                    raise RuntimeError(f"No se pudo validar la salida generada: {output_path}")

                success_detail = build_filesystem_tree_success_message(
                    output_path=output_path,
                    state=state,
                    summary=file_tree_summary,
                    label=output_label,
                )
                _finalize_progress(progress, "Todo quedó listo.", success_detail)
                _set_progress_footer(
                    progress,
                    build_filesystem_tree_success_footer_text(
                        output_path=output_path,
                        summary=file_tree_summary,
                    ),
                )

                _wait_for_user_close(progress)
                open_output_location(output_path.parent)
                destroy_progress_ui(progress)
                progress = None
                continue

            # 6. Analizar dependencias del proyecto
            module_catalog, import_refs, analysis_graph = analyze_project_dependencies(
                selected_path=state.selected_path,
                state=state,
                notify=analysis_notify,
            )
            apply_analysis_summaries(state, module_catalog, import_refs)

            # 7. Construir grafo de dependencias
            notify("Construyendo grafo final...", f"vista {state.view}")
            graph = construct_dependency_graph(
                state=state,
                module_catalog=module_catalog,
                import_refs=import_refs,
                include_external_in_module_view=(
                    state.visibility_preset in {"engineering", "raw"}
                    and state.view in {"module", "focus"}
                ),
            )

            # 8. Fusionar issues
            merge_analysis_issues_into_graph(graph, analysis_graph)

            # 9. Enriquecer grafo para presentación
            graph = enrich_graph_for_presentation(graph, state)

            # 10. Simplificar solo la capa visible, sin tocar discovery
            graph = simplify_visible_graph(graph, state)
            graph = _ensure_graph_has_visible_content(graph, state)

            # 11. Calcular layout
            notify("Calculando layout...", f"{len(graph.nodes)} nodos")
            layout = relayout_dependency_graph_as_layered_hierarchy(
                graph,
                state,
                layout_dependency_graph(graph, state, notify),
                notify,
            )

            # 12. Renderizar SVG
            svg_markup = enhance_svg_markup_for_premium_viewer(render_svg(graph, layout, state, notify), state=state)

            # 13. Guardar SVG
            output_path = make_output_path(
                selected_path=state.selected_path,
                theme=state.theme,
                view=state.view,
                focus_target=state.focus_target,
            )
            write_svg(svg_markup, output_path, notify)

            visual_sidecar: VisualControlExportResult | None = None
            if ENABLE_VISUAL_CONTROL_SIDECAR:
                visual_sidecar = export_visual_control_sidecar(
                    selected_path=state.selected_path,
                    theme_id=state.theme,
                    notify=notify,
                )
                notify(
                    "Sidecar visual exportado.",
                    (
                        f"svg={visual_sidecar.paths.svg_path.name} | "
                        f"md={visual_sidecar.paths.markdown_path.name} | "
                        f"json={visual_sidecar.paths.json_path.name} | "
                        f"forensics={visual_sidecar.paths.forensics_json_path.name}"
                    ),
                )

            # 14. Mostrar éxito SVG
            success_detail = build_success_message(
                output_path=output_path,
                state=state,
                graph=graph,
                visual_sidecar=visual_sidecar,
            )
            _finalize_progress(progress, "Todo quedó listo.", success_detail)
            _set_progress_footer(
                progress,
                build_success_footer_text(
                    output_path=output_path,
                    state=state,
                    graph=graph,
                    visual_sidecar=visual_sidecar,
                ),
            )

            # 15. Esperar cierre manual y volver al selector
            _wait_for_user_close(progress)

            # 16. Abrir carpeta de salida al cierre
            open_output_location(output_path.parent)
            destroy_progress_ui(progress)
            progress = None

    except _PipelineCancelled:
        return 0

    except KeyboardInterrupt:
        destroy_progress_ui(progress)
        progress = None
        return 130

    except FileNotFoundError as exc:
        destroy_progress_ui(progress)
        progress = None
        show_message_dialog("error", APP_TITLE, str(exc), theme_id=selected_theme)
        return 1

    except Exception:
        error_text = traceback.format_exc()
        destroy_progress_ui(progress)
        progress = None
        show_message_dialog(
            "error",
            APP_TITLE,
            f"Se produjo un error inesperado.\n\n{error_text}",
            theme_id=selected_theme,
        )
        return 1

    finally:
        destroy_progress_ui(progress)




# CODE_ATLAS_NO_BLACK_CONSOLE_V1: relanza la app sin consola negra en Windows.
def _code_atlas_relaunch_without_black_console() -> bool:
    """Relaunch this GUI script without a console window on Windows.

    This is intentionally tiny and isolated: it does not modify the UI, the
    glass scene, the selector, the progress window, or any rendering code.
    It only changes the launcher behavior when the script starts under
    python.exe, because Windows loves opening a black rectangle like it owns
    the place.
    """
    try:
        import os as _os
        import subprocess as _subprocess
        import sys as _sys
        from pathlib import Path as _Path

        if _os.name != "nt":
            return False

        if _os.environ.get("CODE_ATLAS_NO_BLACK_CONSOLE_V1") == "1":
            return False

        if _os.environ.get("CODE_ATLAS_KEEP_CONSOLE", "").strip().lower() in {"1", "true", "yes", "on"}:
            return False

        executable = _Path(_sys.executable)
        if executable.name.lower() == "pythonw.exe":
            return False

        script_path = _Path(__file__).resolve()
        pythonw = executable.with_name("pythonw.exe")
        launch_exe = pythonw if pythonw.exists() else executable

        env = _os.environ.copy()
        env["CODE_ATLAS_NO_BLACK_CONSOLE_V1"] = "1"

        creationflags = 0
        for flag_name in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
            creationflags |= int(getattr(_subprocess, flag_name, 0))

        _subprocess.Popen(
            [str(launch_exe), str(script_path), *_sys.argv[1:]],
            cwd=str(script_path.parent),
            env=env,
            stdin=_subprocess.DEVNULL,
            stdout=_subprocess.DEVNULL,
            stderr=_subprocess.DEVNULL,
            close_fds=True,
            creationflags=creationflags,
        )
        return True
    except Exception:
        return False

if __name__ == "__main__":
    if _code_atlas_relaunch_without_black_console():
        raise SystemExit(0)
    raise SystemExit(main())
