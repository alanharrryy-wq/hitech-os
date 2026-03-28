import importlib
import os
from pathlib import Path
from unittest import TestCase

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_ROOT = PACKAGE_ROOT.parent
if str(PLUGINS_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(PLUGINS_ROOT))

session_module = importlib.import_module("orchestrator_bridge.process_session_controller")


class ProcessSessionControllerTests(TestCase):
    def test_begin_launch_blocks_when_already_running(self):
        controller = session_module.ProcessSessionController()
        ok, detail = controller.begin_launch({"mode": "existing"})
        self.assertTrue(ok)
        self.assertEqual(detail, "ok")
        ok_again, detail_again = controller.begin_launch({"mode": "existing"})
        self.assertFalse(ok_again)
        self.assertEqual(detail_again, "run already in progress")

    def test_mark_started_timeout_finished_transitions(self):
        controller = session_module.ProcessSessionController()
        controller.begin_launch({"mode": "existing"})
        self.assertEqual(controller.snapshot.state, "validating")
        controller.mark_started()
        self.assertEqual(controller.snapshot.state, "running")
        controller.mark_run_timeout()
        self.assertEqual(controller.snapshot.state, "failed")
        controller.mark_finished("success")
        self.assertEqual(controller.snapshot.state, "succeeded")
        self.assertFalse(controller.snapshot.run_in_progress)

    def test_restore_last_payload_with_invalid_data_sets_blocked(self):
        controller = session_module.ProcessSessionController()
        ok, detail = controller.restore_last_payload(
            {"mode": "existing"},
            validator=lambda _payload: ["invalid payload"],
        )
        self.assertFalse(ok)
        self.assertIn("invalid payload", detail)
        self.assertEqual(controller.snapshot.state, "blocked")

    def test_transition_notifier_receives_state_changes(self):
        events = []
        controller = session_module.ProcessSessionController(
            transition_notifier=lambda payload: events.append(dict(payload))
        )
        controller.begin_launch({"mode": "existing"})
        controller.mark_started()
        controller.cancel(reason="manual-test")
        self.assertGreaterEqual(len(events), 3)
        self.assertEqual(events[-1]["state"], "cancelled")
        self.assertEqual(events[-1]["reason"], "manual-test")
