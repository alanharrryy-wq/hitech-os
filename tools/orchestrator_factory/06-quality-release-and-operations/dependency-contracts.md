    # Dependency Contracts for 06-quality-release-and-operations

    ## Upstream dependencies
    - `00-governance-core`
- `01-identity-access-and-trust`
- `02-domain-data-and-persistence`
- `03-service-contracts-and-orchestration`
- `04-experience-clients-and-interactions`
- `05-platform-infrastructure-and-delivery`

    ## Consumed artifacts
    - all upstream contracts and acceptance gates

    ## Downstream expectations
    - ['execution proof, release readiness, and operational validation evidence']

    ## Dependency discipline
    - do not silently redefine upstream contracts
    - cite the upstream doc that a local rule depends on
    - if an upstream rule changes, update only the local package-owned docs and runtime paths affected
    - escalate if a dependency change alters package topology or ownership
