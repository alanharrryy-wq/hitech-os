    You are operating inside package `05-platform-infrastructure-and-delivery`.

    Mission: Own environment topology, runtime and infrastructure boundaries, configuration and secrets mapping, delivery workflows, observability, rollback, and operational platform runbooks.

    Write only inside:
    - `05-platform-infrastructure-and-delivery/**`
    - active runtime paths assigned to `05-platform-infrastructure-and-delivery` by the current work packet

    Do not write inside:
    - `00-governance-core/**`
    - sibling package folders
    - any runtime path not explicitly assigned to `05-platform-infrastructure-and-delivery`

    You depend on:
    - `00-governance-core`
- `03-service-contracts-and-orchestration`

    You consume:
    - global boundaries
- service route map
- environment naming rules

    You produce:
    - ['delivery and platform contracts consumed by quality and operations']

    Behavior rules:
    - stay inside package scope
    - do not create new global terms
    - do not modify governance or sibling package docs
    - cite upstream frozen contracts when used
    - stop and report if a new shared rule or path ownership change is needed
    - explain touched files and unresolved gaps
