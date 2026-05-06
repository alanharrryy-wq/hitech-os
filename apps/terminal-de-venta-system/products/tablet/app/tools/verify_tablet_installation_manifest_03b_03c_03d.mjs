#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
let failed = false;
function ok(message){ console.log(`OK ${message}`); }
function fail(message){ console.error(`FAIL ${message}`); failed = true; }
function exists(rel){ return fs.existsSync(path.join(root, rel)); }

const requiredByLayer = {
  shell: [
    "components/tablet-shell/tablet-nav.ts",
    "components/tablet-shell/prisma-tablet-shell.tsx",
    "components/tablet-shell/prisma-tablet-shell.module.css"
  ],
  runtime: [
    "src/lib/tablet-runtime-snapshot/shell-contract.ts",
    "src/lib/tablet-runtime-snapshot/view-model.ts",
    "src/server/tablet-runtime-snapshot/index.ts",
    "src/server/tablet-runtime-snapshot/build.ts",
    "src/server/tablet-runtime-snapshot/queries.prisma.ts",
    "app/api/tablet/runtime/snapshot/route.ts"
  ],
  home: [
    "app/page.tsx",
    "components/tablet-home/tablet-home-screen.tsx",
    "components/tablet-home/tablet-home.module.css",
    "src/lib/tablet-home/home-view-model.ts"
  ],
  cart: [
    "src/lib/pos/cart-engine.ts",
    "src/lib/pos/cart-view-model.ts",
    "src/lib/pos/cart-state.ts",
    "components/pos/pos-screen.tsx",
    "components/pos/pos-ticket-panel.tsx"
  ],
  verify: [
    "tools/verify_tablet_runtime_snapshot_03b.mjs",
    "tools/verify_tablet_route_contract_03b.mjs",
    "tools/verify_tablet_runtime_home_03b_03c_deep.mjs",
    "tools/verify_tablet_sell_cart_03d.mjs",
    "tools/verify_tablet_cart_engine_03d_cases.mjs",
    "tools/verify_tablet_no_filler_gate_03b_03c_03d.mjs"
  ]
};
for (const [layer, files] of Object.entries(requiredByLayer)) {
  let present = 0;
  for (const rel of files) {
    if (exists(rel)) { present++; ok(`${layer} has ${rel}`); }
    else fail(`${layer} missing ${rel}`);
  }
  if (present !== files.length) fail(`${layer} incomplete ${present}/${files.length}`);
  else ok(`${layer} complete ${present}/${files.length}`);
}
const forbidden = [
  "products/pc/app",
  "products/mobile/app",
  "packages/shared-kernel",
  "shared/contracts",
  "schema.prisma"
];
for (const group of Object.values(requiredByLayer)) {
  for (const rel of group) {
    for (const blocked of forbidden) {
      if (rel.includes(blocked)) fail(`blocked target in manifest layer: ${rel}`);
    }
  }
}
if (failed) process.exit(1);
ok("installation manifest layer gate passed");
