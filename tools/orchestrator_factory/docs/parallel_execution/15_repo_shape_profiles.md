# Repo Shape Profiles

These are optional references, not constitutional rules.

## Profile A: website plus portal monorepo
- experience package owns `apps/site/**`, `apps/portal/**`
- service package owns `services/api/**`, `packages/contracts/**`
- platform package owns `infra/**`, deployment workflows
- quality package owns `tests/**`, `ops/runbooks/**`

## Profile B: service-heavy platform
- service package owns `services/**`
- experience package may be light or absent
- platform package owns infrastructure, workflows, observability
- quality package owns integration and resilience tests

## Profile C: migration or refactor overlay
- path ownership is assigned to existing legacy paths instead of greenfield folders
- package chats work through bounded overlays and anti-chaos rules
- governance records which legacy zones are read-only, modifiable, or donor-only
