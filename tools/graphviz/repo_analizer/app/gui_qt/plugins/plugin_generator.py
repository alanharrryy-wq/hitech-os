from __future__ import annotations

"""Generator for manifest-based Repo Analyzer plugins."""

import argparse
import re
from pathlib import Path
from string import Template
from typing import Any


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return value or "new_plugin"


def titleize(plugin_id: str) -> str:
    return " ".join(part.capitalize() for part in plugin_id.split("_"))


class PluginGenerator:
    def __init__(self, plugins_root: Path | None = None) -> None:
        script_dir = Path(__file__).resolve().parent
        self.plugins_root = plugins_root or script_dir
        self.templates_root = script_dir / "templates" / "package_plugin"

    def _read_template(self, name: str) -> Template:
        template_path = self.templates_root / name
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        return Template(template_path.read_text(encoding="utf-8"))

    def _build_context(
        self,
        plugin_id: str,
        display_name: str,
        description: str,
        author: str,
        dependencies: list[str],
    ) -> dict[str, Any]:
        package_name = plugin_id
        class_name = "".join(part.capitalize() for part in plugin_id.split("_")) + "Plugin"
        dependency_block = "[]"
        if dependencies:
            quoted = ", ".join(f'"{item}"' for item in dependencies)
            dependency_block = f"[{quoted}]"

        return {
            "PLUGIN_ID": plugin_id,
            "DISPLAY_NAME": display_name,
            "DESCRIPTION": description,
            "AUTHOR": author,
            "PACKAGE_NAME": package_name,
            "CLASS_NAME": class_name,
            "DEPENDENCIES": dependency_block,
            "MODULE_NAME": "plugin",
        }

    def create_plugin(
        self,
        plugin_name: str,
        *,
        display_name: str | None = None,
        description: str = "",
        author: str = "",
        dependencies: list[str] | None = None,
        force: bool = False,
    ) -> Path:
        plugin_id = slugify(plugin_name)
        display_name = display_name or titleize(plugin_id)
        dependencies = dependencies or []
        context = self._build_context(
            plugin_id=plugin_id,
            display_name=display_name,
            description=description,
            author=author,
            dependencies=dependencies,
        )

        plugin_dir = self.plugins_root / plugin_id
        if plugin_dir.exists() and not force:
            raise FileExistsError(
                f"Plugin directory already exists: {plugin_dir}. Use --force to overwrite."
            )

        plugin_dir.mkdir(parents=True, exist_ok=True)

        files_to_render = {
            "__init__.py": "__init__.py.tpl",
            "plugin.py": "plugin.py.tpl",
            "plugin.json": "plugin.json.tpl",
            "README.md": "README.md.tpl",
        }

        for target_name, template_name in files_to_render.items():
            rendered = self._read_template(template_name).substitute(context)
            (plugin_dir / target_name).write_text(rendered, encoding="utf-8")

        return plugin_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a manifest-based plugin package for Repo Analyzer.",
    )
    parser.add_argument("name", help="Plugin name or identifier, e.g. my_plugin")
    parser.add_argument(
        "--display-name",
        default=None,
        help="Human-readable plugin name shown in UI and plugin.json",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Short description for the plugin manifest",
    )
    parser.add_argument(
        "--author",
        default="",
        help="Plugin author name",
    )
    parser.add_argument(
        "--dependency",
        action="append",
        default=[],
        help="Dependency plugin id. Repeat the flag for multiple dependencies.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Plugins root directory. Defaults to the current plugins package directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing plugin directory if present.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    generator = PluginGenerator(output_dir)
    plugin_dir = generator.create_plugin(
        args.name,
        display_name=args.display_name,
        description=args.description,
        author=args.author,
        dependencies=args.dependency,
        force=args.force,
    )

    print(f"Created plugin package: {plugin_dir}")
    print("Next step:")
    print(f"  1. Edit {plugin_dir / 'plugin.py'}")
    print(f"  2. Review {plugin_dir / 'plugin.json'}")
    print("  3. Launch Repo Analyzer and validate runtime wiring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
