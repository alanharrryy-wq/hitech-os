# UI Map Glossary

- Route: Next.js `app/**/page.tsx` entry point.
- Screen Root: Primary pitch component rendered by a pitch route.
- Component: Exported TS/TSX symbol tracked by deterministic `component_id`.
- State: Store/state module with inferred readers/writers/events.
- Style: CSS file referenced by components.
- Asset: SVG/PNG or CSS background resource used by UI.
- Edge: Directed relation (`imports`, `renders`, `reads`, `writes`, etc.).
- Hotspot: High-leverage area for edits, grouped by risk and change type.
- Deterministic ID: Short stable hash derived from normalized key material.
- BLOCKED report: Generated when minimum discovery thresholds are not met.
