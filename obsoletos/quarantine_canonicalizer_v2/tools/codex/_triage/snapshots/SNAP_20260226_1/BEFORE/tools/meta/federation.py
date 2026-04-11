from __future__ import annotations

import pathlib
import subprocess
from dataclasses import dataclass

from .constants import (
    DOCS_DOCTOR_REL,
    FINAL_REPORT_REL,
    STATUS_BLOCKED,
    STATUS_DEGRADED,
    STATUS_MISSING_TOOLING,
    STATUS_OFFLINE,
    STATUS_OK,
)
from .pathing import as_posix
from .registry import RepoEntry
from .report_parser import MandatoryReadState, ParsedReport, parse_final_report


@dataclass
class RepoEvaluation:
    name: str
    path: str
    online: bool
    status: str
    docs_doctor: dict
    mandatory_first_read: dict
    blockers: dict
    debt_items: list[dict]
    last_report_excerpt: list[str]


def evaluate_repo(
    repo: RepoEntry,
    run_docs_doctor: bool,
) -> RepoEvaluation:
    repo_path = pathlib.Path(repo.path)
    if not repo_path.exists():
        return RepoEvaluation(
            name=repo.name,
            path=as_posix(repo_path),
            online=False,
            status=STATUS_OFFLINE,
            docs_doctor={
                "present": False,
                "check_ran": False,
                "result": "OFFLINE",
                "canonical_docs_root": "docs/govos",
                "report_path": as_posix(repo_path / FINAL_REPORT_REL),
            },
            mandatory_first_read={
                "kernel_present": False,
                "factory_runtime_present": False,
                "additive_only_trigger": True,
                "resolution": "repo offline",
            },
            blockers={
                "constitutional": [],
                "policy": [],
                "tooling": ["repository path unavailable"],
            },
            debt_items=[],
            last_report_excerpt=[],
        )

    docs_doctor_path = repo_path / (repo.docs_doctor or DOCS_DOCTOR_REL)
    report_path = repo_path / FINAL_REPORT_REL
    doctor_present = docs_doctor_path.is_file()
    check_ran = False
    doctor_result = "NOT_RUN"
    policy_blockers: list[str] = []
    tooling_blockers: list[str] = []
    constitutional_blockers: list[str] = []

    if not report_path.is_file() and run_docs_doctor:
        if doctor_present:
            check_ran = True
            cp = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(docs_doctor_path),
                    "--check",
                ],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False,
            )
            doctor_result = _result_from_output(cp.stdout + "\n" + cp.stderr, cp.returncode)
        else:
            doctor_result = "MISSING_TOOLING"
            tooling_blockers.append("Docs-Doctor missing")
    elif doctor_present:
        doctor_result = "PRESENT"
    else:
        doctor_result = "MISSING_TOOLING"
        tooling_blockers.append("Docs-Doctor missing")

    mandatory = MandatoryReadState(
        kernel_present=False,
        factory_runtime_present=False,
        additive_only_trigger=True,
        resolution="report unavailable",
    )
    excerpt: list[str] = []
    parsed_result = "MISSING"
    if report_path.is_file():
        parsed: ParsedReport = parse_final_report(report_path)
        parsed_result = parsed.result
        mandatory = parsed.mandatory
        constitutional_blockers.extend(parsed.constitutional_blockers)
        policy_blockers.extend(parsed.policy_blockers)
        tooling_blockers.extend(parsed.tooling_blockers)
        excerpt = parsed.excerpt
    else:
        tooling_blockers.append("FINAL_REPORT missing")

    status = STATUS_OK
    if constitutional_blockers:
        status = STATUS_BLOCKED
    elif tooling_blockers or policy_blockers or parsed_result in ("BLOCKED", "FAIL", "MISSING"):
        status = STATUS_DEGRADED if doctor_present else STATUS_MISSING_TOOLING

    return RepoEvaluation(
        name=repo.name,
        path=as_posix(repo_path),
        online=True,
        status=status,
        docs_doctor={
            "present": doctor_present,
            "check_ran": check_ran,
            "result": doctor_result if doctor_result != "PRESENT" else parsed_result,
            "canonical_docs_root": "docs/govos",
            "report_path": as_posix(report_path),
        },
        mandatory_first_read={
            "kernel_present": mandatory.kernel_present,
            "factory_runtime_present": mandatory.factory_runtime_present,
            "additive_only_trigger": mandatory.additive_only_trigger,
            "resolution": mandatory.resolution,
        },
        blockers={
            "constitutional": sorted(set(constitutional_blockers)),
            "policy": sorted(set(policy_blockers)),
            "tooling": sorted(set(tooling_blockers)),
        },
        debt_items=[],
        last_report_excerpt=excerpt,
    )


def evaluate_federation_status(repo_states: list[RepoEvaluation], strict: bool) -> str:
    online = [r for r in repo_states if r.online]
    if any(r.status == STATUS_BLOCKED for r in online):
        return STATUS_BLOCKED
    if any(r.status == STATUS_OFFLINE for r in repo_states):
        return STATUS_DEGRADED
    if any(r.status in (STATUS_DEGRADED, STATUS_MISSING_TOOLING) for r in repo_states):
        return STATUS_DEGRADED
    return STATUS_OK


def _result_from_output(output: str, rc: int) -> str:
    for line in output.splitlines():
        if line.strip().startswith("RESULT:"):
            return line.split(":", 1)[1].strip().upper()
    if rc == 0:
        return STATUS_OK
    if rc == 2:
        return STATUS_BLOCKED
    return "FAIL"
