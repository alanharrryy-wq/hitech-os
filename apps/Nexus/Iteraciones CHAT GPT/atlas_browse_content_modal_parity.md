# Atlas 1:1 Fix Plan for `Browse Content` / `Content Picker`

## Short verdict

This interface is **not Atlas 1:1**.

It has the same broad visual family, but it breaks Atlas parity in the places that matter most:

1. the modal shell still looks like a generic dark dialog instead of an Atlas glass dialog
2. borders are too visible, too frequent, and too rectangular
3. the cyan edge language is weak or inconsistent
4. typography hierarchy is too small and too flat
5. spacing and density are off
6. the list/detail split looks utilitarian instead of premium
7. footer actions look like default dark buttons instead of Atlas-composed controls
8. the titlebar / close affordance looks disconnected from the rest of the composition

---

## What is visually wrong right now

## 1. The modal does not feel like an Atlas shell
The whole window reads as:
- black fill
- hard inner boxes
- visible separators
- utilitarian panels

Atlas reads differently:
- dark glass shell
- subtle wash
- ultra-thin cyan edge
- soft atmospheric depth
- fewer “boxed” regions
- more layered composition, less hard segmentation

## 2. Borders are doing too much
Right now this modal has too many visible frames:
- outer modal border
- search bar border
- list panel border
- detail panel border
- footer button borders
- internal dividers

That creates the cheap “UI skeleton visible everywhere” effect.

For Atlas parity:
- default border behavior should be **zero or near-zero**
- when a border exists, it should be:
  - cyan-tinted
  - ultra-thin
  - 1px preferred
  - 2px absolute max only where necessary

## 3. The cyan edge language is weak
Atlas uses cyan as a controlled accent:
- edge glow
- shell edge
- focus ring
- hover emphasis
- selection edge
- micro separators

Here, the cyan either:
- barely appears
- appears only in a few spots
- or gets lost against gray/black framing

That kills the Atlas identity.

## 4. Typography is too small and too flat
The content is readable only if you already know what you are looking at.

Problem areas:
- body labels too small
- list rows too cramped
- secondary text too dim and tiny
- detail panel text too light and too small
- control labels too close in size to metadata text

Atlas needs:
- stronger hierarchy
- larger default body text
- explicit global size control
- higher readability in list/detail workflows

## 5. The left list panel is not Atlas
The left rail should feel like a premium selectable composition list.
Right now it feels like:
- plain list widget
- dark bucket
- thin selection accent
- weak text structure

Atlas parity requires:
- larger row height
- better title/subtitle separation
- softer hover state
- more elegant selected state
- less visible panel framing
- clearer breathing room

## 6. The right detail panel is too empty and too raw
The right side currently feels like a plain black text area.

Atlas-style detail panes should feel like:
- quiet, but intentional
- softened surface
- readable block hierarchy
- subtle cyan structure
- premium preview pane, not terminal void

## 7. The footer action row is wrong
The footer buttons currently read as generic dark controls.

For Atlas parity:
- actions should inherit the same button finish as the rest of the system
- the footer should feel integrated into the modal shell
- action emphasis should be clear without chunky borders

## 8. The top title area is not fully integrated
The title and close behavior still feel like a standard desktop dialog layer laid on top of the content.

Atlas parity requires:
- shell/titlebar/body/footer to feel like one system
- chrome controls visually absorbed into the shell
- no abrupt transition from window frame to content body

---

## Exact implementation target

The target is:

- same visual language as Atlas selector dialogs
- same shell quality as Atlas glass dialogs
- same button finish as Atlas controls
- same cyan edge behavior
- same typography readability policy
- same low-border / ultra-thin-border strategy
- same premium list/detail composition feel

This modal should stop feeling like a “picker utility” and start feeling like an Atlas-native workspace overlay.

---

## Files to change

## Core files that should be touched
- `forgeos/shared/pyside6_glass/theme.py`
- `forgeos/shared/pyside6_glass/atlas_styles.py`
- `forgeos/shared/pyside6_glass/controls.py`
- `forgeos/shared/pyside6_glass/primitives.py`
- `forgeos/shared/pyside6_glass/dashboard.py`
- `forgeos/shared/pyside6_glass/scene.py`
- `forgeos/shared/pyside6_glass/effects.py`

## Modal / picker specific files to inspect and likely change
Find the module that owns this exact interface and apply the changes there.
Typical candidates:
- `forgeos/shared/pyside6_glass/examples/catalog_shell.py`
- `forgeos/shared/pyside6_glass/examples/demo_app.py`
- any `content_picker`, `browse_content`, `catalog_browser`, `workspace_picker`, or similar module

If the dialog is defined inline in an example, extract nothing unless needed.
Just fix the exact composition in place if that is how the current package is structured.

---

## Required 1:1 changes

## 1. Modal shell must become Atlas glass shell

### What to change
The outer dialog container must use the same shell language as Atlas dialogs:
- glass backdrop
- subtle wash
- ultra-thin cyan edge
- premium dark interior
- soft shadow
- integrated footer

### Requirements
- remove the hard black-box feel
- reduce frame visibility
- make the shell feel atmospheric, not boxed
- preserve dark background but add depth

### Implementation rule
Use the exact Atlas shell pattern already established in the shared parity work:
- backdrop
- shell frame
- hero/body/footer card surfaces
- effects helpers
- exact Atlas stylesheet pipeline

---

## 2. Zero-border policy by default

### What to change
All borders in this interface must be audited.

### Rules
- default border width: `0`
- preferred visible edge: `1px`
- absolute max border width: `2px`
- visible borders must be cyan-tinted and intentional
- no gray heavy borders
- no thick panel outlines
- no multi-frame nesting unless absolutely required

### Apply this to
- modal shell
- search box
- filter combo
- left list panel
- right detail panel
- footer container
- all buttons
- internal list rows
- preview/detail blocks

---

## 3. Cyan edge visibility must be fixed

### Problem
The cyan edge is too weak to carry the Atlas identity.

### Required outcome
The modal should have:
- visible but elegant cyan edge on the shell
- visible selected-state cyan language
- visible input focus cyan
- subtle cyan line language in structural transitions

### Rules
- no neon overload
- no giant glows
- just enough to clearly read as Atlas
- keep it refined

### Where to increase cyan presence
- outer shell edge
- selected list row outline or glow
- search input focus state
- key separators if they remain
- hover state on actionable controls

---

## 4. Typography must become readable

### Problem
Text is too small and weak.

### Required outcome
Implement a **global user-selectable text size control** that affects the whole rendered UI for this package.

### Minimum requirement
Provide a global scale or preset that can affect:
- titles
- section labels
- list row titles
- list row subtitles
- body labels
- metadata text
- buttons
- input text
- dashboard labels
- picker detail text

### Recommended preset set
- `Compact`
- `Default`
- `Readable`
- `Large`

### Required behavior
- `Default` should already be more readable than current state
- `Readable` should be the practical human default
- all components must respond consistently
- no isolated widget-only scaling

### Files likely involved
- `theme.py`
- `atlas_styles.py`
- `config.py` if present
- any typography token helper
- picker module itself if font sizes are hardcoded

---

## 5. Search row must be rebuilt visually

### Current problem
The search bar row reads like raw controls dropped into a dark dialog.

### Required outcome
The top control row must feel integrated and premium.

### Changes
- search field: softer surface, no chunky frame, better vertical size
- filter combo: same height and visual finish as search field
- consistent horizontal rhythm
- clearer spacing from title block below/above
- better placeholder readability
- stronger input typography

### Border policy
- no thick frame
- 1px cyan edge only if needed
- rounded but not puffy

---

## 6. Left list panel must be redesigned to Atlas parity

### Problem
The list looks like a plain dark list widget.

### Required outcome
Each row should feel like a curated Atlas entry tile, not a stock list item.

### Required row behavior
- taller row height
- clearer title/subtitle separation
- better left icon alignment
- more padding
- selected row should feel premium, not just lightly tinted
- hover state should be visible but soft
- no thick row borders

### Selected state target
Use Atlas logic:
- subtle cyan edge or glow
- soft lifted surface
- readable text contrast
- no cheap bright rectangle

### Panel surface target
- near-borderless
- quiet cyan edge at most
- softened background surface
- premium list well, not black bucket

---

## 7. Right detail panel must stop looking empty and dead

### Problem
The detail pane looks like blank black output.

### Required outcome
The detail pane must feel intentionally composed.

### Add / improve
- stronger header block hierarchy
- readable description text
- more spacing
- subtle structural grouping
- optional faint internal cyan line language if needed
- consistent typography with list side

### Important
Do **not** solve this by adding thick frames.
Solve it with:
- spacing
- text hierarchy
- soft surfaces
- low-border structure

---

## 8. Footer action row must be Atlas-native

### Problem
Footer buttons read like default dark buttons.

### Required outcome
Footer must inherit the exact Atlas action language.

### Rules
- no chunky borders
- use the corrected Atlas button finish
- distinguish primary vs secondary actions by surface and emphasis, not by thick outlines
- footer container should integrate into the shell, not feel bolted on

### Buttons to audit
- `Add to Current Tab`
- `Preview`
- `Open in New Tab`
- `Close`

Check:
- vertical alignment
- spacing
- padding
- readable font size
- focus state
- hover state
- button hierarchy

---

## 9. Modal chrome must visually disappear into the shell

### Problem
The titlebar and window controls still feel like a separate system.

### Required outcome
The modal chrome should feel absorbed into the same shell as the dialog body.

### Requirements
- same transparency logic
- same top wash logic
- same edge language
- no abrupt hard bar feeling
- close button must not look like a Windows sticker slapped on top

### Important
Keep functionality.
Only fix the visual/system integration.

---

## 10. Cards, dashboards, and other compositions need the same treatment

This picker is not the only broken surface.
The same visual issues affect:
- dashboards
- cards
- preview panes
- forms
- inspectors
- list/detail workspaces
- composition shells

### Therefore
Do not patch only this screen.
Use this picker as the proof case and then apply the same visual rules across:
- cards
- dashboards
- panels
- toolbar rows
- list/detail layouts
- action footers
- form surfaces

---

## Exact file-by-file change guidance

## `theme.py`
### Required
- reduce border defaults aggressively
- remove thick strokes
- ensure cyan-accent edge behavior is visible but refined
- increase default readable font sizing
- add typography variables/tokens that support the global text-size control
- ensure input, combo, button, list, labels all consume the same scale logic

### Border target
- most surfaces: `0`
- shell or selected/focused edge: `1px`
- only rare high-importance cases: `2px max`

---

## `atlas_styles.py`
### Required
- add final overrides for the picker/dialog/list/detail/dashboard surfaces
- tighten Atlas parity for:
  - list rows
  - detail panes
  - footer rows
  - search bars
  - combos
  - modal shell
- reinforce cyan line language where current UI is too gray or too invisible

---

## `controls.py`
### Required
- ensure all buttons used in this picker inherit the corrected Atlas finish
- remove visible default border feel
- maintain hover/focus/pressed hierarchy
- keep borders ultra-thin or absent

---

## `primitives.py`
### Required
Audit reusable surface primitives:
- card shells
- section containers
- list wells
- pane wrappers
- toolbar wrappers

Anything that is creating hard frames or thick outlines must be reduced to Atlas parity.

---

## `dashboard.py`
### Required
Dashboards must follow the same zero-border / thin-cyan-edge rule.
They should not look boxed or panel-heavy.

---

## `scene.py`
### Required
Ensure this picker and similar dialogs are actually getting the exact Atlas stylesheet pipeline and shell setup.

---

## Picker module itself
### Required
Rebuild the layout proportions, spacing, and row/detail composition for this exact interface.

Pay attention to:
- title size
- subtitle size
- search row spacing
- panel gutter width
- list row height
- detail pane padding
- footer spacing
- close/open/add button emphasis

---

## Acceptance criteria

Do not call this “fixed” unless all of these are true:

- the picker looks like an Atlas-native modal, not a dark utility dialog
- shell edge cyan is visible and elegant
- text is readable at default size
- the UI exposes a global text size control for package-wide scaling
- borders are zero by default
- visible borders are cyan and ultra-thin
- selected list rows feel premium
- detail pane feels composed instead of empty
- footer action row feels native
- the same border and typography rules also improve cards and dashboards, not just this picker

---

## Implementation order

## Phase 1. Fix the exact picker
1. modal shell
2. search/filter row
3. left list panel
4. right detail panel
5. footer action row
6. title/chrome integration

## Phase 2. Apply the same rules system-wide
7. buttons
8. cards
9. dashboards
10. generic panels
11. typography scale system
12. border reduction everywhere

---

## Final recommendation

If the goal is literal 1:1 Atlas parity, do **not** keep negotiating with the current hard-framed look.

The correct move is:
- zero-border by default
- visible cyan edge where meaningful
- stronger typography
- global text-size control
- list/detail surfaces rebuilt as Atlas compositions
- same treatment propagated across cards, dashboards, and other shared components

## Brutal translation
- if you only tweak the picker: it will still feel off
- if you only tweak typography: it will still feel boxed
- if you only remove borders: it will still feel dead
- if you apply shell + typography + border policy + list/detail rebuild together: **then it becomes Atlas**
