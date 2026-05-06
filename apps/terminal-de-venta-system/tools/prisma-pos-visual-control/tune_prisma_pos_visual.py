#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

BEGIN = "/* PRISMA_POS_VISUAL_CONTROL_PLANE_BEGIN"
END = "/* PRISMA_POS_VISUAL_CONTROL_PLANE_END */"

TOKEN_REL = Path("products/tablet/app/components/pos/pos.visual.tokens.json")
PRESET_REL = Path("products/tablet/app/components/pos/pos.visual.presets.json")
GEN_REL = Path("products/tablet/app/components/pos/pos.visual.tokens.generated.css")
POS_CSS_REL = Path("products/tablet/app/components/pos/pos.module.css")
SHELL_CSS_REL = Path("products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css")
ROLLBACK_REL = Path("tools/prisma-pos-visual-control/.last_tune_rollback.json")
BACKUP_ROOT_REL = Path("tools/prisma-pos-visual-control/backups")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_VALIDATION = 3
EXIT_IO = 4


@dataclass(frozen=True)
class Token:
    id: str
    css: str
    group: str
    type: str
    unit: str
    minimum: float
    maximum: float
    current: str


def default_repo_root() -> Path:
    # Script is installed at <root>/tools/prisma-pos-visual-control/tune_prisma_pos_visual.py
    return Path(__file__).resolve().parents[2]


def log_dir() -> Path:
    if os.name == "nt":
        return Path("F:/descargasf")
    return Path("/mnt/data") if Path("/mnt/data").exists() else Path.cwd()


def log_path() -> Path:
    log_dir().mkdir(parents=True, exist_ok=True)
    return log_dir() / f"prisma_pos_visual_control_tune_{datetime.now().strftime('%y%m%d_%H%M')}.log"


class Logger:
    def __init__(self) -> None:
        self.path = log_path()
    def write(self, message: str) -> None:
        line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
        print(line)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Missing JSON file: {path.resolve()}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path.resolve()}: {exc}")


def parse_numeric(value: str, token: Token) -> float:
    raw = str(value).strip()
    if token.type == "number":
        try:
            return float(raw)
        except ValueError:
            raise ValueError(f"{token.id} expects number, got {value!r}")
    if token.type in {"length", "time"}:
        if not raw.endswith(token.unit):
            raise ValueError(f"{token.id} expects unit {token.unit}, got {value!r}")
        try:
            return float(raw[: -len(token.unit)])
        except ValueError:
            raise ValueError(f"{token.id} expects numeric prefix, got {value!r}")
    raise ValueError(f"Unsupported token type: {token.type}")


def format_numeric(num: float, token: Token) -> str:
    if token.type == "number":
        return f"{num:.4g}"
    if float(num).is_integer():
        prefix = str(int(num))
    else:
        prefix = f"{num:.4g}"
    return prefix + token.unit


def load_tokens(root: Path) -> tuple[dict[str, Any], dict[str, Token]]:
    data = read_json(root / TOKEN_REL)
    by_id: dict[str, Token] = {}
    for item in data.get("tokens", []):
        t = Token(
            id=item["id"], css=item["css"], group=item["group"], type=item["type"],
            unit=item.get("unit", ""), minimum=float(item["min"]), maximum=float(item["max"]),
            current=str(item["current"]),
        )
        value = parse_numeric(t.current, t)
        if value < t.minimum or value > t.maximum:
            raise ValueError(f"Token {t.id} value {t.current} outside range {t.minimum}..{t.maximum}")
        if t.id in by_id:
            raise ValueError(f"Duplicate token id: {t.id}")
        by_id[t.id] = t
    return data, by_id


def property_registration(data: dict[str, Any]) -> str:
    lines = ["/* PRISMA POS Visual Tokens - generated contract helpers. */"]
    syntax_map = {"length": "<length>", "number": "<number>", "time": "<time>"}
    for item in data["tokens"]:
        syntax = syntax_map[item["type"]]
        lines.append(f"@property {item['css']} {{")
        lines.append(f"  syntax: \"{syntax}\";")
        lines.append("  inherits: true;")
        lines.append(f"  initial-value: {item['default']};")
        lines.append("}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_bridge(data: dict[str, Any], selector: str, groups: set[str] | None = None) -> str:
    lines = [BEGIN, "   Owner: tools/prisma-pos-visual-control/tune_prisma_pos_visual.py", "   Do not edit this block by hand. Adjust tokens or presets instead.", "*/", f"{selector} {{"]
    for item in data["tokens"]:
        if groups and item["group"] not in groups:
            continue
        lines.append(f"  {item['css']}: {item['current']};")
    lines.append("}")
    lines.append(END)
    return "\n".join(lines) + "\n"


def build_generated_css(data: dict[str, Any]) -> str:
    pos = build_bridge(data, ".posWorkspace, .catalogArea, .searchCard, .productCard, .productImageStage, .ticketPanel, .checkoutLink")
    shell_groups = {"glass", "glow", "shadow", "shell", "motion", "accessibility"}
    shell = build_bridge(data, ".shell, .sidebar, .header, .content", shell_groups)
    return property_registration(data) + "\n" + pos + "\n" + shell


def replace_block(text: str, block: str) -> str:
    if BEGIN in text and END in text:
        pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.DOTALL)
        return pattern.sub(block.rstrip(), text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block


def backup_files(root: Path, logger: Logger, files: list[Path]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = root / BACKUP_ROOT_REL / f"tune_{stamp}"
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"created_at": datetime.now().isoformat(timespec="seconds"), "files": []}
    for rel in files:
        src = root / rel
        entry = {"relative_path": rel.as_posix(), "existed": src.exists()}
        if src.exists():
            dst = backup_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            logger.write(f"Backup: {src} -> {dst}")
        manifest["files"].append(entry)
    (root / ROLLBACK_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / ROLLBACK_REL).write_text(json.dumps({"backup_root": str(backup_root), **manifest}, indent=2), encoding="utf-8")
    return backup_root


def restore_last(root: Path, logger: Logger) -> None:
    rb = root / ROLLBACK_REL
    if not rb.exists():
        raise SystemExit(f"No rollback manifest found: {rb.resolve()}")
    data = json.loads(rb.read_text(encoding="utf-8"))
    backup_root = Path(data["backup_root"])
    for entry in data.get("files", []):
        rel = Path(entry["relative_path"])
        target = root / rel
        if entry.get("existed"):
            src = backup_root / rel
            if not src.exists():
                raise SystemExit(f"Rollback source missing: {src.resolve()}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            logger.write(f"Restored: {target}")
        else:
            if target.exists():
                target.unlink()
                logger.write(f"Removed new file: {target}")
    logger.write("Rollback complete")


def apply_changes(root: Path, data: dict[str, Any], dry_run: bool, logger: Logger) -> None:
    paths = [TOKEN_REL, PRESET_REL, GEN_REL, POS_CSS_REL, SHELL_CSS_REL]
    for rel in [TOKEN_REL, PRESET_REL, POS_CSS_REL, SHELL_CSS_REL]:
        if not (root / rel).exists():
            raise SystemExit(f"Required file missing: {(root / rel).resolve()}")
    pos_block = build_bridge(data, ".posWorkspace, .catalogArea, .searchCard, .productCard, .productImageStage, .ticketPanel, .checkoutLink")
    shell_block = build_bridge(data, ".shell, .sidebar, .header, .content", {"glass", "glow", "shadow", "shell", "motion", "accessibility"})
    generated = build_generated_css(data)
    logger.write(f"Target root: {root.resolve()}")
    logger.write(f"Dry run: {dry_run}")
    logger.write("Would update token JSON, generated CSS, and CSS bridge blocks")
    if dry_run:
        return
    backup_files(root, logger, paths)
    (root / TOKEN_REL).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / GEN_REL).write_text(generated, encoding="utf-8")
    for rel, block in [(POS_CSS_REL, pos_block), (SHELL_CSS_REL, shell_block)]:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        path.write_text(replace_block(text, block), encoding="utf-8")
        logger.write(f"Updated bridge block: {path}")


def apply_preset(data: dict[str, Any], preset_name: str, root: Path) -> None:
    presets = read_json(root / PRESET_REL).get("presets", {})
    if preset_name not in presets:
        raise SystemExit(f"Unknown preset {preset_name!r}. Available: {', '.join(sorted(presets))}")
    changes = presets[preset_name]
    for item in data["tokens"]:
        if item["id"] in changes:
            item["current"] = str(changes[item["id"]])


def apply_sets(data: dict[str, Any], sets: list[str], by_id: dict[str, Token]) -> None:
    index = {item["id"]: item for item in data["tokens"]}
    for pair in sets:
        if "=" not in pair:
            raise SystemExit(f"Invalid --set value {pair!r}. Expected token=value")
        key, value = pair.split("=", 1)
        if key not in index:
            raise SystemExit(f"Unknown token: {key}")
        token = by_id[key]
        num = parse_numeric(value, token)
        if num < token.minimum or num > token.maximum:
            raise SystemExit(f"{key}={value} outside range {token.minimum}..{token.maximum}{token.unit}")
        index[key]["current"] = value


def apply_scales(data: dict[str, Any], scales: list[str], by_id: dict[str, Token]) -> None:
    for spec in scales:
        if "=" not in spec:
            raise SystemExit(f"Invalid --scale value {spec!r}. Expected group=factor")
        group, raw_factor = spec.split("=", 1)
        factor = float(raw_factor)
        for item in data["tokens"]:
            if item["group"] != group:
                continue
            token = by_id[item["id"]]
            old = parse_numeric(item["current"], token)
            new = max(token.minimum, min(token.maximum, old * factor))
            item["current"] = format_numeric(new, token)


def verify(root: Path, logger: Logger) -> None:
    data, _ = load_tokens(root)
    for rel in [TOKEN_REL, PRESET_REL, GEN_REL, POS_CSS_REL, SHELL_CSS_REL]:
        if not (root / rel).exists():
            raise SystemExit(f"Missing required file: {(root / rel).resolve()}")
    gen = (root / GEN_REL).read_text(encoding="utf-8")
    pos = (root / POS_CSS_REL).read_text(encoding="utf-8")
    shell = (root / SHELL_CSS_REL).read_text(encoding="utf-8")
    for text, label in [(gen, 'generated css'), (pos, 'pos css'), (shell, 'shell css')]:
        if BEGIN not in text or END not in text:
            raise SystemExit(f"Missing control-plane markers in {label}")
    ids = [t["id"] for t in data["tokens"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate token ids detected")
    logger.write(f"Verify OK. Token count: {len(ids)}")


def list_tokens(root: Path) -> None:
    data, _ = load_tokens(root)
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in data["tokens"]:
        groups.setdefault(item["group"], []).append(item)
    for group in sorted(groups):
        print(f"\n[{group}]")
        for item in groups[group]:
            print(f"  {item['id']} = {item['current']} ({item['css']})")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Tune PRISMA POS visual tokens safely.", epilog="Examples: --list | --preset checkout_focus --apply | --set pos.glass.blur=28px --apply | --scale glow=0.8 --apply")
    p.add_argument("--target-root", default=None, help="terminal-de-venta-system root. Defaults to script-relative root.")
    p.add_argument("--list", action="store_true", help="List tokens and values.")
    p.add_argument("--preset", help="Apply named preset.")
    p.add_argument("--set", action="append", default=[], help="Set token value, e.g. pos.glass.blur=28px")
    p.add_argument("--scale", action="append", default=[], help="Scale all tokens in group, e.g. glow=0.8")
    p.add_argument("--dry-run", action="store_true", help="Show planned change without writing.")
    p.add_argument("--apply", action="store_true", help="Write changes.")
    p.add_argument("--verify", action="store_true", help="Verify control-plane installation.")
    p.add_argument("--sync", action="store_true", help="Regenerate CSS and bridge blocks from current token JSON.")
    p.add_argument("--rollback", action="store_true", help="Rollback last tune operation.")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.target_root).resolve() if args.target_root else default_repo_root()
    logger = Logger()
    try:
        if args.rollback:
            restore_last(root, logger)
            return EXIT_OK
        if args.list:
            list_tokens(root)
            return EXIT_OK
        if args.verify:
            verify(root, logger)
            return EXIT_OK
        data, by_id = load_tokens(root)
        changed = bool(args.sync)
        if args.preset:
            apply_preset(data, args.preset, root)
            changed = True
        if args.set:
            apply_sets(data, args.set, by_id)
            changed = True
        if args.scale:
            apply_scales(data, args.scale, by_id)
            changed = True
        if not changed:
            logger.write("No token changes requested. Use --list, --verify, --preset, --set, or --scale.")
            return EXIT_USAGE
        if not args.apply and not args.dry_run:
            logger.write("No write mode selected. Add --dry-run or --apply.")
            return EXIT_USAGE
        # Re-validate after modifications.
        tmp = {item["id"]: item for item in data["tokens"]}
        for token_id, token in by_id.items():
            parse_numeric(str(tmp[token_id]["current"]), token)
        apply_changes(root, data, args.dry_run, logger)
        if args.apply:
            verify(root, logger)
        logger.write(f"Log: {logger.path}")
        return EXIT_OK
    except ValueError as exc:
        logger.write(f"Validation error: {exc}")
        return EXIT_VALIDATION
    except OSError as exc:
        logger.write(f"IO error: {exc}")
        return EXIT_IO


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
