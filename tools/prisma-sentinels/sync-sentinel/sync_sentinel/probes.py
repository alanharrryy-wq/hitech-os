from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .model import Check, Verdict
from .registry import CANONICAL_AUTHORITY_PATHS, STATIC_PROBES, SYNC_SOURCE_PATHS
from .safety import command_exists, git_head, run


def authority_presence(repo: Path) -> Check:
    missing = [p.as_posix() for p in CANONICAL_AUTHORITY_PATHS if not (repo / p).is_file()]
    if missing:
        return Check("authority_presence", Verdict.BLOCKED, "required authority files are missing", {"missing": missing})
    return Check("authority_presence", Verdict.PASS, "required authority files are present")


def sync_source_presence(repo: Path) -> Check:
    missing = [p.as_posix() for p in SYNC_SOURCE_PATHS if not (repo / p).is_file()]
    if missing:
        return Check("sync_source_presence", Verdict.BLOCKED, "sync source evidence is incomplete", {"missing": missing})
    return Check("sync_source_presence", Verdict.PASS, "Tablet↔PC canonical sync evidence paths are present")


def toolchain_presence() -> Check:
    required = ["git", "python", "node", "pnpm"]
    state = {name: command_exists(name) for name in required}
    missing = [name for name, ok in state.items() if not ok]
    if missing:
        return Check("toolchain_presence", Verdict.BLOCKED, "required local toolchain is incomplete", {"tools": state, "missing": missing})
    return Check("toolchain_presence", Verdict.PASS, "required toolchain commands are available", {"tools": state})


def run_static_probe(repo: Path, spec: dict) -> Check:
    cwd = repo / spec["cwd"]
    try:
        cp = run(spec["cmd"], cwd=cwd, timeout=180)
    except Exception as exc:
        return Check(spec["id"], Verdict.UNKNOWN, f"probe raised {type(exc).__name__}: {exc}")
    text = (cp.stdout or "") + "\n" + (cp.stderr or "")
    if cp.returncode == 0 and spec["pass_token"] in text:
        return Check(spec["id"], Verdict.PASS, "native verifier passed", {"returncode": cp.returncode, "tail": text[-1800:]})
    if cp.returncode == 0:
        return Check(spec["id"], Verdict.UNKNOWN, "native verifier exited zero without its canonical PASS token", {"tail": text[-1800:]})
    return Check(spec["id"], Verdict.FAIL, "native verifier failed", {"returncode": cp.returncode, "tail": text[-2600:]})


def static_probe_suite(repo: Path, workers: int = 3) -> list[Check]:
    out: list[Check] = []
    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(STATIC_PROBES)))) as pool:
        future_map = {pool.submit(run_static_probe, repo, spec): spec for spec in STATIC_PROBES}
        for fut in as_completed(future_map):
            out.append(fut.result())
    return sorted(out, key=lambda c: c.id)


def head_check(repo: Path, expected: str | None = None) -> Check:
    head = git_head(repo)
    if expected and head != expected:
        return Check("head_lock", Verdict.BLOCKED, "repository HEAD does not match expected certification HEAD", {"head": head, "expected": expected})
    return Check("head_lock", Verdict.PASS, "repository HEAD is locked", {"head": head})
