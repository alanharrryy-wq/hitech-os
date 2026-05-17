import fs from 'node:fs';
import path from 'node:path';
import { readJsonSafe } from './safe-json.mjs';

export const DEFAULT_JSON_OUTPUTS = [
  'QUALITY_REPORT.json',
  'QUALITY_DECISION.json',
  'QUALITY_FINDINGS.json',
  'ENVIRONMENT_SNAPSHOT.json',
  'COMMANDS_RUN.json',
  'QUALITY_MACHINE_SUMMARY.json',
  'QUALITY_AUTOMATION_SUMMARY.json',
  'QUALITY_RUN_MANIFEST.json',
  'QUALITY_PROFILE_MATRIX.json',
  'QUALITY_NORMALIZATION_AUDIT.json'
];

export function validateRunOutputs(runDir, jsonFiles = DEFAULT_JSON_OUTPUTS) {
  const checks = [];
  for (const name of jsonFiles) {
    const filePath = path.join(runDir, name);
    if (!fs.existsSync(filePath)) {
      checks.push({ file: name, ok: false, type: 'json', error: 'missing' });
      continue;
    }
    const text = fs.readFileSync(filePath, 'utf8');
    const parse = readJsonSafe(filePath);
    checks.push({
      file: name,
      ok: parse.ok && !text.endsWith('\\n') && !text.includes('}\\n'),
      type: 'json',
      parseable: parse.ok,
      literalBackslashN: text.endsWith('\\n') || text.includes('}\\n'),
      bytes: Buffer.byteLength(text, 'utf8'),
      error: parse.error
    });
  }
  for (const name of ['QUALITY_REPORT.md', 'QUALITY_BLOCKERS.md', 'QUALITY_WARNINGS.md', 'PHASE_EXIT_REPORT.md', 'QUALITY_NEXT_ACTIONS.md']) {
    const filePath = path.join(runDir, name);
    if (!fs.existsSync(filePath)) {
      checks.push({ file: name, ok: false, type: 'markdown', error: 'missing' });
      continue;
    }
    const text = fs.readFileSync(filePath, 'utf8');
    checks.push({
      file: name,
      ok: !text.includes('\\n'),
      type: 'markdown',
      literalBackslashN: text.includes('\\n'),
      bytes: Buffer.byteLength(text, 'utf8'),
      error: text.includes('\\n') ? 'literal backslash-n found' : null
    });
  }
  return {
    schemaVersion: '1.0',
    runDir,
    generatedAt: new Date().toISOString(),
    ok: checks.every((check) => check.ok),
    checks
  };
}
