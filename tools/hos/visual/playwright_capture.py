#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.exec import run_command
from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import dump_json, load_json, write_json
from tools.hos._core.stable_text import write_text

DEFAULT_VIEWPORTS: tuple[tuple[str, int, int], ...] = (
    ("desktop", 1440, 900),
    ("laptop", 1280, 800),
    ("tablet", 834, 1112),
    ("mobile", 390, 844),
)


def _node_capture_script() -> str:
    return r"""
const fs = require("fs");
const path = require("path");

async function run() {
  const configPath = process.argv[2];
  if (!configPath) {
    throw new Error("missing config path");
  }
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const { chromium } = require("playwright");
  const browser = await chromium.launch({ headless: true });
  const report = [];
  try {
    for (const target of config.targets) {
      for (const viewport of config.viewports) {
        const context = await browser.newContext({
          viewport: { width: viewport.width, height: viewport.height },
          deviceScaleFactor: 1,
          locale: "en-US",
          timezoneId: "UTC",
          colorScheme: "light"
        });
        const page = await context.newPage();
        await page.addInitScript(() => {
          const style = document.createElement("style");
          style.innerHTML = `*, *::before, *::after { animation: none !important; transition: none !important; caret-color: transparent !important; }`;
          document.head.appendChild(style);
          const fixed = Date.parse("2026-01-01T00:00:00.000Z");
          // eslint-disable-next-line no-global-assign
          Date.now = () => fixed;
        });
        const targetUrl = config.baseUrl.replace(/\/$/, "") + target.path;
        await page.goto(targetUrl, { waitUntil: "networkidle", timeout: config.timeoutMs });
        await page.waitForTimeout(config.settleMs);
        const outputPath = path.join(
          config.outputDir,
          `${target.name}__${viewport.name}.png`
        );
        await page.screenshot({ path: outputPath, fullPage: true });
        report.push({ target: target.name, viewport: viewport.name, file: outputPath, url: targetUrl });
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify({ ok: true, captures: report }, null, 2));
}

run().catch((error) => {
  const payload = {
    ok: false,
    error: String(error && error.stack ? error.stack : error)
  };
  process.stderr.write(JSON.stringify(payload, null, 2));
  process.exit(1);
});
"""


def capture_screenshots(
    repo_root: Path,
    base_url: str,
    targets: list[dict[str, str]],
    output_dir: Path,
    timeout_ms: int = 45_000,
    settle_ms: int = 500,
) -> dict[str, Any]:
    temp_dir = (repo_root / "tools/_local/visual/_capture_tmp").resolve()
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "baseUrl": base_url,
        "targets": targets,
        "viewports": [{"name": name, "width": width, "height": height} for name, width, height in DEFAULT_VIEWPORTS],
        "outputDir": output_dir.as_posix(),
        "timeoutMs": timeout_ms,
        "settleMs": settle_ms,
    }

    config_path = temp_dir / "capture_config.json"
    script_path = temp_dir / "capture_runner.cjs"
    write_json(config_path, config, indent=2, sort_keys=True)
    write_text(script_path, _node_capture_script(), trailing_newline=True)

    result = run_command(["node", script_path.as_posix(), config_path.as_posix()], cwd=repo_root, check=False)
    if result.ok:
        payload = load_json_text(result.stdout) if result.stdout.strip() else {"ok": True, "captures": []}
        if not isinstance(payload, dict):
            payload = {"ok": True, "captures": []}
        payload["classification"] = result.classification
        payload["returnCode"] = result.returncode
        return payload
    return {
        "ok": False,
        "classification": result.classification,
        "returnCode": result.returncode,
        "stderr": result.stderr.strip(),
        "stdout": result.stdout.strip(),
    }


def load_json_text(text: str) -> Any:
    import json

    return json.loads(text)


def parse_targets(values: list[str]) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    for value in values:
        if "=" in value:
            name, raw_path = value.split("=", 1)
        else:
            name = value.strip("/")
            raw_path = value
        path_value = raw_path if raw_path.startswith("/") else "/" + raw_path
        targets.append({"name": name.replace("/", "_") or "root", "path": path_value})
    unique: dict[str, dict[str, str]] = {}
    for target in targets:
        unique[target["name"]] = target
    return [unique[key] for key in sorted(unique)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture deterministic screenshots through Playwright.")
    parser.add_argument("--base-url", default="http://127.0.0.1:6007", help="Base URL to capture.")
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="Capture target as name=/path or /path. Repeatable.",
    )
    parser.add_argument("--output-dir", default="tools/_local/visual/current", help="Capture output directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    targets = parse_targets(args.target) if args.target else [{"name": "root", "path": "/"}]
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (repo_root / output_dir).resolve()

    payload = capture_screenshots(
        repo_root=repo_root,
        base_url=args.base_url,
        targets=targets,
        output_dir=output_dir,
    )
    if args.json:
        print(dump_json(payload), end="")
    else:
        print(f"[playwright_capture] ok={payload.get('ok', False)} output={output_dir.as_posix()}")
        if payload.get("ok"):
            captures = payload.get("captures", [])
            print(f"[playwright_capture] captures={len(captures)}")
        else:
            print(f"[playwright_capture] classification={payload.get('classification')}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
