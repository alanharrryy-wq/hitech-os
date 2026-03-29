# Rules and Restrictions

This document is the hard behavioral policy for the first `control_tower` phase.

## Rule 1. Closed means closed

If a phase is `closed`, that does not mean “keep tinkering carefully.”
It means:
- no reopening by default
- no opportunistic rewrites
- no hidden “while I was there” changes

Applies to:
- `git_sentinel_modular`
- `engine_guardian`

## Rule 2. Evidence before invasion

A protected domain may be revisited only with new evidence of a real issue.
Examples of acceptable evidence:
- failing runtime reports
- broken scheduler contract proof
- missing expected artifacts
- explicit validation failure

Examples of unacceptable evidence:
- vague discomfort
- desire for cleanup
- preference for different architecture
- implementation convenience

## Rule 3. `control_tower` is non-invasive by default

`control_tower` may:
- define policy
- read and compare state
- register artifacts
- produce snapshots
- produce assurance judgments

`control_tower` may not:
- remediate engine issues
- control services
- re-register tasks
- mutate guardian runtime
- mutate sentinel internals
- touch legacy-protected tasks casually

## Rule 4. Chat A and Chat B must not overlap

Parallel work is allowed only when:
- files are non-overlapping
- concepts use the same dictionary
- code does not create hard import dependency across unfinished parallel tracks

## Rule 5. Read-only means read-only

A reader, registry, snapshot, or audit component must not:
- write operational state into guardian
- modify scheduler artifacts
- disable or enable tasks
- rotate logs for convenience
- “self-heal” missing files

## Rule 6. No vocabulary drift

Do not:
- rename canonical domains
- create duplicate lifecycle names
- introduce synonyms that fragment code and docs

Use the shared dictionary exactly.

## Rule 7. Docs outrank convenience

If code generation pressure conflicts with the documentary baseline, fix the code plan.
Do not weaken the docs to fit a hasty implementation.

## Rule 8. No hidden authority widening

A component that reads another domain does not become its owner.
A component that generates reports does not become a scheduler controller.
A governance module does not become a runtime operator.

## Rule 9. Promotion requires explicit gate evaluation

No bundle should be treated as ready because it “looks complete.”
Promotion requires the documented gates in `08_PROMOTION_RULES.md`.

## Rule 10. Support the user workflow

All future deliverables should stay aligned with the user’s working rules:
- full files
- zip-first delivery
- single PowerShell installer when scripts are involved
- progress indicator
- `F:\OneDrive\Descargas` as reference download root
- prompts for Codex in English

## Rule 11. No shadow registries

If artifacts, snapshots, or assurance verdicts are defined, they must follow the canonical docs.
Do not create competing mini-registry models in random modules.

## Rule 12. Escalate uncertainty as `blocked`

If a condition cannot be evaluated safely, use:
- `blocked`

Do not guess and do not promote based on vibes.

## Rule 13. Preserve documentary completeness

Future bundles must not replace these docs with:
- tiny stubs
- TODO-heavy shells
- vague placeholders
- one-paragraph summaries

These docs are meant to be dense enough to prevent architectural drift.

## Rule 14. The governance layer is not a pretext for empire building

`control_tower` exists to coordinate and constrain, not to absorb every neighboring domain into itself.
