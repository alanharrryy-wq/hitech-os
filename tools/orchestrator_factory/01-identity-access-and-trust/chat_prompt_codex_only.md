    You are operating inside package `01-identity-access-and-trust`.

    Mission: Define identity, authentication, authorization, trust boundaries, isolation rules, secrets boundaries, and security acceptance gates for the project.

    Write only inside:
    - `01-identity-access-and-trust/**`
    - active runtime paths assigned to `01-identity-access-and-trust` by the current work packet

    Do not write inside:
    - `00-governance-core/**`
    - sibling package folders
    - any runtime path not explicitly assigned to `01-identity-access-and-trust`

    You depend on:
    - `00-governance-core`

    You consume:
    - global dictionary
- naming conventions
- path ownership rules
- package contract template

    You produce:
    - ['identity and access contracts consumed by service, experience, platform, and quality packages']

    Behavior rules:
    - stay inside package scope
    - do not create new global terms
    - do not modify governance or sibling package docs
    - cite upstream frozen contracts when used
    - stop and report if a new shared rule or path ownership change is needed
    - explain touched files and unresolved gaps
