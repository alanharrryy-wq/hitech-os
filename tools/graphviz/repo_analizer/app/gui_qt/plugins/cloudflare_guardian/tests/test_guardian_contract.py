from __future__ import annotations

from unittest import TestCase

from app.gui_qt.plugins.cloudflare_guardian.guardian_contract import (
    build_guardian_cards,
    build_orchestrator_intent,
    normalize_guardian_context,
)


class GuardianContractTests(TestCase):
    def test_normalize_guardian_context_from_mapping(self) -> None:
        payload = {
            "hostname": "edge.example.com",
            "tunnel_id": "t-123",
            "origin_expected": "http://127.0.0.1:3100",
            "origin_observed": "http://localhost:3000",
            "config_path": "C:/cfg/config.yml",
            "last_good_state": "200 OK",
            "current_error": "502 bad gateway",
            "last_check_time": "2026-03-28T07:00:00Z",
        }
        normalized = normalize_guardian_context(payload).to_payload()
        self.assertEqual(normalized["hostname"], "edge.example.com")
        self.assertEqual(normalized["origin_observed"], "http://localhost:3000")

    def test_build_guardian_cards_contains_expected_sections(self) -> None:
        cards = build_guardian_cards(
            {
                "hostname": "edge.example.com",
                "tunnel_id": "t-123",
                "origin_expected": "http://127.0.0.1:3100",
                "origin_observed": "http://127.0.0.1:3100",
            }
        )
        self.assertEqual(set(cards.keys()), {"Health", "Path", "Evidence", "Config Drift"})
        self.assertIn("match", cards["Config Drift"].headline.lower())

    def test_build_orchestrator_intent_includes_action_and_identifiers(self) -> None:
        intent = build_orchestrator_intent(
            {
                "hostname": "edge.example.com",
                "tunnel_id": "t-123",
                "origin_expected": "http://127.0.0.1:3100",
                "origin_observed": "http://localhost:3000",
            },
            action="remediation",
        )
        self.assertIn("Apply Cloudflare Guardian remediation", intent)
        self.assertIn("edge.example.com", intent)
        self.assertIn("t-123", intent)

