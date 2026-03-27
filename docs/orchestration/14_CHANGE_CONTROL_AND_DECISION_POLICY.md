# Change Control and Decision Policy

This document defines how changes to the `control_tower` documentary baseline should be controlled.

## Why this exists

Without change control, governance docs decay into soft suggestions and then the implementation layer starts freelancing.
That is exactly the kind of architectural sopa aguada this phase is supposed to prevent.

## What counts as a governed change

A governed change includes any modification to:

- shared dictionary terms
- ownership assignments
- boundary doctrine
- file allocation between chats
- promotion gates
- path authority classifications
- artifact kind definitions
- assurance verdict semantics

## What does not count as a governed change

Purely editorial improvements may be lighter weight if they do not change meaning, such as:
- typo correction
- formatting cleanup
- clearer headings

Even then, they should avoid introducing ambiguity.

## Mandatory inputs for a governed change

A proposal to revise this baseline must state:

1. the exact document(s) affected
2. the current rule
3. the proposed new rule
4. the reason for change
5. the risk if not changed
6. the migration impact
7. the cross-chat compatibility impact
8. whether closed operational fronts remain closed

## Decision standard

A change should not be accepted merely because:
- it is convenient
- it would reduce implementation effort
- it makes one chat “more powerful”
- it collapses multiple roles into one module

## Conservative default

If a change would widen operational authority, the default answer is:
- no, unless explicitly justified by evidence and governance review

## Required review questions

Before accepting a governance change, answer:

- Does this change preserve non-invasive behavior?
- Does it widen ownership into a protected domain?
- Does it create overlap between Chat A and Chat B?
- Does it undermine read-only restrictions?
- Does it weaken the documentary baseline into stubs or vague shells?
- Does it reopen a closed front by implication?

## Emergency exception rule

An emergency exception is not created by stress or impatience.
Only real evidence of a failure may justify crossing into an otherwise protected area, and even then the exception must be explicit and limited.

## Decision outputs

A change proposal should produce one of:
- approved
- rejected
- blocked pending evidence
- deferred

## Documentation rule for approved changes

If a change is approved:
- update the affected canonical document(s)
- update any dependent matrices or glossary terms
- keep the change trace explicit
- do not leave contradictory parallel docs behind

## Final principle

Governance exists to make future implementation sharper, not blurrier.
If a proposed change makes the system easier to misunderstand, that change is probably garbage and should stay outside the gate.
