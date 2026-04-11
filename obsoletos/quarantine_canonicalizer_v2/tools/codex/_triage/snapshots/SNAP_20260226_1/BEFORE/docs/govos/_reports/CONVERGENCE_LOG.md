# CONVERGENCE LOG

## Block 1 - Discovery + Convergence Model

- mode: write
- legacy_governance_docs_detected: 17
- auto_move_eligible: 0
- overflow_deferred: 0

## Block 2 - Canon Creation + Safe Neutralization + Validation

- moved_and_stubbed: 0
- preserved_legacy_docs: 17

## Mandatory File Resolution - 2026-02-26

- target_missing_file: `docs/factory/FACTORY_RUNTIME_EXPLAINED.md`
- action: pointer-only resolution (no content merge, no runtime/code changes)
- selected_canonical_source: `docs/factory/CONTRACT.md`

Candidate ranking (deterministic scoring + tie-break):

- `docs/factory/CONTRACT.md`: highest structural relevance for factory runtime behavior and run-layout execution model (`Run Layout Contract`, `Worker Bundle Contract`, `Integrator Bundle Contract`, `Status Evaluation Contract`, `Runtime Config Contract`)
- `docs/factory/RUNBOOK.md`: strong and more recent (`2026-02-21`) with operator flow, stage order, artifact layout, status semantics
- `docs/codex-kernel/docs/50_INTEGRATION_RULES.md`: strong STATUS/REPORT/DEBT/NEXT semantics, but broader integrator law and less factory-runtime-specific

Selection rationale:

- Multiple candidates existed.
- `docs/factory/CONTRACT.md` was selected as the most complete functional runtime explanation for the missing file purpose.
- A read-only pointer stub was created at `docs/factory/FACTORY_RUNTIME_EXPLAINED.md`.
