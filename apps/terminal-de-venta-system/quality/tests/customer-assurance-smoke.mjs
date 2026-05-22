import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sourceQualityRoot = path.resolve(__dirname, '..');
const fixtureRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'pqos-customer-fixture-'));
const fixtureQualityRoot = path.join(fixtureRoot, 'quality');
const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pqos-customer-out-'));

fs.cpSync(sourceQualityRoot, fixtureQualityRoot, { recursive: true });

function write(relativePath, text) {
  const full = path.join(fixtureRoot, relativePath);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, text, 'utf8');
}

write('package.json', JSON.stringify({
  name: 'terminal-de-venta-system-fixture',
  private: true,
  scripts: {
    'quality:client-readiness': 'node quality/bin/prisma-quality.mjs --profile client-readiness --repo-root .',
    'quality:demo': 'node quality/bin/prisma-quality.mjs --profile demo --repo-root .',
    'quality:first-run': 'node quality/bin/prisma-quality.mjs --profile first-run --repo-root .',
    'quality:support-pack': 'node quality/bin/prisma-quality.mjs --profile support-pack --repo-root .',
    'quality:upgrade': 'node quality/bin/prisma-quality.mjs --profile upgrade --repo-root .',
    'quality:watch': 'node quality/bin/prisma-quality.mjs --profile watch --repo-root .'
  }
}, null, 2));
write('pnpm-workspace.yaml', 'packages:\n  - products/*/app\n');
write('products/tablet/app/package.json', JSON.stringify({ name: 'tablet-app', private: true }, null, 2));
write('products/tablet/app/next.config.mjs', 'export default {};\n');
write('products/tablet/app/app/page.tsx', 'export default function Page(){ return null; }\n');
write('products/tablet/app/src/server/sync/outbox.ts', 'export const outbox = true; export const idempotencyKey = "stable"; export const pending = true;\n');
write('products/pc/app/package.json', JSON.stringify({ name: 'pc-app', private: true }, null, 2));
write('products/pc/app/src/ingest.ts', 'export const ingest = "idempotent outbox replay checkpoint";\n');
write('products/mobile/app/package.json', JSON.stringify({ name: 'mobile-app', private: true }, null, 2));
write('products/mobile/app/src/supervision.ts', 'export const freshness = "offline partial live confidence";\n');
write('products/chart-lab/app/package.json', JSON.stringify({ name: 'chart-lab', private: true }, null, 2));
write('shared/contracts/sync-event-contract.v1.json', JSON.stringify({ version: '1.0', idempotencyKey: true }, null, 2));
write('prisma/schema.prisma', 'datasource db { provider = "sqlite" url = env("DATABASE_URL") }\nmodel OutboxEvent { id String @id idempotencyKey String }\n');
write('prisma/migrations/0001_init/migration.sql', 'CREATE TABLE OutboxEvent (id TEXT PRIMARY KEY, idempotencyKey TEXT NOT NULL);\n');
write('docs/demo-playbook.md', 'Demo mode uses training data only. No production reset. support pack rollback client-readiness.\n');

function run(args, expect = 0) {
  const result = spawnSync(process.execPath, [path.join(fixtureQualityRoot, 'bin', 'prisma-quality.mjs'), ...args], {
    cwd: fixtureRoot,
    encoding: 'utf8'
  });
  if (result.status !== expect) {
    console.error(result.stdout);
    console.error(result.stderr);
    throw new Error(`Command failed (${result.status} != ${expect}): ${args.join(' ')}`);
  }
  return result;
}

function latestRun() {
  const runs = fs.readdirSync(outDir).filter((name) => name.startsWith('PRISMA_QUALITY_OS_')).sort().reverse();
  if (!runs.length) throw new Error('No customer run output found');
  return path.join(outDir, runs[0]);
}

for (const profile of ['demo', 'support-pack', 'upgrade', 'client-readiness', 'pilot']) {
  run(['--profile', profile, '--repo-root', fixtureRoot, '--out-dir', outDir], 0);
  const dir = latestRun();
  const decision = JSON.parse(fs.readFileSync(path.join(dir, 'QUALITY_DECISION.json'), 'utf8'));
  if (decision.decision === 'BLOCKED') throw new Error(`${profile} should not block fixture`);
  JSON.parse(fs.readFileSync(path.join(dir, 'QUALITY_REPORT.json'), 'utf8'));
  if (['support-pack', 'client-readiness', 'pilot'].includes(profile)) {
    const supportManifest = path.join(dir, 'CUSTOMER_SUPPORT_PACK_MANIFEST.json');
    if (!fs.existsSync(supportManifest)) throw new Error(`${profile} did not create support manifest`);
  }
  const customerLedger = path.join(dir, 'CUSTOMER_EVIDENCE_LEDGER.json');
  if (!fs.existsSync(customerLedger)) throw new Error(`${profile} did not create customer evidence ledger`);
}

console.log('PQOS customer assurance smoke OK');
