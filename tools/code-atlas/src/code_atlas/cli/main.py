from __future__ import annotations

import argparse
import sys

from code_atlas.coverage.atlas_audit import main as coverage_main
from code_atlas.coverage.important_gate import main as gate_main
from code_atlas.db_glass.reality_check import main as db_main
from code_atlas.manifest.todo_el_show_plus import main as todo_main


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(prog="code-atlas-plus", description="Code Atlas modular feature CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("coverage")
    sub.add_parser("gate")
    sub.add_parser("db")
    sub.add_parser("todo-plus")
    ns, rest = parser.parse_known_args(argv)
    if ns.command == "coverage":
        return coverage_main(rest)
    if ns.command == "gate":
        return gate_main(rest)
    if ns.command == "db":
        return db_main(rest)
    if ns.command == "todo-plus":
        return todo_main(rest)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
