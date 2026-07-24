#!/usr/bin/env python3
"""Synchronize canonical Tablet UI Certainty contracts from the RIFAT route authority."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PRISMA_HTML_ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_ROOT = PRISMA_HTML_ROOT / "authority" / "rifat"
TABLET_AUTHORITY = AUTHORITY_ROOT / "tablet"
PRISMA_UI_ROOT = AUTHORITY_ROOT / "prisma-ui"
APP_ROOT = "products/tablet/app"
BASE_URL = "http://127.0.0.1:3120"
SURFACE_ORDER = {
    "chart-lab": 0,
    "web": 1,
    "tablet": 2,
    "pc": 3,
    "mobile": 4,
    "control-center": 5,
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def route_id(route: str) -> str:
    if route == "/":
        return "tablet.root.route"
    suffix = re.sub(r"[^A-Za-z0-9]+", ".", route[1:]).strip(".")
    return f"tablet.{suffix}.route"


def page_file(route: str) -> str:
    relative = "" if route == "/" else route[1:]
    return f"{APP_ROOT}/app/{relative + '/' if relative else ''}page.tsx"


def is_dynamic(route: str) -> bool:
    return "[" in route and "]" in route


def contract_entry(binding: dict[str, Any]) -> dict[str, Any]:
    route = binding["route"]
    identifier = route_id(route)
    dynamic = is_dynamic(route)
    layouts = [f"{APP_ROOT}/app/layout.tsx"]
    if route == "/checkout":
        layouts.append(f"{APP_ROOT}/app/checkout/layout.tsx")
    return {
        "route_id": identifier,
        "panel_id": identifier,
        "app": "PRISMA Tablet Core",
        "surface": "tablet",
        "port": 3120,
        "route": route,
        "pageFile": page_file(route),
        "layoutFiles": layouts,
        "ownerComponent": page_file(route),
        "anchorOwnerComponent": f"{APP_ROOT}/app/layout.tsx",
        "middleware": f"{APP_ROOT}/middleware.ts",
        "currentPanelContract": "tablet.pos.workspace" if route == "/pos" else None,
        "runtimeUrl": None if dynamic else f"{BASE_URL}{'/' if route == '/' else route}",
        "runtimeMode": "source-only-dynamic-route" if dynamic else "runtime",
        "sourceJustification": (
            "Dynamic route requires a concrete sale identifier and is source-certified."
            if dynamic
            else None
        ),
        "redirectTarget": None,
        "anchors": {
            "data-prisma-panel": identifier,
            "data-prisma-surface": "tablet",
            "data-prisma-route": route,
        },
        "canonical_selectors": [f'[data-prisma-panel="{identifier}"]'],
        "allowed_files": [
            ".prisma-ui/current/**",
            ".prisma-ui/routes.json",
            "tools/quality/ui-certainty.mjs",
            "tools/quality/ui-runtime-certainty.mjs",
            "package.json",
            page_file(route),
            f"{APP_ROOT}/app/layout.tsx",
            f"{APP_ROOT}/middleware.ts",
            f"{APP_ROOT}/generated/prisma-visual-runtime/**",
        ],
    }


def visual_control_entry(contract: dict[str, Any]) -> dict[str, Any]:
    dynamic = contract["runtimeMode"] == "source-only-dynamic-route"
    return {
        "route_id": contract["route_id"],
        "human_id": f"PRISMA Tablet Core {contract['route']}",
        "app": contract["app"],
        "surface": "tablet",
        "route": contract["route"],
        "routePath": contract["route"],
        "pageFile": contract["pageFile"],
        "layoutFiles": contract["layoutFiles"],
        "ownerComponent": contract["ownerComponent"],
        "ownerCss": [f"{APP_ROOT}/generated/prisma-visual-runtime/prisma-tablet-runtime.css"],
        "currentPanelContract": contract["currentPanelContract"],
        "runtimeUrl": contract["runtimeUrl"],
        "runtimeMode": contract["runtimeMode"],
        "runtimeCertificationStatus": "SOURCE_CERTIFIED",
        "runtimeSourceCertification": "SOURCE_CERTIFIED",
        "certificationEvidence": "prisma-html/authority/rifat/tablet/routes.json",
        "anchors": contract["anchors"],
        "excludedSurfaces": ["chart-lab", "web", "pc", "mobile", "control-center"],
        "safetyClassification": "visualWithFunctionalRisk",
        "sourceOnlyReason": contract["sourceJustification"] if dynamic else None,
    }


def tablet_counts(entries: list[dict[str, Any]]) -> dict[str, Any]:
    dynamic = sum(entry["runtimeMode"] == "source-only-dynamic-route" for entry in entries)
    runtime = len(entries) - dynamic
    return {
        "app": "PRISMA Tablet Core",
        "port": 3120,
        "routeCount": len(entries),
        "runtimeRoutes": runtime,
        "sourceOnlyDynamicRoutes": dynamic,
        "sourceOnlyRedirectRoutes": 0,
        "runtimeCertifiedCount": 0,
        "sourceCertifiedCount": 0,
        "runtimeBlockedCount": 0,
    }


def ordered_with_tablet(
    existing: list[dict[str, Any]],
    tablet_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = [
        *[entry for entry in existing if entry.get("surface") != "tablet"],
        *tablet_entries,
    ]
    return sorted(merged, key=lambda entry: SURFACE_ORDER.get(entry.get("surface"), 99))


def main() -> int:
    route_authority = load(TABLET_AUTHORITY / "routes.json")
    bindings = route_authority["routes"]
    entries = [contract_entry(binding) for binding in bindings]
    route_names = [binding["route"] for binding in bindings]

    routes_path = PRISMA_UI_ROOT / "routes.json"
    routes = load(routes_path)
    routes["routes"] = ordered_with_tablet(routes["routes"], entries)
    routes["routeCount"] = len(routes["routes"])
    routes.setdefault("countsBySurface", {})["tablet"] = tablet_counts(entries)
    write(routes_path, routes)

    surfaces_path = PRISMA_UI_ROOT / "surfaces.json"
    surfaces = load(surfaces_path)
    tablet_surface = next(item for item in surfaces["surfaces"] if item["id"] == "tablet")
    tablet_surface["routes"] = route_names
    tablet_surface["owners"] = [
        f"{APP_ROOT}/app/layout.tsx",
        f"{APP_ROOT}/components/tablet-shell/prisma-tablet-shell.tsx",
        f"{APP_ROOT}/generated/prisma-visual-runtime/prisma-tablet-runtime.css",
    ]
    runtime_page_cert = surfaces.setdefault("runtimePageCertification", {})
    runtime_page_cert["routeCount"] = routes["routeCount"]
    runtime_page_cert.setdefault("countsBySurface", {})["tablet"] = tablet_counts(entries)
    write(surfaces_path, surfaces)

    registry_path = PRISMA_UI_ROOT / "registry.json"
    registry = load(registry_path)
    registry["routeCount"] = routes["routeCount"]
    write(registry_path, registry)

    visual_routes_path = PRISMA_UI_ROOT / "visual-control" / "routes.json"
    visual_routes = load(visual_routes_path)
    visual_entries = [visual_control_entry(entry) for entry in entries]
    visual_routes["routes"] = ordered_with_tablet(visual_routes["routes"], visual_entries)
    visual_routes["routeCount"] = len(visual_routes["routes"])
    write(visual_routes_path, visual_routes)

    print(
        json.dumps(
            {
                "status": "PASS",
                "canonicalRoutes": routes["routeCount"],
                "tabletRoutes": len(entries),
                "customerVisibleRoutes": route_authority["customerVisible"],
                "dynamicSourceCertifiedRoutes": sum(is_dynamic(route) for route in route_names),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
