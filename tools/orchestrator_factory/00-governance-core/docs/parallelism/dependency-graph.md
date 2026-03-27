# Dependency Graph

## Upstream ruler
`00-governance-core` is upstream of every package and every tactical artifact.

## Default six-package dependency graph
- `01-identity-access-and-trust` depends on `00-governance-core`
- `02-domain-data-and-persistence` depends on `00-governance-core`
- `03-service-contracts-and-orchestration` depends on `00-governance-core`, `01-identity-access-and-trust`, `02-domain-data-and-persistence`
- `04-experience-clients-and-interactions` depends on `00-governance-core`, `01-identity-access-and-trust`, `03-service-contracts-and-orchestration`
- `05-platform-infrastructure-and-delivery` depends on `00-governance-core`, `03-service-contracts-and-orchestration`
- `06-quality-release-and-operations` depends on `00-governance-core`, `01-identity-access-and-trust`, `02-domain-data-and-persistence`, `03-service-contracts-and-orchestration`, `04-experience-clients-and-interactions`, `05-platform-infrastructure-and-delivery`

## Practical meaning
- The six package chats may run in parallel once governance is frozen.
- They may draft around provisional upstream interfaces, but they may not claim freeze until those upstream interfaces stabilize.
- Mission control integrates accepted outputs in dependency order, not arrival order.
