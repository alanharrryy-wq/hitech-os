# STATE AUTHORITY

| Slice | Owner | Source of truth | Readers | Writers |
| --- | --- | --- | --- | --- |
| `product.dummy.runtime` | `forge_products_dummy` | in-memory product runtime store | product + host published summary | product runtime |

Rule:

- Host receives only published context, never direct product state mutations.