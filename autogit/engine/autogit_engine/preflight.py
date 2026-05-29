from __future__ import annotations
from .git_cli import Git
from .github_cli import GitHub
from .errors import PreflightError
def run_preflight(ctx):
    git=Git(ctx.shell); branch=git.branch()
    if branch!=ctx.policy.repo_expected_branch: raise PreflightError(f"Expected branch {ctx.policy.repo_expected_branch}, got {branch}",phase="preflight")
    ctx.start_head=git.rev_parse("HEAD"); ctx.write_state("preflight",{"head":ctx.start_head})
    gh=None
    if ctx.policy.mode in {"full","pr-only"}: gh=GitHub(ctx.shell); gh.auth_status()
    return git,gh
