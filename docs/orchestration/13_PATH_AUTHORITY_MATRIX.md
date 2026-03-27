# Path Authority Matrix

This document maps important paths to their authority mode.

## Authority modes

- `owned`
- `read_only`
- `forbidden`

## Matrix

### Path
`F:\repos\hitech-os\tools\hos\git_sentinel_modular\**`

- owner: `git_sentinel_modular`
- `engine_guardian`: `forbidden` by default for internal rewrites
- `control_tower`: `read_only` for observation and governance reference

### Path
`F:\repos\hitech-os\engine_guardian\**`

- owner: `engine_guardian`
- `git_sentinel_modular`: `forbidden` for broad mutation
- `control_tower`: `read_only` except for future code under its own domain

### Path
`F:\OneDrive\Descargas\engine_guardian\**`

- owner: `engine_guardian`
- `control_tower`: `read_only`
- others: `forbidden` unless explicit operational authority exists elsewhere

### Path
`F:\repos\hitech-os\igniters\**`

- owner relationship: `engine_guardian`
- `control_tower`: `read_only`
- unrelated domains: `forbidden`

### Path
`F:\repos\hitech-os\tools\graphviz\repo_analizer\**`

- owner: `repo_analizer`
- `engine_guardian`: wrapper/sibling relationship, not absorption
- `control_tower`: `read_only`

### Path
`F:\repos\hitech-os\control_tower\**`

- owner: `control_tower`
- internal file ownership split governed by `12_CHAT_SPLIT_AND_FILE_ALLOCATION.md`

### Path
`F:\repos\hitech-os\docs\orchestration\**`

- owner: `control_tower` documentary authority
- both chats: bound, but not free to overlap outside file allocation rules
- external domains: `forbidden` from casual redefinition

### Path
`HITECH-OS-GitSentinel-Guardian` related operational surface

- status: protected legacy intact surface
- `control_tower`: `forbidden` by default
- any touching requires explicit evidence-backed decision outside this baseline phase

## Matrix interpretation rule

If a path is marked `read_only`, that does not imply:
- patch permission
- cleanup permission
- reformatting permission
- migration permission

It means observe, reference, compare, and report only.

## Escalation rule

When a desired action conflicts with this matrix:
- do not improvise
- mark blocked
- require governance revision
