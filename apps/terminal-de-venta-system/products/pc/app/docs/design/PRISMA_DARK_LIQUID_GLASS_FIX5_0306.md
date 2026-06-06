# PRISMA Dark Liquid Glass Fix5

Scope: dark-only optical correction for the glass capsule benchmark.

## Visual contract

- No global blue wash. A pill must not carry a permanent cyan/blue field.
- Blur is nearly zero: base token `--pgc-blur: 0.25px`; localized lobe max `.35px`.
- Three perceptible frames are required:
  1. `edgeFrame`: 2px reactive color edge, uses backdrop sampling without blur.
  2. `volumeFrame`: dark middle thickness.
  3. `innerFrame`: inner refractive hairline.
- `lobeLens` is the localized left optical lobe. It may intensify/distort color locally, but must not tint the whole capsule.
- Background is a fixed dark field with text and small solid geometry pairs.
- Geometry pairs use max `1cm` internal spacing and `5cm` spacing between pairs so color fusion only appears by proximity.
- Six pills must be displayed in one horizontal row for visual comparison.

## Verification

- Static contract: `node tools/verify_prisma_glasscaps_dark_contract_0306.mjs`.
- Visual contract: `python tools/verify_prisma_glasscaps_dark_visual_0306.py`.
- Visual evidence is emitted into the package result ZIP under `visual-glasscaps-dark/`.
