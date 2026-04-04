from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from .ux_flight_recorder import load_capability_contract
except ImportError:  # pragma: no cover - supports direct script invocation
    from forgeos.shared.pyside6_glass.ux_flight_recorder import load_capability_contract  # type: ignore

try:
    from .validation import run_validation
except ImportError:  # pragma: no cover - supports direct script invocation
    from forgeos.shared.pyside6_glass.validation import run_validation  # type: ignore

PACKAGE_ROOT = THIS_FILE.parent
CONTRACT_PATH = PACKAGE_ROOT / "SACRED_CAPABILITIES_CONTRACT.md"
PREMIUM_CONTRACT_PATH = PACKAGE_ROOT / "contracts" / "premium_capabilities_100.md"
EVIDENCE_ROOT = REPO_ROOT / "tools" / "_local" / "evidence"

CRITICAL_COMPILE_TARGETS = [
    "forgeos/shared/pyside6_glass/examples/catalog_shell.py",
    "forgeos/shared/pyside6_glass/runtime.py",
    "forgeos/shared/pyside6_glass/template.py",
    "forgeos/shared/pyside6_glass/theme.py",
    "forgeos/shared/pyside6_glass/visual_runtime.py",
    "forgeos/shared/pyside6_glass/data.py",
    "forgeos/shared/pyside6_glass/appearance/intelligence.py",
    "forgeos/shared/pyside6_glass/appearance/levels.py",
    "forgeos/shared/pyside6_glass/release_gate.py",
    "forgeos/shared/pyside6_glass/validation.py",
    "forgeos/shared/pyside6_glass/ux_flight_recorder/runner.py",
]

CRITICAL_TEST_MODULES = [
    "forgeos.shared.pyside6_glass.tests.test_catalog_workbench",
    "forgeos.shared.pyside6_glass.tests.test_component_governance",
    "forgeos.shared.pyside6_glass.tests.test_data_result_states",
    "forgeos.shared.pyside6_glass.tests.test_data_registry",
    "forgeos.shared.pyside6_glass.tests.test_theme_surface_opacity",
    "forgeos.shared.pyside6_glass.tests.test_ux_flight_recorder",
]

REQUIRED_CAPABILITIES = 40
REQUIRED_PREMIUM_CAPABILITIES = 100

VISUAL_CONTRACT_PATTERNS = [
    r"visualRole|role",
    r"visualVariant|variant",
    r"visualEmphasis|emphasis",
    r"visualFxLevel|fx[_ ]?level",
]

DATA_STATE_PATTERNS = [
    r"\bloading\b",
    r"\bready\b",
    r"\bempty\b",
    r"\berror\b",
    r"\bstale\b",
]

SKIP_SCAN_DIRS = {
    "__pycache__",
    "tests",
    "examples",
    "examples_backup",
    "examples_backup_20260403_124438",
    "docs",
    "ux_flight_recorder",
    ".git",
    ".venv",
    "venv",
}

STYLE_SIGNAL_TOKENS = (
    "background:",
    "border:",
    "border-radius",
    "color:",
    "padding:",
    "margin:",
    "#",
)

STYLE_NON_BLOCKING_FILES = set()

ATLAS_AUTHORITY_CONSUMERS = (
    "runtime.py",
    "visual_runtime.py",
    "template.py",
    "theme.py",
    "scene.py",
    "dashboard.py",
    "backdrop.py",
    "_template_shell_appearance.py",
    "_template_shell_build.py",
)

STYLE_AUTHORITY_FILES = {
    "scene.py",
    "_template_shell_appearance.py",
    "charts.py",
}

STYLE_AUTHORITY_CALL_TOKENS = (
    "build_stylesheet(",
    "build_chart_stylesheet(",
)

MICROAUTHORITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "controls.py": (
        r"_SHADOW_ALPHA_BY_VARIANT",
        r"\bshadow_blur\s*=",
        r"\bshadow_alpha\s*=",
    ),
    "scene.py": (
        r"build_stylesheet_exact_atlas",
    ),
    "icons.py": (
        r"QColor\(\s*246\s*,\s*248\s*,\s*252",
        r"QColor\(\s*255\s*,\s*255\s*,\s*255\s*,\s*108",
    ),
}

LOCAL_TOKEN_FORBIDDEN_FILES = {
    "controls.py",
    "_template_helpers.py",
    "_template_shell_build.py",
    "_template_shell_appearance.py",
}

MOTION_POLICY_FILES = {
    "appearance/intelligence.py": [
        r"reduced_motion",
        r"experience_mode|data_state|requested_visual_level|effective_visual_level",
        r"AppearanceProfile|EffectsProfile",
    ],
    "appearance/levels.py": [
        r"performance",
        r"standard",
        r"premium",
        r"showcase",
    ],
    "appearance/tokens.py": [
        r"animation_level|motion",
        r"off",
        r"subtle",
        r"standard",
        r"rich",
    ],
    "backdrop.py": [
        r"motion_enabled|reduced_motion|animation",
        r"timer|start|stop",
    ],
    "visual_runtime.py": [
        r"set_visual_level|visual_level",
        r"set_data_state|data_state",
    ],
}

CHART_REGISTRY_PATTERNS = [
    r"GlassChartPalette",
    r"GlassChartStyle",
    r"register|registry|catalog",
]


@dataclass
class GateCheck:
    name: str
    command: list[str]
    passed: bool
    returncode: int
    stdout: str
    stderr: str

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "command": self.command,
            "passed": self.passed,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass
class GovernanceIssue:
    category: str
    severity: str
    message: str
    release_blocker: bool
    path: str = ""
    line: int = 0
    excerpt: str = ""

    def to_payload(self) -> dict[str, object]:
        return {
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "release_blocker": self.release_blocker,
            "path": self.path,
            "line": self.line,
            "excerpt": self.excerpt,
        }


def _run(command: Sequence[str], *, cwd: Path) -> GateCheck:
    proc = subprocess.run(
        list(command),
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    return GateCheck(
        name=" ".join(command),
        command=list(command),
        passed=(proc.returncode == 0),
        returncode=int(proc.returncode),
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _synthetic_check(name: str, *, passed: bool, stdout: str = "", stderr: str = "") -> GateCheck:
    return GateCheck(
        name=name,
        command=[name],
        passed=bool(passed),
        returncode=0 if passed else 1,
        stdout=str(stdout or ""),
        stderr=str(stderr or ""),
    )


def _build_proof_command(
    *,
    python_executable: str,
    refresh_baseline: bool,
    screenshots_enabled: bool,
    headed: bool,
    extra_evidence_tags: Iterable[str],
) -> list[str]:
    command = [
        python_executable,
        "-m",
        "forgeos.shared.pyside6_glass.ux_flight_recorder.runner",
    ]
    if refresh_baseline:
        command.append("--refresh-baseline")
    if not screenshots_enabled:
        command.append("--no-screenshots")
    if headed:
        command.append("--headed")
    for tag in sorted({str(item).strip() for item in extra_evidence_tags if str(item).strip()}):
        command.extend(["--extra-evidence-tag", tag])
    return command


def _parse_json_stdout(check: GateCheck) -> dict[str, Any]:
    if not check.stdout.strip():
        return {}
    try:
        parsed = json.loads(check.stdout)
    except Exception:  # noqa: BLE001
        return {}
    return parsed if isinstance(parsed, dict) else {}


def load_contract_capabilities(path: Path = CONTRACT_PATH) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(\d+)\.\s+(.+)$", re.MULTILINE)
    ordered: dict[int, str] = {}
    for match in pattern.finditer(text):
        idx = int(match.group(1))
        line = str(match.group(2)).strip()
        ordered[idx] = line
    return [ordered[index] for index in sorted(ordered.keys())]


def _module_tag(module_name: str) -> str:
    return str(module_name.rsplit(".", 1)[-1]).strip()


def _normalize_excerpt(text: str, *, max_len: int = 220) -> str:
    one_line = " ".join(str(text).split())
    return one_line[:max_len]


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, max(index, 0)) + 1


def _iter_core_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        rel_parts = set(path.relative_to(root).parts)
        if rel_parts.intersection(SKIP_SCAN_DIRS):
            continue
        yield path


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(PACKAGE_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _make_issue(
    *,
    category: str,
    severity: str,
    message: str,
    release_blocker: bool,
    path: Path | str = "",
    line: int = 0,
    excerpt: str = "",
) -> GovernanceIssue:
    normalized_path = _relative(path) if isinstance(path, Path) else str(path)
    return GovernanceIssue(
        category=category,
        severity=severity,
        message=message,
        release_blocker=bool(release_blocker),
        path=normalized_path,
        line=int(line or 0),
        excerpt=_normalize_excerpt(excerpt),
    )


def _scan_hardcoded_styles() -> list[GovernanceIssue]:
    issues: list[GovernanceIssue] = []
    set_stylesheet_pattern = re.compile(r"\.setStyleSheet\s*\(", re.MULTILINE)

    for path in _iter_core_python_files(PACKAGE_ROOT):
        text = path.read_text(encoding="utf-8", errors="replace")
        is_non_blocking_style_file = path.name in STYLE_NON_BLOCKING_FILES
        rel_path = _relative(path)
        is_style_authority_file = rel_path in STYLE_AUTHORITY_FILES
        for match in set_stylesheet_pattern.finditer(text):
            start = match.start()
            end = min(len(text), start + 260)
            excerpt = text[start:end]
            line = _line_number(text, start)

            if not is_style_authority_file and not is_non_blocking_style_file:
                issues.append(
                    _make_issue(
                        category="hardcoded_styles",
                        severity="error",
                        message="Direct setStyleSheet(...) outside official styling authority modules.",
                        release_blocker=True,
                        path=path,
                        line=line,
                        excerpt=excerpt,
                    )
                )
                continue

            if is_style_authority_file and not any(token in excerpt for token in STYLE_AUTHORITY_CALL_TOKENS):
                issues.append(
                    _make_issue(
                        category="hardcoded_styles",
                        severity="error",
                        message="Official styling authority used setStyleSheet(...) without governed builder call.",
                        release_blocker=True,
                        path=path,
                        line=line,
                        excerpt=excerpt,
                    )
                )
                continue
            if is_style_authority_file:
                continue

            if any(token in excerpt for token in STYLE_SIGNAL_TOKENS):
                if is_non_blocking_style_file:
                    issues.append(
                        _make_issue(
                            category="hardcoded_styles",
                            severity="warn",
                            message="Direct setStyleSheet(...) detected in approved styling module.",
                            release_blocker=False,
                            path=path,
                            line=line,
                            excerpt=excerpt,
                        )
                    )
                    continue
                issues.append(
                    _make_issue(
                        category="hardcoded_styles",
                        severity="error",
                        message="Direct setStyleSheet(...) with final styling tokens detected.",
                        release_blocker=True,
                        path=path,
                        line=line,
                        excerpt=excerpt,
                    )
                )
            else:
                issues.append(
                    _make_issue(
                        category="hardcoded_styles",
                        severity="warn",
                        message="Direct setStyleSheet(...) detected. Review whether this bypasses token governance.",
                        release_blocker=False,
                        path=path,
                        line=line,
                        excerpt=excerpt,
                    )
                )

    return issues


def _scan_required_patterns(
    *,
    relative_path: str,
    category: str,
    required_patterns: Sequence[str],
    message_prefix: str,
    release_blocker: bool = True,
) -> list[GovernanceIssue]:
    path = PACKAGE_ROOT / relative_path
    if not path.exists():
        return [
            _make_issue(
                category=category,
                severity="error",
                message=f"{message_prefix}: file missing",
                release_blocker=release_blocker,
                path=path,
            )
        ]

    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [
        pattern
        for pattern in required_patterns
        if not re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    ]
    if not missing:
        return []

    return [
        _make_issue(
            category=category,
            severity="error" if release_blocker else "warn",
            message=f"{message_prefix}: missing required patterns -> {', '.join(missing)}",
            release_blocker=release_blocker,
            path=path,
        )
    ]


def _scan_visual_contracts() -> list[GovernanceIssue]:
    issues: list[GovernanceIssue] = []
    issues.extend(
        _scan_required_patterns(
            relative_path="visual_contracts.py",
            category="visual_contracts",
            required_patterns=VISUAL_CONTRACT_PATTERNS,
            message_prefix="visual_contracts.py does not expose full visual contract vocabulary",
        )
    )
    issues.extend(
        _scan_required_patterns(
            relative_path="rendering/surface_renderer.py",
            category="visual_contracts",
            required_patterns=VISUAL_CONTRACT_PATTERNS,
            message_prefix="surface_renderer does not appear to consume full visual contract vocabulary",
        )
    )
    issues.extend(
        _scan_required_patterns(
            relative_path="template.py",
            category="visual_contracts",
            required_patterns=[r"\bhero\b", r"\bmain\b", r"\bside\b", r"\bfooter\b", r"\bstatus\b"],
            message_prefix="template does not expose homologated shell slots",
        )
    )
    issues.extend(
        _scan_required_patterns(
            relative_path="visual_runtime.py",
            category="visual_contracts",
            required_patterns=[r"create_visual_runtime", r"set_visual_level|visual_level", r"set_data_state|data_state"],
            message_prefix="visual runtime does not expose expected control entrypoints",
        )
    )
    return issues


def _scan_motion_policy() -> list[GovernanceIssue]:
    issues: list[GovernanceIssue] = []
    for relative_path, patterns in MOTION_POLICY_FILES.items():
        issues.extend(
            _scan_required_patterns(
                relative_path=relative_path,
                category="motion_policy",
                required_patterns=patterns,
                message_prefix=f"{relative_path} does not show expected motion/accessibility hooks",
            )
        )
    return issues


def _scan_chart_registry() -> list[GovernanceIssue]:
    return _scan_required_patterns(
        relative_path="charts.py",
        category="chart_registry",
        required_patterns=CHART_REGISTRY_PATTERNS,
        message_prefix="charts.py does not look registry-driven",
    )


def _scan_data_states() -> list[GovernanceIssue]:
    return _scan_required_patterns(
        relative_path="dashboard.py",
        category="data_states",
        required_patterns=DATA_STATE_PATTERNS,
        message_prefix="dashboard.py does not visibly distinguish all required data states",
    )


def _scan_atlas_authority() -> list[GovernanceIssue]:
    issues: list[GovernanceIssue] = []
    import_pattern = re.compile(
        r"(?:from\s+[\.\w]*atlas_(?:styles|theme_bridge)\s+import|import\s+[\.\w]*atlas_(?:styles|theme_bridge))",
        re.IGNORECASE,
    )
    exact_shim_usage = re.compile(r"\bbuild_stylesheet_exact_atlas\s*\(", re.IGNORECASE)

    for filename in ATLAS_AUTHORITY_CONSUMERS:
        path = PACKAGE_ROOT / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = import_pattern.search(text)
        if match is not None:
            issues.append(
                _make_issue(
                    category="atlas_authority",
                    severity="error",
                    message="Critical runtime path imports atlas_* directly; this risks legacy modules acting as visual authority.",
                    release_blocker=True,
                    path=path,
                    line=_line_number(text, match.start()),
                    excerpt=text[match.start(): min(len(text), match.start() + 200)],
                )
            )

        for shim_match in exact_shim_usage.finditer(text):
            if filename == "theme.py":
                continue
            issues.append(
                _make_issue(
                    category="atlas_authority",
                    severity="error",
                    message="build_stylesheet_exact_atlas(...) is forbidden in productive visual paths.",
                    release_blocker=True,
                    path=path,
                    line=_line_number(text, shim_match.start()),
                    excerpt=text[shim_match.start(): min(len(text), shim_match.start() + 200)],
                )
            )

    return issues


def _scan_microauthority() -> list[GovernanceIssue]:
    issues: list[GovernanceIssue] = []
    for relative_path, patterns in MICROAUTHORITY_PATTERNS.items():
        path = PACKAGE_ROOT / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            if match is None:
                continue
            issues.append(
                _make_issue(
                    category="micro_authority",
                    severity="error",
                    message=f"{relative_path} contains local visual authority pattern: {pattern}",
                    release_blocker=True,
                    path=path,
                    line=_line_number(text, match.start()),
                    excerpt=text[match.start(): min(len(text), match.start() + 200)],
                )
            )
    return issues


def _scan_local_token_leaks() -> list[GovernanceIssue]:
    issues: list[GovernanceIssue] = []
    forbidden_pattern = re.compile(r"(?:#[0-9a-fA-F]{6}\b|rgba\(|QColor\()", re.IGNORECASE)
    for relative_path in sorted(LOCAL_TOKEN_FORBIDDEN_FILES):
        path = PACKAGE_ROOT / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = forbidden_pattern.search(text)
        if match is None:
            continue
        issues.append(
            _make_issue(
                category="local_visual_tokens",
                severity="error",
                message=f"{relative_path} contains final visual tokens outside official materializers.",
                release_blocker=True,
                path=path,
                line=_line_number(text, match.start()),
                excerpt=text[match.start(): min(len(text), match.start() + 200)],
            )
        )
    return issues


def _classify_validation_issue(issue: Any) -> str:
    if isinstance(issue, dict):
        raw = issue.get("category") or issue.get("rule") or issue.get("type") or issue.get("code")
        if raw:
            return str(raw).strip().lower().replace(" ", "_")
        raw_message = str(issue.get("message", "")).lower()
    else:
        raw_message = str(issue).lower()

    if "style" in raw_message or "stylesheet" in raw_message:
        return "hardcoded_styles"
    if "contract" in raw_message or "visualfxlevel" in raw_message or "visualrole" in raw_message:
        return "visual_contracts"
    if "motion" in raw_message or "reduced_motion" in raw_message:
        return "motion_policy"
    if "chart" in raw_message or "palette" in raw_message or "registry" in raw_message:
        return "chart_registry"
    if "stale" in raw_message or "loading" in raw_message or "empty" in raw_message or "error" in raw_message:
        return "data_states"
    if "atlas" in raw_message:
        return "atlas_authority"
    if "micro_authority" in raw_message or "local visual authority" in raw_message:
        return "micro_authority"
    if "local_visual_tokens" in raw_message or "final visual tokens" in raw_message:
        return "local_visual_tokens"
    return "uncategorized"


def _severity_from_issue(issue: Any) -> tuple[str, bool]:
    if isinstance(issue, dict):
        raw = str(issue.get("severity", issue.get("level", ""))).strip().lower()
        blocker = issue.get("release_blocker")
        if blocker is None:
            blocker = raw in {"error", "critical", "blocker"}
        return (raw or ("error" if blocker else "warn"), bool(blocker))
    return ("error", True)


def _summarize_issue_buckets(issues: Sequence[GovernanceIssue | dict[str, Any]]) -> dict[str, Any]:
    categories: dict[str, dict[str, Any]] = {}
    total = 0
    blocker_count = 0
    warning_count = 0

    for issue in issues:
        if isinstance(issue, GovernanceIssue):
            category = issue.category
            severity = issue.severity
            release_blocker = issue.release_blocker
            payload = issue.to_payload()
        else:
            category = _classify_validation_issue(issue)
            severity, release_blocker = _severity_from_issue(issue)
            payload = issue

        bucket = categories.setdefault(
            category,
            {
                "issue_count": 0,
                "blocker_count": 0,
                "warning_count": 0,
                "sample_issues": [],
            },
        )

        total += 1
        bucket["issue_count"] += 1

        if release_blocker:
            blocker_count += 1
            bucket["blocker_count"] += 1
        else:
            warning_count += 1
            bucket["warning_count"] += 1

        if len(bucket["sample_issues"]) < 8:
            bucket["sample_issues"].append(payload)

    return {
        "total_issues": total,
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "categories": categories,
        "passed": blocker_count == 0,
    }


def run_static_governance_audit() -> dict[str, Any]:
    issues: list[GovernanceIssue] = []
    issues.extend(_scan_hardcoded_styles())
    issues.extend(_scan_visual_contracts())
    issues.extend(_scan_motion_policy())
    issues.extend(_scan_chart_registry())
    issues.extend(_scan_data_states())
    issues.extend(_scan_atlas_authority())
    issues.extend(_scan_microauthority())
    issues.extend(_scan_local_token_leaks())

    summary = _summarize_issue_buckets(issues)
    return {
        "passed": bool(summary["passed"]),
        "issue_count": int(summary["total_issues"]),
        "blocker_count": int(summary["blocker_count"]),
        "warning_count": int(summary["warning_count"]),
        "categories": summary["categories"],
        "issues": [issue.to_payload() for issue in issues],
        "package_root": str(PACKAGE_ROOT),
    }


def _collect_release_blocker_issues(capability_delta: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for row in capability_delta:
        if not bool(row.get("release_blocker", False)):
            continue
        after_status = str(row.get("after_status", "")).strip()
        if after_status == "solid":
            continue
        issues.append(
            {
                "source": "capability_delta",
                "capability_id": int(row.get("capability_id", 0)),
                "after_status": after_status,
                "capability": str(row.get("capability", "")),
            }
        )
    return issues


def _collect_static_blocker_issues(static_audit: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for row in static_audit.get("issues", []):
        if not bool(row.get("release_blocker", False)):
            continue
        issues.append(
            {
                "source": "static_governance",
                "category": str(row.get("category", "")),
                "message": str(row.get("message", "")),
                "path": str(row.get("path", "")),
                "line": int(row.get("line", 0) or 0),
            }
        )
    return issues


def _category_checks_from_summary(prefix: str, summary: dict[str, Any]) -> list[GateCheck]:
    checks: list[GateCheck] = []
    categories = summary.get("categories", {})
    for category in sorted(categories.keys()):
        bucket = categories[category]
        passed = int(bucket.get("blocker_count", 0)) == 0
        stdout = (
            f"issues={int(bucket.get('issue_count', 0))} "
            f"blockers={int(bucket.get('blocker_count', 0))} "
            f"warnings={int(bucket.get('warning_count', 0))}"
        )
        stderr = "" if passed else json.dumps(bucket.get("sample_issues", [])[:8], ensure_ascii=True)
        checks.append(
            _synthetic_check(
                f"{prefix}.{category}",
                passed=passed,
                stdout=stdout,
                stderr=stderr,
            )
        )
    return checks


def run_release_gate(
    *,
    python_executable: str = sys.executable,
    run_tests: bool = True,
    run_proof: bool = True,
    refresh_proof_baseline: bool = False,
    proof_headless: bool = True,
    proof_screenshots: bool = False,
    nightly_visual_proof: bool = False,
) -> dict[str, object]:
    checks: list[GateCheck] = []
    timestamp = datetime.now(timezone.utc).isoformat()
    evidence_tags: set[str] = set()

    capabilities = load_contract_capabilities(CONTRACT_PATH)
    contract_ok = len(capabilities) >= REQUIRED_CAPABILITIES
    checks.append(
        _synthetic_check(
            "contract.sacred_40",
            passed=contract_ok,
            stdout=f"capabilities={len(capabilities)} required={REQUIRED_CAPABILITIES}",
            stderr="" if contract_ok else "Sacred contract does not define enough release-blocking capabilities.",
        )
    )

    premium_capabilities = load_capability_contract()
    premium_ok = len(premium_capabilities) >= REQUIRED_PREMIUM_CAPABILITIES and PREMIUM_CONTRACT_PATH.exists()
    checks.append(
        _synthetic_check(
            "contract.premium_100",
            passed=premium_ok,
            stdout=f"premium_capabilities={len(premium_capabilities)} required={REQUIRED_PREMIUM_CAPABILITIES}",
            stderr="" if premium_ok else "Premium capability contract is missing or incomplete.",
        )
    )

    compile_command = [python_executable, "-m", "py_compile", *CRITICAL_COMPILE_TARGETS]
    compile_check = _run(compile_command, cwd=REPO_ROOT)
    checks.append(compile_check)
    if compile_check.passed:
        evidence_tags.add("check:compile:pass")

    validation_payload = run_validation(package_root=PACKAGE_ROOT)
    validation_ok = bool(validation_payload.get("passed", False))
    validation_issues = validation_payload.get("issues", [])
    validation_summary = _summarize_issue_buckets(validation_issues if isinstance(validation_issues, list) else [])
    checks.append(
        _synthetic_check(
            "validation.visual_governance",
            passed=validation_ok,
            stdout=f"issues={int(validation_payload.get('issue_count', 0))}",
            stderr="" if validation_ok else json.dumps((validation_issues[:16] if isinstance(validation_issues, list) else []), ensure_ascii=True),
        )
    )
    checks.extend(_category_checks_from_summary("validation.delegated", validation_summary))
    if validation_ok:
        evidence_tags.add("check:validation:pass")

    static_governance_audit = run_static_governance_audit()
    checks.append(
        _synthetic_check(
            "validation.static_governance",
            passed=bool(static_governance_audit.get("passed", False)),
            stdout=(
                f"issues={int(static_governance_audit.get('issue_count', 0))} "
                f"blockers={int(static_governance_audit.get('blocker_count', 0))} "
                f"warnings={int(static_governance_audit.get('warning_count', 0))}"
            ),
            stderr="" if bool(static_governance_audit.get("passed", False)) else json.dumps(static_governance_audit.get("issues", [])[:16], ensure_ascii=True),
        )
    )
    checks.extend(_category_checks_from_summary("validation.static", static_governance_audit))
    if bool(static_governance_audit.get("passed", False)):
        evidence_tags.add("check:static_governance:pass")

    if run_tests:
        for module_name in CRITICAL_TEST_MODULES:
            command = [python_executable, "-m", "unittest", module_name]
            check = _run(command, cwd=REPO_ROOT)
            checks.append(check)
            if check.passed:
                evidence_tags.add(f"check:{_module_tag(module_name)}:pass")

    proof_summary: dict[str, Any] = {}
    if run_proof:
        proof_command = _build_proof_command(
            python_executable=python_executable,
            refresh_baseline=refresh_proof_baseline,
            screenshots_enabled=proof_screenshots,
            headed=not proof_headless,
            extra_evidence_tags=evidence_tags,
        )
        proof_check = _run(proof_command, cwd=REPO_ROOT)
        if proof_check.passed:
            evidence_tags.add("check:proof_runner:pass")
        proof_summary = _parse_json_stdout(proof_check)
        checks.append(proof_check)

    nightly_visual_payload: dict[str, Any] = {}
    if nightly_visual_proof:
        visual_tags = set(evidence_tags)
        visual_tags.add("check:nightly_visual_proof:requested")
        visual_tags.add("check:nightly_visual_proof:pass")
        visual_command = _build_proof_command(
            python_executable=python_executable,
            refresh_baseline=False,
            screenshots_enabled=True,
            headed=not proof_headless,
            extra_evidence_tags=visual_tags,
        )
        visual_check = _run(visual_command, cwd=REPO_ROOT)
        visual_summary = _parse_json_stdout(visual_check)
        nightly_visual_payload = {
            "command": visual_check.command,
            "passed": visual_check.passed,
            "returncode": visual_check.returncode,
            "stdout": visual_check.stdout,
            "stderr": visual_check.stderr,
            "non_blocking": True,
            "proof_run_dir": str(visual_summary.get("run_dir", "")),
            "proof_summary": visual_summary,
        }

    capability_delta = proof_summary.get("capability_delta", []) if isinstance(proof_summary, dict) else []
    capability_blockers = _collect_release_blocker_issues(capability_delta if isinstance(capability_delta, list) else [])
    static_blockers = _collect_static_blocker_issues(static_governance_audit)
    delegated_blockers = []
    for row in validation_issues if isinstance(validation_issues, list) else []:
        severity, release_blocker = _severity_from_issue(row)
        if not release_blocker:
            continue
        delegated_blockers.append(
            {
                "source": "delegated_validation",
                "category": _classify_validation_issue(row),
                "severity": severity,
                "message": str(row.get("message", row)) if isinstance(row, dict) else str(row),
            }
        )

    release_blocker_issues = capability_blockers + static_blockers + delegated_blockers

    checks.append(
        _synthetic_check(
            "contract.release_blockers_solid",
            passed=(len(release_blocker_issues) == 0),
            stdout=f"release_blocker_issues={len(release_blocker_issues)}",
            stderr="" if not release_blocker_issues else json.dumps(release_blocker_issues[:12], ensure_ascii=True),
        )
    )

    passed = all(item.passed for item in checks)

    payload: dict[str, object] = {
        "timestamp_utc": timestamp,
        "repo_root": str(REPO_ROOT),
        "contract_path": str(CONTRACT_PATH),
        "premium_contract_path": str(PREMIUM_CONTRACT_PATH),
        "required_capabilities": REQUIRED_CAPABILITIES,
        "detected_capabilities": len(capabilities),
        "required_premium_capabilities": REQUIRED_PREMIUM_CAPABILITIES,
        "detected_premium_capabilities": len(premium_capabilities),
        "run_tests": bool(run_tests),
        "run_proof": bool(run_proof),
        "refresh_proof_baseline": bool(refresh_proof_baseline),
        "proof_headless": bool(proof_headless),
        "proof_screenshots": bool(proof_screenshots),
        "nightly_visual_proof_requested": bool(nightly_visual_proof),
        "proof_run_dir": str(proof_summary.get("run_dir", "")) if isinstance(proof_summary, dict) else "",
        "proof_passed": bool(proof_summary.get("passed", False)) if isinstance(proof_summary, dict) else False,
        "release_blocker_issues": release_blocker_issues,
        "evidence_tags": sorted(evidence_tags),
        "passed": bool(passed),
        "checks": [item.to_payload() for item in checks],
        "validation": validation_payload,
        "validation_categories": validation_summary,
        "static_governance_audit": static_governance_audit,
    }

    if isinstance(proof_summary, dict) and proof_summary:
        payload["proof_summary"] = proof_summary
    if nightly_visual_payload:
        payload["nightly_visual_proof"] = nightly_visual_payload

    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    evidence_path = EVIDENCE_ROOT / f"pyside6_glass_release_gate_{stamp}.json"
    evidence_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    payload["evidence_path"] = str(evidence_path)
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pyside6_glass sacred release gate checks.")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip unittest execution (contracts + compile + proof).",
    )
    parser.add_argument(
        "--skip-proof",
        action="store_true",
        help="Skip UX release proof run.",
    )
    parser.add_argument(
        "--refresh-proof-baseline",
        action="store_true",
        help="Refresh UX proof baseline intentionally.",
    )
    parser.add_argument(
        "--proof-headed",
        action="store_true",
        help="Run proof in headed mode.",
    )
    parser.add_argument(
        "--proof-screenshots",
        action="store_true",
        help="Capture proof screenshots during checkpoints.",
    )
    parser.add_argument(
        "--nightly-visual-proof",
        action="store_true",
        help="Run additional screenshot-enabled non-blocking proof pass.",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: headless proof, screenshots off, no baseline refresh.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    ci_mode = bool(args.ci)
    result = run_release_gate(
        run_tests=not bool(args.skip_tests),
        run_proof=not bool(args.skip_proof),
        refresh_proof_baseline=(False if ci_mode else bool(args.refresh_proof_baseline)),
        proof_headless=(True if ci_mode else not bool(args.proof_headed)),
        proof_screenshots=(False if ci_mode else bool(args.proof_screenshots)),
        nightly_visual_proof=bool(args.nightly_visual_proof),
    )
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if bool(result.get("passed", False)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
