    # Scope and Boundaries for 04-experience-clients-and-interactions

    ## In scope
    - experience architecture
- journey and route map
- client-state policy
- interaction contract map
- screen or surface inventory
- forms and validation rules
- loading, empty, and error state rules
- accessibility and client performance gates

    ## Out of scope
    - changing global naming, dictionary, or path ownership
    - touching another package's folder
    - widening runtime path ownership without a governance decision record
    - redefining the project topology outside this package's responsibility
    - hiding unresolved upstream assumptions

    ## Write permissions
    This package may write only to:
    - `04-experience-clients-and-interactions/**`
    - active runtime paths assigned to `04-experience-clients-and-interactions` by the current work packet

    ## Read permissions
    This package may read governance docs and the specific upstream packages listed in its dependency list.

    ## Conflict rule
    If this package needs an upstream contract that is still provisional, it may draft around the gap but must mark the unresolved dependency explicitly and must not claim freeze.
