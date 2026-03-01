#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import dump_json, load_json
from tools.hos._core.stable_text import write_text

STORYBOOK_MARKERS: tuple[str, ...] = (
    ".storybook/main.ts",
    ".storybook/main.js",
    ".storybook/main.cjs",
    ".storybook/main.mjs",
)


@dataclass(frozen=True)
class StorybookLocation:
    workspace_path: str
    package_name: str
    marker_file: str


def detect_storybook_workspaces(repo_root: Path) -> list[StorybookLocation]:
    matches: list[StorybookLocation] = []
    for package_json in sorted(repo_root.glob("**/package.json")):
        if any(part in {"node_modules", ".git", "tools", "docs"} for part in package_json.parts):
            continue
        workspace = package_json.parent
        marker = None
        for marker_name in STORYBOOK_MARKERS:
            if (workspace / marker_name).exists():
                marker = marker_name
                break
        if marker is None:
            manifest = load_json(package_json)
            if isinstance(manifest, dict):
                deps = {
                    **(manifest.get("dependencies", {}) if isinstance(manifest.get("dependencies"), dict) else {}),
                    **(
                        manifest.get("devDependencies", {})
                        if isinstance(manifest.get("devDependencies"), dict)
                        else {}
                    ),
                }
                if any("storybook" in dep for dep in deps):
                    marker = "<dependency-only>"
        if marker is None:
            continue
        manifest = load_json(package_json)
        package_name = manifest.get("name") if isinstance(manifest, dict) else None
        if not isinstance(package_name, str) or not package_name:
            package_name = workspace.relative_to(repo_root).as_posix()
        matches.append(
            StorybookLocation(
                workspace_path=workspace.relative_to(repo_root).as_posix(),
                package_name=package_name,
                marker_file=marker,
            )
        )
    return sorted(matches, key=lambda item: (item.workspace_path, item.package_name))


def ensure_template(repo_root: Path) -> list[Path]:
    template_root = (repo_root / "tools/hos/visual/templates/.storybook").resolve()
    template_root.mkdir(parents=True, exist_ok=True)

    main_ts = """import type { StorybookConfig } from "@storybook/nextjs";

const config: StorybookConfig = {
  stories: ["../**/*.stories.@(ts|tsx|mdx)"],
  addons: ["@storybook/addon-essentials", "@storybook/addon-interactions"],
  framework: {
    name: "@storybook/nextjs",
    options: {}
  },
  docs: {
    autodocs: "tag"
  }
};

export default config;
"""

    preview_ts = """import type { Preview } from "@storybook/react";

const preview: Preview = {
  parameters: {
    controls: { expanded: true },
    options: { storySort: { method: "alphabetical" } },
    backgrounds: { disable: true },
    layout: "fullscreen"
  },
  decorators: [
    (Story) => {
      return (
        <div data-visual-deterministic="1" style={{ animation: "none", transition: "none" }}>
          <Story />
        </div>
      );
    }
  ]
};

export default preview;
"""

    manager_ts = """import { addons } from "@storybook/manager-api";
import { create } from "@storybook/theming/create";

addons.setConfig({
  theme: create({
    base: "light",
    brandTitle: "HITECH UI Lab",
    brandUrl: "https://example.invalid"
  }),
  panelPosition: "right",
  showPanel: true
});
"""

    readme = """# Storybook Templates

These templates are tooling-only and are not auto-applied to applications.
Use them as a starting point for deterministic visual regression baselines.
"""
    output_map = {
        template_root / "main.ts": main_ts,
        template_root / "preview.ts": preview_ts,
        template_root / "manager.ts": manager_ts,
        (repo_root / "tools/hos/visual/templates/README.md").resolve(): readme,
    }
    written: list[Path] = []
    for path in sorted(output_map):
        write_text(path, output_map[path], trailing_newline=True)
        written.append(path)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect Storybook availability and maintain templates.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--ensure-template", action="store_true", help="Ensure template files exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    matches = detect_storybook_workspaces(repo_root=repo_root)
    templates = ensure_template(repo_root=repo_root) if args.ensure_template else []
    payload: dict[str, Any] = {
        "storybookPresent": len(matches) > 0,
        "matchCount": len(matches),
        "matches": [item.__dict__ for item in matches],
        "templatesWritten": [path.relative_to(repo_root).as_posix() for path in templates],
    }
    if args.json:
        print(dump_json(payload), end="")
    else:
        print(f"[storybook_detect] present={payload['storybookPresent']} matches={payload['matchCount']}")
        for item in matches:
            print(f" - {item.workspace_path} ({item.package_name}) marker={item.marker_file}")
        if templates:
            print(f"[storybook_detect] templates={len(templates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
