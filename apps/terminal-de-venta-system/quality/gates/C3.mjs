import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { exists, packageScripts, pathMatrix } from '../core/customer-assurance.mjs';

export const gateId = 'C3';
export const title = 'First Run Customer Environment';

function canWriteDir(dirPath) {
  if (process.platform !== 'win32') return { checked: false, ok: true, reason: `Skipped literal Windows path write check on ${process.platform}.` };
  try {
    fs.mkdirSync(dirPath, { recursive: true });
    const probe = path.join(dirPath, `.pqos_first_run_probe_${Date.now()}.tmp`);
    fs.writeFileSync(probe, 'probe', 'utf8');
    fs.unlinkSync(probe);
    return { checked: true, ok: true, reason: `${dirPath} is writable.` };
  } catch (error) {
    return { checked: true, ok: false, reason: error?.message || String(error) };
  }
}

export async function run(ctx) {
  const firstRunPaths = [
    'package.json',
    'pnpm-workspace.yaml',
    'quality/bin/prisma-quality.mjs',
    'quality/bin/prisma-quality.ps1',
    'products/tablet/app/package.json',
    'products/tablet/app/next.config.mjs',
    'products/tablet/app/app',
    'products/pc/app/package.json',
    'products/mobile/app/package.json',
    'prisma/schema.prisma'
  ];
  const checks = pathMatrix(ctx, firstRunPaths);
  const rootPackage = packageScripts(ctx);
  const outputProbe = canWriteDir(ctx.outDir || 'F:/descargasf');
  const evidence = [createEvidence(ctx, 'C3', 'first_run_environment', 'First-run environment and install surface scan', {
    node: { version: process.version, platform: process.platform, arch: process.arch },
    checks,
    rootPackage: { ok: rootPackage.ok, scriptNames: rootPackage.scriptNames, error: rootPackage.error },
    outputProbe
  })];
  const findings = [];
  const critical = new Set(['package.json', 'quality/bin/prisma-quality.mjs', 'products/tablet/app/package.json', 'products/tablet/app/next.config.mjs', 'products/tablet/app/app', 'prisma/schema.prisma']);
  for (const check of checks.filter((item) => !item.exists)) {
    findings.push(finding({
      id: `C3_MISSING_${check.path.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: critical.has(check.path) ? 'S1' : 'S3',
      layer: 'Customer',
      title: 'First-run required surface missing',
      detail: `${check.path} was not found.`,
      file: check.path,
      evidence,
      recommendation: critical.has(check.path) ? 'Restore the required first-run path before customer install.' : 'Optional app surface missing; confirm this install shape is intended.'
    }));
  }
  if (!outputProbe.ok) {
    findings.push(finding({
      id: 'C3_OUTPUT_DIR_NOT_WRITABLE',
      severity: 'S1',
      layer: 'Customer',
      title: 'Evidence output directory is not writable',
      detail: outputProbe.reason,
      file: ctx.outDir || 'F:/descargasf',
      evidence,
      recommendation: 'Make the evidence output directory writable before customer first run.'
    }));
  }
  return {
    gateId: 'C3',
    title,
    status: findings.some((item) => ['S0', 'S1'].includes(item.severity)) ? 'BLOCKED' : findings.length ? 'READY_WITH_WARNINGS' : 'READY',
    summary: `${checks.filter((item) => item.exists).length}/${checks.length} first-run paths found; Node ${process.version}.`,
    findings,
    evidence
  };
}
