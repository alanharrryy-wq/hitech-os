#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const required = [
  'products/mobile/infra/cloudflare/repair_prisma_mobile_cloudflare_live_route.py',
  'products/mobile/infra/cloudflare/repair_prisma_mobile_cloudflare_live_route.ps1',
  'products/mobile/infra/cloudflare/smoke_prisma_mobile_public_strict.ps1',
  'products/mobile/infra/cloudflare/README_PRISMA_MOBILE_10B_LIVE_ROUTE_REPAIR.md',
  'docs/mobile/PRISMA_APP_MOBILE_10B_CLOUDFLARE_LIVE_ROUTE_REPAIR.md',
  'manifests/mobile/INSTALL_MANIFEST_PRISMA_APP_MOBILE_10B_CLOUDFLARE_LIVE_ROUTE_REPAIR.json'
];
const missing = required.filter((rel) => !fs.existsSync(path.join(root, rel)));
if (missing.length) {
  console.error('[LIVE ROUTE REPAIR FAIL] Missing files:');
  for (const rel of missing) console.error(` - ${rel}`);
  process.exit(2);
}
const py = fs.readFileSync(path.join(root, 'products/mobile/infra/cloudflare/repair_prisma_mobile_cloudflare_live_route.py'), 'utf8');
for (const needle of ['prisma.hitechrts.com', 'http://127.0.0.1:3140', 'Restart-Service', 'cloudflared']) {
  if (!py.includes(needle)) {
    console.error(`[LIVE ROUTE REPAIR FAIL] Repair script missing marker: ${needle}`);
    process.exit(2);
  }
}
console.log('[LIVE ROUTE REPAIR OK] PRISMA Mobile Cloudflare live-route repair tooling is installed.');
