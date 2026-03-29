    # Dependency Contracts for 01-identity-access-and-trust

    ## Upstream dependencies
    - `00-governance-core`

    ## Consumed artifacts
    - global dictionary
- naming conventions
- path ownership rules
- package contract template

    ## Downstream expectations
    - ['identity and access contracts consumed by service, experience, platform, and quality packages']

    ## Dependency discipline
    - do not silently redefine upstream contracts
    - cite the upstream doc that a local rule depends on
    - if an upstream rule changes, update only the local package-owned docs and runtime paths affected
    - escalate if a dependency change alters package topology or ownership
