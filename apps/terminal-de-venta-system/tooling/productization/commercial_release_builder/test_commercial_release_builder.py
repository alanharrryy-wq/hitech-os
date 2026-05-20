from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import commercial_release_builder as builder

class CommercialReleaseBuilderTests(unittest.TestCase):
    def test_tablet_solo_policy_is_independent(self) -> None:
        self.assertTrue(builder.TABLET_SOLO_POLICY["tabletMaySellWithoutPc"])
        self.assertTrue(builder.TABLET_SOLO_POLICY["tabletMaySellWithoutInternet"])
        self.assertTrue(builder.TABLET_SOLO_POLICY["tabletMaySellWithoutMobile"])
        self.assertFalse(builder.TABLET_SOLO_POLICY["pcRequiredForSales"])
        self.assertFalse(builder.TABLET_SOLO_POLICY["mobileRequiredForSales"])
        self.assertFalse(builder.TABLET_SOLO_POLICY["remoteCareRequiredForSales"])

    def test_exclusion_blocks_db_env_and_legacy_required_names(self) -> None:
        root = Path(tempfile.mkdtemp())
        for name in [".env", "tablet.db", "tablet-pc-required.active.license.json"]:
            path = root / name
            path.write_text("x", encoding="utf-8")
            self.assertTrue(builder.should_exclude(path, root)[0], name)

if __name__ == "__main__":
    unittest.main()
