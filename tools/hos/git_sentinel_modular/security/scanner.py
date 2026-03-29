from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..shared.contracts import SecurityFinding
from ..shared.errors import ConfigurationError
from ..shared.foundation import ensure_inside_root


@dataclass(slots=True, frozen=True)
class SecurityRule:
    rule_id: str
    severity: str
    needle: str
    message: str
    secret_like: bool = False


DEFAULT_RULES: tuple[SecurityRule, ...] = (
    SecurityRule("SEC_API_KEY", "high", "api_key", "Potential API key marker", True),
    SecurityRule("SEC_SECRET", "critical", "secret=", "Potential inline secret assignment", True),
    SecurityRule("SEC_PASSWORD", "high", "password", "Potential password marker", True),
    SecurityRule("SEC_PRIVATE_KEY", "critical", "BEGIN PRIVATE KEY", "Potential private key material", True),
    SecurityRule("SEC_TOKEN", "medium", "token", "Potential access token marker", True),
)


@dataclass(slots=True)
class SecurityScanConfig:
    repo_root: Path
    max_file_bytes: int = 512_000
    text_suffixes: set[str] = field(default_factory=lambda: {
        ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".env", ".ini", ".cfg", ".toml"
    })

    def validate(self) -> "SecurityScanConfig":
        self.repo_root = Path(self.repo_root).resolve()
        if not self.repo_root.exists():
            raise ConfigurationError("SecurityScanConfig repo_root does not exist.", repo_root=str(self.repo_root))
        if self.max_file_bytes <= 0:
            raise ConfigurationError("max_file_bytes must be positive.", max_file_bytes=self.max_file_bytes)
        return self


class SecurityScanner:
    def __init__(self, rules: tuple[SecurityRule, ...] | None = None):
        self.rules = rules or DEFAULT_RULES

    def scan_security(self, repo_root: str) -> list[SecurityFinding]:
        config = SecurityScanConfig(repo_root=Path(repo_root)).validate()
        findings: list[SecurityFinding] = []

        for path in sorted(config.repo_root.rglob("*")):
            ensure_inside_root(config.repo_root, path, reason="security scan")
            if not path.is_file():
                continue
            if path.suffix.lower() not in config.text_suffixes:
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > config.max_file_bytes:
                continue

            text = self._safe_read_text(path)
            if not text:
                continue

            rel = path.relative_to(config.repo_root).as_posix()
            findings.extend(self._scan_text(rel, text))

        return findings

    def _scan_text(self, relative_path: str, text: str) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        lowered = text.lower()

        for rule in self.rules:
            needle = rule.needle.lower()
            if needle not in lowered:
                continue
            findings.append(
                SecurityFinding(
                    rule_id=rule.rule_id,
                    path=relative_path,
                    severity=rule.severity,
                    message=rule.message,
                    secret_like=rule.secret_like,
                    metadata={"detector": "SecurityScanner", "needle": rule.needle},
                ).validate()
            )
        return findings

    @staticmethod
    def _safe_read_text(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""
