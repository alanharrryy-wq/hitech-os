#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const required = [
  'products/tablet/app/app/visual-os/page.tsx',
  'products/tablet/app/app/visual-os/detached/page.tsx',
  'products/tablet/app/app/visual-os/pro/page.tsx',
  'products/tablet/app/app/visual-os/realtime/page.tsx',
  'products/tablet/app/app/visual-os/PrismaStudioProQaClient.tsx',
  'products/tablet/app/app/visual-os/prisma-studio-pro-qa.module.css',
  'products/tablet/app/src/visual-os/realtime/prisma-realtime-client.ts',
  'tools/prisma-visual-os/live-preview-server-00q.mjs',
  'tools/prisma-visual-os/score_prisma_studio_pro_00s.mjs',
  'config/prisma-visual-os/recipes/CRYSTAL_POS_ANGEL_LIVE_v01.json',
  'config/prisma-visual-os/guards/prisma-visual-guardrails-00s.json',
  'docs/design/PRISMA_VISUAL_OS_STUDIO_PRO_QA_00R_00S.md',
  'manifests/PRISMA_VISUAL_OS_STUDIO_PRO_QA_00R_00S_20260503_v01.json'
];
const missing = [];
for (const rel of required) {
  if (!fs.existsSync(path.join(root, rel))) missing.push(rel);
}
const client = path.join(root, 'products/tablet/app/app/visual-os/PrismaStudioProQaClient.tsx');
const css = path.join(root, 'products/tablet/app/app/visual-os/prisma-studio-pro-qa.module.css');
const clientText = fs.existsSync(client) ? fs.readFileSync(client, 'utf8') : '';
const cssText = fs.existsSync(css) ? fs.readFileSync(css, 'utf8') : '';
const checks = [
  ['Studio Pro marker', clientText.includes('Studio Pro + QA')],
  ['Score calculation', clientText.includes('computeScore')],
  ['Snapshot lab', clientText.includes('snapshotLab')],
  ['Publish gate', clientText.includes('publishActive')],
  ['Crystal CSS', cssText.includes('heroCrystal') && cssText.includes('aurora')],
  ['Realtime bridge', clientText.includes('broadcastPrismaRealtimePayload')]
];
const failed = checks.filter(([, ok]) => !ok).map(([name]) => name);
if (missing.length || failed.length) {
  console.error('[PRISMA 00R/00S] VERIFY FAILED');
  if (missing.length) console.error('Missing files:\n' + missing.map((m) => ` - ${m}`).join('\n'));
  if (failed.length) console.error('Failed checks:\n' + failed.map((m) => ` - ${m}`).join('\n'));
  process.exit(1);
}
console.log('[PRISMA 00R/00S] VERIFY OK');
console.log(JSON.stringify({ root, required: required.length, checks: checks.length }, null, 2));
