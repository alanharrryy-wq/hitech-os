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


# ----------------------------
# Metadata general
# ----------------------------

APP_TITLE = "Dependency Graph SVG"

DEFAULT_THEME_ID = "dark"
DEFAULT_VIEW: GraphView = "package"

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
}

# Límites de seguridad
MAX_FILES_ANALYZED = 3000
MAX_EDGES = 12000
MAX_IMPORTS_PER_FILE = 400
MAX_PARSE_ERRORS = 120

# Salida dinámica: se crea dentro de la ruta seleccionada
OUTPUT_SUBDIR_NAME = "_dependency_graphs"
OUTPUT_FILE_PREFIX = "dependency_graph"
DATE_STAMP_FORMAT = "%Y%m%d_%H%M%S"

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

    total_files_seen: int = 0
    source_files_seen: int = 0
    parsed_files: int = 0
    skipped_files: int = 0
    parse_errors: int = 0

    total_nodes: int = 0
    total_edges: int = 0

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


def is_excluded_dir_name(name: str) -> bool:
    return name.strip() in EXCLUDED_DIR_NAMES


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


def build_state_summary(state: AnalysisState) -> str:
    chunks = [
        f"{state.source_files_seen} fuentes",
        f"{state.parsed_files} parseados",
        f"{state.total_nodes} nodos",
        f"{state.total_edges} relaciones",
        f"vista {state.view}",
        f"tema {state.theme}",
    ]

    if state.truncated:
        chunks.append("análisis truncado")

    return " • ".join(chunks)


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

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
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
    QVBoxLayout,
    QWidget,
)


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
) -> SelectionResult:
    return SelectionResult(
        path=path,
        theme=theme,
        view=view,
        focus_target=focus_target,
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


def app_stylesheet(theme_id: Optional[str] = None) -> str:
    resolved_theme = normalize_theme(theme_id or DEFAULT_THEME)
    return build_app_stylesheet(resolved_theme)


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
    button = QPushButton(text, parent)
    button.setCursor(Qt.PointingHandCursor)
    button.setProperty("variant", variant or "secondary")
    button.setEnabled(enabled)
    button.setDefault(bool(default))
    button.setAutoDefault(bool(default) if auto_default is None else bool(auto_default))

    if minimum_width > 0:
        button.setMinimumWidth(int(minimum_width))
    if tooltip:
        button.setToolTip(tooltip)
    if callable(callback):
        button.clicked.connect(callback)

    apply_shadow(button, blur=18.0, y_offset=4.0, alpha=38)
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
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("Shell")
        apply_shadow(shell, blur=34.0, y_offset=10.0, alpha=84)
        outer.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(20, 20, 20, 20)
        shell_layout.setSpacing(16)

        header = QFrame()
        header.setProperty("card", "true")
        apply_shadow(header, blur=18.0, y_offset=4.0, alpha=30)
        shell_layout.addWidget(header)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        header_layout.addLayout(top_row)

        title = QLabel("Dependency Graph SVG")
        title.setProperty("role", "title")
        top_row.addWidget(title, 1)

        self.mode_chip = QLabel("Selector")
        self.mode_chip.setProperty("chip", True)
        self.mode_chip.setProperty("tone", "accent")
        self.mode_chip.setAlignment(Qt.AlignCenter)
        top_row.addWidget(self.mode_chip, 0)

        subtitle = QLabel(
            "Elige la ruta, el tema y la vista. La ruta es editable para pegar, corregir o afinar "
            "sin andar peleándote con el explorador."
        )
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        content = QHBoxLayout()
        content.setSpacing(16)
        shell_layout.addLayout(content, 1)

        self.form_card = QFrame()
        self.form_card.setProperty("card", "true")
        apply_shadow(self.form_card, blur=18.0, y_offset=4.0, alpha=28)
        content.addWidget(self.form_card, 6)

        self.preview_card = QFrame()
        self.preview_card.setProperty("card", "muted")
        apply_shadow(self.preview_card, blur=18.0, y_offset=4.0, alpha=24)
        content.addWidget(self.preview_card, 5)

        self._build_form_panel()
        self._build_preview_panel()

        footer = QFrame()
        footer.setProperty("card", "muted")
        shell_layout.addWidget(footer)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 12)
        footer_layout.setSpacing(10)

        footer_hint = QLabel(
            "La salida se guardará dentro de la carpeta analizada, en una subcarpeta dedicada."
        )
        footer_hint.setProperty("role", "hint")
        footer_hint.setWordWrap(True)
        footer_layout.addWidget(footer_hint, 1)

        self.cancel_button = create_button("Cancelar", "danger", self.cancel, minimum_width=120)
        self.confirm_button = create_button(
            "Generar SVG",
            "primary",
            self.confirm,
            default=True,
            minimum_width=144,
        )
        footer_layout.addWidget(self.cancel_button, 0)
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

        self.setWindowTitle(window_title or _app_title())
        self.setModal(False)
        self.setMinimumSize(760, 260)
        self.resize(820, 290)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet(app_stylesheet(theme_id or DEFAULT_THEME))

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
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(0)

 
        shell = QFrame()
        shell.setObjectName("Shell")
        apply_shadow(shell, blur=30.0, y_offset=10.0, alpha=82)
        outer.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(18, 18, 18, 18)
        shell_layout.setSpacing(14)

        card = QFrame()
        card.setProperty("card", "true")
        apply_shadow(card, blur=18.0, y_offset=4.0, alpha=28)
        shell_layout.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Armando el grafo de dependencias")
        title.setProperty("role", "title")
        layout.addWidget(title)

        subtitle = QLabel(
            "Escaneando estructura, resolviendo imports y preparando el SVG final."
        )
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addWidget(make_separator())

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

        self.state_chip = QLabel("En curso")
        self.state_chip.setProperty("chip", True)
        self.state_chip.setProperty("tone", "accent")
        self.state_chip.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.state_chip, 0, Qt.AlignLeft)

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
    - mete issues como notes visibles
    - recalcula métricas
    - sincroniza totales en state
    """
    if graph.issues:
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
        is_default=True,
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

def build_app_stylesheet(theme_id: str) -> str:
    render = resolve_render_theme(theme_id)
    t = render.tokens
    dark = render.is_dark

    dialog_bg = t["canvas_bg"]
    shell_bg = _mix_hex(t["header_fill"], t["canvas_bg"], 0.34 if dark else 0.10)
    card_bg = t["legend_fill"]
    card_muted_bg = _mix_hex(card_bg, t["canvas_bg"], 0.26 if dark else 0.08)
    soft_border = _with_alpha(t["header_stroke"], 0.14 if dark else 0.34)
    card_border = _with_alpha(t["legend_stroke"], 0.18 if dark else 0.40)
    line = _with_alpha(t["header_stroke"], 0.14 if dark else 0.28)

    title = t["header_title"]
    subtitle = t["header_meta"]
    section = t["header_title"]
    field = t["focus"]
    hint = t["footer_text"]
    value = t["text_main"]
    mono = t["text_soft"]
    neutral_chip_text = t["text_soft"] if dark else t["header_text"]
    neutral_chip_bg = _with_alpha(t["muted_stroke"], 0.10 if dark else 0.12)
    neutral_chip_border = _with_alpha(t["muted_stroke"], 0.16 if dark else 0.24)
    good_chip_text = _mix_hex(t["badge_out"], t["chip_light"], 0.72 if dark else 0.40)
    good_chip_bg = _with_alpha(t["badge_out"], 0.12 if dark else 0.16)
    good_chip_border = _with_alpha(t["badge_out"], 0.24 if dark else 0.30)
    warn_chip_text = _mix_hex(t["warning_stroke"], t["chip_light"], 0.70 if dark else 0.24)
    warn_chip_bg = _with_alpha(t["warning_stroke"], 0.12 if dark else 0.16)
    warn_chip_border = _with_alpha(t["warning_stroke"], 0.26 if dark else 0.32)
    accent_chip_text = _mix_hex(t["focus"], t["chip_light"], 0.78 if dark else 0.30)
    accent_chip_bg = _with_alpha(t["focus"], 0.12 if dark else 0.14)
    accent_chip_border = _with_alpha(t["focus"], 0.24 if dark else 0.30)

    input_bg = _mix_hex(t["canvas_bg"], t["legend_fill"], 0.18 if dark else 0.04)
    input_fg = value
    input_border = _with_alpha(t["legend_stroke"], 0.16 if dark else 0.36)
    input_hover = _with_alpha(t["focus"], 0.26 if dark else 0.34)
    input_focus = _with_alpha(t["focus"], 0.72 if dark else 0.72)
    input_focus_bg = _mix_hex(input_bg, t["header_fill"], 0.12 if dark else 0.05)
    input_disabled_fg = _with_alpha(t["muted_text"], 0.82)
    input_disabled_bg = _mix_hex(input_bg, t["canvas_bg"], 0.22 if dark else 0.10)
    input_disabled_border = _with_alpha(t["legend_stroke"], 0.08 if dark else 0.20)
    dropdown_bg = _mix_hex(card_bg, t["canvas_bg"], 0.10 if dark else 0.02)
    selection_bg = t["focus"]
    selection_fg = t["chip_light"]

    primary_bg = t["focus"]
    primary_border = _with_alpha(t["focus"], 0.34 if dark else 0.38)
    primary_hover = _mix_hex(t["focus"], t["chip_light"], 0.10 if dark else 0.12)
    secondary_bg = _mix_hex(shell_bg, t["canvas_bg"], 0.14 if dark else 0.06)
    secondary_border = _with_alpha(t["legend_stroke"], 0.14 if dark else 0.28)
    secondary_hover = _mix_hex(secondary_bg, t["focus"], 0.10 if dark else 0.06)
    success_bg = t["badge_out"]
    success_border = _with_alpha(t["badge_out"], 0.28 if dark else 0.32)
    success_hover = _mix_hex(t["badge_out"], t["chip_light"], 0.08 if dark else 0.10)
    danger_bg = _mix_hex(shell_bg, t["warning_fill"], 0.18 if dark else 0.10)
    danger_border = _with_alpha(t["warning_stroke"], 0.18 if dark else 0.28)
    danger_hover = _mix_hex(danger_bg, t["warning_stroke"], 0.10 if dark else 0.08)
    disabled_bg = _mix_hex(shell_bg, t["canvas_bg"], 0.18 if dark else 0.08)
    disabled_fg = _with_alpha(t["muted_text"], 0.84)
    disabled_border = _with_alpha(t["legend_stroke"], 0.06 if dark else 0.18)

    progress_bg = input_bg
    progress_border = input_border
    progress_text = value
    progress_chunk = primary_bg

    return f'''
    QDialog {{
        background: {dialog_bg};
        color: {value};
    }}

    QFrame#Shell {{
        background: {shell_bg};
        border: 1px solid {soft_border};
        border-radius: 22px;
    }}

    QFrame[card="true"] {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
    }}

    QFrame[card="muted"] {{
        background: {card_muted_bg};
        border: 1px solid {soft_border};
        border-radius: 16px;
    }}

    QFrame#Line {{
        background: {line};
        min-height: 1px;
        max-height: 1px;
        border-radius: 1px;
    }}

    QLabel[role="title"] {{
        color: {title};
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.2px;
    }}

    QLabel[role="subtitle"] {{
        color: {subtitle};
        font-size: 12px;
    }}

    QLabel[role="section"] {{
        color: {section};
        font-size: 14px;
        font-weight: 700;
    }}

    QLabel[role="field"] {{
        color: {field};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.6px;
    }}

    QLabel[role="hint"] {{
        color: {hint};
        font-size: 11px;
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
        border-radius: 11px;
        padding: 6px 10px;
        font-size: 11px;
        font-weight: 700;
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
    QComboBox {{
        background: {input_bg};
        color: {input_fg};
        border: 1px solid {input_border};
        border-radius: 12px;
        padding: 10px 12px;
        font-size: 12px;
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
    }}

    QLineEdit:hover,
    QComboBox:hover {{
        border: 1px solid {input_hover};
    }}

    QLineEdit:focus,
    QComboBox:focus {{
        border: 1px solid {input_focus};
        background: {input_focus_bg};
    }}

    QLineEdit:disabled,
    QComboBox:disabled {{
        color: {input_disabled_fg};
        background: {input_disabled_bg};
        border: 1px solid {input_disabled_border};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 26px;
        background: transparent;
    }}

    QComboBox::down-arrow {{
        image: none;
        width: 0px;
        height: 0px;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {field};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background: {dropdown_bg};
        color: {value};
        border: 1px solid {card_border};
        selection-background-color: {selection_bg};
        selection-color: {selection_fg};
        outline: none;
        padding: 4px;
    }}

    QPushButton {{
        min-height: 18px;
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 12px;
        font-weight: 700;
        outline: none;
    }}

    QPushButton[variant="primary"] {{
        color: {selection_fg};
        background: {primary_bg};
        border: 1px solid {primary_border};
    }}

    QPushButton[variant="primary"]:hover {{
        background: {primary_hover};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="secondary"] {{
        color: {value};
        background: {secondary_bg};
        border: 1px solid {secondary_border};
    }}

    QPushButton[variant="secondary"]:hover {{
        background: {secondary_hover};
        border: 1px solid {input_hover};
    }}

    QPushButton[variant="success"] {{
        color: {selection_fg};
        background: {success_bg};
        border: 1px solid {success_border};
    }}

    QPushButton[variant="success"]:hover {{
        background: {success_hover};
        border: 1px solid {good_chip_border};
    }}

    QPushButton[variant="danger"] {{
        color: {value};
        background: {danger_bg};
        border: 1px solid {danger_border};
    }}

    QPushButton[variant="danger"]:hover {{
        background: {danger_hover};
        border: 1px solid {warn_chip_border};
    }}

    QPushButton:disabled {{
        color: {disabled_fg};
        background: {disabled_bg};
        border: 1px solid {disabled_border};
    }}

    QProgressBar {{
        min-height: 16px;
        border-radius: 10px;
        background: {progress_bg};
        border: 1px solid {progress_border};
        text-align: center;
        color: {progress_text};
        font-size: 11px;
        font-weight: 700;
    }}

    QProgressBar::chunk {{
        border-radius: 9px;
        background: {progress_chunk};
    }}
    '''.strip()


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


def _edge_tooltip(edge: DependencyEdge, graph: DependencyGraph, role: str) -> str:
    source = graph.nodes.get(edge.source)
    target = graph.nodes.get(edge.target)
    source_label = _clean_text(source.label if source else edge.source)
    target_label = _clean_text(target.label if target else edge.target)
    evidence = sorted(edge.evidence)[:6]
    base = f"{source_label} -> {target_label} | role={role} | weight={int(edge.weight)}"
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
        visuals.append(
            ResolvedEdgeVisual(
                edge=edge,
                role=role,
                preset=preset,
                path_d=_edge_path(source, target, preset),
                tooltip=_edge_tooltip(edge, graph, role),
                layer=preset.layer,
                emphasis=_edge_emphasis(role, edge),
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

    meta = _lane_meta_text(lane)
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
      <text class="lane-title" x="{lane.x + 18.0:.1f}" y="{header_y + 16.0:.1f}" fill="{_escape(p.header_text)}">{_escape(_safe_short(lane.label, 30))}</text>
      <text class="lane-meta" x="{lane.x + 18.0:.1f}" y="{header_y + 31.0:.1f}" fill="{_escape(p.meta_text)}">{_escape(meta)}</text>
      {capsule}
    </g>
    """


def _draw_edge(resolved: ResolvedEdgeVisual) -> str:
    p = resolved.preset
    dash = f' stroke-dasharray="{_escape(p.dasharray)}"' if p.dasharray else ""
    glow = ""
    if p.glow and p.glow_opacity > 0.0:
        glow = (
            f'<path d="{resolved.path_d}" fill="none" stroke="{_escape(p.glow)}" '
            f'stroke-opacity="{p.glow_opacity:.3f}" stroke-width="{p.glow_width:.2f}" '
            f'stroke-linecap="round" filter="url(#glowSoft)"{dash} />'
        )

    return f"""
    <g class="edgeGroup">
      <title>{_escape(resolved.tooltip)}</title>
      {glow}
      <path d="{resolved.path_d}" fill="none"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.opacity:.3f}"
            stroke-width="{p.width:.2f}" stroke-linecap="round"
            marker-end="url(#{_escape(p.marker_id)})"{dash} />
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
    if visual.subtitle:
        subtitle = (
            f'<text class="node-subtitle" x="{label_x:.1f}" y="{subtitle_y:.1f}" '
            f'font-size="{p.subtitle_size:.1f}" font-weight="600" fill="{_escape(p.subtext)}">{_escape(visual.subtitle)}</text>'
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
            font-size="{p.label_size:.1f}" font-weight="{p.text_weight}" fill="{_escape(p.text)}">{_escape(visual.label)}</text>
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
        f"{len(graph.nodes)} nodos",
        f"{len(graph.edges)} relaciones",
    ]
    if state.view == "focus":
        parts.append(f"foco {_clean_text(state.focus_target) or '(auto)'}")
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

    return f"""
    <g class="headerPanel">
      <rect x="{header_x:.1f}" y="{header_y:.1f}" width="{header_w:.1f}" height="{header_h:.1f}"
            rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}"
            filter="url(#shadowSoft)" />
      <rect x="{header_x + 12.0:.1f}" y="{header_y + 12.0:.1f}" width="4.0" height="{header_h - 24.0:.1f}"
            rx="2" ry="2" fill="{_escape(p.accent)}" opacity="0.84" />
      <text class="svg-title" x="{LEFT_MARGIN + 10.0:.1f}" y="{header_y + 38.0:.1f}">{_escape(title)}</text>
      <text class="svg-subtitle" x="{LEFT_MARGIN + 10.0:.1f}" y="{header_y + 58.0:.1f}">{_escape(subtitle)}</text>
      <text class="svg-meta" x="{LEFT_MARGIN + 10.0:.1f}" y="{header_y + 78.0:.1f}">{_escape(path_line)}</text>

      <g transform="translate({identity_x:.1f},{identity_y:.1f})">
        <rect x="0" y="0" width="{identity_w:.1f}" height="26" rx="13" ry="13"
              fill="{_escape(_mix_hex(p.accent, p.fill, 0.20))}" opacity="0.92" />
        <circle cx="16" cy="13" r="4.2" fill="{_escape(p.accent)}" />
        <text class="chip-text" x="{identity_w / 2 + 8.0:.1f}" y="16.0" text-anchor="middle"
              fill="{_escape(p.title)}">{_escape(primary.upper())}</text>
      </g>
      <text class="panel-meta" x="{identity_x + identity_w:.1f}" y="{identity_y + 40.0:.1f}" text-anchor="end" fill="{_escape(p.meta)}">{_escape(identity)}</text>
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


def _draw_legend(width: int, graph: DependencyGraph, state: AnalysisState, theme: SemanticTheme) -> str:
    p = _resolve_panel_preset(theme, "legend")
    counts = _count_nodes_by_kind(graph)
    x = max(LEFT_MARGIN + 12.0, width - 324.0)
    y = 28.0
    w = 286.0
    h = 176.0

    hint = "sin issues relevantes"
    if state.truncated and _clean_text(state.limit_reason):
        hint = _safe_short(state.limit_reason, 36)
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

    return f"""
    <g class="legendPanel">
      <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"
            rx="{p.radius:.1f}" ry="{p.radius:.1f}"
            fill="{_escape(p.fill)}" fill-opacity="{p.fill_opacity:.3f}"
            stroke="{_escape(p.stroke)}" stroke-opacity="{p.stroke_opacity:.3f}" stroke-width="{p.border_width:.2f}"
            filter="url(#shadowSoft)" />
      <rect x="{x + 14.0:.1f}" y="{y + 14.0:.1f}" width="3.6" height="{h - 28.0:.1f}" rx="2" ry="2"
            fill="{_escape(p.accent)}" opacity="0.70" />
      <g transform="translate({x + 18.0:.1f},{y + 12.0:.1f})">
        <text class="panel-title" x="10" y="10" fill="{_escape(p.title)}">Resumen</text>
        {''.join(rows)}
      </g>
    </g>
    """


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

    width = max(1080, int(layout.width or 1080))
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

    header_markup = _draw_header(width, state, graph, semantic_theme)
    legend_markup = _draw_legend(width, graph, state, semantic_theme)
    warning_markup = _draw_warning_panel(width, state, semantic_theme)
    footer_markup = _draw_footer(width, height, state, semantic_theme)

    empty_markup = ""
    if not layout.nodes:
        empty_markup = _empty_state_svg(width, height, semantic_theme, state)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  {semantic_theme.svg_defs}
  {_build_semantic_defs(semantic_theme, width, height)}

  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#semanticCanvasGrad)" />
  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#semanticGrid)" />
  <circle cx="{int(width * 0.16)}" cy="{int(height * 0.08)}" r="{int(max(width, height) * 0.62)}" fill="url(#semanticHaloA)" />
  <circle cx="{int(width * 0.86)}" cy="{int(height * 0.16)}" r="{int(max(width, height) * 0.36)}" fill="url(#semanticHaloB)" />

  {header_markup}
  {legend_markup}
  {warning_markup}

  <g id="lanesLayer">{lanes_markup}</g>
  <g id="edgesLayer">{edges_markup}</g>
  <g id="nodesLayer">{nodes_markup}</g>

  {empty_markup}
  {footer_markup}
</svg>
"""

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
    )


def _initial_progress_detail(selection: SelectionResult, selected_path: Path) -> str:
    chunks = [
        short_path(str(selected_path), 92),
        f"vista {selection.view}",
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
    if graph.nodes or graph.issues:
        return graph

    graph.add_issue(
        "warning",
        "empty_graph",
        "El análisis terminó sin nodos visibles.",
        state.project_root,
    )
    return enrich_graph_for_presentation(graph, state)


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
) -> None:
    ensure_app()

    if level == "info":
        QMessageBox.information(parent, title, message)
        return

    QMessageBox.critical(parent, title, message)


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
) -> str:
    lines = [
        "SVG generado con éxito.",
        "",
        f"Archivo: {output_path}",
        f"Vista: {state.view} • Tema: {state.theme}",
        f"Nodos: {len(graph.nodes)} • Relaciones: {len(graph.edges)}",
    ]

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


def main() -> int:
    progress: Optional[ProgressUI] = None

    try:
        ensure_app()

        # 1. Elegir opciones
        selection = choose_options()

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
        progress = ProgressUI(theme_id=normalize_theme(selection.theme))
        notify = _make_progress_notifier(progress)
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

        # 6. Analizar dependencias del proyecto
        module_catalog, import_refs, analysis_graph = analyze_project_dependencies(
            selected_path=state.selected_path,
            state=state,
            notify=notify,
        )

        # 7. Construir grafo de dependencias
        notify("Construyendo grafo final...", f"vista {state.view}")
        graph = construct_dependency_graph(
            state=state,
            module_catalog=module_catalog,
            import_refs=import_refs,
            include_external_in_module_view=(state.view in {"module", "focus"}),
        )

        # 8. Fusionar issues
        merge_analysis_issues_into_graph(graph, analysis_graph)

        # 9. Enriquecer grafo para presentación
        graph = enrich_graph_for_presentation(graph, state)
        graph = _ensure_graph_has_visible_content(graph, state)

        # 10. Calcular layout
        notify("Calculando layout...", f"{len(graph.nodes)} nodos")
        layout = layout_dependency_graph(graph, state, notify)

        # 11. Renderizar SVG
        svg_markup = render_svg(graph, layout, state, notify)

        # 12. Guardar SVG
        output_path = make_output_path(
            selected_path=state.selected_path,
            theme=state.theme,
            view=state.view,
            focus_target=state.focus_target,
        )
        write_svg(svg_markup, output_path, notify)

        # 13. Mostrar éxito
        _finalize_progress(progress, "Todo quedó listo.", str(output_path))
        show_message_dialog(
            "info",
            APP_TITLE,
            build_success_message(
                output_path=output_path,
                state=state,
                graph=graph,
            ),
            parent=_progress_parent(progress),
        )

        # 14. Abrir carpeta de salida
        open_output_location(output_path.parent)

        # 15. Cierre limpio
        return 0

    except _PipelineCancelled:
        return 0

    except KeyboardInterrupt:
        destroy_progress_ui(progress)
        progress = None
        return 130

    except FileNotFoundError as exc:
        destroy_progress_ui(progress)
        progress = None
        show_message_dialog("error", APP_TITLE, str(exc))
        return 1

    except Exception:
        error_text = traceback.format_exc()
        destroy_progress_ui(progress)
        progress = None
        show_message_dialog(
            "error",
            APP_TITLE,
            f"Se produjo un error inesperado.\n\n{error_text}",
        )
        return 1

    finally:
        destroy_progress_ui(progress)


if __name__ == "__main__":
    raise SystemExit(main())
