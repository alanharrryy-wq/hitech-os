
from __future__ import annotations

from .gates import build_gate_decisions, summarize
from .models import Finding
from .rule_artifact_naming import evaluate as evaluate_artifact_naming
from .rule_cross_reference import evaluate as evaluate_cross_reference
from .rule_done_criteria import evaluate as evaluate_done_criteria
from .rule_exclusions import evaluate as evaluate_exclusions
from .rule_ownership import evaluate as evaluate_ownership
from .rule_promotion_policy import evaluate as evaluate_promotion_policy
from .rule_stage_order import evaluate as evaluate_stage_order
from .rule_write_limits import evaluate as evaluate_write_limits

RULES = [
    evaluate_stage_order,
    evaluate_ownership,
    evaluate_artifact_naming,
    evaluate_exclusions,
    evaluate_write_limits,
    evaluate_promotion_policy,
    evaluate_cross_reference,
    evaluate_done_criteria,
]


def evaluate_case(case: dict) -> dict:
    findings: list[Finding] = []
    for rule in RULES:
        findings.extend(rule(case))
    summary = summarize(findings)
    gates = build_gate_decisions(findings)
    return {
        'case_id': case['case_id'],
        'summary': summary,
        'gates': gates,
        'findings': [item.as_dict() for item in findings],
    }


def evaluate_cases(cases: list[dict]) -> list[dict]:
    return [evaluate_case(case) for case in cases]
