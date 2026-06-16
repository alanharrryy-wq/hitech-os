# Capatch visual delta gates

This fix makes `visual-static-gates` baseline/delta aware.

## Why

Large legacy files such as `pos.module.css` can contain hundreds of historical
`!important` declarations or old dark tokens. A surgical patch should not fail
because of debt that already existed before the patch.

## New behavior

- Existing `!important` debt becomes a warning when a baseline/checkpoint exists.
- The verifier fails only when the patch adds more new `!important` declarations
  than the configured delta limit.
- `#000` inside `mask` or `-webkit-mask` declarations is ignored.
- `#000`, `black`, `#111`, `#0b0b0b`, and similar dark tokens are risky only in
  visual declarations such as `background`, `color`, `border`, `box-shadow`, etc.
- For large legacy files without a baseline, old debt is warning metadata, not a
  hard blocker.

## Context used for delta mode

The verifier first looks for explicit before-text mappings in the verifier
context, then for `checkpoint_dir`. The patch pipeline now passes
`checkpoint_dir` into verifier context so normal Capatch apply/verify runs can
compare final files against the checkpoint backup made before mutation.

## Tunables

- `CAPATCH_VISUAL_IMPORTANT_DELTA_LIMIT`, default `2`.
- `CAPATCH_VISUAL_IMPORTANT_ABSOLUTE_LIMIT`, default `8`.
- `CAPATCH_VISUAL_LEGACY_IMPORTANT_LIMIT`, default `50`.
- `CAPATCH_VISUAL_LEGACY_LINE_LIMIT`, default `1000`.
