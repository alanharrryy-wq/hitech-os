# STATE AUTHORITY

| Slice | Owner | Source of truth | Readers | Writers |
| --- | --- | --- | --- | --- |
| `product.repo_analyzer.runtime` | `forge_products_repo_analyzer` | product runtime memory | product + published host summary | product runtime |
| `product.repo_analyzer.index` | `forge_products_repo_analyzer` | product analysis results | product | product runtime |

Rule:

- Host only receives contribution payloads and never mutates product state.