#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runEnforcer } from './route-budget-enforcer.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const args = process.argv.slice(2);
let repoRoot = process.cwd();
let out = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--repo') repoRoot = args[++i];
  else if (args[i] === '--out') out = args[++i];
}

const policyPath = path.join(__dirname, 'prisma.route-budget.policy.json');
if (!fs.existsSync(policyPath)) {
  throw new Error(`Policy not found: ${policyPath}`);
}

const result = runEnforcer({ repoRoot, policyPath });

const mustPass = ['cleanPos', 'cleanPublic', 'posGateManifest'];
const mustFail = ['dirtyPos'];
const contractFailures = [];

for (const sampleName of mustPass) {
  if (result.samples?.[sampleName]?.status !== 'PASS') {
    contractFailures.push({
      type: 'sample_contract',
      sample: sampleName,
      expected: 'PASS',
      actual: result.samples?.[sampleName]?.status
    });
  }
}
for (const sampleName of mustFail) {
  if (result.samples?.[sampleName]?.status !== 'FAIL') {
    contractFailures.push({
      type: 'sample_contract',
      sample: sampleName,
      expected: 'FAIL',
      actual: result.samples?.[sampleName]?.status
    });
  }
}

const finalResult = {
  ...result,
  verifier_hotfix: '02_semantic_governance_context',
  contract_failures: contractFailures,
  status: result.status === 'PASS' && contractFailures.length === 0 ? 'PASS' : 'FAIL'
};

const json = JSON.stringify(finalResult, null, 2);
if (out) {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, json, 'utf8');
}
console.log(json);
process.exit(finalResult.status === 'PASS' ? 0 : 1);
