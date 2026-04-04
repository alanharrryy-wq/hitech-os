from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from unittest import mock

from forgeos.shared.pyside6_glass import release_gate


class ReleaseGateTests(unittest.TestCase):
    def test_contract_lists_40_capabilities(self) -> None:
        capabilities = release_gate.load_contract_capabilities()
        self.assertGreaterEqual(len(capabilities), release_gate.REQUIRED_CAPABILITIES)
        self.assertIn("Window resize is stable from corners and edges.", capabilities[0])

    def test_release_gate_quick_mode_writes_evidence(self) -> None:
        result = release_gate.run_release_gate(run_tests=False, run_proof=False)
        self.assertTrue(bool(result.get("passed")))
        evidence_path = Path(str(result.get("evidence_path", "")))
        self.assertTrue(evidence_path.is_file())
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["required_capabilities"], release_gate.REQUIRED_CAPABILITIES)
        self.assertGreaterEqual(payload["detected_capabilities"], release_gate.REQUIRED_CAPABILITIES)

        # Keep local evidence, but ensure path stays under allowed local artifact root.
        allowed_root = Path("tools/_local/evidence").resolve()
        common = os.path.commonpath([str(evidence_path.resolve()), str(allowed_root)])
        self.assertEqual(common, str(allowed_root))

    def test_release_gate_consumes_proof_summary(self) -> None:
        fake_delta = [
            {
                "capability_id": index,
                "release_blocker": bool(index <= 40),
                "after_status": "solid",
                "capability": f"capability {index}",
            }
            for index in range(1, 101)
        ]
        fake_summary = {
            "passed": True,
            "run_dir": "f:/tmp/proof",
            "baseline_version": "v1",
            "comparator": {"diff_count": 0},
            "capability_delta": fake_delta,
        }

        def _fake_run(command: list[str], *, cwd: Path) -> release_gate.GateCheck:
            joined = " ".join(command)
            if "ux_flight_recorder.runner" in joined:
                return release_gate.GateCheck(
                    name=joined,
                    command=command,
                    passed=True,
                    returncode=0,
                    stdout=json.dumps(fake_summary),
                    stderr="",
                )
            return release_gate.GateCheck(
                name=joined,
                command=command,
                passed=True,
                returncode=0,
                stdout="ok",
                stderr="",
            )

        with mock.patch("forgeos.shared.pyside6_glass.release_gate._run", side_effect=_fake_run):
            result = release_gate.run_release_gate(run_tests=False, run_proof=True)
        self.assertTrue(bool(result.get("passed")))
        self.assertTrue(bool(result.get("proof_passed")))
        self.assertEqual(result.get("proof_run_dir"), "f:/tmp/proof")

    def test_nightly_visual_proof_is_non_blocking(self) -> None:
        commands: list[list[str]] = []

        def _fake_run(command: list[str], *, cwd: Path) -> release_gate.GateCheck:
            commands.append(command)
            joined = " ".join(command)
            if "py_compile" in joined:
                return release_gate.GateCheck(
                    name=joined,
                    command=command,
                    passed=True,
                    returncode=0,
                    stdout="compiled",
                    stderr="",
                )
            if "ux_flight_recorder.runner" in joined:
                return release_gate.GateCheck(
                    name=joined,
                    command=command,
                    passed=False,
                    returncode=2,
                    stdout='{"passed": false, "run_dir": "f:/tmp/nightly"}',
                    stderr="nightly visual failed",
                )
            return release_gate.GateCheck(
                name=joined,
                command=command,
                passed=True,
                returncode=0,
                stdout="ok",
                stderr="",
            )

        with mock.patch("forgeos.shared.pyside6_glass.release_gate._run", side_effect=_fake_run):
            result = release_gate.run_release_gate(
                run_tests=False,
                run_proof=False,
                nightly_visual_proof=True,
            )

        self.assertTrue(bool(result.get("passed")), msg=f"gate should stay passing: {result}")
        nightly = result.get("nightly_visual_proof", {})
        self.assertIsInstance(nightly, dict)
        self.assertFalse(bool(nightly.get("passed")))
        self.assertTrue(bool(nightly.get("non_blocking")))
        command = nightly.get("command", [])
        self.assertIn("forgeos.shared.pyside6_glass.ux_flight_recorder.runner", " ".join(command))
        self.assertNotIn("--no-screenshots", command)
        self.assertIn("--extra-evidence-tag", command)
        self.assertIn("check:nightly_visual_proof:pass", command)


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    unittest.main()
