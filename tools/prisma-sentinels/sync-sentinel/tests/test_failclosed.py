from __future__ import annotations

import subprocess
import unittest

from sync_sentinel.model import Check, RunReport, Verdict
from sync_sentinel.orchestration import _result_from_process


class FailClosedTests(unittest.TestCase):
    def test_f_unknown_zero_exit_without_pass_token_is_not_green(self):
        cp = subprocess.CompletedProcess(["x"], 0, stdout="hello", stderr="")
        check = _result_from_process("x", cp, ["EXPECTED_PASS"])
        self.assertEqual(check.verdict, Verdict.UNKNOWN)

    def test_g_nonzero_is_fail(self):
        cp = subprocess.CompletedProcess(["x"], 3, stdout="", stderr="bad")
        check = _result_from_process("x", cp)
        self.assertEqual(check.verdict, Verdict.FAIL)

    def test_h_report_fail_dominates(self):
        r = RunReport("test")
        r.add(Check("pass", Verdict.PASS, "ok"))
        r.add(Check("fail", Verdict.FAIL, "bad"))
        self.assertEqual(r.finalize(), Verdict.FAIL)

    def test_i_blocked_dominates_unknown_but_not_fail(self):
        r = RunReport("test")
        r.add(Check("unknown", Verdict.UNKNOWN, "?"))
        r.add(Check("blocked", Verdict.BLOCKED, "blocked"))
        self.assertEqual(r.finalize(), Verdict.BLOCKED)

    def test_j_empty_report_is_unknown(self):
        r = RunReport("test")
        self.assertEqual(r.finalize(), Verdict.UNKNOWN)
