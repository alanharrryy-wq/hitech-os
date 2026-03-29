# STATE AUTHORITY

| Slice | Owner | Source of truth | Readers | Writers |
| --- | --- | --- | --- | --- |
| `product.orchestrator_bridge.workflows` | `forge_products_orchestrator_bridge` | product runtime workflow registry | product runtime | product runtime |
| `product.orchestrator_bridge.last_report` | `forge_products_orchestrator_bridge` | product runtime report cache | product runtime + published host payload | product runtime |

Rule:

- Host receives summarized report payload only.