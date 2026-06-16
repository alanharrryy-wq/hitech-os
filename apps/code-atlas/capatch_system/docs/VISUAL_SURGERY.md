# Visual Surgery

Visual changes require more than syntax success. A UI can compile and still look like a bus station monitor after a thunderstorm.

## Visual surgery gates

- surface allowlist must be explicit
- excluded surfaces must remain untouched
- global CSS changes need high scrutiny
- massive `CSS priority override` usage is suspicious
- dark-theme drift is blocked for Tablet unless explicitly requested
- legacy overlays/layers must not keep covering the new UI
- functional PASS is not visual PASS

## Recommended evidence

- target files before and after
- surface cartridge stack
- selectors/components touched
- visual intent
- screenshots or browser evidence when available
- rollback manifest
