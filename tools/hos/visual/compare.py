#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.hashing import sha256_file
from tools.hos._core.stable_json import dump_json
from tools.hos.visual.baseline_store import list_png_files

try:
    from PIL import Image, ImageChops  # type: ignore

    PIL_AVAILABLE = True
except Exception:  # noqa: BLE001
    PIL_AVAILABLE = False
    Image = None  # type: ignore
    ImageChops = None  # type: ignore


@dataclass(frozen=True)
class ComparisonResult:
    file: str
    exists_in_baseline: bool
    exists_in_current: bool
    equal: bool
    diff_ratio: float
    mode: str


def _diff_ratio_with_pillow(left: Path, right: Path) -> float:
    assert PIL_AVAILABLE
    left_img = Image.open(left).convert("RGBA")
    right_img = Image.open(right).convert("RGBA")
    if left_img.size != right_img.size:
        return 1.0
    diff = ImageChops.difference(left_img, right_img)
    histogram = diff.histogram()
    total_channels = left_img.size[0] * left_img.size[1] * 4
    if total_channels <= 0:
        return 0.0
    non_zero = sum(histogram[idx] for idx in range(1, len(histogram)))
    return min(1.0, max(0.0, non_zero / total_channels))


def compare_images(baseline: Path, current: Path) -> tuple[bool, float, str]:
    if not baseline.exists() or not current.exists():
        return False, 1.0, "missing"
    if PIL_AVAILABLE:
        ratio = _diff_ratio_with_pillow(baseline, current)
        return ratio == 0.0, ratio, "pillow"
    equal = sha256_file(baseline) == sha256_file(current)
    return equal, 0.0 if equal else 1.0, "hash"


def compare_directories(
    baseline_dir: Path,
    current_dir: Path,
    diff_dir: Path,
    threshold: float = 0.0,
) -> dict[str, Any]:
    baseline_files = {path.relative_to(baseline_dir).as_posix(): path for path in list_png_files(baseline_dir)}
    current_files = {path.relative_to(current_dir).as_posix(): path for path in list_png_files(current_dir)}
    all_keys = sorted(set(baseline_files) | set(current_files))

    results: list[ComparisonResult] = []
    failures = 0

    for key in all_keys:
        left = baseline_files.get(key)
        right = current_files.get(key)
        if left is None or right is None:
            result = ComparisonResult(
                file=key,
                exists_in_baseline=left is not None,
                exists_in_current=right is not None,
                equal=False,
                diff_ratio=1.0,
                mode="missing",
            )
            failures += 1
        else:
            equal, diff_ratio, mode = compare_images(left, right)
            passed = equal or diff_ratio <= threshold
            result = ComparisonResult(
                file=key,
                exists_in_baseline=True,
                exists_in_current=True,
                equal=passed,
                diff_ratio=diff_ratio,
                mode=mode,
            )
            if not passed:
                failures += 1
                out = diff_dir / key
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(right, out)
        results.append(result)

    payload = {
        "baselineDir": baseline_dir.as_posix(),
        "currentDir": current_dir.as_posix(),
        "diffDir": diff_dir.as_posix(),
        "mode": "pillow" if PIL_AVAILABLE else "hash",
        "threshold": threshold,
        "total": len(results),
        "failures": failures,
        "results": [
            {
                "file": item.file,
                "existsInBaseline": item.exists_in_baseline,
                "existsInCurrent": item.exists_in_current,
                "equal": item.equal,
                "diffRatio": round(item.diff_ratio, 8),
                "mode": item.mode,
            }
            for item in results
        ],
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare screenshot directories for visual regression.")
    parser.add_argument("--baseline-dir", required=True, help="Baseline images directory.")
    parser.add_argument("--current-dir", required=True, help="Current images directory.")
    parser.add_argument("--diff-dir", required=True, help="Output diff directory.")
    parser.add_argument("--threshold", type=float, default=0.0, help="Allowed diff ratio.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compare_directories(
        baseline_dir=Path(args.baseline_dir).resolve(),
        current_dir=Path(args.current_dir).resolve(),
        diff_dir=Path(args.diff_dir).resolve(),
        threshold=max(0.0, min(1.0, args.threshold)),
    )
    if args.json:
        print(dump_json(payload), end="")
    else:
        print(
            f"[compare] total={payload['total']} failures={payload['failures']} "
            f"mode={payload['mode']} threshold={payload['threshold']}"
        )
    return 0 if payload["failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
