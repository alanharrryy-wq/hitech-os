    # Scope and Boundaries for 02-domain-data-and-persistence

    ## In scope
    - domain entities and aggregates
- entity relationships and state model
- data ownership model
- persistence and storage strategy
- event and history model
- migration and backfill strategy
- indexing and query strategy
- data quality and reconciliation rules

    ## Out of scope
    - changing global naming, dictionary, or path ownership
    - touching another package's folder
    - widening runtime path ownership without a governance decision record
    - redefining the project topology outside this package's responsibility
    - hiding unresolved upstream assumptions

    ## Write permissions
    This package may write only to:
    - `02-domain-data-and-persistence/**`
    - active runtime paths assigned to `02-domain-data-and-persistence` by the current work packet

    ## Read permissions
    This package may read governance docs and the specific upstream packages listed in its dependency list.

    ## Conflict rule
    If this package needs an upstream contract that is still provisional, it may draft around the gap but must mark the unresolved dependency explicitly and must not claim freeze.
