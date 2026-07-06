from __future__ import annotations

import json
import fnmatch
import subprocess
from pathlib import Path
from copy import deepcopy

DEFAULT_POLICY = {
    "schema": "autogit.ag98_policy.v1",
    "description": "Repo-specific operational policy for AutoGit 98 upgrades.",
    "allow_sensitive_named_evidence_globs": [
        "apps/terminal-de-venta-system/docs/ops/licscope/PII_SECRET_SAFETY_MATRIX.*",
        "apps/terminal-de-venta-system/docs/ops/licscope/SECRET_EXPOSURE_RULES.md",
        "apps/terminal-de-venta-system/docs/ops/licscope/live_smoke_outputs/live-pii-secret-safety.*",
        "apps/terminal-de-venta-system/docs/ops/licscope/matrices/PII_SECRET_SAFETY_MATRIX.*",
        "apps/terminal-de-venta-system/docs/ops/licscope/verifier_outputs/verify-pii-secret-safety.*"
    ],
    "runtime_noise_globs": [
        "**/*.db-wal",
        "**/*.db-shm",
        "**/*.sqlite-wal",
        "**/*.sqlite-shm",
        "**/.wrangler/**",
        "**/.cache/**",
        "**/node_modules/**",
        "**/.next/**",
        "**/.turbo/**"
    ],
    "generated_at_only_globs": [
        "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/runtime/prisma-lab-port-override.json",
        "**/internal/runtime/*override*.json",
        "**/runtime/*override*.json"
    ],
    "safe_self_heal_extensions": [".md", ".markdown", ".txt", ".json", ".csv", ".yml", ".yaml"],
    "commit_groups": [
        {"group": "tooling/autogit", "globs": ["autogit/**"]},
        {"group": "docs/licscope-evidence", "globs": ["apps/terminal-de-venta-system/docs/ops/licscope/**"]},
        {"group": "docs/ops-manual", "globs": ["apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md", "apps/terminal-de-venta-system/docs/ops/**/*.md"]},
        {"group": "tooling/code-atlas", "globs": ["tools/code-atlas/**", "**/code_atlas/**"]},
        {"group": "deps", "globs": ["**/package.json", "**/pnpm-lock.yaml", "**/package-lock.json", "**/yarn.lock"]},
        {"group": "app-surfaces", "globs": ["apps/**", "products/**"]},
        {"group": "tooling", "globs": ["tools/**", "scripts/**", "**/*.py", "**/*.ps1", "**/*.cmd", "**/*.bat"]}
    ],
    "messages": {
        "tooling/autogit": "chore(autogit): upgrade AutoGit flight control",
        "docs/licscope-evidence": "docs(licscope): update operational evidence",
        "docs/ops-manual": "docs(prisma): update operational runbooks",
        "tooling/code-atlas": "feat(code-atlas): update operational atlas tooling",
        "deps": "chore(deps): update package metadata",
        "app-surfaces": "feat(prisma): update app surfaces",
        "tooling": "chore(prisma): update tooling",
        "docs": "docs(prisma): update documentation",
        "misc": "chore(prisma): update remaining files"
    },
    "order": [
        "tooling/autogit",
        "docs/licscope-evidence",
        "docs/ops-manual",
        "tooling/code-atlas",
        "deps",
        "app-surfaces",
        "tooling",
        "docs",
        "assets",
        "misc"
    ]
}

def normalize_rel(rel: str) -> str:
    return str(rel or "").replace("\\", "/").strip("/")

def _matches(rel: str, patterns: list[str]) -> bool:
    rel_l = normalize_rel(rel).lower()
    for pat in patterns or []:
        pat_l = normalize_rel(pat).lower()
        if fnmatch.fnmatch(rel_l, pat_l):
            return True
        if pat_l.startswith("**/") and fnmatch.fnmatch(rel_l, pat_l[3:]):
            return True
    return False

def _deep_merge(base: dict, override: dict) -> dict:
    out = deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_policy(repo: Path | str | None = None) -> dict:
    repo = Path(repo) if repo else Path.cwd()
    policy = deepcopy(DEFAULT_POLICY)
    cfg = repo / "autogit" / "config" / "autogit_98_policy.json"
    if cfg.exists():
        try:
            loaded = json.loads(cfg.read_text(encoding="utf-8"))
            policy = _deep_merge(policy, loaded)
        except Exception as exc:
            policy.setdefault("policy_load_warnings", []).append(f"Could not load {cfg}: {exc!r}")
    return policy

def is_sensitive_named_evidence_allowed(repo: Path | str, rel: str) -> bool:
    policy = load_policy(repo)
    return _matches(rel, policy.get("allow_sensitive_named_evidence_globs", []))

def classify_commit_group(repo_or_rel, rel: str | None = None) -> str | None:
    # Accept classify_commit_group(rel) and classify_commit_group(repo, rel).
    if rel is None:
        rel = str(repo_or_rel)
        repo = Path.cwd()
    else:
        repo = Path(repo_or_rel)
    policy = load_policy(repo)
    for entry in policy.get("commit_groups", []):
        if _matches(rel, entry.get("globs", [])):
            return entry.get("group")
    return None

def messages_and_order(repo: Path | str | None = None) -> tuple[dict, list[str]]:
    policy = load_policy(repo or Path.cwd())
    return dict(policy.get("messages", {})), list(policy.get("order", []))

def is_runtime_noise(repo: Path | str, rel: str) -> bool:
    policy = load_policy(repo)
    return _matches(rel, policy.get("runtime_noise_globs", []))

def _git_diff(repo: Path, rel: str) -> str:
    cp = subprocess.run(["git", "diff", "--", rel], cwd=str(repo), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    return cp.stdout or ""

def is_generated_at_only_diff(repo: Path | str, rel: str) -> bool:
    repo = Path(repo)
    policy = load_policy(repo)
    if not _matches(rel, policy.get("generated_at_only_globs", [])):
        return False
    diff = _git_diff(repo, rel)
    if not diff.strip():
        return False
    changed = []
    for line in diff.splitlines():
        if line.startswith(("diff --git", "index ", "--- ", "+++ ", "@@")):
            continue
        if line.startswith("+") or line.startswith("-"):
            changed.append(line)
    return bool(changed) and all('"generatedAt"' in line or "'generatedAt'" in line for line in changed)

def classify_preflight_path(repo: Path | str, rel: str) -> dict:
    repo = Path(repo)
    rel = normalize_rel(rel)
    if is_runtime_noise(repo, rel):
        return {"path": rel, "decision": "EXCLUDE_SAFE", "kind": "runtime_noise", "detail": "runtime/cache/noise path excluded from commit planning"}
    if is_generated_at_only_diff(repo, rel):
        return {"path": rel, "decision": "EXCLUDE_SAFE", "kind": "generated_at_only", "detail": "only generatedAt changed in runtime override"}
    return {"path": rel, "decision": "COMMITTABLE", "kind": "normal", "detail": "eligible for normal AutoGit planning"}

def safe_self_heal_extensions(repo: Path | str | None = None) -> set[str]:
    policy = load_policy(repo or Path.cwd())
    return set(str(x).lower() for x in policy.get("safe_self_heal_extensions", []))
