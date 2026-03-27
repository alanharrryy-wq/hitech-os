# Authority and Usage Policy

## Purpose

This document states how the orchestration docs must be treated during the `control_tower` phase.

These files are not optional commentary.
They are the **normative baseline** for future implementation work.

## Authority level

The documents in this folder are classified as:

- **canonical**
- **normative**
- **pre-implementation**
- **cross-chat binding**

That means:

- they define the rules before code is written
- they constrain both Chat A and Chat B
- they are not to be silently “improved” by implementation bundles
- they can be revised only through explicit governance change

## What is bound by these docs

The following future work is bound by these docs:

- prompt drafting for future chats
- code generation under `F:\repos\hitech-os\control_tower`
- repo documentation under `F:\repos\hitech-os\docs\orchestration`
- any artifact bundle claiming to implement the `control_tower` domain
- any Codex placement task using this package as input

## Conflict resolution order

If there is a conflict, resolve it using this order:

1. hard proven runtime evidence of the existing closed state
2. explicit handoff facts from the startup package
3. these orchestration docs
4. future prompts
5. future implementation drafts
6. convenience assumptions

## Default posture when in doubt

When uncertain:

- do not widen ownership
- do not grant write authority
- do not add scheduler powers
- do not add remediation powers
- do not alter legacy-protected systems
- do not reinterpret an already closed operational success as open work

## Non-goals

These docs do not authorize:

- invasive repairs to `git_sentinel_modular`
- invasive repairs to `engine_guardian`
- runtime mutation of `engine_guardian`
- Cloudflare healing/control
- service restarts
- scheduler registration or task mutation
- ownership grabs across domains

## Required behavior for future chats

Any future chat implementing `control_tower` must:

- preserve the shared dictionary
- preserve the file split
- preserve read-only restrictions where defined
- preserve the no-overlap boundary between Chat A and Chat B
- preserve the existing ownership of stabilized operational domains

## Revision rule

A future revision to any document in this folder must include:

- the reason for the change
- the affected authority boundary
- why the current baseline is insufficient
- the migration impact on both Chat A and Chat B
- confirmation that the change does not reopen closed operational fronts by accident
