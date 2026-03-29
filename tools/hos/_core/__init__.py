"""Core deterministic utilities for HITECH toolchain."""

from .cli import CommandRegistry, Subcommand
from .exec import CommandResult, run_command
from .hashing import hash_directory, sha256_file, sha256_text
from .log import ToolLogger, create_logger
from .paths import assert_within, is_within, safe_join
from .repo_root import find_repo_root
from .reports import write_json_report, write_markdown_report
from .stable_json import load_json, write_json
from .stable_text import write_text

__all__ = [
    "CommandRegistry",
    "CommandResult",
    "Subcommand",
    "ToolLogger",
    "assert_within",
    "create_logger",
    "find_repo_root",
    "hash_directory",
    "is_within",
    "load_json",
    "run_command",
    "safe_join",
    "sha256_file",
    "sha256_text",
    "write_json",
    "write_json_report",
    "write_markdown_report",
    "write_text",
]
