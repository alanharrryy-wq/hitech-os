# Codex Operating Model

## Objective
Use execution agents as **bounded operators**, not as substitute architects. The agent may verify, insert, wire, validate, summarize, and package work only inside the authority granted by the constitution, the project baseline, and the active work packet.

## Roles
### Operator
- chooses priorities
- approves homologation and topology overrides
- decides when a run is opened or closed
- accepts or rejects constitutional changes

### Governance chat
- translates raw intent into governed structure
- owns the constitution and mission-control decisions by default
- freezes shared rules and resolves cross-package conflicts
- reviews package outputs against canonical sources

### Package chats
- own package-local docs and active runtime paths
- consume frozen upstream contracts
- produce package-scoped outputs, handoff artifacts, and bundles
- escalate instead of improvising shared rules

### Execution agent
- verifies docs against code and code against docs
- produces bounded diffs inside allowed paths
- generates or validates bundles, manifests, packets, and reports
- stops when the task requires a new shared rule or a path ownership change

## Allowed execution-agent actions
- audit consistency between implementation and frozen contracts
- insert approved content in allowed files
- wire already-approved integrations into already-approved extension points
- generate bounded packets, manifests, prompts, and validation reports
- package deterministic artifacts for review or handoff

## Forbidden execution-agent actions
- redefine architecture or package topology without governance record
- invent new path families or canonical terms
- widen scope beyond the task contract
- change auth, isolation, persistence, or delivery strategy without explicit authorization
- touch forbidden files even when a small shortcut looks attractive
- treat prompts as permission to break the constitution

## Mandatory task fields for any execution run
1. `project_id`
2. `run_id`
3. `round_id` when applicable
4. `package_id`
5. goal
6. scope
7. allowed paths
8. forbidden paths
9. consumed contracts
10. acceptance criteria
11. non-goals
12. change budget
13. rollback note
14. unresolved questions bucket

## Output discipline
Every bounded run returns:
- touched files
- untouched but relevant files
- assumptions used
- contracts and decision records followed
- unresolved contradictions
- evidence needed before integration

## Stop conditions
Stop and report instead of improvising when:
- the task needs a new shared term or package boundary
- the required file is outside allowed ownership
- two canonical sources disagree
- a frozen interface needs to change without a decision record
- the repo reality contradicts the active baseline and no override exists
