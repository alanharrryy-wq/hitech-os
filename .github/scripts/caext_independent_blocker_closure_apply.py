from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('.')
README = ROOT / 'tools/code-atlas/README.md'
WOW_MD = ROOT / 'tools/code-atlas/docs/CODE_ATLAS_CUSTOMER_WOW_V1.md'
CONTRACT = ROOT / 'tools/code-atlas/docs/CODE_ATLAS_CUSTOMER_WOW_V1.contract.json'
LEDGER = ROOT / 'PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json'
EVIDENCE = ROOT / 'PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json'
MANUAL = ROOT / 'apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md'

BLOCK_STATUS = 'BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR'
BLOCKER = 'GITHUB_COPILOT_POLICY_SETTINGS'
REPL_MESH_RUN = 31915254808
REPL_MESH_ART = 9254730793
REPL_MESH_DIGEST = 'sha256:62625686559fa46e94479c57dcf492e0dd59e9f2b5b7fa202989edae02ce738a'
AVAIL_RUN = 31916081998
AVAIL_ART = 9254928517
AVAIL_DIGEST = 'sha256:9b66acf2461bc765727cf3ff8b6eca6c63c1931e628c47e89e5cf406d4b433f9'
CLOSURE_MESH_RUN = 31916191500
CLOSURE_MESH_ART = 9254953865
CLOSURE_MESH_DIGEST = 'sha256:bb15de6aa6394d61ea22eabe8f2e3a11ddb178429b6430a11a800566fb0184bb'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def add_unique(seq: list, value):
    if value not in seq:
        seq.append(value)


def insert_before(text: str, anchor: str, block: str) -> str:
    marker = block.splitlines()[0].strip()
    if marker and marker in text:
        return text
    if anchor not in text:
        return text.rstrip() + '\n\n' + block.strip() + '\n'
    return text.replace(anchor, block.strip() + '\n\n' + anchor, 1)


contract = load_json(CONTRACT)
if contract.get('status') != 'UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED':
    raise SystemExit('CONTRACT_STATUS_DRIFT')
if contract.get('certifiable') is not False or contract.get('productionCertified') is not False:
    raise SystemExit('CONTRACT_MATURITY_DRIFT')
verification = contract.setdefault('verification', {})
prior_agent = verification.get('externalAgentUsefulness') or {}
if prior_agent.get('status') != 'SINGLE_EXTERNAL_AGENT_PILOT_MEASURED_NO_CAUSAL_CLAIM':
    raise SystemExit('SINGLE_AGENT_PILOT_EVIDENCE_MISSING_OR_DRIFTED')
verification['independentAgentReplication'] = {
    'status': BLOCK_STATUS,
    'classification': 'VERIFY / EXTERNAL EVIDENCE / BLOCKED',
    'design': 'WITHIN_TASK_PAIRED_BASELINE_ASSISTED',
    'plannedTaskCount': 6,
    'plannedEvaluationSessionCount': 12,
    'executedEvaluationSessionCount': 0,
    'scoreProduced': False,
    'humanUsefulness': 'NOT_MEASURED',
    'productFailure': False,
    'fixAuthorized': False,
    'maturityAdvanced': False,
    'blocker': BLOCKER,
    'availabilityEvidence': {
        'directCopilotAssigneeAttempt': 'HTTP_403_FROM_CHAT_GITHUB_CONNECTOR',
        'prMentionAttempt': 'NO_AGENT_RESPONSE_OR_HEAD_MOVEMENT',
        'actionsRunId': AVAIL_RUN,
        'actionsArtifactId': AVAIL_ART,
        'actionsArtifactDigest': AVAIL_DIGEST,
        'githubTokenPermission': 'CopilotRequests: write',
        'copilotCliVersion': '1.0.80',
        'requestResult': 'Access denied by policy settings',
    },
}
add_unique(contract.setdefault('doesNotProve', []), 'successful independent-agent replication while the current external evaluator policy blocker remains')
contract['nextGate'] = (
    'Demonstrate an actually available independent external evaluator, then rerun the paired independent-agent replication. '
    'A bounded human usefulness study remains a separate future gate. Keep hosted/security and production certification '
    'separate, and do not rebuild core from this external policy blocker.'
)
contract.setdefault('externalEvidence', {})['independentAgentReplication'] = {
    'status': BLOCK_STATUS,
    'replicationAuthorityMeshRunId': REPL_MESH_RUN,
    'replicationAuthorityMeshArtifactId': REPL_MESH_ART,
    'replicationAuthorityMeshArtifactDigest': REPL_MESH_DIGEST,
    'availabilityIssue': 293,
    'blockedEvidencePr': 294,
    'blockedEvidencePrMerged': False,
    'availabilityRunId': AVAIL_RUN,
    'availabilityArtifactId': AVAIL_ART,
    'availabilityArtifactDigest': AVAIL_DIGEST,
    'blocker': BLOCKER,
    'closureAuthorityMeshRunId': CLOSURE_MESH_RUN,
    'closureAuthorityMeshArtifactId': CLOSURE_MESH_ART,
    'closureAuthorityMeshArtifactDigest': CLOSURE_MESH_DIGEST,
    'productFailure': False,
    'fixAuthorized': False,
    'scoreProduced': False,
}
save_json(CONTRACT, contract)

ledger = load_json(LEDGER)
matches = [c for c in ledger.get('capabilities', []) if c.get('id') == 'code_atlas.change_intelligence.customer_wow_v1']
if len(matches) != 1:
    raise SystemExit(f'LEDGER_CAPABILITY_MATCH_COUNT_{len(matches)}')
cap = matches[0]
if cap.get('status') != 'LOCAL_VERIFIED' or cap.get('doNotRebuild') is not True:
    raise SystemExit('LEDGER_MATURITY_OR_DONOTREBUILD_DRIFT')
cap['classification'] = 'VERIFY'
cap['stateLabel'] = 'LOCAL_VERIFIED_INDEPENDENT_EVALUATOR_BLOCKED'
cap['nextGate'] = (
    'Prove availability of an independent external evaluator, then rerun the same-task paired replication; bounded human '
    'usefulness remains a separate future study. Do not rebuild Code Atlas core to work around GitHub Copilot policy settings.'
)
for item in [
    f'independent replication Authority Mesh run {REPL_MESH_RUN} artifact {REPL_MESH_ART} {REPL_MESH_DIGEST}',
    'issue #293 independent evaluator availability probe closed not_planned',
    'PR #294 independent evaluator gate closed without merge',
    f'Copilot Actions availability run {AVAIL_RUN} artifact {AVAIL_ART} {AVAIL_DIGEST}',
    'Copilot CLI 1.0.80 with CopilotRequests: write rejected by GitHub: Access denied by policy settings',
    f'independent-evaluator blocker closure Authority Mesh run {CLOSURE_MESH_RUN} artifact {CLOSURE_MESH_ART} {CLOSURE_MESH_DIGEST}',
]:
    add_unique(cap.setdefault('evidence', []), item)
add_unique(cap.setdefault('allowedActions', []), 'prove independent external evaluator availability and rerun the paired replication under fresh evidence')
add_unique(cap.setdefault('allowedActions', []), 'run a bounded human usefulness study as a separate evidence gate')
add_unique(cap.setdefault('forbiddenActions', []), 'rebuild or patch Code Atlas core to work around external GitHub Copilot policy settings')
add_unique(cap.setdefault('forbiddenClaims', []), 'Do not claim successful independent-agent replication while the gate is BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR.')
add_unique(cap.setdefault('doesNotProve', []), 'Successful independent-agent replication; the planned 12 sessions were not executed because the external evaluator was policy-blocked')
ledger['updatedAt'] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
save_json(LEDGER, ledger)

evidence = load_json(EVIDENCE)
artifact_type = 'code_atlas_independent_agent_replication_blocked'
artifacts = evidence.setdefault('artifacts', [])
if not any(a.get('type') == artifact_type for a in artifacts):
    artifacts.append({
        'artifact': f'Code Atlas Independent Agent Replication V1 — BLOCKED / PR #294 / run {AVAIL_RUN}',
        'type': artifact_type,
        'scope': ['code_atlas', 'change_intelligence', 'external_evidence', 'governance'],
        'status': BLOCK_STATUS,
        'proves': [
            'Fresh task-exact Authority Mesh authorized a same-task paired six-task / twelve-session independent-agent replication protocol',
            'Direct copilot-swe-agent assignment through the connected GitHub app returned HTTP 403',
            'PR @copilot mention produced no external agent response or head movement',
            'GitHub Actions granted the built-in GITHUB_TOKEN CopilotRequests: write',
            'GitHub Copilot CLI 1.0.80 installed successfully in the Actions runner',
            'GitHub rejected the Copilot request with Access denied by policy settings',
            'No twelve-session responses were fabricated and no independent-agent usefulness score was produced',
            'The blocker is external policy/dependency evidence, not a Code Atlas product-core failure',
        ],
        'doesNotProve': [
            'Successful independent-agent replication',
            'Causal usefulness uplift',
            'Human usefulness',
            'A Code Atlas product-core defect',
            'Production, enterprise, hosted multi-tenant, IAM/security, privacy/legal or paid-pilot readiness',
        ],
        'evidence': [
            f'replication Authority Mesh run {REPL_MESH_RUN} artifact {REPL_MESH_ART}',
            'issue #293',
            'PR #294 closed without merge',
            f'Copilot availability run {AVAIL_RUN} artifact {AVAIL_ART}',
            f'blocker closure Authority Mesh run {CLOSURE_MESH_RUN} artifact {CLOSURE_MESH_ART}',
        ],
    })
entries = evidence.setdefault('entries', [])
if not any(e.get('runId') == 'PR294_CODE_ATLAS_INDEPENDENT_EVALUATOR_BLOCKED' for e in entries):
    entries.append({
        'capabilityId': 'code_atlas.change_intelligence.customer_wow_v1',
        'status': 'LOCAL_VERIFIED',
        'runId': 'PR294_CODE_ATLAS_INDEPENDENT_EVALUATOR_BLOCKED',
        'evidence': [
            'PR #294 closed without merge',
            f'run {AVAIL_RUN} / artifact {AVAIL_ART}',
            f'closure Authority Mesh {CLOSURE_MESH_RUN} / artifact {CLOSURE_MESH_ART}',
            BLOCK_STATUS,
        ],
    })
evidence['updatedAt'] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
save_json(EVIDENCE, evidence)

readme = README.read_text(encoding='utf-8')
old_next = 'The next evidence gate is **human/agent usefulness evidence**. Hosted/security boundaries remain separate gates.'
new_next = (
    'The bounded single external-agent usefulness pilot is recorded, but the next independent-agent replication attempt is '
    'currently **`BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR`**: GitHub Actions granted `CopilotRequests: write` and installed '
    'Copilot CLI `1.0.80`, then GitHub rejected the request with `Access denied by policy settings`. A bounded human usefulness '
    'study remains a separate future gate; hosted/security boundaries remain separate gates.'
)
if old_next in readme:
    readme = readme.replace(old_next, new_next, 1)
readme_block = f'''## Independent-agent replication gate — external policy blocked

A fresh task-exact Authority Mesh authorized a stronger **same-task paired** replication design: six historical tasks, each evaluated once as `BASELINE` and once as `ASSISTED`, for 12 isolated external-agent sessions with ground truth sealed until paired responses were persisted.

That experiment did **not** run to scoring. Independent evaluator availability failed closed:

- replication Authority Mesh: run `{REPL_MESH_RUN}`, artifact `{REPL_MESH_ART}`, `{REPL_MESH_DIGEST}`;
- direct `copilot-swe-agent[bot]` assignment through the connected GitHub app: HTTP 403;
- `@copilot` PR mention: no agent response or head movement;
- GitHub Actions availability run `{AVAIL_RUN}` received `CopilotRequests: write`, installed Copilot CLI `1.0.80`, then GitHub returned **`Access denied by policy settings`**;
- availability artifact `{AVAIL_ART}`, `{AVAIL_DIGEST}`;
- blocker closure Authority Mesh: run `{CLOSURE_MESH_RUN}`, artifact `{CLOSURE_MESH_ART}`, `{CLOSURE_MESH_DIGEST}`.

Result: **`{BLOCK_STATUS}`**. No 12-session responses were invented, no score was produced, and no Code Atlas core defect was inferred. `LOCAL_VERIFIED`, `doNotRebuild=true`, `certifiable=false`, `productionCertified=false`, and `humanUsefulness=NOT_MEASURED` remain unchanged.
'''
readme = insert_before(readme, '## Architecture', readme_block)
README.write_text(readme, encoding='utf-8')

wow = WOW_MD.read_text(encoding='utf-8')
old_wow_next = 'This is **broader but still bounded external evidence**. Low companion recall is recorded as a measured limitation, not automatically promoted to a source defect. The next gate is human/agent usefulness evidence, not a core rebuild.'
new_wow_next = (
    'This is **broader but still bounded external evidence**. Low companion recall is recorded as a measured limitation, not '
    'automatically promoted to a source defect. The single external-agent usefulness pilot is recorded; the attempted '
    'independent-agent replication is now `BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR` because GitHub Copilot access is denied '
    'by policy in the current environment. This is an external dependency blocker, not a core rebuild trigger.'
)
if old_wow_next in wow:
    wow = wow.replace(old_wow_next, new_wow_next, 1)
wow_block = f'''## Independent-agent replication V1 — blocked before scoring

The next agent-evidence design removed the main confounder from the prior pilot by pairing `BASELINE` and `ASSISTED` on the **same six historical tasks**. Twelve separate evaluator sessions were planned, with no paired-response visibility and ground truth sealed until both responses existed.

Fresh Authority Mesh run `{REPL_MESH_RUN}` / artifact `{REPL_MESH_ART}` authorized that protocol. The external evaluator could not be demonstrated as available: direct Copilot-agent assignment returned HTTP 403, the PR mention produced no agent execution, and Actions run `{AVAIL_RUN}` received `CopilotRequests: write` and installed Copilot CLI `1.0.80` but GitHub rejected the request with **`Access denied by policy settings`**. Availability evidence is artifact `{AVAIL_ART}` (`{AVAIL_DIGEST}`).

Therefore the gate is **`{BLOCK_STATUS}`**. Executed evaluator sessions: `0/12`; independent-agent score: **not produced**. This does not change the earlier single-agent result, does not establish human usefulness, and does not authorize a Code Atlas source fix. Replication may resume only after an actually available independent evaluator is demonstrated. Human usefulness remains a separate future study.
'''
wow = insert_before(wow, '## 1. Product goal', wow_block)
WOW_MD.write_text(wow, encoding='utf-8')

manual = MANUAL.read_text(encoding='utf-8')
manual_marker = '## 2026-08-15 — Code Atlas independent evaluator replication blocked by GitHub policy'
if manual_marker not in manual:
    manual += f'''\n\n{manual_marker}\n\n- Classification: `VERIFY / EXTERNAL EVIDENCE / BLOCKED`; **not** a product failure.\n- Replication Authority Mesh: run `{REPL_MESH_RUN}`, artifact `{REPL_MESH_ART}`, `{REPL_MESH_DIGEST}`.\n- Planned design: six same-task paired historical tasks, 12 independent `BASELINE`/`ASSISTED` sessions, ground truth sealed until paired responses persisted.\n- Direct `copilot-swe-agent[bot]` assignment via connected GitHub app returned HTTP 403.\n- `@copilot` PR mention produced no agent response/head movement.\n- Actions run `{AVAIL_RUN}` explicitly had `CopilotRequests: write`, installed Copilot CLI `1.0.80`, then GitHub rejected the request with `Access denied by policy settings`.\n- Availability artifact: `{AVAIL_ART}`, `{AVAIL_DIGEST}`.\n- Evidence PR #294 and issue #293 were closed without merge / not planned. No 12-session responses were fabricated and no score was produced.\n- Closure Authority Mesh: run `{CLOSURE_MESH_RUN}`, artifact `{CLOSURE_MESH_ART}`, `{CLOSURE_MESH_DIGEST}`.\n- Preserve `LOCAL_VERIFIED`, `VERIFY`, `doNotRebuild=true`, `certifiable=false`, `productionCertified=false`, `humanUsefulness=NOT_MEASURED`; do not advance agent-usefulness maturity.\n- Next allowed gate: prove an actually available independent external evaluator and rerun the paired protocol, or conduct the bounded human usefulness study as a separate gate. Do not rebuild core to work around external Copilot policy.\n'''
MANUAL.write_text(manual, encoding='utf-8')

contract2 = load_json(CONTRACT)
ledger2 = load_json(LEDGER)
cap2 = next(c for c in ledger2['capabilities'] if c.get('id') == 'code_atlas.change_intelligence.customer_wow_v1')
if contract2.get('status') != 'UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED':
    raise SystemExit('POST_CONTRACT_STATUS_DRIFT')
if contract2.get('certifiable') is not False or contract2.get('productionCertified') is not False:
    raise SystemExit('POST_CONTRACT_CERTIFICATION_DRIFT')
if cap2.get('status') != 'LOCAL_VERIFIED' or cap2.get('doNotRebuild') is not True:
    raise SystemExit('POST_LEDGER_MATURITY_DRIFT')
if contract2['verification']['externalAgentUsefulness'].get('status') != 'SINGLE_EXTERNAL_AGENT_PILOT_MEASURED_NO_CAUSAL_CLAIM':
    raise SystemExit('POST_SINGLE_AGENT_EVIDENCE_DRIFT')
if contract2['verification']['independentAgentReplication'].get('status') != BLOCK_STATUS:
    raise SystemExit('POST_BLOCKER_STATUS_MISSING')
print('PASS_CAEXT_INDEPENDENT_BLOCKER_SIX_DOC_CLOSURE')
