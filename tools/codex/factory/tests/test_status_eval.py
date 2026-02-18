from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.status_eval import (  # noqa: E402
    BLOCKED,
    FAIL,
    PASS,
    PENDING,
    combine_statuses,
    evaluate_status,
    make_check,
    normalize_check,
    status_exit_code,
)


class StatusEvalTests(unittest.TestCase):
    def test_pass_when_required_checks_pass(self) -> None:
        evaluation = evaluate_status(
            required_checks=[
                make_check("preflight", rc=0),
                make_check("launch", rc=0),
                make_check("bundle_validate", rc=0),
                make_check("integrate", rc=0),
            ],
            schema_errors=[],
            blockers=[],
            internal_errors=[],
        )
        self.assertEqual(PASS, evaluation.status)
        self.assertEqual(0, evaluation.exit_code)
        self.assertTrue(evaluation.ok)
        self.assertEqual([], list(evaluation.required_failures))

    def test_blocked_when_required_check_fails(self) -> None:
        evaluation = evaluate_status(
            required_checks=[
                make_check("preflight", rc=0),
                make_check("launch", rc=2),
            ],
            schema_errors=[],
            blockers=[],
            internal_errors=[],
        )
        self.assertEqual(BLOCKED, evaluation.status)
        self.assertEqual(2, evaluation.exit_code)
        self.assertEqual(1, len(evaluation.required_failures))
        self.assertEqual("launch", evaluation.required_failures[0]["name"])

    def test_blocked_when_schema_errors_exist(self) -> None:
        evaluation = evaluate_status(
            required_checks=[make_check("bundle_validate", rc=0)],
            schema_errors=["STATUS.json: expected object"],
            blockers=[],
            internal_errors=[],
        )
        self.assertEqual(BLOCKED, evaluation.status)
        self.assertEqual(2, evaluation.exit_code)
        self.assertEqual(("STATUS.json: expected object",), evaluation.schema_errors)

    def test_fail_when_internal_error_exists(self) -> None:
        evaluation = evaluate_status(
            required_checks=[make_check("integrate", rc=0)],
            schema_errors=[],
            blockers=[],
            internal_errors=["traceback: boom"],
        )
        self.assertEqual(FAIL, evaluation.status)
        self.assertEqual(1, evaluation.exit_code)
        self.assertEqual(("traceback: boom",), evaluation.internal_errors)

    def test_make_check_default_status_follows_rc(self) -> None:
        self.assertEqual("PASS", make_check("ok", rc=0)["status"])
        self.assertEqual("BLOCKED", make_check("bad", rc=2)["status"])

    def test_normalize_check_rc_overrides_pass_status(self) -> None:
        normalized = normalize_check(
            {
                "name": "schema",
                "status": "PASS",
                "rc": 2,
                "required": True,
            }
        )
        self.assertEqual("BLOCKED", normalized["status"])
        self.assertEqual(2, normalized["rc"])

    def test_status_exit_code_mapping(self) -> None:
        self.assertEqual(0, status_exit_code("PASS"))
        self.assertEqual(2, status_exit_code("BLOCKED"))
        self.assertEqual(1, status_exit_code("FAIL"))
        self.assertEqual(0, status_exit_code("WARN"))
        self.assertEqual(3, status_exit_code(PENDING))

    def test_combine_statuses(self) -> None:
        self.assertEqual(PASS, combine_statuses(["PASS", "PASS"]))
        self.assertEqual(BLOCKED, combine_statuses(["PASS", "BLOCKED"]))
        self.assertEqual(FAIL, combine_statuses(["PASS", "FAIL"]))
        self.assertEqual(BLOCKED, combine_statuses(["PASS", "WARN"], fail_on_warn=True))

    def test_evaluation_dict_shape(self) -> None:
        evaluation = evaluate_status(
            required_checks=[make_check("preflight", rc=0)],
            optional_checks=[make_check("open_report", rc=1, required=False)],
            schema_errors=[],
            blockers=[],
            internal_errors=[],
        )
        payload = evaluation.to_dict()
        self.assertEqual(PASS, payload["status"])
        self.assertIn("required_checks", payload)
        self.assertIn("optional_checks", payload)
        self.assertIn("exit_code", payload)


if __name__ == "__main__":
    unittest.main()

