# Dev Console Architectural Laws

Status: active  
Enforced by: `tools/dev-console/architecture_guard.py`

## Law 1: Inspect Panels Are Read-Only Over Presentation

Inspect-domain panel files must not perform direct presentation mutation.

Machine checks:
- forbid direct DOM mutation patterns in inspect panel files

## Law 2: Compose Panels Cannot Mutate Diagnostics State

Compose-domain panel files must not call diagnostics mutation APIs.

Machine checks:
- forbid diagnostics mutation tokens in compose panel files (`setDiagnosticsSnapshot`, direct diagnostics request triggers, etc.)

## Law 3: ConsoleCore Cannot Hide Domain Logic

Core modules may orchestrate infrastructure but may not replace inspect/compose responsibilities.

Machine checks:
- panel contracts require explicit domain mapping
- scanner fails if panel files exist without declared domain contract

## Law 4: Contractual Events Require Consumers

Any contractual event marked as required must have at least one listener.

Machine checks:
- detect emitter/listener presence for contract event symbols
- fail if required listener missing

## Law 5: SceneLookModel Is Canonical For Visual Composition

Compose panels marked with `requires_scene_look_model=true` must use `SceneLookModel` APIs.

Machine checks:
- scanner verifies declared compose files include `sceneLookModel`/`updateSceneLookModel` usage

## Law 6: Domain Contracts Are Mandatory

Every panel file under Dev Console panel directories must have a contract entry with:
- `id`
- `domain`
- `file`
- `requires_scene_look_model`

Machine checks:
- scanner compares discovered panel files against `docs/dev-console/contracts/panels.json`

## Law 7: Violations Fail CI

Any architecture guard violation must fail CI.

Machine checks:
- dedicated workflow executes scanner with strict mode
