from __future__ import annotations
class AutoGitError(RuntimeError):
    def __init__(self, message: str, *, phase: str = "unknown", detail: dict | None = None):
        super().__init__(message); self.phase = phase; self.detail = detail or {}
class PreflightError(AutoGitError): pass
class SafetyError(AutoGitError): pass
class ValidationError(AutoGitError): pass
class RecipeError(AutoGitError): pass
class GitError(AutoGitError): pass
class GitHubError(AutoGitError): pass
class DirtyTreeError(AutoGitError): pass
class StageMismatchError(AutoGitError): pass
class RollbackError(AutoGitError): pass
