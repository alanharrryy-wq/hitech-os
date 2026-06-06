# CODE_ATLAS_MOTOR_HUB_MODULE_V01
"""Declarative registry for Atlas, Playwright Mamastrophic and PRISMA_CTX motors."""

from __future__ import annotations

import os
from pathlib import Path

from .specs import MotorSpec


def _repo_root() -> Path:
    return Path(os.environ.get("CODE_ATLAS_REPO_ROOT", r"F:\repos\hitech-os"))


def _code_atlas_root() -> Path:
    fallback = _repo_root() / "tools" / "code-atlas"
    return Path(os.environ.get("CODE_ATLAS_APP_ROOT", str(fallback)))


def _playwright_root() -> Path:
    return _repo_root() / "tools" / "Plawright Mamastrophic"


def _prisma_ctx_root() -> Path:
    return Path(os.environ.get("PRISMA_CTX_ROOT", r"F:\PRISMA_CTX"))


def _powershell_script(root: Path, script: Path, args: tuple[str, ...] = ()) -> MotorSpecCommand:
    return MotorSpecCommand(
        root=str(root),
        program="powershell.exe",
        args=("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args),
    )


def _cmd_script(root: Path, script: Path) -> MotorSpecCommand:
    return MotorSpecCommand(
        root=str(root),
        program="cmd.exe",
        args=("/d", "/s", "/c", str(script)),
    )


class MotorSpecCommand:
    def __init__(self, *, root: str, program: str, args: tuple[str, ...]) -> None:
        self.root = root
        self.program = program
        self.args = args


def build_motor_registry() -> list[MotorSpec]:
    atlas = _code_atlas_root()
    playwright = _playwright_root()
    prisma = _prisma_ctx_root()

    specs: list[MotorSpec] = []

    atlas_cmd = _powershell_script(
        atlas,
        atlas / "scripts" / "RUN_TODO_EL_SHOW_PLUS.ps1",
    )
    specs.append(
        MotorSpec(
            motor_id="atlas.todo_el_show_plus",
            group="Atlas",
            label="Todo El Show Plus",
            description="Ejecuta el paquete modular existente de Code Atlas y deja reportes en reports\\todo_el_show_plus.",
            root=atlas_cmd.root,
            program=atlas_cmd.program,
            args=atlas_cmd.args,
        )
    )

    playwright_run = playwright / "RUN.ps1"
    for mode, label in (
        ("discovery", "Discovery"),
        ("critical", "Critical"),
        ("quick", "Quick"),
        ("full", "Full"),
    ):
        cmd = _powershell_script(playwright, playwright_run, ("-Mode", mode))
        specs.append(
            MotorSpec(
                motor_id="playwright." + mode,
                group="Playwright",
                label=label,
                description="Ejecuta Playwright Mamastrophic en modo {0} sin auto-start ni auto-kill desde el hub.".format(mode),
                root=cmd.root,
                program=cmd.program,
                args=cmd.args,
            )
        )

    ctx_commands = (
        ("prisma_ctx.todo", "CTX Todo", "00_ALL.cmd"),
        ("prisma_ctx.tablet", "CTX Tablet", "03_TABLET.cmd"),
        ("prisma_ctx.pc", "CTX PC", "04_PC.cmd"),
        ("prisma_ctx.control", "CTX Control", "06_CONTROL_CENTER.cmd"),
        ("prisma_ctx.gobierno", "CTX Gobierno", "07_GOBIERNO.cmd"),
        ("prisma_ctx.verify", "CTX Verificar", "11_VERIFY_PACKAGE.cmd"),
    )
    for motor_id, label, cmd_name in ctx_commands:
        cmd = _cmd_script(prisma, prisma / cmd_name)
        specs.append(
            MotorSpec(
                motor_id=motor_id,
                group="PRISMA_CTX",
                label=label,
                description="Ejecuta {0} desde F:\\PRISMA_CTX.".format(cmd_name),
                root=cmd.root,
                program=cmd.program,
                args=cmd.args,
            )
        )

    return specs


def grouped_motor_registry() -> dict[str, list[MotorSpec]]:
    grouped: dict[str, list[MotorSpec]] = {"Atlas": [], "Playwright": [], "PRISMA_CTX": []}
    for spec in build_motor_registry():
        grouped.setdefault(spec.group, []).append(spec)
    return grouped
