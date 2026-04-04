#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
DeltaForge · Instalador seguro de blindaje MD

Qué hace:
- Busca el bundle `deltaforge_migracion_blindaje_md.zip` o los 4 .md sueltos
  dentro de la carpeta de insumos.
- Valida rutas y archivos.
- Crea una salida limpia dentro de `apps\delta-forge`.
- Reemplaza la carpeta destino completa para evitar parches raros.
- Deja manifest y log de ejecución.

Uso recomendado en Windows:
    py F:\OneDrive\Descargas\deltaforge_instalar_blindaje_md.py

Opcional:
    py F:\OneDrive\Descargas\deltaforge_instalar_blindaje_md.py \
        --input-dir "F:\repos\hitech-os\apps\Nexus\Iteraciones CHAT GPT" \
        --output-root "F:\repos\hitech-os\apps\delta-forge"
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import textwrap
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

SCRIPT_NAME = "deltaforge_instalar_blindaje_md.py"
DEFAULT_INPUT_DIR = Path(r"F:\repos\hitech-os\apps\Nexus\Iteraciones CHAT GPT")
DEFAULT_OUTPUT_ROOT = Path(r"F:\repos\hitech-os\apps\delta-forge")
TARGET_FOLDER_NAME = "migration_blindaje_md"
EXPECTED_MD_FILES = [
    "01_deltaforge_ui_signal_wiring_matrix_1a1.md",
    "02_deltaforge_projection_payload_mapping_1a1.md",
    "03_deltaforge_refresh_lifecycle_matrix_1a1.md",
    "04_deltaforge_import_packaging_dependency_map_1a1.md",
]
PRIMARY_ZIP_NAME = "deltaforge_migracion_blindaje_md.zip"
OPTIONAL_REFERENCE_FILES = [
    "deltaforge_motor_parity_map.md",
    "deltaforge_glass_shell_swap_blueprint.md",
    "deltaforge.zip",
    "shared (4).zip",
]


class UserFacingError(Exception):
    pass


@dataclass
class SourceSelection:
    mode: str
    source_path: Path
    found_md_files: List[Path]
    optional_reference_files: List[Path]


@dataclass
class InstallResult:
    target_dir: Path
    log_path: Path
    manifest_path: Path
    source_mode: str
    source_path: Path
    installed_files: List[Path]
    optional_reference_files: List[Path]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def info(step: int, total: int, message: str) -> None:
    print(f"[{step}/{total}] {message}")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def find_existing_path(candidates: Sequence[Path]) -> Optional[Path]:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def candidate_input_dirs(script_path: Path, cli_input: Optional[Path]) -> List[Path]:
    candidates: List[Path] = []
    if cli_input:
        candidates.append(cli_input)
    candidates.append(DEFAULT_INPUT_DIR)

    # Fallbacks por si cambia la letra de unidad o se mueve el workspace.
    possible_roots = []
    if script_path.drive:
        possible_roots.append(Path(f"{script_path.drive}\\"))
    if Path.cwd().drive:
        possible_roots.append(Path(f"{Path.cwd().drive}\\"))

    seen = {str(p).lower() for p in candidates}
    for root in possible_roots:
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

    possible_roots = []
    if script_path.drive:
        possible_roots.append(Path(f"{script_path.drive}\\"))
    if Path.cwd().drive:
        possible_roots.append(Path(f"{Path.cwd().drive}\\"))

    seen = {str(p).lower() for p in candidates}
    for root in possible_roots:
        alt = root / "repos" / "hitech-os" / "apps" / "delta-forge"
        if str(alt).lower() not in seen:
            candidates.append(alt)
            seen.add(str(alt).lower())
    return candidates


def resolve_paths(script_path: Path, cli_input: Optional[Path], cli_output: Optional[Path]) -> Tuple[Path, Path]:
    input_dir = find_existing_path(candidate_input_dirs(script_path, cli_input))
    if not input_dir:
        attempted = "\n  - ".join(str(p) for p in candidate_input_dirs(script_path, cli_input))
        raise UserFacingError(
            "No encontré la carpeta de insumos. Busqué en:\n"
            f"  - {attempted}\n\n"
            "Ajusta con --input-dir si la moviste."
        )

    output_root = find_existing_path(candidate_output_roots(script_path, cli_output))
    if not output_root:
        # Si no existe, sí lo creamos en la primera ruta candidata para respetar el flujo.
        output_root = candidate_output_roots(script_path, cli_output)[0]
        ensure_dir(output_root)

    return input_dir, output_root


def optional_refs_in_dir(input_dir: Path) -> List[Path]:
    refs: List[Path] = []
    for name in OPTIONAL_REFERENCE_FILES:
        p = input_dir / name
        if p.exists():
            refs.append(p)
    return refs


def select_source(input_dir: Path) -> SourceSelection:
    bundle_zip = input_dir / PRIMARY_ZIP_NAME
    if bundle_zip.exists():
        return SourceSelection(
            mode="zip_bundle",
            source_path=bundle_zip,
            found_md_files=[],
            optional_reference_files=optional_refs_in_dir(input_dir),
        )

    loose_files = [input_dir / name for name in EXPECTED_MD_FILES]
    if all(p.exists() for p in loose_files):
        return SourceSelection(
            mode="loose_md_files",
            source_path=input_dir,
            found_md_files=loose_files,
            optional_reference_files=optional_refs_in_dir(input_dir),
        )

    missing = [str(p.name) for p in loose_files if not p.exists()]
    msg = textwrap.dedent(
        f"""
        No encontré una fuente válida para instalar el blindaje.

        Busqué primero:
          - {bundle_zip}

        Y luego estos 4 archivos sueltos:
          - {EXPECTED_MD_FILES[0]}
          - {EXPECTED_MD_FILES[1]}
          - {EXPECTED_MD_FILES[2]}
          - {EXPECTED_MD_FILES[3]}

        Faltan:
          - {chr(10).join(missing) if missing else '(sin detalle)'}
        """
    ).strip()
    raise UserFacingError(msg)


def safe_extract_md_only(zip_path: Path, dest_dir: Path) -> List[Path]:
    extracted: List[Path] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        zip_members = zf.namelist()
        for expected_name in EXPECTED_MD_FILES:
            matching = [m for m in zip_members if Path(m).name == expected_name]
            if not matching:
                raise UserFacingError(
                    f"El zip no trae el archivo esperado: {expected_name}\nZip: {zip_path}"
                )
            member = matching[0]
            output_path = dest_dir / expected_name
            ensure_dir(output_path.parent)
            with zf.open(member) as src, output_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted.append(output_path)
    return extracted


def copy_loose_files(files: Iterable[Path], dest_dir: Path) -> List[Path]:
    copied: List[Path] = []
    for src in files:
        dst = dest_dir / src.name
        shutil.copy2(src, dst)
        copied.append(dst)
    return copied


def validate_installed_files(installed_files: Sequence[Path]) -> None:
    names = sorted(p.name for p in installed_files)
    expected = sorted(EXPECTED_MD_FILES)
    if names != expected:
        raise UserFacingError(
            "La salida no quedó completa.\n"
            f"Esperado: {expected}\n"
            f"Encontrado: {names}"
        )
    for path in installed_files:
        if path.stat().st_size == 0:
            raise UserFacingError(f"El archivo quedó vacío: {path}")


def write_manifest(
    target_dir: Path,
    source: SourceSelection,
    installed_files: Sequence[Path],
) -> Path:
    manifest_path = target_dir / "_install_manifest.json"
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "script": SCRIPT_NAME,
        "source_mode": source.mode,
        "source_path": str(source.source_path),
        "target_dir": str(target_dir),
        "installed_files": [str(p) for p in installed_files],
        "optional_reference_files_detected": [str(p) for p in source.optional_reference_files],
        "replace_mode": "fresh_full_replace",
        "notes": [
            "La carpeta destino se recrea completa en cada corrida.",
            "Solo se instalan los 4 .md esperados.",
            "No se usan parches incrementales.",
        ],
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest_path


def write_log(
    output_root: Path,
    target_dir: Path,
    source: SourceSelection,
    installed_files: Sequence[Path],
    manifest_path: Path,
) -> Path:
    log_path = output_root / f"blindaje_install_log_{now_stamp()}.txt"
    lines = [
        "DeltaForge · Instalación de blindaje MD",
        "=" * 48,
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"Script: {SCRIPT_NAME}",
        f"Source mode: {source.mode}",
        f"Source path: {source.source_path}",
        f"Output root: {output_root}",
        f"Target dir: {target_dir}",
        "",
        "Installed files:",
    ]
    lines.extend(f"- {p}" for p in installed_files)
    lines.append("")
    lines.append("Optional reference files detected:")
    if source.optional_reference_files:
        lines.extend(f"- {p}" for p in source.optional_reference_files)
    else:
        lines.append("- (ninguno detectado)")
    lines.append("")
    lines.append(f"Manifest: {manifest_path}")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_path


def install_blindaje(input_dir: Path, output_root: Path) -> InstallResult:
    target_dir = output_root / TARGET_FOLDER_NAME
    ensure_dir(output_root)
    source = select_source(input_dir)

    temp_base = Path(tempfile.mkdtemp(prefix="deltaforge_blindaje_", dir=str(output_root)))
    staged_dir = temp_base / TARGET_FOLDER_NAME
    ensure_dir(staged_dir)

    try:
        if source.mode == "zip_bundle":
            installed_files = safe_extract_md_only(source.source_path, staged_dir)
        elif source.mode == "loose_md_files":
            installed_files = copy_loose_files(source.found_md_files, staged_dir)
        else:
            raise UserFacingError(f"Modo de fuente no soportado: {source.mode}")

        validate_installed_files(installed_files)
        manifest_path = write_manifest(staged_dir, source, installed_files)

        if target_dir.exists():
            shutil.rmtree(target_dir)

        shutil.move(str(staged_dir), str(target_dir))
        moved_files = [target_dir / p.name for p in installed_files]
        moved_manifest = target_dir / manifest_path.name
        log_path = write_log(output_root, target_dir, source, moved_files, moved_manifest)
        shutil.rmtree(temp_base, ignore_errors=True)

        return InstallResult(
            target_dir=target_dir,
            log_path=log_path,
            manifest_path=moved_manifest,
            source_mode=source.mode,
            source_path=source.source_path,
            installed_files=moved_files,
            optional_reference_files=source.optional_reference_files,
        )
    except Exception:
        shutil.rmtree(temp_base, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Instala de forma segura los 4 .md de blindaje DeltaForge en apps\\delta-forge."
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

    total_steps = 6
    try:
        info(1, total_steps, "Resolviendo rutas...")
        input_dir, output_root = resolve_paths(script_path, args.input_dir, args.output_root)
        print(f"    Input dir : {input_dir}")
        print(f"    Output root: {output_root}")

        info(2, total_steps, "Validando fuente de insumos...")
        source = select_source(input_dir)
        print(f"    Source mode: {source.mode}")
        print(f"    Source path: {source.source_path}")

        info(3, total_steps, "Preparando instalación limpia...")
        ensure_dir(output_root)

        info(4, total_steps, "Copiando / extrayendo los 4 .md...")
        result = install_blindaje(input_dir, output_root)

        info(5, total_steps, "Validando salida final...")
        validate_installed_files(result.installed_files)

        info(6, total_steps, "Listo. Todo quedó instalado sin parches raros.")
        print("")
        print("Salida final:")
        print(f"  - Carpeta:  {result.target_dir}")
        print(f"  - Manifest: {result.manifest_path}")
        print(f"  - Log:      {result.log_path}")
        print("")
        print("Archivos instalados:")
        for path in result.installed_files:
            print(f"  - {path.name}")
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
