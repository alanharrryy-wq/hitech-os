from __future__ import annotations

import argparse
import importlib
import sys

from code_atlas.coverage.atlas_audit import main as coverage_main
from code_atlas.coverage.important_gate import main as gate_main
from code_atlas.db_glass.reality_check import main as db_main
from code_atlas.intelligence.cli import main as intelligence_main
from code_atlas.manifest.todo_el_show_plus import main as todo_main
from code_atlas.operational.main import main as operational_main


def _run_explicit_adapter(module_name: str, argv: list[str]) -> int:
    """Load a product adapter only after the operator selected its dedicated command."""
    module = importlib.import_module(module_name)
    entrypoint = getattr(module, "main", None)
    if not callable(entrypoint):
        raise RuntimeError(f"ADAPTER_ENTRYPOINT_MISSING:{module_name}")
    return int(entrypoint(argv))


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(prog="code-atlas-plus", description="Code Atlas modular feature CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("coverage")
    sub.add_parser("gate")
    sub.add_parser("db")
    sub.add_parser("todo-plus")
    sub.add_parser("operational")
    sub.add_parser("intelligence")
    sub.add_parser("uimap")
    sub.add_parser("ui-bridge")
    ns, rest = parser.parse_known_args(argv)
    if ns.command == "coverage":
        return coverage_main(rest)
    if ns.command == "gate":
        return gate_main(rest)
    if ns.command == "db":
        return db_main(rest)
    if ns.command == "todo-plus":
        return todo_main(rest)
    if ns.command == "operational":
        return operational_main(rest)
    if ns.command == "intelligence":
        return intelligence_main(rest)
    if ns.command == "uimap":
        return _run_explicit_adapter("code_atlas.app_map.uimap.cli", rest)
    if ns.command == "ui-bridge":
        return _run_explicit_adapter("code_atlas.ui_bridge.cli", rest)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


# Backward-compatible operational bridge kept neutral.
def _catlas_operational_v3_main(argv=None):
    from code_atlas.operational.cli import main as _main
    return _main(argv)
