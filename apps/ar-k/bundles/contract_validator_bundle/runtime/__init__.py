
"""Runtime package for the governed handoff validator bundle."""

from .evaluator import evaluate_case, evaluate_cases
from .severities import Severity, bundle_status_from_findings
