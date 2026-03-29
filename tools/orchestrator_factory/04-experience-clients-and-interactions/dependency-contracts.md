    # Dependency Contracts for 04-experience-clients-and-interactions

    ## Upstream dependencies
    - `00-governance-core`
- `01-identity-access-and-trust`
- `03-service-contracts-and-orchestration`

    ## Consumed artifacts
    - identity and access contracts
- service contracts
- naming and path rules

    ## Downstream expectations
    - ['client-facing contracts and interaction-ready implementation plans']

    ## Dependency discipline
    - do not silently redefine upstream contracts
    - cite the upstream doc that a local rule depends on
    - if an upstream rule changes, update only the local package-owned docs and runtime paths affected
    - escalate if a dependency change alters package topology or ownership
