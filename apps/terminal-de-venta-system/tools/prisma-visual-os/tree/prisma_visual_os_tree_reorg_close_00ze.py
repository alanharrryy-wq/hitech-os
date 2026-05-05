from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

PKG = "PRISMA_VISUAL_OS_TREE_REORG_CLOSE_00ZE_20260505_v02"
SYSTEM = Path("apps") / "terminal-de-venta-system"
VISUAL_REL = SYSTEM / "tools" / "prisma-visual-os"
REQ_DIRS = [
    "doctors",
    "launchers",
    "verifiers",
    "realtime",
    "scoring",
    "generators",
    "gates",
    "qa",
    "docs",
    "tree",
    "_plans",
]
HARD_VERIFY_COMMANDS = [
    ["node", "tools/prisma-visual-os/verify_prisma_show_pos_doctor_00x.mjs"],
    ["node", "tools/prisma-visual-os/verify_prisma_show_pos_ai_doctor_00y.mjs"],
    ["node", "tools/prisma-visual-os/verify_prisma_show_pos_doctor_00u.mjs"],
    ["node", "tools/prisma-visual-os/verify_prisma_visual_os_readme_status_00w.mjs"],
    ["node", "tools/visual/verify_prisma_reference_visual_scope_01h.mjs"],
]
ADVISORY_VERIFY_COMMANDS = [
    ["node", "tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs"],
    ["node", "tools/prisma-visual-os/gate_prisma_visual_release_00n.mjs"],
]


def stamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M%S")


def resolve_system_root(target_root: Path) -> Path:
    root = target_root.resolve()
    if root.name == "terminal-de-venta-system":
        return root
    for parent in [root, *root.parents]:
        if parent.name == "terminal-de-venta-system":
            return parent
    candidate = root / SYSTEM
    if candidate.exists():
        return candidate.resolve()
    return candidate


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_log(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def rel_to_system(system_root: Path, file_path: Path) -> str:
    try:
        return str(file_path.relative_to(system_root)).replace("\\", "/")
    except ValueError:
        return str(file_path)


def collect_checks(system_root: Path) -> list[dict]:
    visual_root = system_root / "tools" / "prisma-visual-os"
    checks: list[dict] = [
        {"name": "system root exists", "ok": system_root.exists(), "path": str(system_root)},
        {"name": "visual root exists", "ok": visual_root.exists(), "path": str(visual_root)},
    ]
    for name in REQ_DIRS:
        path = visual_root / name
        checks.append({"name": f"visual dir {name}", "ok": path.exists() and path.is_dir(), "path": str(path)})

    shim_pairs = [
        ("doctor 00U root shim", visual_root / "doctor_prisma_show_pos_scan_00u.py", visual_root / "doctors" / "doctor_prisma_show_pos_scan_00u.py"),
        ("doctor 00X root shim", visual_root / "doctor_prisma_show_pos_scan_00x.py", visual_root / "doctors" / "doctor_prisma_show_pos_scan_00x.py"),
        ("AI doctor 00Y root shim", visual_root / "ai_doctor_prisma_show_pos_00y.py", visual_root / "doctors" / "ai_doctor_prisma_show_pos_00y.py"),
    ]
    for label, root_file, impl_file in shim_pairs:
        root_text = root_file.read_text(encoding="utf-8", errors="ignore") if root_file.exists() else ""
        checks.append({"name": f"{label} exists", "ok": root_file.exists(), "path": str(root_file)})
        checks.append({"name": f"{label} impl exists", "ok": impl_file.exists(), "path": str(impl_file)})
        checks.append({"name": f"{label} points to doctors", "ok": impl_file.name in root_text and "doctors" in root_text, "path": str(root_file)})

    verifier_pairs = [
        ("verifier 00X", visual_root / "verify_prisma_show_pos_doctor_00x.mjs", visual_root / "verifiers" / "verify_prisma_show_pos_doctor_00x.mjs"),
        ("verifier 00Y", visual_root / "verify_prisma_show_pos_ai_doctor_00y.mjs", visual_root / "verifiers" / "verify_prisma_show_pos_ai_doctor_00y.mjs"),
        ("verifier 00U", visual_root / "verify_prisma_show_pos_doctor_00u.mjs", visual_root / "verifiers" / "verify_prisma_show_pos_doctor_00u.mjs"),
    ]
    for label, root_file, impl_file in verifier_pairs:
        root_text = root_file.read_text(encoding="utf-8", errors="ignore") if root_file.exists() else ""
        impl_text = impl_file.read_text(encoding="utf-8", errors="ignore") if impl_file.exists() else ""
        checks.append({"name": f"{label} root import exists", "ok": root_file.exists() and "./verifiers/" in root_text, "path": str(root_file)})
        checks.append({"name": f"{label} implementation exists", "ok": impl_file.exists(), "path": str(impl_file)})
        if label in {"verifier 00X", "verifier 00Y"}:
            checks.append({"name": f"{label} reorg-aware impl", "ok": "doctorImplPath" in impl_text and "resolvedDoctorSource" in impl_text, "path": str(impl_file)})

    return checks


def run_command(system_root: Path, command: list[str]) -> dict:
    try:
        proc = subprocess.run(
            command,
            cwd=system_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=90,
        )
        return {
            "command": command,
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdoutTail": proc.stdout[-4000:],
            "stderrTail": proc.stderr[-4000:],
        }
    except FileNotFoundError as exc:
        return {"command": command, "ok": False, "returncode": None, "error": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "ok": False, "returncode": None, "error": f"timeout: {exc}"}


def apply_dirs(system_root: Path) -> list[dict]:
    visual_root = system_root / "tools" / "prisma-visual-os"
    results = []
    for name in REQ_DIRS:
        path = visual_root / name
        existed = path.exists()
        path.mkdir(parents=True, exist_ok=True)
        results.append({"dir": name, "path": str(path), "created": not existed, "exists": path.exists()})
    return results


def execute(args: argparse.Namespace) -> int:
    target_root = Path(args.target_root).resolve()
    system_root = resolve_system_root(target_root)
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = stamp()
    log_path = out_dir / f"prisma_visual_os_tree_reorg_close_00ze_int_{run_id}.log"

    if args.apply:
        dir_results = apply_dirs(system_root)
        write_log(log_path, f"APPLY {PKG}")
        for item in dir_results:
            write_log(log_path, f"DIR {item['dir']} exists={item['exists']} created={item['created']}")
    else:
        dir_results = []
        write_log(log_path, f"{('DRY-RUN' if args.dry_run else 'VERIFY')} {PKG}")

    checks = collect_checks(system_root)
    hard_results = []
    advisory_results = []
    if args.verify or args.apply:
        for command in HARD_VERIFY_COMMANDS:
            result = run_command(system_root, command)
            hard_results.append(result)
            write_log(log_path, f"HARD CMD {'OK' if result['ok'] else 'FAIL'} {' '.join(command)} rc={result.get('returncode')}")
        for command in ADVISORY_VERIFY_COMMANDS:
            result = run_command(system_root, command)
            advisory_results.append(result)
            write_log(log_path, f"ADVISORY CMD {'OK' if result['ok'] else 'FAIL'} {' '.join(command)} rc={result.get('returncode')}")

    hard_ok = all(check["ok"] for check in checks) and all(result["ok"] for result in hard_results)
    advisory_ok = all(result["ok"] for result in advisory_results) if advisory_results else True
    status = "verified" if hard_ok and advisory_ok else "verified_with_advisories" if hard_ok else "blocked"
    payload = {
        "package": PKG,
        "mode": "apply" if args.apply else "verify" if args.verify else "dry-run",
        "status": status,
        "targetRoot": str(target_root),
        "systemRoot": str(system_root),
        "log": str(log_path),
        "dirResults": dir_results,
        "checks": checks,
        "hardCommandResults": hard_results,
        "advisoryCommandResults": advisory_results,
        "advisoryNote": "00T/00N se reportan pero no bloquean 00ZE porque este paquete cierra arbol/shims.",
    }
    write_json(out_dir / f"prisma_visual_os_tree_reorg_close_00ze_int_{run_id}.json", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if hard_ok else 4


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA Visual OS tree reorg close 00ZE verifier")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--verify", action="store_true")
    parser.add_argument("--target-root", default=r"F:\repos\hitech-os")
    parser.add_argument("--out-dir", default=r"F:\descargasf")
    args = parser.parse_args()
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
