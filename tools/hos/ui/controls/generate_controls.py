#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import re
from pathlib import Path

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_text import write_text

NAME_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9]+$")
KINDS = ("toggle", "slider", "dropdown")

DEFAULT_TEMPLATE_NAMES = (
    "Component.tsx.tpl",
    "Component.styles.css.tpl",
    "Component.stories.tsx.tpl",
    "Component.test.tsx.tpl",
    "index.ts.tpl",
)


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"template not found: {path}")
    return path.read_text(encoding="utf-8")


def render_template(raw: str, name: str, kind: str) -> str:
    return (
        raw.replace("{{COMPONENT_NAME}}", name)
        .replace("{{CONTROL_KIND}}", kind)
        .replace("{{component_name}}", name.lower())
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Toggle/Slider/Dropdown component templates.")
    parser.add_argument("--kind", choices=KINDS, required=True, help="Control kind template.")
    parser.add_argument("--name", required=True, help="Component name in PascalCase.")
    parser.add_argument(
        "--out-dir",
        default="tools/_local/ui_scaffold/controls",
        help="Output parent folder.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not NAME_PATTERN.match(args.name):
        raise ValueError("name must be PascalCase and start with uppercase letter")

    repo_root = find_repo_root()
    template_root = (repo_root / "tools/hos/ui/controls/templates" / args.kind).resolve()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (repo_root / out_dir).resolve()
    component_dir = out_dir / args.name
    if component_dir.exists() and not args.force:
        raise FileExistsError(f"destination already exists: {component_dir}")

    output_map = {
        component_dir / f"{args.name}.tsx": "Component.tsx.tpl",
        component_dir / f"{args.name}.styles.css": "Component.styles.css.tpl",
        component_dir / f"{args.name}.stories.tsx": "Component.stories.tsx.tpl",
        component_dir / f"{args.name}.test.tsx": "Component.test.tsx.tpl",
        component_dir / "index.ts": "index.ts.tpl",
    }

    for output in sorted(output_map):
        template_name = output_map[output]
        template_file = template_root / template_name
        raw = load_template(template_file)
        rendered = render_template(raw=raw, name=args.name, kind=args.kind)
        write_text(output, rendered, trailing_newline=True)
        print(f"[generate_controls] wrote {output.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
