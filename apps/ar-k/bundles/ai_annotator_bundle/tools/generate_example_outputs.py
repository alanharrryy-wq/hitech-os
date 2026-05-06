
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.example_builder import generate_outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--limit', type=int, default=18)
    ns = parser.parse_args()
    summary = generate_outputs(Path(ns.output_dir), limit=ns.limit)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
