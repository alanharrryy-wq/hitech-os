#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();

function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}

function assert(cond, msg) {
  if (!cond) {
    throw new Error(msg);
  }
}

const supportApi = read('Prisma Cloud Ctr/internal/py/support_resolver_api.py');
const cloudJs = read('Prisma Cloud Ctr/internal/web/cloud_command_center.js');
const pkg = JSON.parse(read('package.json'));

assert(supportApi.includes('PRISMA RECON5 SETUP CLAIM APPLY PREFLIGHT START'), 'missing recon5 py marker');
assert(supportApi.includes('SETUP_CLAIM_OR_REFRESH_PREFLIGHT_READY'), 'missing preflight ready code');
assert(supportApi.includes('SETUP_CLAIM_OR_REFRESH_INPUT_REQUIRED'), 'missing setup code required code');
assert(supportApi.includes('setup_claim_or_refresh_apply_with_backup_rollback'), 'missing future apply action id');
assert(supportApi.includes('mutationPerformed'), 'missing non-mutation guard');
assert(supportApi.includes('applyPlan'), 'missing support applyPlan response');

assert(cloudJs.includes('supportSetupCodeField'), 'missing setup code UI field');
assert(cloudJs.includes('supportApplyPlanPanel'), 'missing apply plan panel');
assert(cloudJs.includes('SETUP_CLAIM_OR_REFRESH_PREFLIGHT_READY'), 'missing preflight UI status');
assert(cloudJs.includes('operatorConfirmation'), 'missing operator confirmation payload');

assert(pkg.scripts && pkg.scripts['verify:support-resolver-recon5'], 'missing package script verify:support-resolver-recon5');

const casePath = path.join(root, 'prisma-support-resolver/tests/cases/setup-claim-or-refresh-apply-preflight.case.json');
assert(fs.existsSync(casePath), 'missing recon5 case fixture');

const fixture = JSON.parse(fs.readFileSync(casePath, 'utf8'));
assert(fixture.resultCode === 'SETUP_CLAIM_OR_REFRESH_PREFLIGHT_READY', 'bad fixture resultCode');
assert(fixture.primaryIssueCode === 'CROSS_SOURCE_IDENTITY_SPLIT', 'bad fixture primaryIssueCode');
assert(fixture.selectedAuthority === 'setup_claim_or_refresh', 'bad fixture selectedAuthority');
assert(fixture.setupCodePresent === true, 'fixture must represent setup code present');
assert(fixture.mutationPerformed === false, 'fixture must be non-mutating');
assert(fixture.wouldMutate === false, 'fixture wouldMutate must be false');
assert(fixture.safeToApply === false, 'fixture safeToApply must remain false');
assert(fixture.rollbackAvailable === false, 'fixture rollbackAvailable must remain false');
assert(fixture.secretsExposed === false, 'fixture secrets exposed');

assert(fixture.applyPlan && typeof fixture.applyPlan === 'object', 'fixture missing applyPlan');
assert(Array.isArray(fixture.applyPlan.localWritePlan) && fixture.applyPlan.localWritePlan.length >= 3, 'fixture missing localWritePlan');
assert(Array.isArray(fixture.applyPlan.rollbackPlan) && fixture.applyPlan.rollbackPlan.length >= 3, 'fixture missing rollbackPlan');
assert(Array.isArray(fixture.applyPlan.postChecks) && fixture.applyPlan.postChecks.length >= 4, 'fixture missing postChecks');
assert(Array.isArray(fixture.applyPlan.requiredBeforeMutation) && fixture.applyPlan.requiredBeforeMutation.length >= 4, 'fixture missing requiredBeforeMutation');
assert(fixture.applyPlan.mutationPerformed === false, 'applyPlan must be non-mutating');
assert(fixture.applyPlan.secretsExposed === false, 'applyPlan secrets exposed');
assert(fixture.applyPlan.futureApplyAction === 'setup_claim_or_refresh_apply_with_backup_rollback', 'bad future apply action');

const output = {
  ok: true,
  resultCode: 'PASS_RECON5D_APPLY_PREFLIGHT_FIXTURE_AND_ESM_VERIFIER',
  verifierModule: 'esm',
  fixtureResultCode: fixture.resultCode,
  hasApplyPlan: Boolean(fixture.applyPlan),
  localWritePlan: fixture.applyPlan.localWritePlan.length,
  rollbackPlan: fixture.applyPlan.rollbackPlan.length,
  postChecks: fixture.applyPlan.postChecks.length,
  requiredBeforeMutation: fixture.applyPlan.requiredBeforeMutation.length,
  mutationPerformed: fixture.mutationPerformed,
  wouldMutate: fixture.wouldMutate,
  safeToApply: fixture.safeToApply,
  secretsExposed: fixture.secretsExposed,
  scripts: Object.keys(pkg.scripts || {}).filter((key) => key.includes('support-resolver')),
};

console.log(JSON.stringify(output, null, 2));
