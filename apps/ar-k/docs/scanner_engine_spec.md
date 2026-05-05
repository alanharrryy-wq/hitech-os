# Scanner Engine Spec

Iteration-2 behavior:
- inventory files with stable normalized paths
- parse Python imports and exports
- observe frontend-adjacent surfaces in TS, TSX, JS, JSX, JSON, HTML, CSS, and Markdown
- classify surface kinds such as `entrypoint`, `route_surface`, `screen`, `component`, `desktop_bridge`, and `module_config`
- classify source paths with canon policy (`canonical_source` + `non_product_class`) so non-product classes stay observable but non-canonical
- emit `observed`, `candidate`, and `ambiguous` signals only
- emit route candidate artifacts and boundary candidate artifacts as non-canonical evidence
- keep canonical ownership untouched: scanner still writes only `signals`
