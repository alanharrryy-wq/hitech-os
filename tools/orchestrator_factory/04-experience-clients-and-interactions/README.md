    # 04-experience-clients-and-interactions - Experience, Clients, and Interactions

    ## Mission
    Own user-facing experiences, client architecture, journeys, interaction contracts, routing and navigation, client-state policy, and accessibility/performance rules.

    ## Owned framework path families
    - `04-experience-clients-and-interactions/**`

    ## Runtime path ownership
    Project runtime paths are assigned during homologation and activated per round through the active work packet.

    ## Forbidden write zones
    - `00-governance-core/**`
    - sibling package folders
    - any runtime path not assigned to this package by the active path policy and work packet

    ## Dependencies
    - `00-governance-core`
- `01-identity-access-and-trust`
- `03-service-contracts-and-orchestration`

    ## Consumes
    - identity and access contracts
- service contracts
- naming and path rules

    ## Produces
    - ['client-facing contracts and interaction-ready implementation plans']

    ## Deliverables in this package
    - experience architecture
- journey and route map
- client-state policy
- interaction contract map
- screen or surface inventory
- forms and validation rules
- loading, empty, and error state rules
- accessibility and client performance gates

    ## Parallel safety rule
    This package may run in parallel with the other five downstream packages, but it may not redefine shared rules or touch another package's paths directly. If a new cross-cutting rule is needed, escalate to `00-governance-core`.
