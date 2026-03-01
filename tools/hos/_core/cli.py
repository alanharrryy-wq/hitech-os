#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

Handler = Callable[[argparse.Namespace], int]
Configure = Callable[[argparse.ArgumentParser], None]


@dataclass(frozen=True)
class Subcommand:
    name: str
    help: str
    handler: Handler
    configure: Configure | None = None


class CommandRegistry:
    def __init__(self, description: str) -> None:
        self._description = description
        self._commands: list[Subcommand] = []

    def add(self, command: Subcommand) -> None:
        if any(existing.name == command.name for existing in self._commands):
            raise ValueError(f"duplicate subcommand: {command.name}")
        self._commands.append(command)

    def build(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=self._description)
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
        parser.add_argument(
            "--deterministic-time",
            action="store_true",
            help="Emit deterministic timestamps when supported by tool logger.",
        )
        subs = parser.add_subparsers(dest="subcommand", required=True)

        for command in sorted(self._commands, key=lambda item: item.name):
            sub = subs.add_parser(command.name, help=command.help, description=command.help)
            sub.set_defaults(_handler=command.handler)
            if command.configure is not None:
                command.configure(sub)
        return parser

    def run(self, argv: Sequence[str] | None = None) -> int:
        parser = self.build()
        args = parser.parse_args(argv)
        handler: Handler | None = getattr(args, "_handler", None)
        if handler is None:
            parser.print_help()
            return 2
        return handler(args)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive integer")
    return parsed


def existing_path(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {value}")
    return path

