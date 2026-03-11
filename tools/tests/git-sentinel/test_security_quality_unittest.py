from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos._core.stable_json import write_json
from tools.hos.git_sentinel.config import build_config
from tools.hos.git_sentinel.false_positive import apply_false_positive_feedback, load_feedback
from tools.hos.git_sentinel.security_quality import evaluate_security_dataset
from tools.hos.git_sentinel.security_scanner import scan_text_security


class SecurityQualityTests(unittest.TestCase):
    def test_entropy_detection_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = build_config(repo_root=tmp)
            findings = scan_text_security(
                config=config,
                rel_path="apps/api/auth.ts",
                text='const token = "A8f9K2LmQ1xZ7pV4nR6tY3wB5cD8eF1g";\n',
            )
            kinds = {str(row.get("kind", "")) for row in findings}
            self.assertIn("generic_api_key", kinds)
            self.assertIn("high_entropy_secret", kinds)

    def test_docs_context_downgrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = build_config(repo_root=tmp)
            findings = scan_text_security(
                config=config,
                rel_path="docs/example.md",
                text='const apiKey = "abc123456789";\n',
            )
            self.assertTrue(findings)
            generic_rows = [row for row in findings if str(row.get("kind", "")) == "generic_api_key"]
            self.assertTrue(generic_rows)
            self.assertEqual("low", str(generic_rows[0].get("severity", "")))

    def test_expired_suppression_does_not_hide_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            config_override = {
                "false_positive_feedback_path": "tools/_local/git_sentinel/state/false_positive_feedback.json"
            }
            config_override_path = repo_root / "config.json"
            write_json(config_override_path, config_override, indent=2, sort_keys=True)

            config = build_config(repo_root=tmp, config_path=str(config_override_path))
            feedback_path = repo_root / "tools/_local/git_sentinel/state/false_positive_feedback.json"
            feedback_path.parent.mkdir(parents=True, exist_ok=True)
            write_json(
                feedback_path,
                {
                    "version": 2,
                    "suppressions": [
                        {
                            "id": "expired-1",
                            "match": {"type": "kind", "value": "generic_api_key"},
                            "owner": "qa",
                            "reason": "expired test",
                            "createdAt": "2026-01-01T00:00:00+00:00",
                            "expiresAt": "2026-01-02T00:00:00+00:00",
                            "active": True,
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )

            feedback = load_feedback(config)
            kept, suppressed, summary, _audit = apply_false_positive_feedback(
                findings=[
                    {
                        "kind": "generic_api_key",
                        "path": "apps/x.ts",
                        "line": 1,
                        "fingerprint": "f1",
                    }
                ],
                feedback=feedback,
            )
            self.assertEqual(1, len(kept))
            self.assertEqual(0, len(suppressed))
            self.assertEqual(1, int(summary.get("expiredSuppressionCount", 0)))

    def test_golden_dataset_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            dataset_path = repo_root / "golden.json"
            write_json(
                dataset_path,
                {
                    "version": 1,
                    "cases": [
                        {
                            "id": "c1",
                            "path": "apps/x.py",
                            "content": 'API_KEY = "sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n',
                            "expected": [
                                {"kind": "openai_key", "line": 1},
                                {"kind": "generic_api_key", "line": 1},
                            ],
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            config = build_config(repo_root=tmp)
            payload = evaluate_security_dataset(config=config, dataset_path=str(dataset_path))
            self.assertTrue(bool(payload.get("passed", False)))


if __name__ == "__main__":
    unittest.main()
