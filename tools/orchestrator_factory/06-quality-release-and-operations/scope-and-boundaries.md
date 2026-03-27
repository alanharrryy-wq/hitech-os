    # Scope and Boundaries for 06-quality-release-and-operations

    ## In scope
    - test strategy
- smoke and regression plan
- contract verification matrix
- release gates
- operational readiness checklist
- post-release validation plan
- incident drill matrix
- observability verification checklist

    ## Out of scope
    - changing global naming, dictionary, or path ownership
    - touching another package's folder
    - widening runtime path ownership without a governance decision record
    - redefining the project topology outside this package's responsibility
    - hiding unresolved upstream assumptions

    ## Write permissions
    This package may write only to:
    - `06-quality-release-and-operations/**`
    - active runtime paths assigned to `06-quality-release-and-operations` by the current work packet

    ## Read permissions
    This package may read governance docs and the specific upstream packages listed in its dependency list.

    ## Conflict rule
    If this package needs an upstream contract that is still provisional, it may draft around the gap but must mark the unresolved dependency explicitly and must not claim freeze.
