from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

from .constants import EXCERPT_LINES


@dataclass(frozen=True)
class MandatoryReadState:
    kernel_present: bool
    factory_runtime_present: bool
    additive_only_trigger: bool
    resolution: str


@dataclass(frozen=True)
class ParsedReport:
    result: str
    mandatory: MandatoryReadState
    constitutional_blockers: list[str]
    policy_blockers: list[str]
    tooling_blockers: list[str]
    excerpt: list[str]


def parse_final_report(path: pathlib.Path) -> ParsedReport:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    result = _extract_result(lines)
    mandatory = _extract_mandatory(lines)
    constitutional, policy, tooling = _extract_blockers(lines)
    excerpt = lines[:EXCERPT_LINES]

    return ParsedReport(
        result=result,
        mandatory=mandatory,
        constitutional_blockers=sorted(set(constitutional)),
        policy_blockers=sorted(set(policy)),
        tooling_blockers=sorted(set(tooling)),
        excerpt=excerpt,
    )


def _extract_result(lines: list[str]) -> str:
    for line in lines:
        if line.startswith("RESULT:"):
            value = line.split(":", 1)[1].strip().upper()
            return value or "UNKNOWN"
    return "UNKNOWN"


def _extract_mandatory(lines: list[str]) -> MandatoryReadState:
    kernel = _line_has(lines, "- KERNEL_CONTEXT.md: present")
    factory = _line_has(lines, "- docs/factory/FACTORY_RUNTIME_EXPLAINED.md: present")
    additive = _line_has(lines, "- additive_only_trigger: true")
    resolution = ""
    for line in lines:
        if line.lower().startswith("- resolution:"):
            resolution = line.split(":", 1)[1].strip()
            break
    if not resolution:
        for line in lines:
            if line.lower().startswith("- reason:"):
                resolution = line.split(":", 1)[1].strip()
                break
    return MandatoryReadState(
        kernel_present=kernel,
        factory_runtime_present=factory,
        additive_only_trigger=additive,
        resolution=resolution,
    )


def _line_has(lines: list[str], text: str) -> bool:
    needle = text.lower().strip()
    return any(line.lower().strip() == needle for line in lines)


def _extract_blockers(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    constitutional: list[str] = []
    policy: list[str] = []
    tooling: list[str] = []
    for line in lines:
        low = line.lower()
        if "blocker" not in low and not low.startswith("- "):
            continue
        cleaned = re.sub(r"\s+", " ", line.strip())
        if "constitutional" in low or "constitution" in low:
            constitutional.append(cleaned)
        elif "tool" in low or "missing" in low or "doctor" in low:
            tooling.append(cleaned)
        elif "policy" in low or "governance" in low or "blocked" in low:
            policy.append(cleaned)
    return constitutional, policy, tooling
