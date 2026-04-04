from __future__ import annotations

import unittest

from infrastructure.event_bus_in_memory import InMemoryEventBus


class EventBusContractTests(unittest.TestCase):
    def test_publish_delivers_payload(self) -> None:
        bus = InMemoryEventBus()
        received: list[object] = []

        bus.subscribe("session_created", received.append)
        bus.publish("session_created", {"session_id": "s-1"})

        self.assertEqual(received, [{"session_id": "s-1"}])

    def test_unsubscribe_stops_delivery(self) -> None:
        bus = InMemoryEventBus()
        received: list[object] = []

        unsubscribe = bus.on("filesystem_changed", received.append)
        unsubscribe()
        bus.emit("filesystem_changed", {"path": "/tmp/demo.txt"})

        self.assertEqual(received, [])

    def test_emit_event_infers_name_from_dict(self) -> None:
        bus = InMemoryEventBus()
        received: list[object] = []

        bus.subscribe("plan_finished", received.append)
        bus.emit_event({"event_name": "plan_finished", "ok": True})

        self.assertEqual(received, [{"event_name": "plan_finished", "ok": True}])


if __name__ == "__main__":
    unittest.main()
