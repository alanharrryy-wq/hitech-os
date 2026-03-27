# Shared Dictionary

This dictionary is frozen for the initial `control_tower` phase.
Future chats must reuse these exact terms unless a formal governance revision changes them.

## Managed domains

### `git_sentinel_modular`
Meaning:
The modular Git Sentinel package under:

`F:\repos\hitech-os\tools\hos\git_sentinel_modular`

Role:
- repo hygiene
- package-internal rollout logic
- package-internal docs/tests/plugins

### `engine_guardian`
Meaning:
The public engine guardian domain under:

`F:\repos\hitech-os\engine_guardian`

Role:
- public engine orchestration
- origin checks and remediation wrapper
- cloudflared service/tunnel validation wrapper
- public endpoint truth model
- official engine scheduler contract

### `repo_analizer`
Meaning:
The sibling system under:

`F:\repos\hitech-os\tools\graphviz\repo_analizer`

Role:
- sibling analytical domain
- wrapped by `engine_guardian`
- not absorbed as an internal owner of engine critical health

### `control_tower`
Meaning:
The governance and assurance layer under:

`F:\repos\hitech-os\control_tower`

Role:
- boundaries
- ownership
- gates
- artifacts
- snapshots
- assurance
- coordination rules

## Lifecycle states

These lifecycle states are canonical labels.

### `bundle`
Meaning:
A deliverable package exists and is structured for application.

### `validated`
Meaning:
Checks passed for the intended validation scope.

### `applied`
Meaning:
The deliverable was placed into the real target location.

### `activated`
Meaning:
A runtime or privileged activation step was completed where applicable.

### `closed`
Meaning:
The phase is considered complete and should not be reopened absent real evidence.

## Artifact kinds

### `zip_bundle`
A zip deliverable intended for application or handoff.

### `manifest`
A structured listing of files, intent, and placement metadata.

### `validation_report`
Evidence that a validation scope completed successfully or failed explicitly.

### `activation_report`
Evidence for privileged or runtime activation status.

### `snapshot`
A point-in-time structured state capture.

### `audit_record`
A durable trace of a governance or assurance observation.

### `evidence`
Any durable file, log, report, or record used to justify a state or decision.

## Verdicts

### `pass`
Condition satisfied.

### `fail`
Condition not satisfied.

### `blocked`
Condition cannot be evaluated or promoted due to a missing prerequisite or hard stop.

### `not_applicable`
The rule does not apply to the evaluated subject.

## Access modes

### `owned`
The domain is the recognized authority for the target object/path/capability.

### `read_only`
The domain may inspect, register, compare, or report but may not mutate.

### `forbidden`
The domain must neither mutate nor silently assume authority.

## Decision words

### `authoritative`
A source that is intended to control downstream interpretation.

### `normative`
A rule-defining source.

### `evidence-backed`
Supported by runtime or documentary evidence rather than assumption.

### `protected`
A system or path that must not be casually modified.

### `non-invasive`
Allowed to observe or define policy without mutating operational ownership.

## Naming rules

Future chats must not:
- rename `repo_analizer` to “repo_analyzer” in canonical docs unless a formal migration occurs
- invent new lifecycle names for the same lifecycle
- create parallel synonyms that fragment implementation
- silently widen the meaning of `activated` or `closed`

## Usage rule

If a future bundle needs extra terminology, it must:
- preserve this dictionary unchanged
- add new terms in an additive appendix
- avoid redefining existing canonical terms
