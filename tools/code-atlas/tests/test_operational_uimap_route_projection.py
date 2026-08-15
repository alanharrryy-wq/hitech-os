from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from code_atlas.app_map.uimap.discovery import (
    RouteRecord,
    build_route_reachability,
    discover_routes,
    extract_ui_candidates_from_file,
    parallel_hash,
    resolve_import,
)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def route(path: str, source: str) -> RouteRecord:
    slug = path.strip("/").replace("/", ".") or "home"
    return RouteRecord(
        runtime_alias="pc",
        route_id=f"ROUTE.pc.{slug}",
        route_path=path,
        source_file=source,
        source_hash="A" * 64,
        kind="page",
    )


class UimapRouteProjectionTests(unittest.TestCase):
    def test_relative_import_behavior_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write(root / "src/a.ts", 'import "./b";\n')
            target = write(root / "src/b.ts", "export const b = 1;\n")
            self.assertEqual(resolve_import(source, "./b", root), target.resolve())

    def test_tsconfig_alias_resolves_and_external_package_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "tsconfig.json", json.dumps({
                "compilerOptions": {
                    "paths": {"@/*": ["./src/*"], "@components/*": ["./components/*"]}
                }
            }))
            source = write(root / "app/page.tsx", 'import X from "@components/widget";\n')
            expected = write(root / "components/widget.tsx", "export default function X(){return null}\n")
            write(root / "src/components/widget.tsx", "export default 0\n")
            self.assertEqual(resolve_import(source, "@components/widget", root), expected.resolve())
            self.assertIsNone(resolve_import(source, "react", root))

    def test_alias_escape_outside_runtime_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "runtime"
            write(root / "tsconfig.json", json.dumps({
                "compilerOptions": {"paths": {"@shared/*": ["../shared/*"]}}
            }))
            source = write(root / "app/page.tsx", 'import X from "@shared/widget";\n')
            write(base / "shared/widget.tsx", "export default 1\n")
            self.assertIsNone(resolve_import(source, "@shared/widget", root))

    def test_one_route_behavior_stays_single_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write(root / "workspace.tsx", 'export function W(){return <section className={styles.productFicha}/>;}')
            rows = extract_ui_candidates_from_file(
                "pc", source, root, [route("/stock", "app/stock/page.tsx")], hashlib.sha256(source.read_bytes()).hexdigest().upper()
            )
            self.assertTrue(rows)
            self.assertEqual({row.route_path for row in rows}, {"/stock"})

    def test_three_proven_routes_emit_three_route_specific_candidate_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write(root / "workspace.tsx", 'export function W(){return <section className={styles.productFicha}/>;}')
            routes = [
                route("/stock", "app/stock/page.tsx"),
                route("/auditoria-inventario", "app/auditoria-inventario/page.tsx"),
                route("/counts", "app/counts/page.tsx"),
            ]
            rows = extract_ui_candidates_from_file(
                "pc", source, root, routes, hashlib.sha256(source.read_bytes()).hexdigest().upper()
            )
            product_rows = [row for row in rows if row.class_name == "productFicha"]
            self.assertEqual(
                {row.route_path for row in product_rows},
                {"/auditoria-inventario", "/counts", "/stock"},
            )
            for route_path in {"/auditoria-inventario", "/counts", "/stock"}:
                self.assertTrue(any(row.route_path == route_path for row in product_rows))

    def test_duplicate_route_evidence_does_not_duplicate_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write(root / "workspace.tsx", 'export function W(){return <section className={styles.productFicha}/>;}')
            one = [route("/stock", "app/stock/page.tsx")]
            duplicate = [
                route("/stock", "app/stock/page.tsx"),
                route("/stock", "app/stock/alternate.tsx"),
            ]
            digest = hashlib.sha256(source.read_bytes()).hexdigest().upper()
            self.assertEqual(
                len(extract_ui_candidates_from_file("pc", source, root, one, digest)),
                len(extract_ui_candidates_from_file("pc", source, root, duplicate, digest)),
            )

    def test_route_order_does_not_change_candidate_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write(root / "workspace.tsx", 'export function W(){return <section className={styles.productFicha}/>;}')
            routes = [route("/stock", "s.tsx"), route("/counts", "c.tsx"), route("/auditoria-inventario", "a.tsx")]
            digest = hashlib.sha256(source.read_bytes()).hexdigest().upper()
            first = extract_ui_candidates_from_file("pc", source, root, routes, digest)
            second = extract_ui_candidates_from_file("pc", source, root, list(reversed(routes)), digest)
            shape = lambda rows: [
                (row.route_id, row.route_path, row.render_source_file, row.class_name, row.tag_name, row.widget_kind)
                for row in rows
            ]
            self.assertEqual(shape(first), shape(second))

    def test_unrouted_fallback_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write(root / "orphan.tsx", 'export function W(){return <button>Go</button>;}')
            rows = extract_ui_candidates_from_file(
                "pc", source, root, [], hashlib.sha256(source.read_bytes()).hexdigest().upper()
            )
            self.assertTrue(rows)
            self.assertEqual({row.route_path for row in rows}, {"/"})
            self.assertTrue(all(row.route_id.endswith(".unrouted") for row in rows))

    def test_alias_reachability_preserves_all_three_real_route_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            write(root / "tsconfig.json", json.dumps({"compilerOptions": {"paths": {"@components/*": ["./components/*"]}}}))
            workspace = write(root / "components/inventory/inventory-workspace.tsx", 'export function W(){return <section className={styles.productFicha}/>;}')
            pages = []
            for route_path in ("auditoria-inventario", "counts", "stock"):
                pages.append(write(
                    root / f"app/{route_path}/page.tsx",
                    'import { W } from "@components/inventory/inventory-workspace"; export default function Page(){return <W/>;}\n',
                ))
            hashes = parallel_hash([workspace, *pages])
            routes = discover_routes("pc", root, root, hashes)
            reach = build_route_reachability(root, root, routes)
            key = "components/inventory/inventory-workspace.tsx"
            self.assertIn(key, reach)
            self.assertEqual(
                {row.route_path for row in reach[key]},
                {"/auditoria-inventario", "/counts", "/stock"},
            )


if __name__ == "__main__":
    unittest.main()
