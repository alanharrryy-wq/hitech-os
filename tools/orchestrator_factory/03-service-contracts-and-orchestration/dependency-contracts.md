    # Dependency Contracts for 03-service-contracts-and-orchestration

    ## Upstream dependencies
    - `00-governance-core`
- `01-identity-access-and-trust`
- `02-domain-data-and-persistence`

    ## Consumed artifacts
    - identity and access contracts
- domain and data contracts
- package contract template

    ## Downstream expectations
    - ['service contracts consumed by experience, platform, and quality packages']

    ## Dependency discipline
    - do not silently redefine upstream contracts
    - cite the upstream doc that a local rule depends on
    - if an upstream rule changes, update only the local package-owned docs and runtime paths affected
    - escalate if a dependency change alters package topology or ownership
