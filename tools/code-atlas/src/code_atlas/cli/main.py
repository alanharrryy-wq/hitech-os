from __future__ import annotations

import argparse
import sys

from code_atlas.coverage.atlas_audit import main as coverage_main
from code_atlas.coverage.important_gate import main as gate_main
from code_atlas.db_glass.reality_check import main as db_main
from code_atlas.manifest.todo_el_show_plus import main as todo_main
from code_atlas.operational.main import main as operational_main
from code_atlas.surface_target_atlas.runner import main as surface_target_main

COMMANDS = {
    "coverage": coverage_main,
    "gate": gate_main,
    "db": db_main,
    "todo-plus": todo_main,
    "operational": operational_main,
    "surface-target": surface_target_main,
}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="code-atlas",
        description="Repository-neutral Code Atlas CLI. Optional project adapters are not imported by the base command surface.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for command in COMMANDS:
        sub.add_parser(command)
    namespace, rest = parser.parse_known_args(args)
    handler = COMMANDS.get(namespace.command)
    if handler is None:
        parser.error("unknown command")
        return 2
    return int(handler(rest))


if __name__ == "__main__":
    raise SystemExit(main())
