
# Parallel Launch Order

## Phase -1: Framework install and hygiene check
- verify the framework root is complete
- run `python tools/execution_framework/smoke_framework_checks.py`
- run `python tools/execution_framework/check_framework_readiness.py`
- do not open chats until install readiness is `ready`

## Phase 0: Idea intake
- capture the raw initiative in the idea intake template
- record the problem, outcome, constraints, repo reality, and what is still unknown
- do not open package chats yet

## Phase 1: Homologation and project baseline
- convert the raw idea into a homologated project baseline
- instantiate `ops/projects/<project_id>/`
- freeze `project_id`, proposed `run_id`, success conditions, default package topology, runtime path ownership draft, canonical source register, and contract register
- if the project truly needs a custom topology, record the override before any package chat opens

## Phase 2: Governance freeze
- open the governance chat first
- finalize the constitutional docs that apply to this project: naming, dictionary extensions, path ownership, dependency graph, change budgets, review model, communication policy, waiver policy, contract versioning, and freeze protocol
- governance chat also becomes mission control by default for the first run

## Phase 3: Package launch
Launch six package chats in parallel using the default topology:
- `01-identity-access-and-trust`
- `02-domain-data-and-persistence`
- `03-service-contracts-and-orchestration`
- `04-experience-clients-and-interactions`
- `05-platform-infrastructure-and-delivery`
- `06-quality-release-and-operations`

Each package chat receives:
- its package folder
- the frozen governance docs it must consume
- the active project baseline under `ops/projects/<project_id>/`
- the active work packet for the current round, when rounds are in use

## Phase 4: Run creation
- initialize the run folder under `ops/runs/<run_id>/`
- freeze the objective, active package list, and baseline references
- initialize round `rd-001` unless a later round is intentionally being created

## Phase 5: Round execution
- generate work packets and prompts for the six package chats
- package chats produce bundles or package-local outputs inside their allowed paths
- package chats do not edit another package's folder or runtime path assignment directly
- cross-package questions route through governance only

## Phase 6: Validation and acceptance
- governance or delegated mission control validates bundles for structure, ownership, manifest integrity, and overlap
- acceptance decisions are written before integration begins
- rejected packages receive retry prompts; accepted packages move forward
- any exception uses a written waiver record

## Phase 7: Integration and handoff
- apply accepted bundles in dependency order
- record any conditions, residual risk, or required follow-up decisions
- update downstream consumers only through frozen handoff artifacts

## Phase 8: Closeout or next round
- if the run objective is met, close the run and archive evidence
- if the objective remains open, prepare the next round from validated outputs only

## Default precedence
1. Governance constitution wins.
2. Homologated project baseline comes next.
3. Active run and round manifests interpret the baseline for the current cycle.
4. Generated prompts and examples are derivative and never outrank the frozen docs.
