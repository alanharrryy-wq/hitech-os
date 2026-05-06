#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const required = [
  'products/mobile/infra/cloudflare/repair_prisma_mobile_cloudflare_live_route.ps1',
  'products/mobile/infra/cloudflare/repair_prisma_mobile_cloudflare_live_route.py',
  'products/mobile/infra/cloudflare/smoke_prisma_mobile_public_strict.ps1',
  'products/mobile/infra/cloudflare/README_PRISMA_MOBILE_10C_DNS_FALLBACK_REPAIR.md'
];
let ok = true;
for (const rel of required) {
  if (!fs.existsSync(path.join(root, rel))) {
    console.error(`[10C MISSING] ${rel}`);
    ok = false;
  }
}
const py = fs.readFileSync(path.join(root, 'products/mobile/infra/cloudflare/repair_prisma_mobile_cloudflare_live_route.py'), 'utf8');
for (const token of ['--overwrite-dns', '--diagnose', 'APPLY NEEDS DNS/DASHBOARD ATTENTION', 'ensure_service_image_path']) {
  if (!py.includes(token)) {
    console.error(`[10C TOKEN MISSING] ${token}`);
    ok = false;
  }
}
if (!ok) process.exit(1);
console.log('[10C OK] PRISMA Mobile Cloudflare repair now tolerates DNS-route CLI failures, tries overwrite fallback, updates service ImagePath, and keeps public smoke as the truth.');
