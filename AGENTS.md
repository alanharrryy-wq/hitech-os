Eso significa convertir AGENTS.md en un verdadero sistema operativo de agentes, no solo un README bonito.

Así que hice esto mentalmente:

v1  → lo que ya tienes
v2  → versión fuerte
v3  → la versión "vomitada / refinada"

Lo que te entrego abajo es la versión final refinada (v3).
Está diseñada para:

Codex

Cursor

Claude Code

Copilot Agents

y minimiza desviaciones del agente.

AGENTS.md — HITECH OS (v3 · Hardened)
# HITECH OS — AGENTS.md
Codex / VS Code / AI Agents Operational Manual

This document defines how autonomous coding agents must operate inside
the HITECH OS repository.

Agents must treat this file as **the governing execution contract**.

If instructions exist deeper in the tree, the **closest AGENTS.md overrides** this file.

---

# 0 — Mission (Invariant)

PROJECT_REASON:  
Menos fricción, más sistema, cero paja.

The repository exists to produce:

- deterministic systems
- low-friction workflows
- repeatable execution

Agents must prefer **systems over improvisation**.

---

# 1 — Core Operating Philosophy

Agents must prioritize:

1. Determinism
2. Evidence-driven changes
3. Reproducibility
4. Modularity
5. Low operational friction

Avoid:

- ad-hoc scripts
- hidden side effects
- environment-dependent behavior

If a workflow cannot be repeated, it is considered **broken**.

---

# 2 — Hard Rules (Non-Negotiable)

1. **Do not add dependencies** unless explicitly requested.
2. **Do not modify visual baselines** unless explicitly requested.
3. **Never generate dump artifacts in source trees.**
4. **Do not ask clarification questions unless blocked.**
5. **All code must remain modular and expandable 10×.**

Additional safety rules:

Agents must never run destructive commands:


rm -rf
del /s /q
git clean -fdx
git reset --hard


Never rewrite git history.

---

# 3 — Repository Structure

Repo root:


F:\repos\hitech-os


Key areas:

Keystone app

apps/keystone


Keystone routes (Next.js)

apps/keystone/app


Studio modules

apps/keystone/src


Codex Factory runtime

tools/codex


Skills catalog

.codex/skills


Governance documents:


docs/CONTRACT.md
docs/CONSTITUTION.md
docs/codex-kernel/INDEX.md
docs/factory/FACTORY_RUNTIME_EXPLAINED.md


Agents must read governance documents when relevant.

---

# 4 — Operating Modes

Agents may operate in two modes.

## Unicodex (single agent)

Use when:

- small refactors
- wiring components
- quick bug fixes

## Multi-Codex Factory

Use when:

- large features
- multi-module changes
- heavy refactors

Factory workers:


A_core
B_tooling
C_features
D_validation
Z_aggregator


Worker expectations:

- isolated workspaces
- additive changes
- evidence bundles required

Aggregator responsibilities:

- read worker outputs
- consolidate reports
- never modify source code

---

# 5 — Dev Runner Policy (Mandatory)

Agents must **never start framework servers directly**.

Correct:


pnpm -C apps/keystone keystone:scene:studio


Forbidden:


next dev
pnpm next dev
vite
node server.js


If a runner script does not exist:

- report the missing script
- do not invent one

---

# 6 — Port Policy

Default development port:


3100


If 3100 is unavailable:

Fallback range:


3110–3199


Rules:

- report the chosen port
- do not kill unrelated processes
- avoid binding to `0.0.0.0`
- prefer explicit localhost binding

---

# 7 — Temporary Artifacts

Temporary artifacts must be stored only in:


tools/_local


Allowed:


tools/_local/logs
tools/_local/tmp
tools/_local/debug
tools/_local/evidence


Forbidden locations:


src/**
apps/**
repo root


Artifacts must not be committed to git.

---

# 8 — Evidence Requirements

Every completed task must include evidence.

Minimum evidence:


STATUS
FILES_CHANGED
DIFF summary


If tests run:


TEST_COMMAND
TEST_RESULT


Evidence must never be written inside `src`.

---

# 9 — Keystone Scene Studio Rules

Run studio using repo scripts:


pnpm -C apps/keystone keystone:scene:studio


Visual testing:


pnpm -C apps/keystone keystone:scene:visual:smoke


Baseline update:


pnpm -C apps/keystone keystone:scene:visual:update


Agents must **never run Playwright directly** if repo scripts exist.

---

# 10 — Visual Snapshot Policy

If snapshot tests fail:

Agents must:

1. report mismatch
2. provide failing diff
3. wait for operator decision

Agents must **never auto-update baselines**.

---

# 11 — Dependency Policy

If a dependency appears required:

Agents must:

1. report the dependency
2. explain why it is needed
3. wait for approval

Never auto-install dependencies.

---

# 12 — Skill Activation

Skills live under:


.codex/skills


Agents load skills through progressive discovery:

1. read metadata
2. load skill instructions
3. apply workflow

Skill domains include:

CI troubleshooting  
Deployments  
Security reviews  
Observability  
Visual testing  

If a skill exists but activation is uncertain:

- mirror the skill workflow manually.

---

# 13 — Logging Policy

Runtime logs must go to:


tools/_local/logs


Logs must never be committed.

---

# 14 — Path Conventions

All reports must use Windows absolute paths.

Example:


F:\repos\hitech-os\apps\keystone\components...


Avoid:


./relative/path


---

# 15 — Required Output Format

Every task response must include a final section named:

Rutas completas

This section lists every referenced file using **full Windows paths**.

Example:


F:\repos\hitech-os\apps\keystone\components\brand\HitechLogo.tsx


Even if no files changed, list the files inspected.

This section is mandatory.

---