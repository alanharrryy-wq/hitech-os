
# 00 Governance Core

## Mission
This is the constitutional package. It owns the operating model, project intake and homologation rules, run lifecycle, canonical source rules, naming, package boundaries, review model, decision logging rules, and the tactical subsystem used by every governed run.

## Why this package exists
Parallel chats drift unless one package owns the language, the boundaries, the handoff model, and the criteria for what counts as valid work. This package exists to prevent duplicate effort, hidden scope drift, interface confusion, and merge chaos.

## Scope
- operating model for the operator, governance chat, package chats, and execution agents
- idea intake and homologation
- install versus bootstrap versus run versus round separation
- framework readiness gates and go-live discipline
- run lifecycle and run ID standard
- canonical source rules and documentation layering
- inter-chat communication policy
- waiver and exception policy
- contract versioning policy
- package topology, dependency graph, path ownership, and change budgets
- freeze protocol, merge protocol, and handoff protocol
- review model, escalation model, decision logging rules, and canonical-tree hygiene
- tactical subsystem governance for rounds, packets, bundles, validation, and acceptance

## Non-goals
- it does not define domain-specific product behavior in detail
- it does not define service payloads in detail
- it does not define UI behavior in detail
- it does not define provider-specific infrastructure steps in detail
- it does not replace package-local contracts with vague central summaries
- it does not let prompts outrank the constitution

## Rule of authority
If a downstream package, generated prompt, or tactical artifact disagrees with a frozen governance rule, the governance rule wins until governance explicitly records a change.
