# HITECH-OS ☢️  
**Deterministic Multi-Agent Factory Monorepo**

HITECH-OS is **not** a typical monorepo.

It is a **deterministic, multi-agent execution factory** designed to run **real parallel AI work** without human chaos, editor crashes, or “PASS but nothing happened” lies.

This repo is built to survive:
- Multiple Codex agents
- Parallel execution
- Strict verification
- Reproducible runs
- Human operators doing dumb things (we planned for that)

If you’re looking for a cute starter template — wrong repo.  
If you’re looking for **industrial-grade AI execution** — welcome 😈

---

## 🧠 Core Idea (Read This First)

HITECH-OS separates **three different realities** that most systems dangerously mix:

1. **Factory Runtime (Canonical, Deterministic)**
2. **Operator Workspaces (Human / Interactive)**
3. **Shared Bridge (Controlled Transit Zone)**

Each layer has **one job**.  
Nothing overlaps.  
Nothing is implicit.

This is why the system scales without collapsing.

---

## 🏭 Factory Runtime (Canonical Layer)

The **Factory** is the **single source of truth**.

It owns:
- Execution
- Determinism
- Artifacts
- Verification
- Aggregation

### 🔒 Canonical Paths (DO NOT CHANGE)

```text
tools/codex/worktrees/<RUN_ID>/<WORKER>
tools/codex/runs/<RUN_ID>/
If something is not produced here, it does not exist.

The Factory:

Spawns isolated worker worktrees

Executes agents

Collects bundles

Verifies outputs

Produces a final, hash-stable report

No VS Code.
No humans.
No vibes.
Only facts.

📌 Canonical reference:
docs/factory/FACTORY_RUNTIME_EXPLAINED.md

🧩 Multi-Agent Model
HITECH-OS runs multiple Codex agents in parallel, each with strict isolation.

Workers
Worker	Responsibility
A_worker	Core architecture & foundations
B_worker	Tooling, scripts, infra
C_worker	Features & surface implementation
D_worker	Validation, contracts, verification
Z_integrator	Final merge, reports, attestations

Each worker:

Executes independently

Produces its own bundle

Cannot corrupt others

Is verified before integration

Parallelism without madness.

🌉 Shared Bridge (Optional, Feature-Flagged)
Humans and interactive Codex sessions do NOT touch the Factory directly.

Instead, we use a Shared Bridge.

The bridge:

Is a neutral transit zone

Syncs inputs and outputs

Never changes canonical paths

Is fully optional

Controlled via Environment Flags
text
Copiar código
HITECH_SHARED_MODE=off|consume|publish|both   (default: off)
HITECH_SHARED_DRYRUN=0|1
HITECH_SHARED_STRICT_SCHEMA=0|1
Shared is:

NOT a source of truth

NOT required for execution

NOT allowed to mutate canonical outputs

It is a bridge. Nothing more.

📌 Bridge spec:
docs/factory/SHARED_BRIDGE.md

🧑‍💻 Operator Workspaces (Human Layer)
Humans work outside the Factory.

Typical layout:

text
Copiar código
F:\repos\HITECHOS__A_core__<RUN>
F:\repos\HITECHOS__B_tooling__<RUN>
F:\repos\HITECHOS__C_features__<RUN>
F:\repos\HITECHOS__D_validation__<RUN>
Rules:

1 VS Code window = 1 workspace

No shared git root

No factory mutation

Outputs go through Shared (if enabled)

This avoids:

VS Code crashes

Codex context corruption

Multi-window repo conflicts

“Add a project” hell

Humans stay productive.
Factory stays pure.

🧬 Verification Is Not Optional
A run is NOT successful unless:

Worker bundles exist

Files are non-empty

Schemas validate

Hashes are stable

Final report passes verification

Verification artifacts live here:

text
Copiar código
tools/codex/runs/<RUN_ID>/VERIFY_*
PASS means real execution, not vibes.

🧱 Stack (Implementation Detail, Not the Point)
HITECH-OS happens to use:

Package manager: PNPM workspaces

Task runner: Turborepo

Web: Vite + React + TypeScript

Core API: Node + Fastify

AI Agent: Python + FastAPI + Pydantic

Schemas: Zod → JSON Schema

Verification: Python-based, deterministic

But the stack is replaceable.

The architecture is not.

⚙️ Quick Start (Offline-Safe)
bash
Copiar código
node -v
python --version
Optional:

bash
Copiar código
pnpm -v
pnpm install
Run baseline checks:

bash
Copiar código
pnpm health
pnpm turbo:typecheck
Or fully offline:

bash
Copiar código
node tools/health/src/check_repo_health.mjs
🧠 Principles (Law, Not Suggestions)
Deterministic artifacts and ordering

Feature flags OFF by default

Canonical paths never change

No binary or dump artifacts under src/**

Verification > optimism

Parallelism without shared state

Humans are optional; determinism is not

☢️ Final Warning
If you:

Touch Factory paths from a workspace

Commit run artifacts

Skip verification

Mix runtime and interaction layers

You will break determinism.

And the system will tell you.
