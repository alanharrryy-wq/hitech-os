    # Scope and Boundaries for 05-platform-infrastructure-and-delivery

    ## In scope
    - environment and topology map
- runtime and infrastructure plan
- configuration and secrets matrix
- deployment and release workflow
- observability and telemetry strategy
- rollback and recovery plan
- operations runbooks
- platform limits and assumptions register

    ## Out of scope
    - changing global naming, dictionary, or path ownership
    - touching another package's folder
    - widening runtime path ownership without a governance decision record
    - redefining the project topology outside this package's responsibility
    - hiding unresolved upstream assumptions

    ## Write permissions
    This package may write only to:
    - `05-platform-infrastructure-and-delivery/**`
    - active runtime paths assigned to `05-platform-infrastructure-and-delivery` by the current work packet

    ## Read permissions
    This package may read governance docs and the specific upstream packages listed in its dependency list.

    ## Conflict rule
    If this package needs an upstream contract that is still provisional, it may draft around the gap but must mark the unresolved dependency explicitly and must not claim freeze.
