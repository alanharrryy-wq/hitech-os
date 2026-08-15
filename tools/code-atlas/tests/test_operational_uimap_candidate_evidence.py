from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from code_atlas.app_map.uimap.discovery import RouteRecord, extract_ui_candidates_from_file


def route(path: str) -> RouteRecord:
    slug = path.strip('/').replace('/', '.') or 'home'
    return RouteRecord(
        runtime_alias='pc',
        route_id=f'ROUTE.pc.{slug}',
        route_path=path,
        source_file=f'app/{slug}/page.tsx',
        source_hash='A' * 64,
        kind='page',
    )


def extract(source_text: str):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / 'workspace.tsx'
        source.write_text(source_text, encoding='utf-8')
        digest = hashlib.sha256(source.read_bytes()).hexdigest().upper()
        return extract_ui_candidates_from_file('pc', source, root, [route('/stock')], digest)


class UimapCandidateEvidenceTests(unittest.TestCase):
    def test_rich_jsx_candidate_wins_over_css_fallback_for_same_class(self):
        rows = extract('''
export function W(){
  return <section
    className={styles.productFicha}
    data-prisma-component-ui-id="PC-STOCK-FICHA-PANEL-01"
    data-prisma-binding="BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1"
    data-prisma-region="ZONE.pc.stock.detail"
    data-prisma-slot="SLOT.pc.stock.detail.primary"
  />;
}
''')
        product = [row for row in rows if row.class_name == 'productFicha']
        self.assertEqual(len(product), 1)
        self.assertEqual(product[0].tag_name, 'section')
        self.assertEqual(product[0].data_attributes['data-prisma-component-ui-id'], 'PC-STOCK-FICHA-PANEL-01')
        self.assertEqual(product[0].data_attributes['data-prisma-binding'], 'BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1')

    def test_distinct_governed_markers_on_same_class_are_not_collapsed(self):
        rows = extract('''
export function W(){
  return <>
    <section className={styles.shared} data-prisma-component-ui-id="PC-A" data-prisma-binding="BND.A" />
    <section className={styles.shared} data-prisma-component-ui-id="PC-B" data-prisma-binding="BND.B" />
  </>;
}
''')
        shared = [row for row in rows if row.class_name == 'shared']
        self.assertEqual(len(shared), 2)
        self.assertEqual(
            {row.data_attributes['data-prisma-component-ui-id'] for row in shared},
            {'PC-A', 'PC-B'},
        )

    def test_css_only_fallback_is_preserved_when_no_jsx_owner_exists(self):
        rows = extract('''
export function W(){
  const visual = styles.cssOnlyPanel;
  return <div data-testid="root" />;
}
''')
        fallback = [row for row in rows if row.class_name == 'cssOnlyPanel']
        self.assertEqual(len(fallback), 1)
        self.assertEqual(fallback[0].tag_name, 'styled-slot')
        self.assertEqual(fallback[0].data_attributes, {})


if __name__ == '__main__':
    unittest.main()
