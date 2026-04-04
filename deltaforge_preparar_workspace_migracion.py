#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
DeltaForge · Preparador seguro de workspace de migración

Qué hace:
- Busca los insumos en la carpeta de iteraciones.
- Congela copia de los insumos dentro de apps\delta-forge.
- Extrae deltaforge.zip y shared*.zip a un workspace limpio.
- Instala los 4 .md de blindaje desde zip o archivos sueltos.
- Copia los 2 .md de referencia.
- Genera manifest, inventario y log.
- Crea un zip de handoff ligero con manifests y docs para el siguiente análisis.

Rutas default:
- Input dir : F:\repos\hitech-os\apps\Nexus\Iteraciones CHAT GPT
- Output dir: F:\repos\hitech-os\apps\delta-forge

Uso:
    py F:\OneDrive\Descargas\deltaforge_preparar_workspace_migracion.py

Opcional:
    py F:\OneDrive\Descargas\deltaforge_preparar_workspace_migracion.py \
        --input-dir "F:\repos\hitech-os\apps\Nexus\Iteraciones CHAT GPT" \
        --output-root "F:\repos\hitech-os\apps\delta-forge"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import textwrap
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SCRIPT_NAME = "deltaforge_preparar_workspace_migracion.py"
DEFAULT_INPUT_DIR = Path(r"F:\repos\hitech-os\apps\Nexus\Iteraciones CHAT GPT")
DEFAULT_OUTPUT_ROOT = Path(r"F:\repos\hitech-os\apps\delta-forge")
WORKSPACE_DIR_NAME = "_migration_workspace"
LOGS_DIR_NAME = "_logs"
INCOMING_DIR_NAME = "incoming_snapshot"
EXTRACTED_DIR_NAME = "extracted"
DOCS_DIR_NAME = "docs"
HANDOFF_DIR_NAME = "handoff"
REFERENCE_DOCS_DIR_NAME = "reference"
BLINDAJE_DOCS_DIR_NAME = "migration_blindaje_md"

PRIMARY_DELTAFORGE_ZIP = "deltaforge.zip"
REFERENCE_DOC_NAMES = [
    "deltaforge_motor_parity_map.md",
    "deltaforge_glass_shell_swap_blueprint.md",
]
BLINDAJE_ZIP_NAME = "deltaforge_migracion_blindaje_md.zip"
EXPECTED_BLINDAJE_MD = [
    "01_deltaforge_ui_signal_wiring_matrix_1a1.md",
    "02_deltaforge_projection_payload_mapping_1a1.md",
    "03_deltaforge_refresh_lifecycle_matrix_1a1.md",
    "04_deltaforge_import_packaging_dependency_map_1a1.md",
]
SHARED_ZIP_CANDIDATES = [
    "shared (4).zip",
    "shared (3).zip",
    "shared.zip",
]
MAX_TREE_ENTRIES = 2500


class UserFacingError(Exception):
    pass


@dataclass
class SourceFiles:
    input_dir: Path
    deltaforge_zip: Path
    shared_zip: Path
    reference_docs: List[Path]
    blindaje_zip: Optional[Path]
    blindaje_md_files: List[Path]


@dataclass
class RunPaths:
    output_root: Path
    workspace_dir: Path
    logs_dir: Path
    incoming_dir: Path
    extracted_dir: Path
    docs_dir: Path
    handoff_dir: Path
    reference_docs_dir: Path
    blindaje_docs_dir: Path


@dataclass
class RunResult:
    workspace_dir: Path
    log_path: Path
    manifest_path: Path
    handoff_zip_path: Path
    readme_path: Path
    input_dir: Path
    output_root: Path
    deltaforge_extract_dir: Path
    shared_extract_dir: Path
    reference_docs_dir: Path
    blindaje_docs_dir: Path


def now_local() -> datetime:
    return datetime.now()


def stamp() -> str:
    return now_local().strftime("%Y%m%d_%H%M%S")


def info(step: int, total: int, message: str) -> None:
    print(f"[{step}/{total}] {message}")


# ---------- utilidades de archivos ----------

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def file_info(path: Path) -> Dict[str, object]:
    stat = path.stat()
    return {
        "name": path.name,
        "path": str(path),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "sha256": sha256_file(path),
    }


def copy_file(src: Path, dst: Path) -> Path:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return dst


def find_existing_path(candidates: Sequence[Path]) -> Optional[Path]:
    for path in candidates:
        if path.exists():
            return path
    return None


def candidate_input_dirs(script_path: Path, cli_input: Optional[Path]) -> List[Path]:
    candidates: List[Path] = []
    if cli_input:
        candidates.append(cli_input)
    candidates.append(DEFAULT_INPUT_DIR)

    roots: List[Path] = []
    if script_path.drive:
        roots.append(Path(f"{script_path.drive}\\"))
    cwd_drive = Path.cwd().drive
    if cwd_drive:
        roots.append(Path(f"{cwd_drive}\\"))

    seen = {str(p).lower() for p in candidates}
    for root in roots:
        alt = root / "repos" / "hitech-os" / "apps" / "Nexus" / "Iteraciones CHAT GPT"
        if str(alt).lower() not in seen:
            candidates.append(alt)
            seen.add(str(alt).lower())
    return candidates


def candidate_output_roots(script_path: Path, cli_output: Optional[Path]) -> List[Path]:
    candidates: List[Path] = []
    if cli_output:
        candidates.append(cli_output)
    candidates.append(DEFAULT_OUTPUT_ROOT)

    roots: List[Path] = []
    if script_path.drive:
        roots.append(Path(f"{script_path.drive}\\"))
    cwd_drive = Path.cwd().drive
    if cwd_drive:
        roots.append(Path(f"{cwd_drive}\\"))

    seen = {str(p).lower() for p in candidates}
    for root in roots:
        alt = root / "repos" / "hitech-os" / "apps" / "delta-forge"
        if str(alt).lower() not in seen:
            candidates.append(alt)
            seen.add(str(alt).lower())
    return candidates


def resolve_main_paths(script_path: Path, cli_input: Optional[Path], cli_output: Optional[Path]) -> Tuple[Path, Path]:
    input_dir = find_existing_path(candidate_input_dirs(script_path, cli_input))
    if not input_dir:
        attempted = "\n  - ".join(str(p) for p in candidate_input_dirs(script_path, cli_input))
        raise UserFacingError(
            "No encontré la carpeta de insumos. Busqué en:\n"
            f"  - {attempted}\n\n"
            "Si la moviste, usa --input-dir."
        )

    output_root = find_existing_path(candidate_output_roots(script_path, cli_output))
    if not output_root:
        output_root = candidate_output_roots(script_path, cli_output)[0]
        ensure_dir(output_root)

    return input_dir, output_root


def find_shared_zip(input_dir: Path) -> Optional[Path]:
    for name in SHARED_ZIP_CANDIDATES:
        candidate = input_dir / name
        if candidate.exists():
            return candidate
    return None


def resolve_source_files(input_dir: Path) -> SourceFiles:
    deltaforge_zip = input_dir / PRIMARY_DELTAFORGE_ZIP
    if not deltaforge_zip.exists():
        raise UserFacingError(
            f"Falta el archivo requerido: {deltaforge_zip.name}\nRuta esperada: {deltaforge_zip}"
        )

    shared_zip = find_shared_zip(input_dir)
    if not shared_zip:
        joined = ", ".join(SHARED_ZIP_CANDIDATES)
        raise UserFacingError(
            "No encontré el zip de Shared. Probé estas variantes:\n"
            f"  - {joined}\n"
            f"Dentro de: {input_dir}"
        )

    reference_docs: List[Path] = []
    missing_reference_docs: List[str] = []
    for name in REFERENCE_DOC_NAMES:
        p = input_dir / name
        if p.exists():
            reference_docs.append(p)
        else:
            missing_reference_docs.append(name)
    if missing_reference_docs:
        raise UserFacingError(
            "Faltan docs de referencia obligatorios:\n"
            + "\n".join(f"  - {name}" for name in missing_reference_docs)
        )

    blindaje_zip = input_dir / BLINDAJE_ZIP_NAME
    blindaje_md_files: List[Path] = []
    if blindaje_zip.exists():
        return SourceFiles(
            input_dir=input_dir,
            deltaforge_zip=deltaforge_zip,
            shared_zip=shared_zip,
            reference_docs=reference_docs,
            blindaje_zip=blindaje_zip,
            blindaje_md_files=[],
        )

    loose_md = [input_dir / name for name in EXPECTED_BLINDAJE_MD]
    missing_loose = [p.name for p in loose_md if not p.exists()]
    if missing_loose:
        raise UserFacingError(
            "No encontré el blindaje en zip ni completo en .md sueltos.\n"
            f"Zip esperado: {blindaje_zip}\n"
            "Faltan estos .md:\n"
            + "\n".join(f"  - {name}" for name in missing_loose)
        )

    blindaje_md_files = loose_md
    return SourceFiles(
        input_dir=input_dir,
        deltaforge_zip=deltaforge_zip,
        shared_zip=shared_zip,
        reference_docs=reference_docs,
        blindaje_zip=None,
        blindaje_md_files=blindaje_md_files,
    )


def build_run_paths(output_root: Path) -> RunPaths:
    workspace_dir = output_root / WORKSPACE_DIR_NAME
    logs_dir = workspace_dir / LOGS_DIR_NAME
    incoming_dir = workspace_dir / INCOMING_DIR_NAME
    extracted_dir = workspace_dir / EXTRACTED_DIR_NAME
    docs_dir = workspace_dir / DOCS_DIR_NAME
    handoff_dir = workspace_dir / HANDOFF_DIR_NAME
    reference_docs_dir = docs_dir / REFERENCE_DOCS_DIR_NAME
    blindaje_docs_dir = docs_dir / BLINDAJE_DOCS_DIR_NAME
    return RunPaths(
        output_root=output_root,
        workspace_dir=workspace_dir,
        logs_dir=logs_dir,
        incoming_dir=incoming_dir,
        extracted_dir=extracted_dir,
        docs_dir=docs_dir,
        handoff_dir=handoff_dir,
        reference_docs_dir=reference_docs_dir,
        blindaje_docs_dir=blindaje_docs_dir,
    )


def safe_extract_all(zip_path: Path, dest_dir: Path) -> int:
    ensure_dir(dest_dir)
    extracted_files = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info_item in zf.infolist():
            member_name = info_item.filename
            member_path = Path(member_name)
            if member_path.is_absolute():
                raise UserFacingError(f"Zip con ruta absoluta no permitida: {member_name}")
            normalized = Path(*member_path.parts)
            if any(part == ".." for part in normalized.parts):
                raise UserFacingError(f"Zip con path traversal no permitido: {member_name}")
            target_path = dest_dir / normalized
            if info_item.is_dir():
                ensure_dir(target_path)
                continue
            ensure_dir(target_path.parent)
            with zf.open(info_item) as src, target_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted_files += 1
    return extracted_files


def extract_blindaje_docs_from_zip(zip_path: Path, dest_dir: Path) -> List[Path]:
    ensure_dir(dest_dir)
    written: List[Path] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.namelist()
        for expected_name in EXPECTED_BLINDAJE_MD:
            matches = [m for m in members if Path(m).name == expected_name]
            if not matches:
                raise UserFacingError(
                    f"El blindaje zip no trae el archivo esperado: {expected_name}"
                )
            member = matches[0]
            out_path = dest_dir / expected_name
            with zf.open(member) as src, out_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            written.append(out_path)
    return written


def install_blindaje_docs(source: SourceFiles, blindaje_docs_dir: Path) -> List[Path]:
    ensure_dir(blindaje_docs_dir)
    if source.blindaje_zip:
        installed = extract_blindaje_docs_from_zip(source.blindaje_zip, blindaje_docs_dir)
    else:
        installed = []
        for src in source.blindaje_md_files:
            installed.append(copy_file(src, blindaje_docs_dir / src.name))

    installed_names = sorted(p.name for p in installed)
    expected_names = sorted(EXPECTED_BLINDAJE_MD)
    if installed_names != expected_names:
        raise UserFacingError(
            "Los .md de blindaje quedaron incompletos.\n"
            f"Esperado: {expected_names}\n"
            f"Encontrado: {installed_names}"
        )
    return installed


def write_text(path: Path, content: str) -> Path:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return path


def format_tree(root: Path, max_entries: int = MAX_TREE_ENTRIES) -> str:
    lines: List[str] = [f"{root.name}/"]
    count = 0
    root = root.resolve()

    for current_root, dirnames, filenames in os.walk(root):
        dirnames.sort(key=str.lower)
        filenames.sort(key=str.lower)
        rel = Path(current_root).resolve().relative_to(root)
        depth = 0 if str(rel) == "." else len(rel.parts)
        indent = "    " * depth

        if str(rel) != ".":
            lines.append(f"{indent}{Path(current_root).name}/")
            count += 1
            if count >= max_entries:
                lines.append("    ... [tree truncado] ...")
                break

        child_indent = "    " * (depth + 1)
        for name in filenames:
            lines.append(f"{child_indent}{name}")
            count += 1
            if count >= max_entries:
                lines.append("    ... [tree truncado] ...")
                return "\n".join(lines)
    return "\n".join(lines)


def collect_markdown_files(base_dir: Path) -> List[Path]:
    return sorted(base_dir.rglob("*.md"), key=lambda p: str(p).lower())


def create_handoff_zip(workspace_dir: Path, handoff_dir: Path) -> Path:
    ensure_dir(handoff_dir)
    handoff_zip_path = handoff_dir / f"deltaforge_next_analysis_inputs_{stamp()}.zip"
    include_paths: List[Path] = []

    candidates = [
        workspace_dir / DOCS_DIR_NAME,
        workspace_dir / LOGS_DIR_NAME,
        workspace_dir / "README_PRIMERO.txt",
        workspace_dir / "workspace_manifest.json",
        workspace_dir / "extracted_tree.txt",
    ]

    for path in candidates:
        if path.exists():
            include_paths.append(path)

    with zipfile.ZipFile(handoff_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in include_paths:
            if path.is_file():
                zf.write(path, arcname=path.relative_to(workspace_dir))
            else:
                for file_path in sorted(path.rglob("*"), key=lambda p: str(p).lower()):
                    if file_path.is_file():
                        zf.write(file_path, arcname=file_path.relative_to(workspace_dir))
    return handoff_zip_path


def write_readme(workspace_dir: Path, source: SourceFiles, run_paths: RunPaths, deltaforge_extract_dir: Path, shared_extract_dir: Path) -> Path:
    body = textwrap.dedent(
        f"""
        DeltaForge · Workspace listo para migración
        ==========================================

        Este workspace fue generado por: {SCRIPT_NAME}
        Fecha: {now_local().isoformat(timespec='seconds')}

        Qué quedó aquí:
        - Insumos congelados: {run_paths.incoming_dir}
        - DeltaForge extraído: {deltaforge_extract_dir}
        - Shared extraído: {shared_extract_dir}
        - Docs de referencia: {run_paths.reference_docs_dir}
        - Blindaje MD: {run_paths.blindaje_docs_dir}
        - Logs: {run_paths.logs_dir}
        - Handoff zip: {run_paths.handoff_dir}

        Inputs detectados:
        - DeltaForge zip: {source.deltaforge_zip.name}
        - Shared zip: {source.shared_zip.name}
        - Docs referencia: {', '.join(p.name for p in source.reference_docs)}
        - Blindaje: {source.blindaje_zip.name if source.blindaje_zip else '4 .md sueltos'}

        Nota de seguridad:
        - El script NO pisa el repo base fuera de esta carpeta de trabajo administrada.
        - Todo lo que genera vive dentro de: {workspace_dir}
        - En cada corrida reemplaza completa esta carpeta para evitar parches chuecos.
        """
    ).strip() + "\n"
    return write_text(workspace_dir / "README_PRIMERO.txt", body)


def write_manifest(
    workspace_dir: Path,
    source: SourceFiles,
    run_paths: RunPaths,
    deltaforge_extract_dir: Path,
    shared_extract_dir: Path,
    installed_blindaje_files: Sequence[Path],
    copied_reference_docs: Sequence[Path],
    handoff_zip_path: Optional[Path] = None,
) -> Path:
    manifest = {
        "generated_at": now_local().isoformat(timespec="seconds"),
        "script": SCRIPT_NAME,
        "input_dir": str(source.input_dir),
        "output_root": str(run_paths.output_root),
        "workspace_dir": str(workspace_dir),
        "managed_workspace_policy": "replace_full_workspace_every_run",
        "source_files": {
            "deltaforge_zip": file_info(source.deltaforge_zip),
            "shared_zip": file_info(source.shared_zip),
            "reference_docs": [file_info(p) for p in source.reference_docs],
            "blindaje_zip": file_info(source.blindaje_zip) if source.blindaje_zip else None,
            "blindaje_md_files": [file_info(p) for p in source.blindaje_md_files],
        },
        "output_paths": {
            "incoming_dir": str(run_paths.incoming_dir),
            "deltaforge_extract_dir": str(deltaforge_extract_dir),
            "shared_extract_dir": str(shared_extract_dir),
            "reference_docs_dir": str(run_paths.reference_docs_dir),
            "blindaje_docs_dir": str(run_paths.blindaje_docs_dir),
            "logs_dir": str(run_paths.logs_dir),
            "handoff_dir": str(run_paths.handoff_dir),
            "handoff_zip_path": str(handoff_zip_path) if handoff_zip_path else None,
        },
        "installed_docs": {
            "reference_docs": [str(p) for p in copied_reference_docs],
            "blindaje_docs": [str(p) for p in installed_blindaje_files],
        },
        "notes": [
            "El workspace se genera dentro de _migration_workspace para no pisar el repo principal.",
            "Shared y DeltaForge se extraen completos para inspección local.",
            "El handoff zip contiene docs y manifests, no el árbol completo extraído.",
        ],
    }
    return write_text(
        workspace_dir / "workspace_manifest.json",
        json.dumps(manifest, indent=2, ensure_ascii=False),
    )


def write_log(run_paths: RunPaths, lines: Sequence[str]) -> Path:
    ensure_dir(run_paths.logs_dir)
    log_path = run_paths.logs_dir / f"run_{stamp()}.log"
    write_text(log_path, "\n".join(lines) + "\n")
    return log_path


def prepare_workspace(source: SourceFiles, output_root: Path) -> RunResult:
    run_paths = build_run_paths(output_root)
    parent_dir = run_paths.workspace_dir.parent
    ensure_dir(parent_dir)

    temp_root = Path(tempfile.mkdtemp(prefix="deltaforge_workspace_", dir=str(parent_dir)))
    staged_workspace = temp_root / WORKSPACE_DIR_NAME
    ensure_dir(staged_workspace)

    staged_paths = build_run_paths(temp_root)
    ensure_dir(staged_paths.incoming_dir)
    ensure_dir(staged_paths.extracted_dir)
    ensure_dir(staged_paths.reference_docs_dir)
    ensure_dir(staged_paths.blindaje_docs_dir)
    ensure_dir(staged_paths.logs_dir)
    ensure_dir(staged_paths.handoff_dir)

    log_lines: List[str] = []
    log_lines.append(f"Fecha: {now_local().isoformat(timespec='seconds')}")
    log_lines.append(f"Script: {SCRIPT_NAME}")
    log_lines.append(f"Input dir: {source.input_dir}")
    log_lines.append(f"Output root: {output_root}")

    try:
        # Congelar snapshot de insumos.
        copied_inputs: List[Path] = []
        copied_inputs.append(copy_file(source.deltaforge_zip, staged_paths.incoming_dir / source.deltaforge_zip.name))
        copied_inputs.append(copy_file(source.shared_zip, staged_paths.incoming_dir / source.shared_zip.name))
        for ref in source.reference_docs:
            copied_inputs.append(copy_file(ref, staged_paths.incoming_dir / ref.name))
        if source.blindaje_zip:
            copied_inputs.append(copy_file(source.blindaje_zip, staged_paths.incoming_dir / source.blindaje_zip.name))
        else:
            for md_file in source.blindaje_md_files:
                copied_inputs.append(copy_file(md_file, staged_paths.incoming_dir / md_file.name))

        # Extraer zips.
        deltaforge_extract_dir = staged_paths.extracted_dir / "deltaforge_zip_extracted"
        shared_extract_dir = staged_paths.extracted_dir / "shared_zip_extracted"
        deltaforge_count = safe_extract_all(source.deltaforge_zip, deltaforge_extract_dir)
        shared_count = safe_extract_all(source.shared_zip, shared_extract_dir)

        # Copiar docs de referencia e instalar blindaje.
        copied_reference_docs: List[Path] = []
        for ref in source.reference_docs:
            copied_reference_docs.append(copy_file(ref, staged_paths.reference_docs_dir / ref.name))
        installed_blindaje_files = install_blindaje_docs(source, staged_paths.blindaje_docs_dir)

        # Inventario del árbol.
        tree_text = textwrap.dedent(
            f"""
            DeltaForge · Árbol resumido del workspace
            =======================================

            Workspace root: {staged_workspace}
            Generado: {now_local().isoformat(timespec='seconds')}

            {format_tree(staged_workspace)}
            """
        ).strip() + "\n"
        write_text(staged_workspace / "extracted_tree.txt", tree_text)

        # README y manifest preliminar.
        readme_path = write_readme(staged_workspace, source, staged_paths, deltaforge_extract_dir, shared_extract_dir)
        manifest_path = write_manifest(
            staged_workspace,
            source,
            staged_paths,
            deltaforge_extract_dir,
            shared_extract_dir,
            installed_blindaje_files,
            copied_reference_docs,
            handoff_zip_path=None,
        )

        # Handoff zip y manifest final.
        handoff_zip_path = create_handoff_zip(staged_workspace, staged_paths.handoff_dir)
        manifest_path = write_manifest(
            staged_workspace,
            source,
            staged_paths,
            deltaforge_extract_dir,
            shared_extract_dir,
            installed_blindaje_files,
            copied_reference_docs,
            handoff_zip_path=handoff_zip_path,
        )

        # Log.
        log_lines.extend(
            [
                f"Workspace staged: {staged_workspace}",
                f"DeltaForge zip extraído en: {deltaforge_extract_dir} (archivos: {deltaforge_count})",
                f"Shared zip extraído en: {shared_extract_dir} (archivos: {shared_count})",
                f"Docs referencia: {len(copied_reference_docs)}",
                f"Docs blindaje: {len(installed_blindaje_files)}",
                f"Handoff zip: {handoff_zip_path}",
                f"Manifest: {manifest_path}",
                f"README: {readme_path}",
            ]
        )
        log_path = write_log(staged_paths, log_lines)

        # Promover staged al destino real.
        if run_paths.workspace_dir.exists():
            shutil.rmtree(run_paths.workspace_dir)
        shutil.move(str(staged_workspace), str(run_paths.workspace_dir))
        shutil.rmtree(temp_root, ignore_errors=True)

        final_log_path = run_paths.workspace_dir / LOGS_DIR_NAME / log_path.name
        final_manifest_path = run_paths.workspace_dir / manifest_path.name
        final_readme_path = run_paths.workspace_dir / readme_path.name
        final_handoff_zip_path = run_paths.workspace_dir / HANDOFF_DIR_NAME / handoff_zip_path.name
        final_deltaforge_extract_dir = run_paths.workspace_dir / EXTRACTED_DIR_NAME / deltaforge_extract_dir.name
        final_shared_extract_dir = run_paths.workspace_dir / EXTRACTED_DIR_NAME / shared_extract_dir.name

        return RunResult(
            workspace_dir=run_paths.workspace_dir,
            log_path=final_log_path,
            manifest_path=final_manifest_path,
            handoff_zip_path=final_handoff_zip_path,
            readme_path=final_readme_path,
            input_dir=source.input_dir,
            output_root=output_root,
            deltaforge_extract_dir=final_deltaforge_extract_dir,
            shared_extract_dir=final_shared_extract_dir,
            reference_docs_dir=run_paths.workspace_dir / DOCS_DIR_NAME / REFERENCE_DOCS_DIR_NAME,
            blindaje_docs_dir=run_paths.workspace_dir / DOCS_DIR_NAME / BLINDAJE_DOCS_DIR_NAME,
        )
    except Exception:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepara un workspace seguro de migración de DeltaForge dentro de apps\\delta-forge."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help=f"Ruta de insumos. Default: {DEFAULT_INPUT_DIR}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=f"Raíz de salida. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    script_path = Path(__file__).resolve()

    total_steps = 7
    try:
        info(1, total_steps, "Resolviendo rutas...")
        input_dir, output_root = resolve_main_paths(script_path, args.input_dir, args.output_root)
        print(f"    Input dir  : {input_dir}")
        print(f"    Output root: {output_root}")

        info(2, total_steps, "Validando insumos...")
        source = resolve_source_files(input_dir)
        print(f"    DeltaForge : {source.deltaforge_zip.name}")
        print(f"    Shared     : {source.shared_zip.name}")
        print(f"    Blindaje   : {source.blindaje_zip.name if source.blindaje_zip else '4 .md sueltos'}")

        info(3, total_steps, "Preparando workspace limpio administrado...")
        print(f"    Carpeta administrada: {output_root / WORKSPACE_DIR_NAME}")

        info(4, total_steps, "Congelando snapshot de insumos y extrayendo zips...")
        result = prepare_workspace(source, output_root)

        info(5, total_steps, "Validando salida final...")
        if not result.deltaforge_extract_dir.exists():
            raise UserFacingError(f"No quedó la extracción de DeltaForge: {result.deltaforge_extract_dir}")
        if not result.shared_extract_dir.exists():
            raise UserFacingError(f"No quedó la extracción de Shared: {result.shared_extract_dir}")
        if not result.reference_docs_dir.exists():
            raise UserFacingError(f"No quedó la carpeta de docs referencia: {result.reference_docs_dir}")
        if not result.blindaje_docs_dir.exists():
            raise UserFacingError(f"No quedó la carpeta de blindaje: {result.blindaje_docs_dir}")
        for name in EXPECTED_BLINDAJE_MD:
            if not (result.blindaje_docs_dir / name).exists():
                raise UserFacingError(f"Falta doc de blindaje instalado: {name}")

        info(6, total_steps, "Generando resumen final...")
        print("")
        print("Salida final:")
        print(f"  - Workspace:   {result.workspace_dir}")
        print(f"  - DeltaForge:  {result.deltaforge_extract_dir}")
        print(f"  - Shared:      {result.shared_extract_dir}")
        print(f"  - Referencia:  {result.reference_docs_dir}")
        print(f"  - Blindaje MD: {result.blindaje_docs_dir}")
        print(f"  - Manifest:    {result.manifest_path}")
        print(f"  - Log:         {result.log_path}")
        print(f"  - Handoff zip: {result.handoff_zip_path}")
        print(f"  - README:      {result.readme_path}")

        info(7, total_steps, "Listo. Ya quedó el workspace sin pisar el repo base.")
        print("")
        print("Ejecútalo así:")
        print(f"  py {Path(__file__).name}")
        return 0
    except UserFacingError as exc:
        print("\n[ERROR]", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[ERROR] Ejecución cancelada por el usuario.", file=sys.stderr)
        return 130
    except Exception as exc:
        print("\n[ERROR] Falló algo fuera de guion.", file=sys.stderr)
        print(f"Tipo: {type(exc).__name__}", file=sys.stderr)
        print(f"Detalle: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
