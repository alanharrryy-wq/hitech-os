from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
checks = []

def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"MISSING: {rel}")
    return p.read_text(encoding="utf-8", errors="replace")

def require(rel: str, needle: str) -> None:
    text = read(rel)
    if needle not in text:
        raise SystemExit(f"FAIL: {rel} no contiene {needle!r}")
    checks.append(f"PASS contains {needle}: {rel}")

def reject(rel: str, needle: str) -> None:
    text = read(rel)
    if needle in text:
        raise SystemExit(f"FAIL: {rel} todavía contiene {needle!r}")
    checks.append(f"PASS rejects {needle}: {rel}")

def brace_balance(rel: str) -> None:
    text = read(rel)
    stack = 0
    for ch in text:
        if ch == "{": stack += 1
        elif ch == "}": stack -= 1
        if stack < 0:
            raise SystemExit(f"FAIL: brace balance underflow en {rel}")
    if stack != 0:
        raise SystemExit(f"FAIL: brace balance final {stack} en {rel}")
    checks.append(f"PASS brace balance: {rel}")

require("products/pc/app/app/components/PrismaAtmosphericBackground.tsx", "cloudglass-mist-v2-executive-pearl")
require("products/pc/app/app/components/PrismaAtmosphericBackground.tsx", "prisma-bg-pearl-mist")
require("products/pc/app/app/components/PrismaAtmosphericBackground.tsx", "prisma-bg-distant-mist")
require("products/pc/app/app/prisma-atmospheric-background.css", "--prisma-bg-asset-size: auto 96%")
require("products/pc/app/app/prisma-atmospheric-background.css", ".prisma-bg-pearl-mist")
require("products/pc/app/app/prisma-atmospheric-background.css", "prismaPearlMistDrift")
require("products/pc/app/app/prisma-atmospheric-background.css", "prefers-reduced-motion")
reject("products/pc/app/app/prisma-atmospheric-background.css", "background-size: cover")
require("products/pc/app/app/dashboard/hoy-premium.module.css", "Executive Pearl")
require("products/pc/app/app/dashboard/hoy-premium.module.css", "Diamond Specular Kiss")
require("products/pc/app/app/dashboard/hoy-premium.module.css", ".heroPanel::after")
require("products/pc/app/app/dashboard/hoy-premium.module.css", ".urgentCard::after")
require("products/pc/app/app/dashboard/hoy-premium.module.css", "outline-offset: -9px")
brace_balance("products/pc/app/app/prisma-atmospheric-background.css")
brace_balance("products/pc/app/app/dashboard/hoy-premium.module.css")
print("\n".join(checks))
print("PASS: PRISMA PC Dashboard Cloudglass Mist v2 verifier complete")
