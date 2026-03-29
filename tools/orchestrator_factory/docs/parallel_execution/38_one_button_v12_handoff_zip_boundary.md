# One-Button v1.2 Handoff Zip Boundary

## Document Status
- Status: Frozen
- Version: v1.2
- Scope: boundary between local runtime artifacts and conversational orchestration

## 1. Why this boundary matters
The one-button launcher is not the final prompt generator for the six chat threads. Its job is to produce a clean, canonical session bundle that captures enough runtime state to let ChatGPT synthesize those prompts later.

This boundary keeps responsibilities clean:
- the launcher gathers, normalizes, validates, and exports runtime state,
- ChatGPT consumes the zip later and generates the six final prompts.

This split is deliberate. It prevents the launcher from becoming tightly coupled to conversational prompt templates that may evolve faster than the runtime state model.

## 2. What the zip must contain for handoff
The zip must provide enough context for downstream orchestration to answer:
- what session was created,
- which project/run/round it targets,
- what the normalized intent was,
- whether the session is new or reused,
- what coordination state exists,
- whether acceptance is pending or completed,
- which warnings matter before chat-level dispatch.

The required v1.2 artifacts already cover this minimum.

## 3. What the zip must not try to do
The v1.2 zip is **not** responsible for:
- storing final human-ready six-chat prompts,
- encoding a GUI plugin state,
- becoming an all-purpose project archive.

If prompt seed files exist under `round/prompts/`, they remain runtime prompt seeds or coordination seeds, not the final human chat prompts.

## 4. Handoff copy behavior
The implementation may create an operator-friendly copy of the canonical zip in a configured handoff directory, typically under a downloads path. This is a delivery convenience, not the source of truth.

Source of truth:
`ops\projects\<project_id>\bundles\sessions\<session_id>.zip`

Handoff copy:
configured via `one_button_config.json`

## 5. Handoff quality bar
A handoff zip is acceptable when:
1. it validates structurally,
2. its manifest is complete,
3. its issues make warnings and blockers visible,
4. its file index is internally consistent,
5. it is sufficient for ChatGPT to derive downstream prompts without reopening fragile runtime internals.

## 6. Relationship to operator instructions
`session/operator_instructions.md` should tell the human:
- the canonical zip location,
- the handoff copy location if created,
- the exact next step: provide the zip back into ChatGPT.

The operator should not need to inspect internal packet files manually unless debugging.

## 7. Why `dispatch_plan.json` is excluded in v1.2
The handoff boundary requires the minimum reliable coordination state, not speculative or placeholder artifacts. Since `dispatch_plan.json` is not guaranteed by the current runtime contract, v1.2 excludes it from the minimum. This reduces false certainty and keeps the bundle honest.

## 8. Expected downstream use
A downstream conversational consumer should be able to:
- parse the manifest,
- inspect project/run/round state,
- read normalized intent,
- inspect readiness and acceptance state,
- derive final prompt instructions.

That consumer should not depend on ephemeral lock files, local temp directories, or console logs.

## 9. Future evolution
Future versions may add:
- richer coordination plans,
- prompt synthesis metadata,
- dispatch-ready thread manifests.

Those additions should remain additive and versioned rather than silently mutating the v1.2 boundary.

## 10. Acceptance criteria
The handoff boundary is correct when:
- the zip is self-describing enough for downstream prompt generation,
- final chat prompts are intentionally generated later,
- the runtime remains focused on deterministic local orchestration.
