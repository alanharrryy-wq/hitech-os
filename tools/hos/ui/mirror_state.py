#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
from pathlib import Path

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_text import write_text

MIRROR_HELPER_TS = """export type MirrorListener<TValue> = (value: TValue, source: string) => void;

export interface MirrorState<TValue> {
  readonly value: TValue;
  readonly source: string;
  readonly updatedAt: string;
}

export interface MirrorStore<TValue> {
  getState(): MirrorState<TValue>;
  setValue(value: TValue, source: string): void;
  patch(transform: (current: TValue) => TValue, source: string): void;
  subscribe(listener: MirrorListener<TValue>): () => void;
}

export function createMirrorStore<TValue>(
  initialValue: TValue,
  initialSource = "init"
): MirrorStore<TValue> {
  let state: MirrorState<TValue> = {
    value: initialValue,
    source: initialSource,
    updatedAt: new Date(0).toISOString()
  };
  const listeners = new Set<MirrorListener<TValue>>();

  function emit(): void {
    const snapshot = state;
    for (const listener of listeners) {
      listener(snapshot.value, snapshot.source);
    }
  }

  function setValue(value: TValue, source: string): void {
    state = {
      value,
      source,
      updatedAt: new Date().toISOString()
    };
    emit();
  }

  function patch(transform: (current: TValue) => TValue, source: string): void {
    setValue(transform(state.value), source);
  }

  function getState(): MirrorState<TValue> {
    return state;
  }

  function subscribe(listener: MirrorListener<TValue>): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }

  return {
    getState,
    setValue,
    patch,
    subscribe
  };
}
"""


MIRROR_DEMO_TS = """import { createMirrorStore } from "./mirror-store";

const store = createMirrorStore("", "initial-input");

const unsubscribe = store.subscribe((value, source) => {
  console.log(`[mirror] source=${source} value=${value}`);
});

store.setValue("first", "input-a");
store.patch((current) => current.toUpperCase(), "input-b");

unsubscribe();
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate mirror-input state helpers.")
    parser.add_argument(
        "--out-dir",
        default="tools/_local/ui_scaffold/mirror",
        help="Output directory for generated mirror helpers.",
    )
    parser.add_argument("--with-demo", action="store_true", help="Emit usage demo file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (repo_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    mirror_file = out_dir / "mirror-store.ts"
    write_text(mirror_file, MIRROR_HELPER_TS, trailing_newline=True)
    print(f"[mirror_state] wrote {mirror_file.as_posix()}")

    if args.with_demo:
        demo_file = out_dir / "mirror-demo.ts"
        write_text(demo_file, MIRROR_DEMO_TS, trailing_newline=True)
        print(f"[mirror_state] wrote {demo_file.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
