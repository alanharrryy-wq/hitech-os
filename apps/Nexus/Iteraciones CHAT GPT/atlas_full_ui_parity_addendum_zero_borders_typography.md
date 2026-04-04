# Atlas Full UI Parity Addendum

## Scope of this addendum
This addendum is for the remaining full-surface visual mismatch outside the backdrop/chrome parity pass.

It covers three concrete problems that are still visible right now:

1. the cyan edge/readability cue is still too weak or missing on many components
2. text is still too small across the workbench and examples
3. there are still too many visible borders/frames, when the current target should be almost borderless

This is **not** a redesign pass.
This is a **strict visual correction pass** to make the package easier to read and visually closer to the intended Atlas feel.

---

## Short verdict
The package is still failing parity at the full-component level because the problem is no longer just the backdrop.

The real mismatch is now in:
- global stylesheet density and typography defaults
- border policy across cards, buttons, dashboards, search bars, segmented controls, pills, inputs, and container frames
- weak cyan edge signaling in the exact places where the eye needs separation
- examples opening with a typography scale that is too small for practical use

---

## Desired target for this pass
Apply this target literally:

- text must become visibly larger by default
- all decorative borders should be removed or reduced to ultra-thin cyan edges
- buttons should read as soft surfaces, not boxed controls
- dashboards/panels/cards should read as floating glass blocks, not framed boxes
- the cyan separation line should exist only where it helps readability
- border thickness must stay at `0px`, `1px`, or at most `2px`
- default user experience should prioritize readability over density

---

## Critical interpretation rule
For now, the border policy is:

- **Buttons:** zero visible frame unless hover/focus/active state needs a 1px cyan cue
- **Cards / panels / dashboards:** no heavy frames; default to either no border or a 1px very soft cyan edge
- **Inputs / search bars / segmented controls:** 1px cyan edge max
- **Window chrome:** 1px is acceptable
- **No component should ship with thick gray/silver framing right now**

---

## What is already present but underused
The package already contains typography infrastructure.

Specifically:
- `config.py` already has `GlassTypographyConfig.scale`
- `theme.py` already supports `typography_scale`
- examples already reference `sm`, `md`, `lg` in places

So the problem is **not** “missing typography support”.
The problem is:
- the default is still too small for real use
- that setting is not surfaced as a simple obvious control across the examples/workbench flow
- the stylesheet still produces weak readability for secondary text

---

# Exact change matrix

| Priority | File | Problem | Required action | Create new file? | Connection |
|---|---|---|---|---|---|
| 1 | `theme.py` | text too small + too many borders | raise default readable typography and collapse border policy | No | global stylesheet source of truth |
| 2 | `atlas_styles.py` | chrome/button overrides still framed | make Atlas overrides border-minimal with cyan-only cues | No | already concatenated through exact stylesheet pipeline |
| 3 | `config.py` | typography scale exists but is not ergonomic for readability | make larger default and expose clear user-facing scale options | No | consumed by examples/workbench settings |
| 4 | `scene.py` | stylesheet pipeline does not expose user typography choice clearly enough | ensure exact stylesheet can receive explicit typography scale | No | pass-through from examples/app shell |
| 5 | `examples/catalog_shell.py` | default UI still opens too small and too framed | set larger default typography and expose obvious scale selector | No | workbench entrypoint |
| 6 | `examples/demo_app.py` | demo still opens too small | set larger default typography | No | demo entrypoint |
| 7 | `controls.py` | buttons still read too boxed | enforce border-minimal default behavior | No | every call to `create_button()` |
| 8 | `dashboard.py` + `primitives.py` + `charts.py` | dashboards/cards/metric shells still feel boxed | remove decorative borders and keep ultra-thin cyan cues only where needed | No | shared component surface styling |

---

# 1) `theme.py`

## File to change
`forgeos/shared/pyside6_glass/theme.py`

## This is the main source of truth for the remaining mismatch
The biggest remaining problem is here.

The global stylesheet is still creating too much visual boxing and too-small text.

## Required changes

### A. Raise default readability
Do not leave the practical default at the current too-small feel.

Set the effective default so the package opens in a clearly readable size.
For this pass:
- use `lg` as the default runtime typography target for examples/workbench
- keep `md` available, but do not use it as the default visible workbench size

### B. Increase secondary text readability
The following roles are currently too tiny/faint in real use and need a noticeable bump:
- `subtitle`
- `hint`
- `value`
- `caption`
- `microcopy`
- `eyebrow`
- `field`
- `panel_title`
- `panel_subtitle`
- `window_title`

Do not make them huge.
Make them readable.

### C. Collapse border policy globally
Audit all global selectors in `theme.py` and apply this rule:

#### Default borders
- default containers: `border: none` or `1px solid rgba(140, 235, 255, 0.10 to 0.18)` max
- no silver/gray heavy outline look
- no multi-frame look

#### Buttons
For `QPushButton` default state:
- remove visible heavy frame
- use soft glass fill
- `border: none` by default
- hover: `1px solid rgba(140, 235, 255, 0.35 to 0.55)`
- pressed/focus: `1px solid rgba(140, 235, 255, 0.70 to 0.90)`
- max thickness: `1px`

#### Cards / panels
For:
- `QFrame[card="hero"]`
- `QFrame[card="true"]`
- `QFrame[card="muted"]`
- `QFrame[card="footer"]`
- all `panelRole=*`

use:
- either `border: none`
- or `1px solid rgba(140, 235, 255, 0.10 to 0.16)` if separation is needed

No thick shell look.
No obvious boxed dashboard feel.

#### Search bars / segmented controls / pills
For:
- `assetRole="segmented"`
- `assetRole="filter_chip_bar"`
- `assetRole="compact_toolbar"`
- `assetRole="search_bar"`
- `assetRole="status_pill"`
- `assetRole="stat_pill"`
- `assetRole="control_card"`
- `assetRole="hero_panel"`

reduce framing to:
- default `border: none` or `1px` ultra-soft cyan
- active/selected/focus may use a stronger `1px` cyan edge
- absolute max `2px`, but prefer `1px`

### D. Make cyan cues visible where they matter
The screenshot shows that the cyan edge language is not carrying through strongly enough.

Add or strengthen the cyan cue only in these places:
- panel separation
- hoverable cards
- active segmented button
- focused input
- focused search bar
- selected pill/chip
- active tab / active section edge

Do not blanket everything with cyan borders.
Use it as a precision readability cue.

---

# 2) `atlas_styles.py`

## File to change
`forgeos/shared/pyside6_glass/atlas_styles.py`

## Problem
The current override layer still keeps too much framed behavior, especially in `WindowChrome` buttons and hoverable borders.

## Required changes

### Window chrome container
Keep:
- `1px` border is acceptable

But make it softer and more cyan-led, less silver-led.
The chrome shell may keep a thin edge.

### Window chrome buttons
Current style is still too boxed.
Change to this behavior:
- default: no visible frame or ultra-soft 1px cyan-tinted edge
- hover: 1px cyan edge, clearly visible
- pressed: 1px stronger cyan edge
- close hover: same rule, do not make it a boxed blob

### Hoverable cards
The current generic hover rule is too weak.
Make hover state clearly readable with:
- border-color shift toward cyan
- no thickness increase beyond `1px`

---

# 3) `config.py`

## File to change
`forgeos/shared/pyside6_glass/config.py`

## Problem
Typography scale support exists, but the practical default experience is still too small.

## Required changes

### A. Change practical default
Change the default typography target used by the examples/workbench path so the visible experience opens larger.

For this pass:
- default to `lg`

### B. Expose explicit user choice
Ensure the user can choose text size globally in a simple way.
The choices should be visible and obvious, not hidden.

Required visible options:
- `sm`
- `md`
- `lg`
- `xl`

Label it clearly, for example:
- `Text Size`

Do not call it “typography scale” in the visible UI if a simpler label is available.
Use plain language.

### C. Scope of the control
This control should affect:
- titles
- section labels
- form labels
- input text
- button text
- dashboard text
- inspector text
- captions / microcopy

It must be global for the current running UI session.

---

# 4) `scene.py`

## File to change
`forgeos/shared/pyside6_glass/scene.py`

## Problem
The exact stylesheet pipeline exists, but typography choice is still not obviously flowing from the user-facing app state.

## Required change
Where the scene builds/applies the exact stylesheet, allow an explicit `typography_scale` input to flow through.

The exact Atlas pipeline should become:
- exact base theme
- exact Atlas overrides
- chosen text size

Do not hardcode small text in the scene.
The scene must accept the chosen size.

---

# 5) `examples/catalog_shell.py`

## File to change
`forgeos/shared/pyside6_glass/examples/catalog_shell.py`

## This is the most important visible app entrypoint for this pass
The screenshot problem lives here.

## Required changes

### A. Open larger by default
Set the shell to open with a clearly readable global text size.
For now:
- default to `lg`

### B. Add a visible text size control
Add a simple visible UI control in the shell toolbar/header/settings area:
- label: `Text Size`
- values: `SM`, `MD`, `LG`, `XL`

This must update the current UI session visibly.

### C. Border cleanup in shell-specific surfaces
Review shell-specific frames/buttons/search/tools areas and remove extra framing.
Specifically clean:
- toolbar button group boxing
- search field boxing
- blank workspace action button boxing
- inspector summary card boxing
- metadata card boxing
- provider/runtime cards if they still look like framed blocks

The shell should feel like floating layers, not boxed panels inside boxed panels.

---

# 6) `examples/demo_app.py`

## File to change
`forgeos/shared/pyside6_glass/examples/demo_app.py`

## Required change
If this demo still launches at `sm` or similarly cramped scale, change it to launch at `lg`.

Do not leave the user squinting.

---

# 7) `controls.py`

## File to change
`forgeos/shared/pyside6_glass/controls.py`

## Problem
Buttons may already have better shadows now, but the visual shape can still read too boxed because the stylesheet layer still frames them.

## Required changes
Coordinate button behavior with the new border-minimal policy.

### Required button behavior
- default: no hard visible frame
- hover: clear 1px cyan cue
- pressed/focus: stronger 1px cyan cue
- no thick border
- no silver box look

If needed, adjust button properties/classing so the stylesheet can distinguish:
- normal
- primary
- subtle
- ghost
- danger
- success

But do not redesign the API.

---

# 8) `dashboard.py`, `primitives.py`, `charts.py`

## Files to review/change
- `forgeos/shared/pyside6_glass/dashboard.py`
- `forgeos/shared/pyside6_glass/primitives.py`
- `forgeos/shared/pyside6_glass/charts.py`

## Problem
The remaining mismatch is often caused by component-local shells still looking framed even if the global theme improved.

## Required changes
Review every shared surface component used for:
- dashboard cards
- metric panels
- control cards
- chart wrappers
- detail panes
- summary panes
- stat pills
- container shells

Apply this exact rule:
- remove decorative border unless it is doing real readability work
- if a border is necessary, use cyan and keep it at `1px`
- `2px` only if there is a very specific selected/active state that genuinely needs it
- no heavy neutral border

### Chart wrappers
Charts should not look like boxed widgets inside a boxed card.
Keep only the outer card/panel cue, not an extra inner frame unless functionally needed.

---

# 9) Exact visual target for cyan edges

## Cyan edge policy
Use cyan where the eye needs help, not everywhere.

### Keep cyan visible on:
- focused input
- selected segment / chip
- active tab or active tool state
- hover card edge
- key panel separation when the background values are too close

### Do not put cyan heavily on:
- every idle button
- every idle card
- every dashboard shell
- every container inside another container

## Thickness policy
- idle: `0px` or `1px`
- interactive hover/focus/selected: `1px`
- emergency max: `2px`

That is the hard cap for this pass.

---

# 10) Acceptance criteria
Only consider this pass complete if all of this is true:

- text is readable without squinting in the workbench/examples
- the user can choose text size easily
- default launch size is larger than before
- buttons no longer look boxed by default
- dashboard/cards/panels no longer look overframed
- cyan cues are clearly visible where needed
- cyan cues are not sprayed everywhere
- no thick border remains in normal idle state
- max frame thickness is `2px`, but most of the UI stays at `0px` or `1px`

---

# 11) Implementation order

## Phase 1: readability first
1. `theme.py` typography bump
2. `config.py` default to larger text target
3. `catalog_shell.py` visible `Text Size` control
4. `demo_app.py` launch larger

## Phase 2: border cleanup
5. `theme.py` global border-minimal rewrite
6. `atlas_styles.py` chrome/button hover cleanup
7. `controls.py` align button states with border-minimal styling
8. `dashboard.py` / `primitives.py` / `charts.py` remove local boxiness

## Phase 3: final polish
9. re-run examples
10. keep only cyan cues that improve readability
11. delete any leftover thick neutral frame look

---

# Executive summary
The package is now failing full parity mostly because:
- text is too small
- borders are too present
- cyan separation cues are too weak or too inconsistent

The correction is not a redesign.
The correction is:
- bigger text
- visible text-size choice
- borderless by default
- ultra-thin cyan cues only where useful

That is the exact direction for this pass.
