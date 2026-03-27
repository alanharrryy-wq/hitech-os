    # 05-platform-infrastructure-and-delivery - Platform, Infrastructure, and Delivery

    ## Mission
    Own environment topology, runtime and infrastructure boundaries, configuration and secrets mapping, delivery workflows, observability, rollback, and operational platform runbooks.

    ## Owned framework path families
    - `05-platform-infrastructure-and-delivery/**`

    ## Runtime path ownership
    Project runtime paths are assigned during homologation and activated per round through the active work packet.

    ## Forbidden write zones
    - `00-governance-core/**`
    - sibling package folders
    - any runtime path not assigned to this package by the active path policy and work packet

    ## Dependencies
    - `00-governance-core`
- `03-service-contracts-and-orchestration`

    ## Consumes
    - global boundaries
- service route map
- environment naming rules

    ## Produces
    - ['delivery and platform contracts consumed by quality and operations']

    ## Deliverables in this package
    - environment and topology map
- runtime and infrastructure plan
- configuration and secrets matrix
- deployment and release workflow
- observability and telemetry strategy
- rollback and recovery plan
- operations runbooks
- platform limits and assumptions register

    ## Parallel safety rule
    This package may run in parallel with the other five downstream packages, but it may not redefine shared rules or touch another package's paths directly. If a new cross-cutting rule is needed, escalate to `00-governance-core`.
