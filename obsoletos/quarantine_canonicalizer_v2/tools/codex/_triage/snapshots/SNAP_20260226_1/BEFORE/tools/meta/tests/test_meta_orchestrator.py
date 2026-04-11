from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from tools.meta.debt_parser import parse_repo_debt
from tools.meta.federation import evaluate_federation_status
from tools.meta.hashing import deterministic_debt_id
from tools.meta.meta_orchestrator import orchestrate, parse_args


class MetaGovDeterminismTests(unittest.TestCase):
    def test_debt_id_is_deterministic(self) -> None:
        a = deterministic_debt_id("repo-a", "  TODO: Fix parser  ")
        b = deterministic_debt_id("repo-a", "TODO:   fix parser")
        c = deterministic_debt_id("repo-b", "TODO: fix parser")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_federation_law(self) -> None:
        class Repo:
            def __init__(self, online: bool, status: str) -> None:
                self.online = online
                self.status = status

        blocked = evaluate_federation_status(
            [Repo(True, "BLOCKED"), Repo(True, "OK")], strict=False
        )
        self.assertEqual(blocked, "BLOCKED")

        degraded = evaluate_federation_status(
            [Repo(True, "OK"), Repo(False, "OFFLINE")], strict=True
        )
        self.assertEqual(degraded, "DEGRADED")

        degraded_default = evaluate_federation_status(
            [Repo(True, "OK"), Repo(False, "OFFLINE")], strict=False
        )
        self.assertEqual(degraded_default, "DEGRADED")


class MetaGovSmokeTests(unittest.TestCase):
    def _write(self, path: pathlib.Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = text if text.endswith("\n") else text + "\n"
        path.write_text(payload, encoding="utf-8")

    def _build_fake_repo(self, root: pathlib.Path, name: str, report_result: str) -> pathlib.Path:
        repo = root / name
        report = repo / "docs/govos/_reports/FINAL_REPORT.md"
        self._write(
            report,
            "\n".join(
                [
                    "# FINAL REPORT",
                    "",
                    f"RESULT: {report_result}",
                    "REPO_ROOT: C:/fake/" + name,
                    "CANONICAL_DOCS_ROOT: docs/govos",
                    "",
                    "## Mandatory First Read",
                    "",
                    "- KERNEL_CONTEXT.md: present",
                    "- docs/factory/FACTORY_RUNTIME_EXPLAINED.md: present",
                    "- additive_only_trigger: false",
                    "- resolution: pointer stub linked to docs/factory/CONTRACT.md",
                    "",
                    "## Debt",
                    "- TODO: audit cross-repo output",
                    "- DEBT: add canonical schema checks",
                ]
            ),
        )
        # fake docs doctor so repo is not marked missing tooling.
        self._write(repo / "tools/ops/Docs-Doctor.ps1", "Write-Host 'RESULT: OK'")
        return repo

    def test_smoke_orchestrator_generates_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            main_repo = self._build_fake_repo(root, "hitech-os", "OK")
            other_repo = root / "missing-repo"
            registry = root / "meta-root/docs/meta-gov/REPO_REGISTRY.yaml"
            registry.parent.mkdir(parents=True, exist_ok=True)
            registry.write_text(
                "\n".join(
                    [
                        "version: 1",
                        "timezone: America/Mexico_City",
                        "feature_flags:",
                        "  convergence_actions: OFF",
                        "  forced_repo_changes: OFF",
                        "repos:",
                        "  - name: hitech-os",
                        f"    path: {main_repo}",
                        "    docs_doctor: tools/ops/Docs-Doctor.ps1",
                        "  - name: offline-repo",
                        f"    path: {other_repo}",
                        "    docs_doctor: tools/ops/Docs-Doctor.ps1",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            # Compose args exactly as CLI does, using an explicit repo root.
            ns = parse_args(
                [
                    "--registry",
                    str(registry),
                    "--repo-root",
                    str(root / "meta-root"),
                    "--write",
                    "--no-run-docs-doctor",
                ]
            )
            rc = orchestrate(ns)
            self.assertEqual(rc, 0)

            status_path = root / "meta-root/docs/meta-gov/FEDERATION_STATUS.json"
            report_path = root / "meta-root/docs/meta-gov/META_REPORT.md"
            debt_path = root / "meta-root/docs/meta-gov/GLOBAL_DEBT_LOG.json"

            self.assertTrue(status_path.is_file())
            self.assertTrue(report_path.is_file())
            self.assertTrue(debt_path.is_file())

            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertIn(status["federation"]["status"], {"OK", "DEGRADED"})
            self.assertEqual(status["federation"]["timezone"], "America/Mexico_City")
            self.assertIn("inputs_hash", status["determinism"])
            self.assertIn("outputs_hash", status["determinism"])

    def test_repo_debt_parser_reads_reports_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            reports = root / "docs/govos/_reports"
            reports.mkdir(parents=True, exist_ok=True)
            (reports / "FINAL_REPORT.md").write_text(
                "# FINAL REPORT\n\n- TODO: follow up\n- DEBT: explicit item\n",
                encoding="utf-8",
            )
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src/app.py").write_text("TODO should be ignored\n", encoding="utf-8")

            items = parse_repo_debt("demo", root)
            self.assertEqual(len(items), 2)
            self.assertTrue(all(item.source_file.startswith("docs/govos/_reports/") for item in items))


if __name__ == "__main__":
    unittest.main(verbosity=2)
