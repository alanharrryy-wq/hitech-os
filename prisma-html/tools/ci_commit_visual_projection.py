#!/usr/bin/env python3
"""Commit generated PRISMA visual projection outputs safely from CI.

This helper intentionally refuses to stage or push GitHub workflow changes. It exists
because GitHub Actions' token can be rejected when a generated commit also edits
`.github/workflows/**`, even when ordinary repository contents are writable.

The tool derives the generated-file allowlist from the Tablet runtime manifest,
adds the two RIFAT integrity manifests, stages only those files, proves the remote
branch has not moved, commits, pushes fast-forward only, and verifies the remote
head after push. If nothing changed it exits successfully without creating a commit.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

SCRIPT_PATH = Path(__file__).resolve()
PRISMA_HTML_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = PRISMA_HTML_ROOT.parent
RUNTIME_MANIFEST = (
    REPO_ROOT
    / "apps"
    / "terminal-de-venta-system"
    / "products"
    / "tablet"
    / "app"
    / "generated"
    / "prisma-visual-runtime"
    / "runtime-manifest.json"
)

STATIC_ALLOWED = {
    "apps/terminal-de-venta-system/.prisma-ui/AUTHORITY_LOCK.json",
    "apps/terminal-de-venta-system/products/tablet/app/generated/prisma-visual-runtime/authority-lock.json",
    "apps/terminal-de-venta-system/products/tablet/app/generated/prisma-visual-runtime/runtime-manifest.json",
    "prisma-html/FILES_MANIFEST.json",
    "prisma-html/authority/rifat/visual-source-manifest.json",
}
FORBIDDEN_PREFIXES = (".github/workflows/",)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def status_paths() -> list[str]:
    result = git("status", "--porcelain=v1")
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        rel = line[3:].strip()
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        paths.append(normalize(rel))
    return sorted(set(paths))


def allowed_paths() -> set[str]:
    if not RUNTIME_MANIFEST.is_file():
        raise RuntimeError(f"RUNTIME_MANIFEST_MISSING:{RUNTIME_MANIFEST.relative_to(REPO_ROOT)}")
    doc = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
    files = doc.get("files")
    if not isinstance(files, list):
        raise RuntimeError("RUNTIME_MANIFEST_FILES_INVALID")
    allowed = set(STATIC_ALLOWED)
    for row in files:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("RUNTIME_MANIFEST_FILE_ROW_INVALID")
        allowed.add(normalize(row["path"]))
    return allowed


def remote_head(branch: str) -> str:
    ref = f"refs/heads/{branch}"
    result = git("ls-remote", "--heads", "origin", ref)
    rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
    if len(rows) != 1 or len(rows[0]) < 2 or rows[0][1] != ref:
        raise RuntimeError(f"REMOTE_BRANCH_RESOLUTION_FAILED:{branch}")
    return rows[0][0].lower()


def write_report(path: Path | None, payload: dict[str, object]) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text, end="")


def stage(paths: Iterable[str]) -> None:
    selected = list(paths)
    if not selected:
        return
    git("add", "--", *selected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--message", default="chore(visual): commit deterministic Tablet projection")
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    report_path = Path(args.report).resolve() if args.report else None
    expected = args.expected_head.strip().lower()
    branch = args.branch.strip()
    payload: dict[str, object] = {
        "schema": "prisma.visual-projection-ci-commit.v1",
        "status": "STARTED",
        "expectedHead": expected,
        "branch": branch,
    }

    try:
        local = git("rev-parse", "HEAD").stdout.strip().lower()
        if local != expected:
            raise RuntimeError(f"LOCAL_HEAD_DRIFT:{local}!={expected}")

        remote_before = remote_head(branch)
        if remote_before != expected:
            raise RuntimeError(f"REMOTE_HEAD_DRIFT:{remote_before}!={expected}")

        changed = status_paths()
        forbidden = [p for p in changed if p.startswith(FORBIDDEN_PREFIXES)]
        if forbidden:
            raise RuntimeError("BLOCKED_WORKFLOW_SELF_MUTATION:" + ",".join(forbidden))

        allowed = allowed_paths()
        unexpected = sorted(set(changed) - allowed)
        if unexpected:
            raise RuntimeError("UNEXPECTED_PROJECTION_MUTATION:" + ",".join(unexpected))

        stage(changed)
        cached = git("diff", "--cached", "--name-only").stdout.splitlines()
        cached = [normalize(p) for p in cached if p.strip()]
        cached_forbidden = [p for p in cached if p.startswith(FORBIDDEN_PREFIXES)]
        if cached_forbidden:
            raise RuntimeError("BLOCKED_STAGED_WORKFLOW_MUTATION:" + ",".join(cached_forbidden))

        if not cached:
            payload.update(
                {
                    "status": "PASS_NOOP_PROJECTION_ALREADY_MATERIALIZED",
                    "remoteHead": remote_before,
                    "changed": [],
                }
            )
            write_report(report_path, payload)
            return 0

        git("diff", "--cached", "--check")
        git("config", "user.name", "prisma-visual-projection[bot]")
        git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
        git("commit", "-m", args.message)
        final = git("rev-parse", "HEAD").stdout.strip().lower()

        remote_pre_push = remote_head(branch)
        if remote_pre_push != expected:
            raise RuntimeError(f"REMOTE_HEAD_MOVED_BEFORE_PUSH:{remote_pre_push}!={expected}")

        push = git("push", "--porcelain", "origin", f"HEAD:refs/heads/{branch}", check=False)
        if push.returncode != 0:
            detail = (push.stderr or push.stdout).strip().replace("\n", " | ")
            raise RuntimeError(f"PROJECTION_PUSH_FAILED:{detail}")

        remote_after = remote_head(branch)
        if remote_after != final:
            raise RuntimeError(f"REMOTE_POST_PUSH_MISMATCH:{remote_after}!={final}")

        payload.update(
            {
                "status": "PASS_PROJECTION_COMMITTED_AND_PUSHED",
                "sourceHead": expected,
                "finalHead": final,
                "changed": cached,
            }
        )
        write_report(report_path, payload)
        return 0
    except Exception as exc:
        payload.update({"status": "FAIL", "error": str(exc), "changed": status_paths()})
        write_report(report_path, payload)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
