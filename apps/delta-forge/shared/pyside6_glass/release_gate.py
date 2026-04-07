from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from .ux_flight_recorder import load_capability_contract
except ImportError:  # pragma: no cover - supports direct script invocation
    from forgeos.shared.pyside6_glass.ux_flight_recorder import load_capability_contract  # type: ignore
PACKAGE_ROOT = THIS_FILE.parent
CONTRACT_PATH = PACKAGE_ROOT / "SACRED_CAPABILITIES_CONTRACT.md"
PREMIUM_CONTRACT_PATH = PACKAGE_ROOT / "contracts" / "premium_capabilities_100.md"
EVIDENCE_ROOT = REPO_ROOT / "tools" / "_local" / "evidence"


CRITICAL_COMPILE_TARGETS = [
    "forgeos/shared/pyside6_glass/examples/catalog_shell.py",
    "forgeos/shared/pyside6_glass/template.py",
    "forgeos/shared/pyside6_glass/theme.py",
    "forgeos/shared/pyside6_glass/data.py",
    "forgeos/shared/pyside6_glass/release_gate.py",
    "forgeos/shared/pyside6_glass/ux_flight_recorder/runner.py",
]

CRITICAL_TEST_MODULES = [
    "forgeos.shared.pyside6_glass.tests.test_catalog_workbench",
    "forgeos.shared.pyside6_glass.tests.test_data_result_states",
    "forgeos.shared.pyside6_glass.tests.test_data_registry",
    "forgeos.shared.pyside6_glass.tests.test_theme_surface_opacity",
    "forgeos.shared.pyside6_glass.tests.test_ux_flight_recorder",
]

REQUIRED_CAPABILITIES = 40
REQUIRED_PREMIUM_CAPABILITIES = 100


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
    if not isinstance(parsed, dict):
        return {}
    return parsed


def _synthetic_check(name: str, *, passed: bool, stdout: str = "", stderr: str = "") -> GateCheck:
    return GateCheck(
        name=name,
        command=[name],
        passed=bool(passed),
        returncode=0 if passed else 1,
        stdout=str(stdout or ""),
        stderr=str(stderr or ""),
    )


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
                "capability_id": int(row.get("capability_id", 0)),
                "after_status": after_status,
                "capability": str(row.get("capability", "")),
            }
        )
    return issues


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

    if run_tests:
        for module_name in CRITICAL_TEST_MODULES:
            command = [python_executable, "-m", "unittest", module_name]
            check = _run(command, cwd=REPO_ROOT)
            checks.append(check)
            if check.passed:
                evidence_tags.add(f"check:{_module_tag(module_name)}:pass")

    proof_summary: dict[str, Any] = {}
    proof_check: GateCheck | None = None
    if run_proof:
        proof_command = _build_proof_command(
            python_executable=python_executable,
            refresh_baseline=refresh_proof_baseline,
            screenshots_enabled=proof_screenshots,
            headed=not proof_headless,
            extra_evidence_tags=evidence_tags,
        )
        command_check = _run(proof_command, cwd=REPO_ROOT)
        proof_check = command_check
        if command_check.passed:
            evidence_tags.add("check:proof_runner:pass")
        proof_summary = _parse_json_stdout(command_check)
        checks.append(proof_check)

    nightly_visual_payload: dict[str, Any] = {}
    if nightly_visual_proof:
        # Nightly visual proof is intentionally non-blocking and always screenshot-enabled.
        visual_tags = set(evidence_tags)
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
    blocker_issues = _collect_release_blocker_issues(capability_delta if isinstance(capability_delta, list) else [])
    checks.append(
        _synthetic_check(
            "contract.release_blockers_solid",
            passed=(len(blocker_issues) == 0),
            stdout=f"release_blocker_issues={len(blocker_issues)}",
            stderr="" if not blocker_issues else json.dumps(blocker_issues[:12], ensure_ascii=True),
        )
    )

    passed = all(item.passed for item in checks)
    payload = {
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
        "release_blocker_issues": blocker_issues,
        "evidence_tags": sorted(evidence_tags),
        "passed": bool(passed),
        "checks": [item.to_payload() for item in checks],
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
