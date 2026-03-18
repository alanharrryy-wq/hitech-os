# 54_BRIDGE_ADAPTER_ROUTING_RULES

## Adapter role

Adapters translate approved mutation envelopes into bridge-facing or runtime-facing operations without leaking policy ownership into UI surfaces.

## Requirements
- adapter routing must remain explicit
- adapter selection must be based on typed mutation class
- adapter failures must be surfaced clearly
- adapters must not swallow bridge rejection reasons
- adapter code must not invent authority the bridge did not grant

## Example routing groups
- scene appearance adapter
- layout mutation adapter
- slot insertion adapter
- widget props/style adapter
- draft workflow adapter

## Anti-patterns
- one giant adapter that handles everything informally
- routing by string hacks with hidden fallbacks
- direct UI import of runtime-specific APIs
