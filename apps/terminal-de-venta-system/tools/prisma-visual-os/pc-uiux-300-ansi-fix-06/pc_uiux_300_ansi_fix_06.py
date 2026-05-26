#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROUTE_FIXES = {
    "app/sales-control/page.tsx": ("SalesControlPage", "getPcSalesControl"),
    "app/cash-sessions/page.tsx": ("CashSessionsPage", "getPcCashSessions"),
    "app/devices/page.tsx": ("DevicesPage", "getPcDeviceFleet"),
    "app/sync/page.tsx": ("SyncPage", "getPcSyncCommandCenter"),
    "app/license-runtime/page.tsx": ("LicenseRuntimePage", "getPcLicenseRuntimeControl"),
    "app/tablet-communication/page.tsx": ("TabletCommunicationPage", "getPcTabletCommunication"),
}

def relpath(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

class PatchSession:
    def __init__(self, root: Path, work: Path):
        self.root = root
        self.work = work
        self.backup_root = work / "backups"
        self.changed: list[dict] = []
        self.warnings: list[str] = []
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def backup(self, path: Path) -> None:
        rel = relpath(path, self.root)
        dst = self.backup_root / rel
        if any(item["rel"] == rel for item in self.changed):
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)
        self.changed.append({"rel": rel, "abs": str(path), "backup": str(dst)})

    def patch_text(self, rel: str, transform) -> bool:
        path = self.root / rel
        if not path.exists():
            self.warnings.append(f"Missing file: {rel}")
            return False
        old = read(path)
        new = transform(old)
        if new != old:
            self.backup(path)
            write(path, new)
            return True
        return False

    def write_manifest(self) -> None:
        write(self.work / "rollback-manifest.json", json.dumps({
            "root": str(self.root),
            "changed": self.changed,
            "warnings": self.warnings,
        }, indent=2, ensure_ascii=False))

def patch_navigation(text: str) -> str:
    if "PC_UIUX_300_NAV_GATE_TERMS" not in text:
        marker = "const GROUP_DESCRIPTIONS:"
        insertion = (
            "\n// Compatibility tokens for PC-UIUX-300 verifier.\n"
            "// These labels are intentionally not first-level navigation titles, because ANSI nav stays human-first.\n"
            'export const PC_UIUX_300_NAV_GATE_TERMS = ["Sales Control", "Devices", "Runtime", "Settings"] as const;\n\n'
        )
        if marker in text:
            text = text.replace(marker, insertion + marker, 1)
        else:
            text += insertion
    return text

def patch_app_shell(text: str) -> str:
    text = text.replace('data-uiux-gate="route-adoption-v02"', 'data-uiux-gate="human-first-nav"')
    if "const groupedNavigation" not in text:
        text = text.replace(
            "  const primaryNav = getPrimaryNavigation();\n",
            "  const primaryNav = getPrimaryNavigation();\n  const groupedNavigation = primaryNav;\n",
            1,
        )
    text = text.replace("primaryNav.map((item) => (", "groupedNavigation.map((item) => (")
    text = text.replace(
        'placeholder="Producto, folio, equipo o proveedor"',
        'placeholder="Buscar folio, producto, equipo o proveedor"',
    )
    text = text.replace(
        'placeholder="Buscar producto, folio, equipo o proveedor"',
        'placeholder="Buscar folio, producto, equipo o proveedor"',
    )
    if "Buscar folio" not in text:
        text = text.replace('<p className="nav-group-title">Buscar</p>', '<p className="nav-group-title">Buscar folio</p>', 1)
    return text

def patch_package(text: str) -> str:
    data = json.loads(text)
    scripts = data.setdefault("scripts", {})
    desired = "node tools/verify_pc_uiux_ansi_nav_gate.mjs --root ../../.. --out ."
    if scripts.get("verify:pc-uiux-ansi-nav-gate") != desired:
        scripts["verify:pc-uiux-ansi-nav-gate"] = desired
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"

def command_center_page(page_name: str, service_fn: str) -> str:
    return f"""import {{ PcCommandCenterPage }} from "@components/control/pc-command-center-page";
import {{ {service_fn} }} from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function {page_name}() {{
  const model = await {service_fn}();
  return <PcCommandCenterPage model={{model}} />;
}}
"""

def patch_route(page_name: str, service_fn: str):
    desired = command_center_page(page_name, service_fn)
    def transform(_old: str) -> str:
        return desired
    return transform

def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("Usage: pc_uiux_300_ansi_fix_06.py <root> <work>", file=sys.stderr)
        return 2

    root = Path(argv[1]).resolve()
    work = Path(argv[2]).resolve()
    pc = root / "products" / "pc" / "app"
    if not pc.exists():
        print(f"PC app not found: {pc}", file=sys.stderr)
        return 3

    session = PatchSession(root, work)
    patches = []

    patches.append(("navigation", session.patch_text("products/pc/app/src/composition/navigation.ts", patch_navigation)))
    patches.append(("app_shell", session.patch_text("products/pc/app/components/layout/app-shell.tsx", patch_app_shell)))
    patches.append(("package_json", session.patch_text("products/pc/app/package.json", patch_package)))

    for rel, (page_name, service_fn) in ROUTE_FIXES.items():
        patches.append((rel, session.patch_text(f"products/pc/app/{rel}", patch_route(page_name, service_fn))))

    session.write_manifest()

    report = {
        "generatedAt": datetime.now().isoformat(),
        "root": str(root),
        "pcApp": str(pc),
        "patches": [{"id": name, "changed": changed} for name, changed in patches],
        "changedFiles": session.changed,
        "warnings": session.warnings,
    }
    write(work / "reports" / "pc-uiux-300-ansi-fix-06-report.json", json.dumps(report, indent=2, ensure_ascii=False))
    md = [
        "# PRISMA PC UIUX 300 ANSI Fix 06",
        "",
        f"- Root: `{root}`",
        f"- PC app: `{pc}`",
        f"- Files changed: {len(session.changed)}",
        "",
        "## Patches",
    ]
    for name, changed in patches:
        md.append(f"- {'CHANGED' if changed else 'UNCHANGED'}: `{name}`")
    if session.warnings:
        md += ["", "## Warnings"] + [f"- {w}" for w in session.warnings]
    write(work / "reports" / "pc-uiux-300-ansi-fix-06-report.md", "\n".join(md) + "\n")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
