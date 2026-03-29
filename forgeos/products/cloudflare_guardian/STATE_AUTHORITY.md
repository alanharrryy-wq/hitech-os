# STATE AUTHORITY

| Slice | Owner | Source of truth | Readers | Writers |
| --- | --- | --- | --- | --- |
| `product.cloudflare_guardian.snapshots` | `forge_products_cloudflare_guardian` | product runtime memory | product runtime | product runtime |
| `product.cloudflare_guardian.report` | `forge_products_cloudflare_guardian` | product runtime report cache | product runtime + published host payload | product runtime |

Rule:

- Host receives only contribution payload summaries.