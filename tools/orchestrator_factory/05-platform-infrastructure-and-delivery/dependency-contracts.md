    # Dependency Contracts for 05-platform-infrastructure-and-delivery

    ## Upstream dependencies
    - `00-governance-core`
- `03-service-contracts-and-orchestration`

    ## Consumed artifacts
    - global boundaries
- service route map
- environment naming rules

    ## Downstream expectations
    - ['delivery and platform contracts consumed by quality and operations']

    ## Dependency discipline
    - do not silently redefine upstream contracts
    - cite the upstream doc that a local rule depends on
    - if an upstream rule changes, update only the local package-owned docs and runtime paths affected
    - escalate if a dependency change alters package topology or ownership
