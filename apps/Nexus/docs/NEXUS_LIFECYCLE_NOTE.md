# Nexus Hosted Lifecycle Note

```
Desktop Operator
    |
    v
NexusGlassDesktopWindow (host composition)
    |
    | command/query/snapshot/event calls
    v
NexusHostedModule
    |
    v
InProcessIntegrationAdapter
    |
    v
IntegrationService (neutral contracts)
    |
    +--> GlassRuntimeIntegrationBridge (workspace.* commands/queries/snapshots)
    |
    +--> Nexus contract handlers (nexus.*)
              |
              v
        NexusRuntimeEngine (business/runtime state + timeline)
```

## Execution profile

- Desktop-first: in-process adapter is the primary route.
- Optional local HTTP bridge exists for external test clients.
- Shared glass host remains reusable and Nexus-specific behavior stays under `apps/Nexus`.

