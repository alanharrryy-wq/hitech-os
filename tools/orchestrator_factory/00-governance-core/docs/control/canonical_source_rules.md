# Canonical Source Rules

## Principle
Every important fact needs a single place where it is considered authoritative. Everything else is derivative.

## Source precedence
1. frozen docs in `00-governance-core/`
2. `parallel_manifest.json`
3. homologated project baseline and project manifest
4. active run manifest
5. active round manifest
6. frozen package-local docs
7. generated work packets
8. generated prompts
9. validation reports and summaries
10. templates and examples

## Resolution rule
If two sources disagree, the higher-ranked source wins unless a newer decision record explicitly supersedes it.

## What is never canonical by itself
- chat memory
- prompt wording
- narrative summaries not linked to a frozen artifact
- examples
- outdated copies of contracts
- stale bundle reports

## Required canonical records
- package topology
- path ownership
- change budgets
- dictionary extensions
- freeze state
- accepted interface contracts
- run objective
- acceptance decisions
- topology overrides

## Update discipline
When a canonical source changes:
- record the reason
- record what it supersedes
- identify downstream consumers
- regenerate derivative packets and prompts when necessary
