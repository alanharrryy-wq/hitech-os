from __future__ import annotations

import unittest

from tools.ui_map.ids import asset_id, component_id, route_id, state_id, style_id


class IdDeterminismTests(unittest.TestCase):
    def test_component_id_is_stable(self) -> None:
        first = component_id("apps/keystone/components/pitch/screen-double-engine.tsx", "ScreenDoubleEngine")
        second = component_id("apps/keystone/components/pitch/screen-double-engine.tsx", "ScreenDoubleEngine")
        self.assertEqual(first, second)

    def test_ids_change_when_seed_changes(self) -> None:
        self.assertNotEqual(route_id("/pitch/01-double-engine"), route_id("/pitch/02-industrial-flow"))
        self.assertNotEqual(state_id("a.ts"), state_id("b.ts"))
        self.assertNotEqual(style_id("a.css"), style_id("b.css"))
        self.assertNotEqual(asset_id("a.svg"), asset_id("b.svg"))


if __name__ == "__main__":
    unittest.main()
