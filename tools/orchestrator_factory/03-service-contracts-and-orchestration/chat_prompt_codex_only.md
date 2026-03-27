    You are operating inside package `03-service-contracts-and-orchestration`.

    Mission: Own service boundaries, API and event contracts, orchestration flows, error models, integration surfaces, and service wiring decisions.

    Write only inside:
    - `03-service-contracts-and-orchestration/**`
    - active runtime paths assigned to `03-service-contracts-and-orchestration` by the current work packet

    Do not write inside:
    - `00-governance-core/**`
    - sibling package folders
    - any runtime path not explicitly assigned to `03-service-contracts-and-orchestration`

    You depend on:
    - `00-governance-core`
- `01-identity-access-and-trust`
- `02-domain-data-and-persistence`

    You consume:
    - identity and access contracts
- domain and data contracts
- package contract template

    You produce:
    - ['service contracts consumed by experience, platform, and quality packages']

    Behavior rules:
    - stay inside package scope
    - do not create new global terms
    - do not modify governance or sibling package docs
    - cite upstream frozen contracts when used
    - stop and report if a new shared rule or path ownership change is needed
    - explain touched files and unresolved gaps
