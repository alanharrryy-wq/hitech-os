from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# AG98_IMPORT_BLOCK_V1
try:
    from .ag98_policy import (
        is_sensitive_named_evidence_allowed as ag98_is_sensitive_named_evidence_allowed,
        classify_commit_group as ag98_classify_commit_group,
        messages_and_order as ag98_messages_and_order,
    )
    from .ag98_runtime import filter_changed_paths as ag98_filter_changed_paths
    from .ag98_selfheal import autofix_staged_whitespace as ag98_autofix_staged_whitespace
    from .ag98_dashboard import (
        write_plan_dashboard as ag98_write_plan_dashboard,
        write_apply_dashboard as ag98_write_apply_dashboard,
        write_ci_decision as ag98_write_ci_decision,
    )
except Exception:
    def ag98_is_sensitive_named_evidence_allowed(repo, rel): return False
    def ag98_classify_commit_group(rel): return None
    def ag98_messages_and_order(repo=None): return ({}, [])
    def ag98_filter_changed_paths(repo, runner, changed_paths, report=None):
        return {"committable_paths": changed_paths, "excluded": [], "blockers": [], "warnings": []}
    def ag98_autofix_staged_whitespace(repo, runner, report, group_paths=None):
        return {"ok": False, "fixed": [], "skipped": [], "disabled": True}
    def ag98_write_plan_dashboard(*args, **kwargs): return None
    def ag98_write_apply_dashboard(*args, **kwargs): return None
    def ag98_write_ci_decision(*args, **kwargs): return None
# /AG98_IMPORT_BLOCK_V1

# AG100_IMPORT_BLOCK_V1
try:
    from .ag100_learning import (
        json_text_for_validation as ag100_json_text_for_validation,
        autofix_staged_whitespace as ag100_autofix_staged_whitespace,
        capture_failure_context as ag100_capture_failure_context,
        write_group_checkpoint as ag100_write_group_checkpoint,
        write_post_run_hygiene_report as ag100_write_post_run_hygiene_report,
        # AG100_POST_RUN_HYGIENE_V1 marker: post-run hygiene report is wired into apply/merge summaries.
    )
except Exception:
    def ag100_json_text_for_validation(path, max_text_bytes=2 * 1024 * 1024, max_json_bytes=None):
        p = Path(path)
        if not p.exists() or not p.is_file():
            return ""
        try:
            limit = max_json_bytes or max(max_text_bytes * 64, 64 * 1024 * 1024)
            if p.stat().st_size > limit:
                return ""
            return p.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
    def ag100_autofix_staged_whitespace(repo, runner, report, group_paths=None, label=None):
        return ag98_autofix_staged_whitespace(repo, runner, report, group_paths)
    def ag100_capture_failure_context(*args, **kwargs):
        return None
    def ag100_write_group_checkpoint(*args, **kwargs):
        return None
    def ag100_write_post_run_hygiene_report(*args, **kwargs):
        return None
# /AG100_IMPORT_BLOCK_V1



SCHEMA = "autogit.flight_control.v2"
DEFAULT_OUT = Path(r"F:\descargasf")
PROTECTED_BRANCHES = {"main", "master", "prod", "production", "release"}
MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_DIFF_BYTES = 24 * 1024 * 1024
MAX_WORKERS = 18
SECRET_PATTERNS = [
    ("github_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("ghp", re.compile(r"ghp_[A-Za-z0-9_]{20,}")),
    ("openai_key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY-----")),
    ("cloudflare_token", re.compile(r"(?i)cloudflare[_-]?(?:api)?[_-]?token\s*[:=]\s*['\"]?[A-Za-z0-9_\-.]{20,}")),
]
SENSITIVE_NAMES = {".env", ".env.local", ".env.production", ".env.development", "id_rsa", "id_dsa", "credentials.json", "secrets.json"}
LOCK_NAMES = {"pnpm-lock.yaml", "package-lock.json", "yarn.lock", "bun.lockb"}
PKG_NAMES = {"package.json"}
TEXT_EXTS = {".ps1", ".psm1", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".md", ".css", ".html", ".yml", ".yaml", ".cmd", ".bat", ".txt"}

class FlightError(RuntimeError):
    pass

class Runner:
    def __init__(self, repo: Path, report: Path):
        self.repo = repo
        self.report = report
        self.logs = report / "logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.counter = 0
    def run(self, args, *, cwd=None, timeout=120, check=False, name=None, stdin=None):
        self.counter += 1
        name = name or f"cmd_{self.counter:04d}"
        log = self.logs / f"{self.counter:04d}_{safe_name(name)}.txt"
        payload = {"args": list(map(str,args)), "cwd": str(cwd or self.repo), "timeout": timeout, "started": dt.datetime.now().isoformat()}
        try:
            cp = subprocess.run(list(map(str,args)), cwd=str(cwd or self.repo), input=stdin, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            payload.update({"returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr, "finished": dt.datetime.now().isoformat()})
            log.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            if check and cp.returncode != 0:
                raise FlightError(f"Command failed [{name}] code={cp.returncode}: {' '.join(map(str,args))}\n{cp.stderr or cp.stdout}")
            return cp
        except subprocess.TimeoutExpired as exc:
            payload.update({"timeout_expired": True, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "finished": dt.datetime.now().isoformat()})
            log.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            raise FlightError(f"Command timeout [{name}] after {timeout}s: {' '.join(map(str,args))}")

def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s)[:90] or "item"

def progress(pct: int, msg: str):
    width = 28
    done = int(width * pct / 100)
    bar = "#" * done + "-" * (width - done)
    print(f"[{pct:3d}%] [{bar}] {msg} | restante {100-pct}%", flush=True)

def now_stamp():
    return dt.datetime.now().strftime("%d%m %H%M%S")

def ensure_repo(path: Path) -> Path:
    path = path.resolve()
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(path), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise FlightError(f"No pude detectar Git root desde {path}: {r.stderr}")
    return Path(r.stdout.strip()).resolve()

def sha256_file(p: Path) -> str | None:
    if not p.exists() or not p.is_file(): return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def text_or_empty(p: Path) -> str:
    if not p.exists() or not p.is_file(): return ""
    try:
        if p.stat().st_size > MAX_TEXT_BYTES: return ""
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
# AG98_JSON_VALIDATION_LARGE_JSON_V1
def json_text_for_validation(p: Path) -> str:
    # AG100_LARGE_JSON_VALIDATION_V1
    # Validate real working-tree JSON files without the small evidence-text cap.
    # This prevents false blockers for large Code Atlas registers such as
    # PATH_ROLE_INDEX.json while keeping text_or_empty() capped for snapshots.
    return ag100_json_text_for_validation(p, max_text_bytes=MAX_TEXT_BYTES)
# /AG100_LARGE_JSON_VALIDATION_V1

def is_text_path(rel: str) -> bool:
    return Path(rel).suffix.lower() in TEXT_EXTS or Path(rel).name in {"package.json", "pnpm-lock.yaml", "yarn.lock"}

def is_sensitive_name(rel: str) -> bool:
    name = Path(rel).name.lower()
    return name in SENSITIVE_NAMES or name.startswith(".env") or "secret" in name or "credential" in name or "token" in name

def sanitize_remote_text(text: str) -> str:
    text = re.sub(r"https://([^/@:\s]+):([^/@\s]+)@", r"https://<USER>:<TOKEN>@", text)
    text = re.sub(r"(ghp|github_pat|glpat|sk-(?:proj-)?)\S+", "<TOKEN_REDACTED>", text)
    return text

def parse_status_z(raw: str):
    out=[]; parts=raw.split("\0"); i=0
    while i < len(parts):
        e=parts[i]
        if not e:
            i+=1; continue
        st=e[:2]; path=e[3:] if len(e)>3 else ""
        if st[:1] in {"R","C"}:
            old=path; i+=1; new=parts[i] if i < len(parts) else ""
            out.append({"status": st, "path": new.replace('\\','/'), "old_path": old.replace('\\','/')})
        else:
            out.append({"status": st, "path": path.replace('\\','/')})
        i+=1
    return out

def classify_path(rel: str) -> str:
    # AG98_CLASSIFY_GROUP_HOOK_V1
    try:
        _ag98_group = ag98_classify_commit_group(rel)
        if _ag98_group:
            return _ag98_group
    except Exception:
        pass
    p = rel.replace('\\','/')
    name = Path(p).name.lower()
    if name in LOCK_NAMES or name in PKG_NAMES:
        return "deps"
    if p.startswith("autogit/"):
        return "tooling/autogit"
    if "prisma-control-center/internal/wrappers" in p or "PRISMA VSCode Menu" in p:
        return "control-center/wrappers"
    if "3160" in p or "cloud_command_center" in p:
        return "control-center/3160-runtime"
    if p.startswith("docs/") or p.endswith(".md"):
        return "docs"
    if p.startswith("apps/terminal-de-venta-system/prisma-control-center/"):
        return "control-center"
    if p.startswith("apps/") or p.startswith("products/"):
        return "app-surfaces"
    if p.startswith("tools/") or p.endswith((".ps1",".py",".cmd",".bat")):
        return "tooling"
    if re.search(r"\.(png|jpg|jpeg|webp|gif|svg|ico|mp4|mov|woff2?)$", p, re.I):
        return "assets"
    return "misc"

MESSAGE_BY_GROUP = {
    "tooling/autogit": "chore(autogit): upgrade flight-control workflow",
    "control-center/wrappers": "fix(control-center): stabilize launcher wrappers",
    "control-center/3160-runtime": "fix(control-center): stabilize cloud command center 3160",
    "control-center": "feat(control-center): update control center workflow",
    "docs": "docs(prisma): update operational documentation",
    "deps": "chore(deps): update package metadata",
    "app-surfaces": "feat(prisma): update app surfaces",
    "tooling": "chore(prisma): update tooling",
    "assets": "chore(assets): update visual assets",
    "misc": "chore(prisma): update remaining files",
}
ORDER = ["tooling/autogit", "control-center/wrappers", "control-center/3160-runtime", "control-center", "docs", "deps", "app-surfaces", "tooling", "assets", "misc"]


# AG98_ORDER_MESSAGE_OVERRIDE_V1
try:
    _ag98_messages, _ag98_order = ag98_messages_and_order()
    MESSAGE_BY_GROUP.update(_ag98_messages)
    if _ag98_order:
        ORDER = _ag98_order + [g for g in ORDER if g not in _ag98_order]
except Exception:
    pass
# /AG98_ORDER_MESSAGE_OVERRIDE_V1

def read_json(p: Path):
    try: return json.loads(json_text_for_validation(p))
    except Exception: return None

def version_tuple(v: str):
    s = re.sub(r"^[~^<>=\s]+", "", str(v or ""))
    m = re.match(r"(\d+)\.(\d+)\.(\d+)", s)
    if not m: return None
    return tuple(map(int, m.groups()))

def collect_package_downgrades(repo: Path, runner: Runner, changed_paths: list[str]):
    findings=[]
    for rel in changed_paths:
        if Path(rel).name != "package.json": continue
        cur = read_json(repo/rel)
        head = runner.run(["git", "show", f"HEAD:{rel}"], timeout=60, name=f"git_show_HEAD_{safe_name(rel)}")
        try: old = json.loads(head.stdout) if head.returncode == 0 and head.stdout.strip() else None
        except Exception: old = None
        if not cur or not old: continue
        for section in ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]:
            cdeps = cur.get(section) or {}; odeps = old.get(section) or {}
            for name, newv in cdeps.items():
                if name not in odeps: continue
                ov = odeps.get(name)
                ot = version_tuple(ov); nt = version_tuple(newv)
                if ot and nt and nt < ot:
                    findings.append({"path": rel, "section": section, "package": name, "old": ov, "new": newv, "severity": "BLOCKER", "reason": "possible_dependency_downgrade"})
    return findings


# AUTOGIT_PRISMA_LICSCOPE_SENSITIVE_EVIDENCE_ALLOWLIST_V3
AUTOGIT_PRISMA_LICSCOPE_SENSITIVE_EVIDENCE_ALLOWLIST_V3 = {
    'apps/terminal-de-venta-system/docs/ops/licscope/PII_SECRET_SAFETY_MATRIX.csv',
    'apps/terminal-de-venta-system/docs/ops/licscope/PII_SECRET_SAFETY_MATRIX.json',
    'apps/terminal-de-venta-system/docs/ops/licscope/PII_SECRET_SAFETY_MATRIX.md',
    'apps/terminal-de-venta-system/docs/ops/licscope/SECRET_EXPOSURE_RULES.md',
    'apps/terminal-de-venta-system/docs/ops/licscope/live_smoke_outputs/live-pii-secret-safety.json',
    'apps/terminal-de-venta-system/docs/ops/licscope/live_smoke_outputs/live-pii-secret-safety.md',
    'apps/terminal-de-venta-system/docs/ops/licscope/matrices/PII_SECRET_SAFETY_MATRIX.csv',
    'apps/terminal-de-venta-system/docs/ops/licscope/matrices/PII_SECRET_SAFETY_MATRIX.json',
    'apps/terminal-de-venta-system/docs/ops/licscope/matrices/PII_SECRET_SAFETY_MATRIX.md',
    'apps/terminal-de-venta-system/docs/ops/licscope/verifier_outputs/verify-pii-secret-safety.json',
    'apps/terminal-de-venta-system/docs/ops/licscope/verifier_outputs/verify-pii-secret-safety.md',
}

def autogit_prisma_licscope_sensitive_evidence_allowed_v3(rel: str) -> bool:
    normalized = str(rel).replace("\\", "/")
    return normalized in AUTOGIT_PRISMA_LICSCOPE_SENSITIVE_EVIDENCE_ALLOWLIST_V3

def secret_scan_file(repo: Path, rel: str):
    p = repo / rel
    # AG98_SENSITIVE_POLICY_HOOK_V1
    try:
        ag98_sensitive_allowlisted = ag98_is_sensitive_named_evidence_allowed(repo, rel)
    except Exception:
        ag98_sensitive_allowlisted = False
    if not p.exists() or not p.is_file(): return []
    allowlisted_sensitive_evidence = autogit_prisma_licscope_sensitive_evidence_allowed_v3(rel)
    if is_sensitive_name(rel) and not ((allowlisted_sensitive_evidence) or ag98_sensitive_allowlisted):
        return [{"path": rel, "severity": "BLOCKER", "kind": "sensitive_filename", "detail": "Sensitive filename changed; review manually."}]
    if not is_text_path(rel) or p.stat().st_size > MAX_TEXT_BYTES: return []
    text = text_or_empty(p)
    rows=[]
    for name, rx in SECRET_PATTERNS:
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            rows.append({"path": rel, "severity": "BLOCKER", "kind": name, "line": line, "detail": "secret-like token pattern"})
    if allowlisted_sensitive_evidence and rows:
        for row in rows:
            row["detail"] = "allowlisted PRISMA licscope safety evidence failed content secret scan"
    return rows

def write_ps_parse_tool(report: Path) -> Path:
    """Create a robust PowerShell parser helper.

    Important: do not use `powershell -Command ... $args[0] ...` for file paths.
    On Windows/PowerShell, complex command-line parsing can split or mangle paths
    with spaces. Use `-File` with a named parameter instead.
    """
    tools = report / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    script = tools / "parse_one.ps1"
    script.write_text("""
param(
  [Parameter(Mandatory=$true)]
  [string] $LiteralTargetPath
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $LiteralTargetPath -PathType Leaf)) {
  Write-Error ("file_not_found: {0}" -f $LiteralTargetPath)
  exit 1
}

$tokens = $null
$parseErrors = $null

try {
  [System.Management.Automation.Language.Parser]::ParseFile($LiteralTargetPath, [ref]$tokens, [ref]$parseErrors) | Out-Null
} catch {
  Write-Error ("parse_exception: {0}" -f $_.Exception.Message)
  exit 1
}

if (@($parseErrors).Count -gt 0) {
  foreach ($err in @($parseErrors)) {
    Write-Error ("{0}:{1} {2}" -f $err.Extent.StartLineNumber, $err.Extent.StartColumnNumber, $err.Message)
  }
  exit 1
}

Write-Output ("PARSE_OK: {0}" -f $LiteralTargetPath)
exit 0
""".lstrip(), encoding="utf-8")
    return script


def validate_changed_files(repo: Path, runner: Runner, changed_paths: list[str], report: Path):
    validations=[]; blockers=[]; warnings=[]
    diffcheck = runner.run(["git","diff","--check"], timeout=180, name="git_diff_check")
    validations.append({"name":"git diff --check", "ok": diffcheck.returncode == 0, "stdout": diffcheck.stdout[-4000:], "stderr": diffcheck.stderr[-4000:]})
    if diffcheck.returncode != 0:
        blockers.append({"severity":"BLOCKER", "kind":"whitespace_or_conflict_marker", "detail":"git diff --check failed"})

    ps_parse_tool = write_ps_parse_tool(report) if os.name == "nt" and shutil.which("powershell.exe") else None

    def one(rel):
        rows=[]
        p=repo/rel
        if not p.exists() or not p.is_file(): return rows
        suf=p.suffix.lower(); name=p.name.lower()
        if suf == ".json" or name == "package.json":
            try:
                json.loads(json_text_for_validation(p))
                rows.append({"path":rel,"check":"json_parse","ok":True})
            except Exception as e:
                rows.append({"path":rel,"check":"json_parse","ok":False,"error":repr(e)})
        if suf == ".py":
            cp = runner.run([sys.executable, "-m", "py_compile", str(p)], timeout=120, name=f"py_compile_{safe_name(rel)}")
            rows.append({"path":rel,"check":"py_compile","ok":cp.returncode==0,"stderr":cp.stderr[-2000:]})
        if suf in {".js", ".mjs", ".cjs"} and shutil.which("node"):
            cp = runner.run(["node", "--check", str(p)], timeout=120, name=f"node_check_{safe_name(rel)}")
            rows.append({"path":rel,"check":"node_check","ok":cp.returncode==0,"stderr":cp.stderr[-2000:]})
        if suf in {".ps1", ".psm1"}:
            if ps_parse_tool:
                cp = runner.run([
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ps_parse_tool),
                    "-LiteralTargetPath",
                    str(p),
                ], timeout=120, name=f"ps_parse_{safe_name(rel)}")
                rows.append({
                    "path": rel,
                    "check": "powershell_parse",
                    "ok": cp.returncode == 0,
                    "stdout": cp.stdout[-2000:],
                    "stderr": cp.stderr[-2000:],
                })
            else:
                rows.append({"path":rel,"check":"powershell_parse","ok":None,"reason":"not_windows_or_no_powershell"})
        return rows
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs=[ex.submit(one, rel) for rel in changed_paths]
        for fut in as_completed(futs):
            for row in fut.result():
                validations.append(row)
                if row.get("ok") is False:
                    blockers.append({"severity":"BLOCKER", "kind": row.get("check"), "path": row.get("path"), "detail": row.get("error") or row.get("stderr")})
    return validations, blockers, warnings

def copy_evidence(repo: Path, changed_paths: list[str], report: Path, runner: Runner):
    cur_root=report/"current_files"; head_root=report/"head_preimage"
    cur_root.mkdir(parents=True, exist_ok=True); head_root.mkdir(parents=True, exist_ok=True)
    rows=[]
    for rel in changed_paths:
        p=repo/rel
        item={"path": rel, "current_exists": p.exists(), "current_sha256": sha256_file(p) if p.exists() and p.is_file() else None}
        if p.exists() and p.is_file() and not is_sensitive_name(rel) and p.stat().st_size <= MAX_TEXT_BYTES*2:
            dest=cur_root/rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p,dest); item["current_copied"]=True
        else:
            item["current_copied"]=False
        show=runner.run(["git","show",f"HEAD:{rel}"], timeout=80, name=f"head_preimage_{safe_name(rel)}")
        if show.returncode == 0 and show.stdout:
            dest=head_root/rel; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(show.stdout, encoding="utf-8", errors="replace"); item["head_preimage_copied"]=True
        else:
            item["head_preimage_copied"]=False
        rows.append(item)
    (report/"evidence_files.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def make_zip(report: Path, zip_path: Path):
    if zip_path.exists(): zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in report.rglob("*"):
            if p.is_file(): z.write(p, p.relative_to(report).as_posix())


def build_plan(args):
    out = Path(args.out or DEFAULT_OUT); out.mkdir(parents=True, exist_ok=True)
    repo = ensure_repo(Path(args.repo))
    stamp = now_stamp()
    report = out / f"autogit plan {stamp}"
    report.mkdir(parents=True, exist_ok=True)
    runner = Runner(repo, report)
    progress(5, "Leyendo estado Git")
    head = runner.run(["git","rev-parse","HEAD"], check=True, name="git_head").stdout.strip()
    branch = runner.run(["git","branch","--show-current"], check=True, name="git_branch").stdout.strip()
    status_raw = runner.run(["git","status","--porcelain=v1","-z","--untracked-files=all"], check=True, name="git_status_z").stdout
    status = parse_status_z(status_raw)
    changed_paths = sorted({x.get("path") for x in status if x.get("path")})
    # AG98_RUNTIME_FILTER_HOOK_V1
    ag98_preflight_blockers = []
    ag98_preflight_warnings = []
    ag98_noise_summary = {"committable_paths": changed_paths, "excluded": [], "blockers": [], "warnings": []}
    try:
        ag98_noise_summary = ag98_filter_changed_paths(repo, runner, changed_paths, report)
        changed_paths = sorted(ag98_noise_summary.get("committable_paths", changed_paths))
        ag98_preflight_blockers.extend(ag98_noise_summary.get("blockers") or [])
        ag98_preflight_warnings.extend(ag98_noise_summary.get("warnings") or [])
    except Exception as ag98_exc:
        ag98_preflight_warnings.append({"severity": "WARNING", "kind": "ag98_runtime_filter_failed", "detail": repr(ag98_exc)})
    remote_text = sanitize_remote_text(runner.run(["git","remote","-v"], name="git_remotes").stdout)
    (report/"git_remote_sanitized.txt").write_text(remote_text, encoding="utf-8")
    (report/"git_status.json").write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
    diff = runner.run(["git","diff","--binary","HEAD"], timeout=180, name="git_diff_binary").stdout
    if len(diff.encode("utf-8", "replace")) <= MAX_DIFF_BYTES:
        (report/"diff.patch").write_text(diff, encoding="utf-8", errors="replace")
    else:
        (report/"diff_TOO_LARGE.txt").write_text(f"Diff too large: {len(diff)} chars", encoding="utf-8")
    progress(20, "Validando cambios")
    secret_rows=[]
    for rel in changed_paths:
        secret_rows.extend(secret_scan_file(repo, rel))
    downgrades = collect_package_downgrades(repo, runner, changed_paths)
    validations, vblockers, warnings = validate_changed_files(repo, runner, changed_paths, report)
    lock_changed=[p for p in changed_paths if Path(p).name in LOCK_NAMES]
    if lock_changed:
        warnings.append({"severity":"WARNING", "kind":"lockfile_changed", "paths": lock_changed, "detail":"Lockfile changed; no-downgrade review required before merge."})
    # AG98_PREFLIGHT_BLOCKERS_HOOK_V1
    warnings = [*ag98_preflight_warnings, *warnings]
    blockers = [*ag98_preflight_blockers, *secret_rows, *downgrades, *vblockers]
    progress(45, "Agrupando commits")
    groups={}
    for rel in changed_paths:
        groups.setdefault(classify_path(rel), []).append(rel)
    commit_groups=[]
    for group in ORDER + sorted(set(groups)-set(ORDER)):
        paths=sorted(groups.get(group, []))
        if not paths: continue
        msg = MESSAGE_BY_GROUP.get(group, f"chore(prisma): update {group}")
        commit_groups.append({"group":group,"message":msg,"paths":paths,"body":f"AutoGit Flight Control planned commit for {group}.\n\nTask: {args.task}\nFiles: {len(paths)}\n"})
    path_hashes={rel: sha256_file(repo/rel) for rel in changed_paths}
    progress(62, "Copiando evidencia segura")
    copy_evidence(repo, changed_paths, report, runner)
    plan = {
        "schema": SCHEMA,
        "created_at": dt.datetime.now().isoformat(),
        "task": args.task,
        "repo": str(repo),
        "base_branch": args.base,
        "head": head,
        "branch": branch,
        "status": status,
        "changed_paths": changed_paths,
        "path_hashes": path_hashes,
        "commit_groups": commit_groups,
        "validations": validations,
        "blockers": blockers,
        "warnings": warnings,
        "policy": {
            "no_force_push": True,
            "no_reset_hard": True,
            "no_git_clean": True,
            "no_remote_branch_delete_without_explicit": True,
            "merge_requires_explicit_flag": True,
            "no_source_sanitization": True,
        }
    }
    plan["plan_id"] = hashlib.sha256(json.dumps({k:v for k,v in plan.items() if k!="plan_id"}, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    # AG98_PLAN_DASHBOARD_HOOK_V1
    try:
        ag98_write_plan_dashboard(report, plan, ag98_noise_summary, validations)
    except Exception as ag98_exc:
        (report/"AG98_DASHBOARD_ERROR.txt").write_text(repr(ag98_exc), encoding="utf-8")
    progress(76, "Escribiendo plan lock")
    (report/"AUTOGIT_PLAN.lock.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [f"# AutoGit Flight Control Plan", "", f"Plan ID: `{plan['plan_id']}`", f"Task: {args.task}", f"Repo: `{repo}`", f"Branch: `{branch}`", f"HEAD: `{head}`", "", f"Blockers: {len(blockers)}", f"Warnings: {len(warnings)}", "", "## Commit groups"]
    for g in commit_groups:
        md.append(f"\n### {g['group']}\n\nMessage: `{g['message']}`\n\nFiles:")
        md.extend([f"- `{p}`" for p in g["paths"]])
    if blockers:
        md.append("\n## BLOCKERS")
        for b in blockers: md.append(f"- {b}")
    if warnings:
        md.append("\n## Warnings")
        for w in warnings: md.append(f"- {w}")
    (report/"AUTOGIT_PLAN.md").write_text("\n".join(md), encoding="utf-8")
    (report/"report.json").write_text(json.dumps({"result":"blocked" if blockers else "ok", "plan_id": plan["plan_id"], "blockers": len(blockers), "warnings": len(warnings), "groups": len(commit_groups)}, indent=2), encoding="utf-8")
    (report/"CONTINUATION.md").write_text(f"Subir este ZIP o ejecutar apply-plan con AUTOGIT_PLAN.lock.json. Plan: {plan['plan_id']}\n", encoding="utf-8")
    zip_path = out / f"autogit plan {stamp}.zip"
    progress(92, "Comprimiendo plan")
    make_zip(report, zip_path)
    progress(100, "Plan listo")
    print(f"PLAN_ZIP: {zip_path}")
    print(f"PLAN_LOCK: {report/'AUTOGIT_PLAN.lock.json'}")
    if blockers:
        print("BLOCKED: hay blockers; no ejecutes apply-plan hasta corregirlos.")
        return 2
    return 0

def load_plan(path: Path):
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA: raise FlightError(f"Plan schema incompatible: {data.get('schema')}")
    return data

def verify_plan(repo: Path, runner: Runner, plan: dict, allow_drift: bool=False):
    head=runner.run(["git","rev-parse","HEAD"], check=True, name="verify_head").stdout.strip()
    if head != plan.get("head") and not allow_drift:
        raise FlightError(f"HEAD drift: plan={plan.get('head')} current={head}")
    for rel, expected in (plan.get("path_hashes") or {}).items():
        current=sha256_file(repo/rel)
        if current != expected and not allow_drift:
            raise FlightError(f"File drift: {rel}\nplan={expected}\ncurrent={current}")
    if plan.get("blockers"):
        raise FlightError(f"Plan has blockers: {len(plan['blockers'])}")


def ensure_branch(repo: Path, runner: Runner, base: str, task: str, branch_name: str|None):
    current=runner.run(["git","branch","--show-current"], check=True, name="current_branch").stdout.strip()
    if branch_name:
        if current != branch_name:
            runner.run(["git","checkout","-B",branch_name], check=True, timeout=180, name="checkout_branch")
        return branch_name
    if current in PROTECTED_BRANCHES:
        slug=safe_name(task.lower().replace("_","-")).strip("-")[:32] or "autogit-flight"
        new=f"autogit/{slug}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        runner.run(["git","checkout","-b",new], check=True, timeout=180, name="checkout_new_branch")
        return new
    return current

def apply_plan(args):
    if not args.allow_commit:
        raise FlightError("apply-plan requires --allow-commit. This is intentional.")
    plan_path=Path(args.plan).resolve()
    plan=load_plan(plan_path)
    repo=ensure_repo(Path(args.repo or plan.get("repo") or "."))
    out=Path(args.out or DEFAULT_OUT); out.mkdir(parents=True, exist_ok=True)
    stamp=now_stamp(); report=out/f"autogit apply {stamp}"; report.mkdir(parents=True, exist_ok=True)
    runner=Runner(repo, report)
    progress(5, "Verificando plan lock")
    verify_plan(repo, runner, plan, allow_drift=args.allow_drift)
    progress(15, "Preparando rama")
    branch=ensure_branch(repo, runner, args.base or plan.get("base_branch") or "main", plan.get("task","autogit"), args.branch)
    created=[]
    progress(30, "Ejecutando commits separados")
    total=max(1,len(plan.get("commit_groups") or []))
    for idx,g in enumerate(plan.get("commit_groups") or [],1):
        paths=[p for p in g.get("paths",[]) if p]
        ag100_write_group_checkpoint(repo, runner, report, index=idx, total=total, group=g, phase="before_reset")
        runner.run(["git","reset"], check=True, timeout=120, name=f"reset_before_{idx}")
        if not paths:
            ag100_write_group_checkpoint(repo, runner, report, index=idx, total=total, group=g, phase="skipped_empty_paths")
            continue
        runner.run(["git","add","--",*paths], check=True, timeout=240, name=f"git_add_{idx}_{safe_name(g.get('group','group'))}")
        ag100_write_group_checkpoint(repo, runner, report, index=idx, total=total, group=g, phase="after_stage_before_diff")
        diffq=runner.run(["git","diff","--cached","--quiet"], timeout=120, name=f"cached_quiet_{idx}")
        if diffq.returncode == 0:
            ag100_write_group_checkpoint(repo, runner, report, index=idx, total=total, group=g, phase="skipped_no_cached_diff")
            continue
        # AG100_SELF_HEAL_CACHED_CHECK_V1
        ag100_cached = runner.run(["git","diff","--cached","--check"], timeout=180, name=f"cached_diff_check_{idx}_before_ag100")
        ag100_fix = {"ok": ag100_cached.returncode == 0, "fixed": [], "skipped": [], "not_needed": ag100_cached.returncode == 0}
        if ag100_cached.returncode != 0:
            ag100_fix = ag100_autofix_staged_whitespace(repo, runner, report, group_paths=paths, label=f"commit_{idx}_{safe_name(g.get('group','group'))}")
            if not ag100_fix.get("ok"):
                # Keep the AG98 bridge as a fallback for older installs.
                ag98_fix = ag98_autofix_staged_whitespace(repo, runner, report, paths)
                if not ag98_fix.get("ok"):
                    runner.run(["git","diff","--cached","--check"], check=True, timeout=180, name=f"cached_diff_check_{idx}_after_ag100")
        ag100_write_group_checkpoint(repo, runner, report, index=idx, total=total, group=g, phase="after_self_heal", extra={"self_heal": ag100_fix})
        runner.run(["git","diff","--cached","--check"], check=True, timeout=180, name=f"cached_diff_check_{idx}")
        ag100_write_group_checkpoint(repo, runner, report, index=idx, total=total, group=g, phase="before_commit")
        runner.run(["git","commit","-m",g.get("message") or "chore(prisma): update files","-m",g.get("body") or "AutoGit Flight Control commit."], check=True, timeout=600, name=f"git_commit_{idx}")
        sha=runner.run(["git","rev-parse","HEAD"], check=True, name=f"head_after_commit_{idx}").stdout.strip()
        created.append({"group":g.get("group"),"message":g.get("message"),"sha":sha,"paths":paths})
        ag100_write_group_checkpoint(repo, runner, report, index=idx, total=total, group=g, phase="after_commit", extra={"sha": sha})
        progress(30+int(30*idx/total), f"Commit {idx}/{total}")
    runner.run(["git","reset"], check=True, timeout=120, name="reset_after_commits")
    pr=None; checks=None; merged=None
    if args.allow_push or args.allow_pr:
        progress(66, "Push")
        remote=args.remote or "origin"
        runner.run(["git","push","-u",remote,branch], check=True, timeout=900, name="git_push")
    if args.allow_pr:
        progress(75, "Crear PR")
        if not shutil.which("gh"):
            raise FlightError("gh CLI no encontrado; no puedo crear PR")
        body=report/"PR_BODY.md"
        body.write_text(make_pr_body(plan, created), encoding="utf-8")
        title=args.pr_title or infer_pr_title(plan, created)
        cp=runner.run(["gh","pr","create","--base",args.base or plan.get("base_branch") or "main","--head",branch,"--title",title,"--body-file",str(body)], check=True, timeout=300, name="gh_pr_create")
        url=(cp.stdout.strip().splitlines()[-1] if cp.stdout.strip() else "")
        pr={"url":url,"title":title,"branch":branch}
        if args.wait_checks:
            progress(84, "Esperar checks")
            chk=runner.run(["gh","pr","checks",url,"--watch","--fail-fast"], timeout=args.check_timeout, name="gh_pr_checks")
            checks={"returncode":chk.returncode,"stdout":chk.stdout,"stderr":chk.stderr,"ok":chk.returncode==0 or "no checks" in (chk.stdout+chk.stderr).lower()}
            # AG98_CI_DECISION_APPLY_HOOK_V1
            try:
                ag98_write_ci_decision(report, chk.stdout, chk.stderr, chk.returncode, context="apply_pr_checks")
            except Exception:
                pass
            if not checks["ok"]:
                raise FlightError("GitHub checks failed; merge blocked")
        if args.allow_merge:
            if not args.wait_checks and not args.allow_merge_no_checks:
                raise FlightError("Merge requires --wait-checks or --allow-merge-no-checks")
            progress(90, "Merge PR")
            m=runner.run(["gh","pr","merge",url,"--merge","--delete-branch"], timeout=600, name="gh_pr_merge")
            merged={"returncode":m.returncode,"stdout":m.stdout,"stderr":m.stderr,"ok":m.returncode==0}
            if m.returncode != 0:
                raise FlightError("PR merge failed")
    hygiene = ag100_write_post_run_hygiene_report(repo, runner, report, context="apply_plan")
    summary={"result":"ok","branch":branch,"created_commits":created,"pr":pr,"checks":checks,"merged":merged,"post_run_hygiene":hygiene,"rollback":"Use generated revert commands; no reset --hard was executed."}
    # AG98_APPLY_DASHBOARD_HOOK_V1
    try:
        ag98_write_apply_dashboard(report, summary)
    except Exception as ag98_exc:
        (report/"AG98_DASHBOARD_ERROR.txt").write_text(repr(ag98_exc), encoding="utf-8")
    (report/"summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (report/"REVERT_COMMANDS.ps1").write_text(make_revert_script(created), encoding="utf-8")
    (report/"REPORT.md").write_text(make_apply_md(summary), encoding="utf-8")
    zip_path=out/f"autogit apply {stamp} result.zip"
    progress(96, "Comprimiendo resultado")
    make_zip(report, zip_path)
    progress(100, "Apply listo")
    print(f"RESULT_ZIP: {zip_path}")
    return 0

def infer_pr_title(plan, commits):
    task=plan.get("task") or "AutoGit Flight Control changes"
    return ("AutoGit: " + task)[:90]

def make_pr_body(plan, commits):
    lines=["## AutoGit Flight Control", "", f"Task: {plan.get('task','')}", "", "## Commits"]
    for c in commits:
        lines.append(f"- `{c.get('sha','')[:12]}` {c.get('message')} ({len(c.get('paths',[]))} files)")
    lines += ["", "## Safety", "- No force push", "- No git reset --hard", "- No git clean", "- No source sanitizer", "- No merge without explicit flag"]
    return "\n".join(lines)

def make_revert_script(commits):
    lines=["$ErrorActionPreference = 'Stop'", "# Review before running. Reverts created commits newest-first."]
    for c in reversed(commits):
        if c.get("sha"): lines.append(f"git revert --no-edit {c['sha']}")
    return "\n".join(lines)+"\n"

def make_apply_md(summary):
    return "# AutoGit apply result\n\n```json\n"+json.dumps(summary, indent=2, ensure_ascii=False)+"\n```\n"

def merge_command(args):
    if not args.allow_merge:
        raise FlightError("merge command requires --allow-merge")
    out=Path(args.out or DEFAULT_OUT); out.mkdir(parents=True, exist_ok=True)
    repo=ensure_repo(Path(args.repo)); stamp=now_stamp(); report=out/f"autogit merge {stamp}"; report.mkdir(parents=True, exist_ok=True)
    runner=Runner(repo, report)
    if not shutil.which("gh"):
        raise FlightError("gh CLI no encontrado")
    if args.wait_checks:
        chk=runner.run(["gh","pr","checks",args.pr,"--watch","--fail-fast"], timeout=args.check_timeout, name="gh_pr_checks")
        # AG98_CI_DECISION_MERGE_HOOK_V1
        try:
            ag98_write_ci_decision(report, chk.stdout, chk.stderr, chk.returncode, context="merge_pr_checks")
        except Exception:
            pass
        if chk.returncode != 0 and "no checks" not in (chk.stdout+chk.stderr).lower():
            raise FlightError("Checks failed; merge blocked")
    elif not args.allow_merge_no_checks:
        raise FlightError("Merge requires --wait-checks or --allow-merge-no-checks")
    m=runner.run(["gh","pr","merge",args.pr,"--merge","--delete-branch"], timeout=600, name="gh_pr_merge")
    summary={"result":"ok" if m.returncode==0 else "failed", "returncode":m.returncode, "stdout":m.stdout, "stderr":m.stderr}
    summary["post_run_hygiene"] = ag100_write_post_run_hygiene_report(repo, runner, report, context="merge_command")
    # AG98_SYNC_LOCAL_MAIN_HOOK_V1
    if m.returncode == 0 and getattr(args, "sync_local_main", False):
        sync_steps = []
        for _cmd, _name in [
            (["git", "fetch", "origin", "main"], "ag98_sync_fetch_main"),
            (["git", "checkout", "main"], "ag98_sync_checkout_main"),
            (["git", "pull", "--ff-only", "origin", "main"], "ag98_sync_pull_main"),
            (["git", "status", "--short", "--branch"], "ag98_sync_status_main"),
        ]:
            _cp = runner.run(_cmd, timeout=600, name=_name)
            sync_steps.append({"cmd": _cmd, "returncode": _cp.returncode, "stdout": _cp.stdout, "stderr": _cp.stderr})
            if _cp.returncode != 0:
                raise FlightError("AG98 local main sync failed")
        summary["sync_local_main"] = sync_steps
    (report/"summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    zip_path=out/f"autogit merge {stamp} result.zip" if m.returncode==0 else out/f"autogit merge {stamp} fail.zip"
    make_zip(report, zip_path)
    if m.returncode != 0: raise FlightError("gh pr merge failed")
    print(f"RESULT_ZIP: {zip_path}")
    return 0

def fail_zip(out: Path, report: Path|None, exc: BaseException):
    stamp=now_stamp(); fail=out/f"autogit flight {stamp} fail"
    fail.mkdir(parents=True, exist_ok=True)
    (fail/"ERROR.txt").write_text(repr(exc), encoding="utf-8")
    # AG100_FAIL_ZIP_CONTEXT_V1
    try:
        ag100_capture_failure_context(Path.cwd(), fail, report=report, exc=exc)
    except Exception as ag100_exc:
        (fail/"AG100_FAILURE_CONTEXT_ERROR.txt").write_text(repr(ag100_exc), encoding="utf-8")
    # AG98_FAIL_ZIP_STATUS_HOOK_V1
    try:
        _status = subprocess.run(["git", "status", "--short", "--branch"], cwd=str(Path.cwd()), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        (fail/"git_status_failure.txt").write_text((_status.stdout or "") + (_status.stderr or ""), encoding="utf-8", errors="replace")
    except Exception:
        pass
    if report and report.exists():
        dest=fail/"partial_report"; shutil.copytree(report,dest,dirs_exist_ok=True)
    zip_path=out/f"autogit flight {stamp} fail.zip"; make_zip(fail, zip_path)
    print(f"FAIL_ZIP: {zip_path}", file=sys.stderr)

def main(argv=None):
    ap=argparse.ArgumentParser(description="AutoGit Flight Control v2")
    ap.add_argument("--repo", default=r"F:\repos\hitech-os")
    ap.add_argument("--out", default=r"F:\descargasf")
    sub=ap.add_subparsers(dest="cmd", required=True)
    p=sub.add_parser("plan"); p.add_argument("--task", required=True); p.add_argument("--base", default="main")
    a=sub.add_parser("apply-plan"); a.add_argument("--plan", required=True); a.add_argument("--task", default=""); a.add_argument("--base", default="main"); a.add_argument("--branch"); a.add_argument("--remote", default="origin"); a.add_argument("--allow-commit", action="store_true"); a.add_argument("--allow-push", action="store_true"); a.add_argument("--allow-pr", action="store_true"); a.add_argument("--allow-merge", action="store_true"); a.add_argument("--allow-merge-no-checks", action="store_true"); a.add_argument("--wait-checks", action="store_true"); a.add_argument("--check-timeout", type=int, default=1800); a.add_argument("--pr-title"); a.add_argument("--allow-drift", action="store_true")
    m=sub.add_parser("merge"); m.add_argument("--pr", required=True); m.add_argument("--allow-merge", action="store_true"); m.add_argument("--allow-merge-no-checks", action="store_true"); m.add_argument("--wait-checks", action="store_true"); m.add_argument("--check-timeout", type=int, default=1800); m.add_argument("--sync-local-main", action="store_true")  # AG98_SYNC_LOCAL_MAIN_ARG_V1
    ns=ap.parse_args(argv)
    out=Path(ns.out or DEFAULT_OUT); report=None
    try:
        if ns.cmd == "plan": return build_plan(ns)
        if ns.cmd == "apply-plan": return apply_plan(ns)
        if ns.cmd == "merge": return merge_command(ns)
    except BaseException as exc:
        try: fail_zip(out, report, exc)
        except Exception: pass
        print(f"AUTOGIT FLIGHT FAILED: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
