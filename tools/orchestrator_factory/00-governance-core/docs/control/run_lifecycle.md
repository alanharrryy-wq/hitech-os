
# Run Lifecycle

A **project** may outlive many runs. A **run** is the governed execution campaign for one bounded objective. A **round** is a tactical synchronization window inside a run.

## Lifecycle stages

### 0. Install readiness
Input: framework copied or attached.

Work:
- verify framework layout
- verify tactical tools exist
- verify canonical tree hygiene

Exit criteria:
- install readiness is `ready`

### 1. Intake
Input: raw idea, bug, request, initiative, or modernization target.

Exit criteria:
- problem statement exists
- outcome is stated
- obvious constraints are captured

### 2. Homologation
Input: intake record.

Work:
- assign `project_id`
- classify initiative type
- instantiate `ops/projects/<project_id>/`
- select default or overridden package topology
- draft runtime path ownership
- define canonical sources
- register likely shared contracts
- define first-run objective

Exit criteria:
- homologation record exists
- project baseline is coherent enough to freeze

### 3. Constitutional freeze
Input: homologated baseline.

Work:
- confirm dictionary and naming
- confirm package topology and dependency graph
- confirm path ownership and change budgets
- confirm review, escalation, waiver, and merge rules

Exit criteria:
- governance docs are frozen enough for package launch

### 4. Run creation
Input: frozen governance and project baseline.

Work:
- create `run_id`
- initialize `ops/runs/<run_id>/`
- record objective, package list, baseline references, and decision links

Exit criteria:
- run manifest exists and is authoritative for the run

### 5. Round planning
Input: active run.

Work:
- initialize `rd-001` or later round
- generate work packets and prompts
- freeze the inputs each package may consume

Exit criteria:
- round manifest, packets, and prompts exist

### 6. Parallel execution
Input: active round.

Work:
- package chats produce outputs or bundles
- package chats stay inside allowed ownership
- package chats escalate unresolved cross-package issues through governance only

Exit criteria:
- submissions exist for every package expected in the round

### 7. Validation and acceptance
Input: submitted bundles and package outputs.

Work:
- schema and structure validation
- ownership enforcement
- overlap detection
- acceptance decision per package
- waiver review if an exception was requested

Exit criteria:
- acceptance report exists
- integration readiness is known

### 8. Integration and handoff
Input: accepted outputs.

Work:
- integrate in dependency order
- record conditions, residual risks, waiver references, and downstream effects
- hand off frozen artifacts to consumers

Exit criteria:
- accepted outputs are integrated or staged for integration

### 9. Closeout or continuation
Input: integrated state.

Work:
- close the run if objective is met
- otherwise prepare the next round or next run from validated evidence only

Exit criteria:
- run closed or next step explicitly opened
