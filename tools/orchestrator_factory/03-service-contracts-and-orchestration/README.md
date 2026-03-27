    # 03-service-contracts-and-orchestration - Service Contracts and Orchestration

    ## Mission
    Own service boundaries, API and event contracts, orchestration flows, error models, integration surfaces, and service wiring decisions.

    ## Owned framework path families
    - `03-service-contracts-and-orchestration/**`

    ## Runtime path ownership
    Project runtime paths are assigned during homologation and activated per round through the active work packet.

    ## Forbidden write zones
    - `00-governance-core/**`
    - sibling package folders
    - any runtime path not assigned to this package by the active path policy and work packet

    ## Dependencies
    - `00-governance-core`
- `01-identity-access-and-trust`
- `02-domain-data-and-persistence`

    ## Consumes
    - identity and access contracts
- domain and data contracts
- package contract template

    ## Produces
    - ['service contracts consumed by experience, platform, and quality packages']

    ## Deliverables in this package
    - service inventory
- API, event, or task contract map
- request and response contracts
- error and retry contract
- orchestration flow map
- integration boundary rules
- service wiring decisions
- payload examples and mock contracts

    ## Parallel safety rule
    This package may run in parallel with the other five downstream packages, but it may not redefine shared rules or touch another package's paths directly. If a new cross-cutting rule is needed, escalate to `00-governance-core`.
