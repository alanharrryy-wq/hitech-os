import os
import re
import sys
import time
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from graphviz import Digraph

# ============================================================
# HITECH Repo Graphviz Generator
# ------------------------------------------------------------
# - Scans a repo
# - Groups files by folder
# - Generates graphs per folder
# - Updates only NEW or CHANGED folder graphs since last run
# - Keeps previous generated outputs on disk
# - Uses stable output folder names so new folders do not break old links
# - Optional auto-refresh watch mode
# ============================================================

# ---------------------------
# CONFIG
# ---------------------------
REPO_PATH = Path(r"F:\repos\hitech-os")
TOOLS_ROOT = REPO_PATH / "tools" / "graphviz"
OUTPUT_ROOT = TOOLS_ROOT / "graphs"
STATE_FILE = TOOLS_ROOT / ".graphviz_state.json"
MANIFEST_FILE = TOOLS_ROOT / ".graphviz_manifest.json"

WATCH_MODE = False          # True = keep watching for changes
OPEN_INDEX_ON_FINISH = True # Opens graphs folder when done on Windows
OPEN_FIRST_SVG = False      # Opens the first generated SVG
SLEEP_SECONDS = 15

INCLUDE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"}
EXCLUDE_DIRS = {
    ".git",
    ".next",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".turbo",
    ".venv",
    "venv",
    "out",
    "tmp",
    "temp",
}
EXCLUDE_FILE_SUFFIXES = {
    ".d.ts",
    ".min.js",
}

MAX_EDGES_PER_FOLDER = 400
MAX_LABEL_LENGTH = 64
INTERNAL_ONLY = True
STATE_VERSION = 2

# ---------------------------
# REGEX
# ---------------------------
RE_IMPORT_FROM = re.compile(r'import\s+[\s\S]*?\s+from\s+[\'\"]([^\'\"]+)[\'\"]', re.MULTILINE)
RE_IMPORT_BARE = re.compile(r'(?m)^\s*import\s+[\'\"]([^\'\"]+)[\'\"]')
RE_REQUIRE = re.compile(r'require\(\s*[\'\"]([^\'\"]+)[\'\"]\s*\)')
RE_DYNAMIC_IMPORT = re.compile(r'import\(\s*[\'\"]([^\'\"]+)[\'\"]\s*\)')

# ---------------------------
# HELPERS
# ---------------------------
def is_windows() -> bool:
    return os.name == "nt"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        clean = " ".join(str(a).encode("ascii", "replace").decode("ascii") for a in args)
        print(clean, **kwargs)


def should_skip_dir(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    return any(ex.lower() in parts for ex in EXCLUDE_DIRS)


def should_skip_file(path: Path) -> bool:
    if path.suffix.lower() not in INCLUDE_EXTENSIONS:
        return True
    name_lower = path.name.lower()
    return any(name_lower.endswith(sfx.lower()) for sfx in EXCLUDE_FILE_SUFFIXES)


def truncate_label(value: str, max_len: int = MAX_LABEL_LENGTH) -> str:
    value = value.replace("\\", "/")
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def slugify_folder(rel_folder: str) -> str:
    if rel_folder in (".", ""):
        return "root"
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", rel_folder.replace("\\", "_").replace("/", "_"))
    cleaned = cleaned.strip("._")
    return cleaned or "unnamed"


def hash_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def stable_folder_id(rel_folder: str) -> str:
    slug = slugify_folder(rel_folder)
    short_hash = hash_text(rel_folder)[:10]
    return f"{slug}__{short_hash}"


def read_text(path: Path) -> str:
    encodings = ("utf-8", "utf-8-sig", "latin-1")
    for enc in encodings:
        try:
            return path.read_text(encoding=enc, errors="strict")
        except Exception:
            pass
    return path.read_text(encoding="utf-8", errors="ignore")


def collect_imports(content: str) -> list[str]:
    imports: list[str] = []
    imports.extend(RE_IMPORT_FROM.findall(content))
    imports.extend(RE_IMPORT_BARE.findall(content))
    imports.extend(RE_REQUIRE.findall(content))
    imports.extend(RE_DYNAMIC_IMPORT.findall(content))
    return imports


def is_external_import(spec: str) -> bool:
    if spec.startswith(".") or spec.startswith("/"):
        return False
    if spec.startswith("@/") or spec.startswith("~/"):
        return False
    return True


def normalize_specifier(spec: str) -> str:
    return spec.strip()


def is_within_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_PATH.resolve())
        return True
    except Exception:
        return False


def try_resolve_repo_path(spec: str, current_file: Path) -> Path | None:
    spec = normalize_specifier(spec)

    if spec.startswith("."):
        base = (current_file.parent / spec).resolve()
        candidates = [
            base,
            *(base.with_suffix(ext) for ext in INCLUDE_EXTENSIONS),
            *(base / f"index{ext}" for ext in INCLUDE_EXTENSIONS),
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                return c
        return None

    alias_roots = []
    if spec.startswith("@/"):
        alias_roots = [REPO_PATH / "apps", REPO_PATH / "src", REPO_PATH]
        spec_tail = spec[2:]
    elif spec.startswith("~/"):
        alias_roots = [REPO_PATH / "src", REPO_PATH]
        spec_tail = spec[2:]
    elif spec.startswith("/"):
        alias_roots = [REPO_PATH]
        spec_tail = spec[1:]
    else:
        return None

    for root in alias_roots:
        base = (root / spec_tail).resolve()
        candidates = [
            base,
            *(base.with_suffix(ext) for ext in INCLUDE_EXTENSIONS),
            *(base / f"index{ext}" for ext in INCLUDE_EXTENSIONS),
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                return c
    return None


def node_id(label: str) -> str:
    return "n_" + hash_text(label)


def add_node(graph: Digraph, label: str, kind: str):
    nid = node_id(label)
    if kind == "file":
        graph.node(nid, label=truncate_label(label), shape="box", style="rounded")
    elif kind == "external":
        graph.node(nid, label=truncate_label(label), shape="ellipse", style="dashed")
    else:
        graph.node(nid, label=truncate_label(label))
    return nid


def file_fingerprint(path: Path) -> str:
    try:
        stat = path.stat()
        seed = f"{path}:{stat.st_size}:{stat.st_mtime_ns}"
    except Exception:
        seed = str(path)
    return hash_text(seed)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"version": STATE_VERSION, "folders": {}}
    try:
        raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "folders" in raw:
            raw.setdefault("version", STATE_VERSION)
            return raw
        if isinstance(raw, dict):
            return {"version": 1, "folders": {k: {"digest": v} for k, v in raw.items()}}
    except Exception:
        pass
    return {"version": STATE_VERSION, "folders": {}}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def load_manifest() -> dict:
    if not MANIFEST_FILE.exists():
        return {"version": STATE_VERSION, "folders": {}}
    try:
        raw = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "folders" in raw:
            raw.setdefault("version", STATE_VERSION)
            return raw
    except Exception:
        pass
    return {"version": STATE_VERSION, "folders": {}}


def save_manifest(manifest: dict):
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def open_path(path: Path):
    if not is_windows():
        return
    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
    except Exception:
        pass

# ---------------------------
# SCAN
# ---------------------------
def iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for root, dirs, filenames in os.walk(REPO_PATH):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        if should_skip_dir(root_path):
            continue

        for fname in filenames:
            path = root_path / fname
            if should_skip_file(path):
                continue
            files.append(path)
    return files


def build_folder_graph_data(files: list[Path]) -> dict[str, dict]:
    data: dict[str, dict] = {}

    for file_path in files:
        rel_file = file_path.relative_to(REPO_PATH).as_posix()
        rel_folder = file_path.parent.relative_to(REPO_PATH).as_posix() if file_path.parent != REPO_PATH else "."

        if rel_folder not in data:
            data[rel_folder] = {
                "files": set(),
                "edges": set(),
                "externals": set(),
                "fingerprints": {},
            }

        bucket = data[rel_folder]
        bucket["files"].add(rel_file)
        bucket["fingerprints"][rel_file] = file_fingerprint(file_path)

        try:
            content = read_text(file_path)
        except Exception:
            continue

        imports = collect_imports(content)

        for raw_spec in imports:
            spec = normalize_specifier(raw_spec)

            if INTERNAL_ONLY and is_external_import(spec):
                continue

            resolved = try_resolve_repo_path(spec, file_path)

            if resolved and resolved.exists() and is_within_repo(resolved):
                try:
                    target_rel = resolved.resolve().relative_to(REPO_PATH.resolve()).as_posix()
                    bucket["edges"].add((rel_file, target_rel))
                except Exception:
                    pass
            elif not INTERNAL_ONLY:
                bucket["externals"].add(spec)
                bucket["edges"].add((rel_file, f"pkg::{spec}"))

    return data

# ---------------------------
# RENDER
# ---------------------------
def compute_folder_digest(payload: dict) -> str:
    files = sorted(payload["files"])
    edges = sorted(payload["edges"])
    externals = sorted(payload["externals"])
    fingerprints = payload["fingerprints"]
    digest_seed = json.dumps(
        {
            "files": files,
            "edges": edges[:MAX_EDGES_PER_FOLDER],
            "externals": externals,
            "fingerprints": fingerprints,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hash_text(digest_seed)


def render_folder_graph(display_index: int, rel_folder: str, folder_id: str, payload: dict) -> Path:
    files = sorted(payload["files"])
    edges = sorted(payload["edges"])
    externals = sorted(payload["externals"])

    out_dir = OUTPUT_ROOT / folder_id
    out_dir.mkdir(parents=True, exist_ok=True)

    graph = Digraph(name=f"folder_{folder_id}")
    graph.attr(rankdir="LR", splines="true", overlap="false")
    graph.attr("node", fontname="Arial", fontsize="10")
    graph.attr("edge", fontname="Arial", fontsize="9")
    graph.attr(label=rel_folder, labelloc="t", fontsize="18")

    for rel_file in files:
        add_node(graph, rel_file, "file")

    if not INTERNAL_ONLY:
        for ext in externals:
            add_node(graph, f"pkg::{ext}", "external")

    limited_edges = edges[:MAX_EDGES_PER_FOLDER]
    for a, b in limited_edges:
        graph.edge(node_id(a), node_id(b))

    dot_path = out_dir / "graph.dot"
    svg_base = out_dir / "graph"

    graph.save(str(dot_path))
    graph.render(str(svg_base), format="svg", cleanup=True)

    summary = {
        "folder_id": folder_id,
        "folder": rel_folder,
        "display_index": display_index,
        "file_count": len(files),
        "edge_count_total": len(edges),
        "edge_count_rendered": len(limited_edges),
        "external_count": len(externals),
        "internal_only": INTERNAL_ONLY,
        "rendered_at": now_iso(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "README.txt").write_text(
        "\n".join(
            [
                f"Folder: {rel_folder}",
                f"Folder ID: {folder_id}",
                f"Display index (current run): {display_index:03d}",
                f"Files: {len(files)}",
                f"Edges total: {len(edges)}",
                f"Edges rendered: {len(limited_edges)}",
                f"External imports tracked: {len(externals)}",
                f"Internal only mode: {INTERNAL_ONLY}",
                f"Rendered at: {now_iso()}",
                "",
                "Files in this folder graph:",
                *files[:500],
            ]
        ),
        encoding="utf-8",
    )

    return out_dir / "graph.svg"


def write_master_index(current_rows: list[dict], manifest: dict):
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    lines = [
        "<html><head><meta charset='utf-8'><title>HITECH Graphviz Index</title></head><body>",
        "<h1>HITECH Graphviz Index</h1>",
        "<p>Current scan plus preserved historical outputs. Existing graph folders are never deleted by this script.</p>",
        "<h2>Current folders</h2>",
        "<ol>",
    ]

    for row in current_rows:
        lines.append(
            f"<li><b>{row['display_index']:03d}</b> | {row['folder']} | "
            f"<a href='./{row['dir_name']}/graph.svg'>graph.svg</a> | "
            f"<a href='./{row['dir_name']}/graph.dot'>graph.dot</a> | "
            f"<a href='./{row['dir_name']}/summary.json'>summary.json</a></li>"
        )

    lines.extend(["</ol>"])

    legacy_rows = []
    current_set = {row["folder"] for row in current_rows}
    for rel_folder, entry in sorted(manifest.get("folders", {}).items()):
        if rel_folder in current_set:
            continue
        dir_name = entry.get("dir_name")
        if not dir_name:
            continue
        legacy_rows.append(
            {
                "folder": rel_folder,
                "dir_name": dir_name,
                "last_seen_at": entry.get("last_seen_at", "?"),
            }
        )

    if legacy_rows:
        lines.extend(["<h2>Historical folders kept on disk</h2>", "<ul>"])
        for row in legacy_rows:
            lines.append(
                f"<li>{row['folder']} | last seen: {row['last_seen_at']} | "
                f"<a href='./{row['dir_name']}/graph.svg'>graph.svg</a> | "
                f"<a href='./{row['dir_name']}/graph.dot'>graph.dot</a> | "
                f"<a href='./{row['dir_name']}/summary.json'>summary.json</a></li>"
            )
        lines.append("</ul>")

    lines.extend(["</body></html>"])
    (OUTPUT_ROOT / "index.html").write_text("\n".join(lines), encoding="utf-8")

# ---------------------------
# MAIN
# ---------------------------
def run_once() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    previous_state = load_state()
    manifest = load_manifest()

    next_state = {"version": STATE_VERSION, "folders": {}}
    manifest.setdefault("version", STATE_VERSION)
    manifest.setdefault("folders", {})

    safe_print("\n====================================")
    safe_print(" HITECH Graphviz Folder Generator")
    safe_print("====================================")
    safe_print(f"Repo:   {REPO_PATH}")
    safe_print(f"Output: {OUTPUT_ROOT}")
    safe_print(f"Mode:   {'WATCH' if WATCH_MODE else 'ONE-SHOT'}")
    safe_print(f"Scope:  {'INTERNAL ONLY' if INTERNAL_ONLY else 'INTERNAL + EXTERNAL'}")
    safe_print("Policy: update only new/changed folders; keep previous outputs")
    safe_print("")

    files = iter_repo_files()
    safe_print(f"[1/4] Files found: {len(files)}")

    graph_data = build_folder_graph_data(files)
    safe_print(f"[2/4] Folder buckets: {len(graph_data)}")

    changed_count = 0
    first_svg: Path | None = None
    current_rows: list[dict] = []
    seen_folders: set[str] = set()

    previous_folder_state = previous_state.get("folders", {})

    for display_index, rel_folder in enumerate(sorted(graph_data.keys()), start=1):
        payload = graph_data[rel_folder]
        folder_id = stable_folder_id(rel_folder)
        dir_name = folder_id
        digest = compute_folder_digest(payload)
        prev_entry = previous_folder_state.get(rel_folder, {})
        prev_digest = prev_entry.get("digest")
        changed = prev_digest != digest

        current_rows.append(
            {
                "display_index": display_index,
                "folder": rel_folder,
                "dir_name": dir_name,
                "folder_id": folder_id,
            }
        )
        seen_folders.add(rel_folder)

        next_state["folders"][rel_folder] = {
            "digest": digest,
            "folder_id": folder_id,
            "dir_name": dir_name,
            "last_index": display_index,
            "last_seen_at": now_iso(),
        }

        manifest["folders"][rel_folder] = {
            **manifest["folders"].get(rel_folder, {}),
            "folder_id": folder_id,
            "dir_name": dir_name,
            "last_index": display_index,
            "last_seen_at": now_iso(),
            "active": True,
        }

        if changed:
            svg_path = render_folder_graph(display_index, rel_folder, folder_id, payload)
            changed_count += 1
            if first_svg is None:
                first_svg = svg_path
            safe_print(f"[3/4] Rendered {display_index:03d} | {rel_folder}")
        else:
            safe_print(f"[3/4] Skipped   {display_index:03d} | {rel_folder} (no changes)")

    for rel_folder, entry in manifest.get("folders", {}).items():
        if rel_folder not in seen_folders:
            entry["active"] = False

    write_master_index(current_rows, manifest)
    save_state(next_state)
    save_manifest(manifest)

    safe_print(f"[4/4] Done. Updated graphs: {changed_count}")
    safe_print(f"Index: {OUTPUT_ROOT / 'index.html'}")
    safe_print("")

    if OPEN_INDEX_ON_FINISH:
        open_path(OUTPUT_ROOT / "index.html")
    if OPEN_FIRST_SVG and first_svg is not None:
        open_path(first_svg)

    return changed_count


def main():
    if not REPO_PATH.exists():
        safe_print(f"ERROR: Repo path does not exist: {REPO_PATH}")
        input("\nPress ENTER to close...")
        sys.exit(1)

    if WATCH_MODE:
        safe_print("Watch mode active. Press Ctrl+C to stop.\n")
        try:
            while True:
                run_once()
                safe_print(f"Sleeping {SLEEP_SECONDS}s...\n")
                time.sleep(SLEEP_SECONDS)
        except KeyboardInterrupt:
            safe_print("\nStopped by user.")
    else:
        run_once()
        input("Press ENTER to close...")


if __name__ == "__main__":
    main()
