from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

from tests.helpers import project_root


class SmokeTests(unittest.TestCase):
    def test_doctor_and_run_pipeline(self) -> None:
        root = project_root()
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root)
        with tempfile.TemporaryDirectory() as out_dir:
            doctor = subprocess.run(
                [sys.executable, "-m", "pya.tools.pya", "doctor", "--root", str(root)],
                cwd=str(root),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(doctor.returncode, 0, msg=doctor.stdout + doctor.stderr)
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pya.tools.pya",
                    "run",
                    "--root",
                    str(root),
                    "--target",
                    str(root / "examples" / "sample_app"),
                    "--out",
                    out_dir,
                ],
                cwd=str(root),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, msg=run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
