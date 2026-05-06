#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
let failed = false;
function ok(message) { console.log(`OK ${message}`); }
function fail(message) { console.error(`FAIL ${message}`); failed = true; }
function read(rel) { const file = path.join(root, rel); if (!fs.existsSync(file)) { fail(`missing ${rel}`); return ""; } return fs.readFileSync(file, "utf8"); }
function fileSize(rel) { return Buffer.byteLength(read(rel), "utf8"); }
function meaningfulLineCount(text) { return text.split(/\r?\n/).filter((line) => { const t = line.trim(); return t && !t.startsWith("//") && !t.startsWith("/*") && !t.startsWith("*"); }).length; }
function duplicateLineRatio(text) { const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean); if (!lines.length) return 0; return 1 - new Set(lines).size / lines.length; }
function assertProfessionalFile(rel, options = {}) {
  const text = read(rel);
  const size = fileSize(rel);
  const loc = meaningfulLineCount(text);
  const duplicate = duplicateLineRatio(text);
  if (size < (options.minSize ?? 200)) fail(`${rel} too small to be meaningful: ${size}`); else ok(`${rel} size ${size}`);
  if (loc < (options.minLoc ?? 10)) fail(`${rel} weak LOC: ${loc}`); else ok(`${rel} meaningful LOC ${loc}`);
  if (duplicate > (options.maxDuplicate ?? 0.55)) fail(`${rel} duplicate ratio too high: ${duplicate.toFixed(2)}`); else ok(`${rel} duplicate ratio ${duplicate.toFixed(2)}`);
  for (const forbidden of ["lorem", "TODO TODO", "foo", "bar", "dummy", "placeholder placeholder"]) {
    if (text.toLowerCase().includes(forbidden)) fail(`${rel} contains filler marker ${forbidden}`);
  }
}

const implementationFiles = [
  ["src/server/tablet-runtime-snapshot/build.ts", { minSize: 3500, minLoc: 70 }],
  ["src/server/tablet-runtime-snapshot/queries.prisma.ts", { minSize: 3500, minLoc: 70 }],
  ["src/lib/tablet-runtime-snapshot/shell-contract.ts", { minSize: 3000, minLoc: 80 }],
  ["src/lib/tablet-runtime-snapshot/view-model.ts", { minSize: 2500, minLoc: 45 }],
  ["src/lib/tablet-home/home-view-model.ts", { minSize: 3500, minLoc: 65 }],
  ["src/lib/tablet-home/operational-priority.ts", { minSize: 6200, minLoc: 130 }],
  ["components/tablet-home/tablet-home-screen.tsx", { minSize: 3000, minLoc: 60 }],
  ["components/tablet-home/tablet-home.module.css", { minSize: 5200, minLoc: 110 }],
  ["src/lib/pos/cart-engine.ts", { minSize: 4500, minLoc: 90 }],
  ["src/lib/pos/cart-view-model.ts", { minSize: 1100, minLoc: 25 }],
  ["components/pos/pos-screen.tsx", { minSize: 4500, minLoc: 85 }],
  ["components/pos/pos-ticket-panel.tsx", { minSize: 4500, minLoc: 85 }]
];
for (const [rel, opts] of implementationFiles) assertProfessionalFile(rel, opts);

const importRules = [
  { rel: "components/tablet-shell/prisma-tablet-shell.tsx", must: ["TabletRuntimeStatusStrip", "DEFAULT_TABLET_RUNTIME_SNAPSHOT", "TabletRuntimeSnapshot"] },
  { rel: "app/page.tsx", must: ["getTabletRuntimeSnapshot", "TabletHomeScreen", "runtimeSnapshot={snapshot}"] },
  { rel: "src/lib/tablet-home/home-view-model.ts", must: ["buildTabletOperationalPriorities", "alerts: TabletHomeAlert[]"] },
  { rel: "src/lib/tablet-home/operational-priority.ts", must: ["buildTabletOperationalPriorities", "getHighestOperationalPriority", "reasonSignals", "connection_conflict"] },
  { rel: "components/pos/pos-screen.tsx", must: ["addProductToCart", "incrementCartLine", "decrementCartLine", "removeCartLine", "clearCart"] },
  { rel: "components/pos/pos-ticket-panel.tsx", must: ["buildCartPanelViewModel", "view.checkoutReady", "view.checkoutReason"] }
];
for (const rule of importRules) {
  const text = read(rule.rel);
  for (const needle of rule.must) text.includes(needle) ? ok(`${rule.rel} imports/uses ${needle}`) : fail(`${rule.rel} missing ${needle}`);
}

const blockedWriteTargets = [
  "schema.prisma",
  "packages/shared-kernel",
  "products/pc",
  "products/mobile",
  "shared/contracts"
];
const installedDocs = [
  "docs/ux/PRISMA_TABLET_RUNTIME_SNAPSHOT_03B.md",
  "docs/ux/PRISMA_TABLET_HOME_SCREEN_03C.md",
  "docs/ux/PRISMA_TABLET_SELL_CART_03D_FOUNDATION.md",
  "docs/architecture/PRISMA_TABLET_RUNTIME_HOME_03B_03C_CONTRACT.md"
];
function hasBlockedWriteClaim(lower, blocked) {
  const b = blocked.toLowerCase();
  const positiveClaims = [
    `modifica ${b}`,
    `modificar ${b}`,
    `escribe ${b}`,
    `escribir ${b}`,
    `toca ${b}`,
    `tocar ${b}`,
    `crea ${b}`,
    `crear ${b}`
  ];
  const safeNegations = [
    `no modifica ${b}`,
    `no modificar ${b}`,
    `no se modifica ${b}`,
    `no escribe ${b}`,
    `no escribir ${b}`,
    `no se escribe ${b}`,
    `no toca ${b}`,
    `no tocar ${b}`,
    `no se toca ${b}`,
    `sin tocar ${b}`,
    `no crea ${b}`,
    `no crear ${b}`,
    `no se crea ${b}`
  ];
  return positiveClaims.some((claim) => lower.includes(claim)) && !safeNegations.some((safe) => lower.includes(safe));
}

for (const rel of installedDocs) {
  const text = read(rel);
  for (const blocked of blockedWriteTargets) {
    const lower = text.toLowerCase();
    if (hasBlockedWriteClaim(lower, blocked)) fail(`${rel} appears to claim blocked target ${blocked}`);
  }
  ok(`${rel} does not claim blocked writes`);
}

const manifestHints = [
  "Runtime Snapshot",
  "Home Screen",
  "carrito",
  "No toca",
  "schema.prisma",
  "shared-kernel"
];
const readme = read("docs/ux/PRISMA_TABLET_SELL_CART_03D_FOUNDATION.md") + read("docs/ux/PRISMA_TABLET_RUNTIME_SNAPSHOT_03B.md") + read("docs/ux/PRISMA_TABLET_HOME_SCREEN_03C.md");
for (const hint of manifestHints) {
  if (!readme.includes(hint)) fail(`documentation missing hint ${hint}`); else ok(`documentation covers ${hint}`);
}

if (failed) process.exit(1);
ok("quality gate confirms non-filler implementation shape");
