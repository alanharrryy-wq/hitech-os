# 77_RUNTIME_ADAPTER_BINDING_ASSUMPTIONS

This pack assumes runtime integration remains adapter-driven.

It does not assume:

- unrestricted runtime ownership by the composer
- debug console authority transfer
- route-level hacks as a substitute for adapters

It does assume:

- named adapter seams
- explicit bridge routing
- diagnostics on rejection and adapter mismatch
