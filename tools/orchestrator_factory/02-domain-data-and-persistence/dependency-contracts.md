    # Dependency Contracts for 02-domain-data-and-persistence

    ## Upstream dependencies
    - `00-governance-core`

    ## Consumed artifacts
    - global dictionary
- naming conventions
- path ownership rules

    ## Downstream expectations
    - ['domain and data contracts consumed by service, platform, and quality packages']

    ## Dependency discipline
    - do not silently redefine upstream contracts
    - cite the upstream doc that a local rule depends on
    - if an upstream rule changes, update only the local package-owned docs and runtime paths affected
    - escalate if a dependency change alters package topology or ownership
