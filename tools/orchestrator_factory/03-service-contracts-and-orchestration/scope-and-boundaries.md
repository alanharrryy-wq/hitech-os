    # Scope and Boundaries for 03-service-contracts-and-orchestration

    ## In scope
    - service inventory
- API, event, or task contract map
- request and response contracts
- error and retry contract
- orchestration flow map
- integration boundary rules
- service wiring decisions
- payload examples and mock contracts

    ## Out of scope
    - changing global naming, dictionary, or path ownership
    - touching another package's folder
    - widening runtime path ownership without a governance decision record
    - redefining the project topology outside this package's responsibility
    - hiding unresolved upstream assumptions

    ## Write permissions
    This package may write only to:
    - `03-service-contracts-and-orchestration/**`
    - active runtime paths assigned to `03-service-contracts-and-orchestration` by the current work packet

    ## Read permissions
    This package may read governance docs and the specific upstream packages listed in its dependency list.

    ## Conflict rule
    If this package needs an upstream contract that is still provisional, it may draft around the gap but must mark the unresolved dependency explicitly and must not claim freeze.
