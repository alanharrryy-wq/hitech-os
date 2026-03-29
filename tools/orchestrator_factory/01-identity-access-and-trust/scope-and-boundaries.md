    # Scope and Boundaries for 01-identity-access-and-trust

    ## In scope
    - identity model
- authentication and session model
- authorization vocabulary and policy rules
- isolation model
- secrets and credential boundaries
- threat model v1
- security acceptance gates
- incident and trust response playbook

    ## Out of scope
    - changing global naming, dictionary, or path ownership
    - touching another package's folder
    - widening runtime path ownership without a governance decision record
    - redefining the project topology outside this package's responsibility
    - hiding unresolved upstream assumptions

    ## Write permissions
    This package may write only to:
    - `01-identity-access-and-trust/**`
    - active runtime paths assigned to `01-identity-access-and-trust` by the current work packet

    ## Read permissions
    This package may read governance docs and the specific upstream packages listed in its dependency list.

    ## Conflict rule
    If this package needs an upstream contract that is still provisional, it may draft around the gap but must mark the unresolved dependency explicitly and must not claim freeze.
