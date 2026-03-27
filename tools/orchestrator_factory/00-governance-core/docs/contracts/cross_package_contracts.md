# Cross-Package Contracts

## Contract philosophy
Downstream packages consume frozen or explicitly provisional outputs from upstream packages. When a contract is provisional, downstream work may draft against it but may not claim production readiness.

## Mandatory shared contract flows

### Identity, Access, and Trust -> Service and Experience
- identity vocabulary
- authentication and session boundaries
- authorization terms
- isolation rules
- secrets and trust assumptions

### Domain, Data, and Persistence -> Service
- identifiers
- state and event semantics
- ownership rules
- persistence constraints
- migration assumptions

### Service Contracts and Orchestration -> Experience
- service boundaries
- request and response contracts
- error and retry contract
- integration timing assumptions

### Service Contracts and Orchestration -> Platform
- route and integration map
- runtime dependencies
- environment and secret requirements

### Platform and Delivery -> Quality and Operations
- deploy environments
- telemetry surfaces
- rollback assumptions
- operational commands and thresholds

### All upstream packages -> Quality, Release, and Operations
- acceptance gates
- invariants worth testing
- release blockers
- operational failure modes

## Conflict resolution
If two packages define the same concept differently, governance selects the canonical definition and records what is superseded.
