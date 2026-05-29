from __future__ import annotations
from .whitespace import WhitespaceRecipe
from .enobufs import GitLsFilesBufferRecipe
from .codeowners import CodeownersCoverageRecipe
from .local_paths import LocalPathRecipe
from .pr_branch_policy import AutoMergePolicyRecipe
from .github_checks import GitHubChecksRecipe
from .dirty_worktree import DirtyWorktreeRecipe
from .lockfile import LockfileRecipe
RECIPES=[WhitespaceRecipe(),GitLsFilesBufferRecipe(),CodeownersCoverageRecipe(),LocalPathRecipe(),AutoMergePolicyRecipe(),GitHubChecksRecipe(),DirtyWorktreeRecipe(),LockfileRecipe()]
def matching(text:str): return [r for r in RECIPES if r.matches(text or "")]
