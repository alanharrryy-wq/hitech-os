---
name: prompt-factory
description: generate codex and vs code prompts in english with strict structure (tasks, deliverables, validation, stop conditions) and optional multicodex prompt packs. use when the user asks for a prompt, says "dame prompt" / "promps", mentions codex, unicodex, multicodex, prompt pack, deep research prompt, or wants a reusable prompt template for implementation.
---

# Prompt Factory

## Overview
Turn a vague request into a **ready-to-copy prompt** for Codex/VS Code that is **structured, deterministic, and deliverable-driven**.

## Output rules (non-negotiable)
- Always respond in **two parts**:
  1) **Spanish**: short explanation of what the prompt will do + what to check.
  2) **English prompt** in a single fenced code block.
- The English prompt must be **self-contained** and must not require follow-up questions.
- Prefer **clear constraints over creativity**. If info is missing, make a reasonable assumption and list it under **ASSUMPTIONS**.

## Decide the prompt type
Choose the best fit automatically:

### A) Unicodex prompt
Use when the user wants:
- architecture changes, refactors, governance, contracts, standards
- or they did not explicitly ask for multicodex

### B) Multicodex prompt pack
Use when the user wants:
- execution at scale, multiple modules/features in parallel
- or they explicitly mention multicodex, prompt pack, workers, A/B/C/D/Z

## Canonical structure for every English prompt
Your prompt must contain these sections, in this order:

1. **GOAL** (definition of done)
2. **CONTEXT** (what the user told you)
3. **CONSTRAINTS** (hard rules; safe defaults)
4. **ASSUMPTIONS** (only if needed)
5. **TASKS (10)**
   - Exactly 10 tasks, numbered 1-10
   - Each task has: objective, steps, and acceptance criteria
6. **DELIVERABLES**
   - Explicit files and outputs expected
7. **VALIDATION**
   - What to run/check; prefer smoke tests first
8. **STOP CONDITIONS**
   - When the agent must stop and report
9. **FINAL REPORT FORMAT**
   - Must include: files created/modified/deleted; commands run; summary; risks; next steps

## Multicodex prompt pack format (strict)
When producing a multicodex pack, output **exactly 5 sections** with these headers:

- === A_core PROMPT ===
- === B_tooling PROMPT ===
- === C_features PROMPT ===
- === D_validation PROMPT ===
- === Z_aggregator PROMPT ===

Inside each section, the first lines must be:
- YOU ARE CODEX WORKER: <id>
- RUN_ID: {{RUN_ID}}
- CODEX_ID: <id>

### Multicodex mandatory rules to embed
Include these constraints inside every worker prompt:
- Work exclusively inside: tools/codex/runs/{{RUN_ID}}/<worker>/
- Produce a bundle containing: STATUS.json, SUMMARY.md, FILES_CHANGED.json, DIFF.patch, SUGGESTIONS.md, FILES/, DONE.marker
- DONE.marker must contain: DONE {{RUN_ID}} <worker>
- Feature flags off by default.
- Keep builds deterministic.
- Prefer quick smoke validation per block; full suite only at the end or on critical paths.

### Special case: hitech os
If the user mentions **HITECH OS** or the repo is **hitech-os**, the prompt must:
- require reading KERNEL_CONTEXT.md first
- keep modularity strict (expand 10x without touching unrelated modules)
- treat powershell as wrapper; python as main engine when automation is needed

## Prompt quality checklist
Before sending the final prompt, ensure:
- every task has acceptance criteria
- file paths are explicit
- output/reporting format is explicit
- no "ask the user" steps
