# PRISMA Mobile Interface Canon

**Status:** `CURRENT_CANONICAL_PRODUCT_INTERFACE_AUTHORITY`  
**Authority ID:** `PRISMA.MOBILE.INTERFACE.CANON.V1`  
**Surface:** `Mobile`  
**Product role:** supervision and owner decision surface  
**Effective date:** 2026-08-25  
**Supersedes:** all previous PRISMA Mobile UI/UX/navigation/product-interface iteration specifications listed in `PRISMA_MOBILE_INTERFACE_CANON_MIGRATION_20260825.md`.

## 1. Canon rule

This document is the **single product authority for PRISMA Mobile interfaces**.

A mismatch between this canon and the current Mobile runtime or source code is **implementation drift**. Current code, current routes, Atlas snapshots, visual ownership maps, verifier-era labels, or previous iteration documents must not silently redefine this product canon.

The separation is intentional:

- **This canon defines what PRISMA Mobile should be.**
- **Atlas defines what implementation currently exists and where it lives.**
- **Runtime/source code proves current implementation, not desired product truth.**
- **Technical release, PWA, security, sync, verifier, and evidence documents prove bounded engineering facts, not product information architecture.**

If a future implementation changes the product model, the product decision must update this canon explicitly. Implementation drift alone is not product authorization.

## 2. Product doctrine

PRISMA Mobile is not a pocket POS and is not a miniature PC backoffice.

Its job is to answer, quickly and truthfully:

> **¿Cómo va mi negocio, qué necesita atención y qué debo decidir desde el celular?**

Canonical surface boundary:

- **Tablet operates and sells independently.**
- **PC governs, administers, consolidates, and audits when present.**
- **Mobile supervises, summarizes, prioritizes, and guides decisions.**
- **Core records evidence.**
- **Control audits.**

Mobile must remain useful for a one-location business and scale naturally to multi-location operations without making MultiSucursal the identity of the product.

## 3. Primary information architecture

PRISMA Mobile has exactly **six primary product sections**:

| Order | Surface ID | Label | Human question |
| --- | --- | --- | --- |
| 1 | `SURF.MB.PULSE` | **Inicio / Pulso** | ¿Cómo va mi negocio hoy? |
| 2 | `SURF.MB.SALES` | **Ventas** | ¿Estoy vendiendo como debería? |
| 3 | `SURF.MB.CASH` | **Caja** | ¿La caja está sana o requiere revisión? |
| 4 | `SURF.MB.INVENTORY` | **Inventario** | ¿Qué se me está acabando, sobrando o frenando ventas? |
| 5 | `SURF.MB.COMMAND` | **Mando** | ¿Qué requiere atención y qué decisión sigue? |
| 6 | `SURF.MB.SYSTEM` | **Sistema** | ¿La operación móvil está conectada, autorizada y confiable? |

No seventh primary section is created for Alerts, Reports, MultiSucursal, Sync, Licenses, or generic Operations. Those concepts are resolved into the six canonical sections or into transversal controls described below.

## 4. Global Mobile shell

Every primary section shares one compact, stable shell.

### 4.1 Header

The first viewport should expose, without forcing navigation:

- PRISMA Mobile identity;
- current business/customer context;
- current branch/location context when applicable;
- data freshness timestamp or relative freshness;
- source/confidence state;
- offline, stale, partial, or degraded state when present;
- access to the global context switcher;
- one restrained status indicator, never a decorative fake-green badge.

### 4.2 Navigation

Primary navigation exposes the six canonical sections only. The implementation may use a bottom rail, compact tab rail, native navigation, or another touch-appropriate mechanism, but the product hierarchy remains these six sections.

### 4.3 Density

Mobile is read-first and decision-first. It should not render every advanced module in one endless vertical sheet. Progressive disclosure, internal sub-navigation, expandable evidence, compact cards, and detail drawers are preferred over desktop-density waterfalls.

## 5. Interface contract: Inicio / Pulso

**Surface ID:** `SURF.MB.PULSE`

### Purpose

Give the owner the shortest trustworthy answer to: **¿Cómo va mi negocio hoy?**

### Required first-order information

- sales today;
- ticket count;
- average ticket;
- cash health summary;
- highest-priority operational signal;
- critical/replenishment stock count;
- overall health/readiness;
- data freshness and confidence;
- the two or three items that most need attention now.

### Preferred composition

1. **Primary pulse metric:** sales today, with source/freshness context.
2. **Compact KPI strip:** tickets, average ticket, cash state, critical stock.
3. **Needs attention:** top actionable signals only.
4. **Quick context:** current branch/business and data health.
5. **Next best action:** one or two routes into Mando, Caja, Inventario, or Sistema.

### What does not belong here

- long audit trails;
- full inventory catalogs;
- full report builders;
- long technical diagnostics;
- every alert;
- every branch card;
- all six Mando modules expanded simultaneously.

### Empty / stale / offline behavior

The screen must never invent a healthy number. If data is absent, stale, partial, timed out, cached, or offline, that state is visible next to the affected metric or section.

## 6. Interface contract: Ventas

**Surface ID:** `SURF.MB.SALES`

### Human question

**¿Estoy vendiendo como debería a esta hora?**

### Core information

- accumulated sales today;
- tickets;
- average ticket;
- hourly rhythm or time progression;
- comparison to a meaningful prior period when reliable;
- recent trustworthy sales activity;
- top product and/or category when data supports it;
- branch context when a multi-location context is active;
- freshness/source/confidence for sales data.

### Decision intent

Ventas should help the owner distinguish normal rhythm from a meaningful deviation. It is not a financial BI workbench and should not import PC-level filter density.

### Drill-down

A user may open a compact detail for a sale, period, category, or branch when evidence exists, but Mobile remains a supervision surface rather than a transaction editor.

## 7. Interface contract: Caja

**Surface ID:** `SURF.MB.CASH`

### Human question

**¿La caja está sana o requiere revisión?**

### Core information

- expected cash;
- counted cash when a trustworthy source exists;
- difference and severity;
- last cut/close state;
- cash movements;
- withdrawals;
- expenses;
- tender mix summary when available;
- active anomaly or review signal;
- freshness/source/confidence.

### Decision intent

Caja is evidence-first. A discrepancy should lead to a clear review path, not accusatory copy. Money-sensitive values must be traceable to their source or consolidation state.

### Actions

Mobile may offer read-only evidence, guidance, or a handoff to the authoritative operating surface. Mutating cash operations are not implied by this interface canon.

## 8. Interface contract: Inventario

**Surface ID:** `SURF.MB.INVENTORY`

### Human question

**¿Qué se me está acabando, sobrando o costando venta?**

### Core information

- critical items;
- replenish-soon items;
- normal/healthy count;
- overstock when supported;
- current stock;
- recent or weekly sales velocity;
- priority based on business impact;
- top or high-velocity items;
- source/freshness/confidence;
- branch context when applicable.

### Decision intent

The phone should not become an 8,000-SKU warehouse screen. It should rank what deserves attention and explain why.

### Recommended presentation

Use prioritized watchlists, compact filters, severity, velocity, and a detail drawer. Full catalog administration belongs to the authoritative operational/admin surface.

## 9. Interface contract: Mando

**Surface ID:** `SURF.MB.COMMAND`

Mando is the **owner decision center** and the most important advanced Mobile surface. It absorbs the best capabilities previously specified as separate iterations and prevents them from becoming disconnected product islands.

Mando contains six canonical sub-surfaces plus compact owner analytics.

### 9.1 Command Center

**Sub-surface:** `SURF.MB.COMMAND.CENTER`

Purpose: rank the operation by what deserves attention first.

Must expose:

- readiness/health summary;
- prioritized decision queue;
- strongest signals;
- data quality/confidence context;
- recommended next action;
- evidence/source link where available.

### 9.2 Action Inbox

**Sub-surface:** `SURF.MB.COMMAND.INBOX`

Purpose: turn signals into a practical owner queue.

Each actionable item should expose:

- priority/severity;
- area;
- recommended action;
- suggested responsible owner when supported;
- evidence/source;
- practical due/attention window when supported;
- status, without implying a mutation that Mobile is not authorized to perform.

Alerts are therefore **signals feeding Mando**, not a competing primary app section.

### 9.3 Daily Brief

**Sub-surface:** `SURF.MB.COMMAND.BRIEF`

Purpose: provide a concise executive summary for the day or operational close.

It may contain:

- key KPIs;
- important decisions;
- immediate actions;
- follow-up items;
- inventory and cash highlights;
- a share/export representation for WhatsApp, mail, or handoff when supported.

This is the canonical home for the old standalone Reports concept. Reports are contextual summaries and evidence, not a separate navigation silo.

### 9.4 Decision Ledger

**Sub-surface:** `SURF.MB.COMMAND.LEDGER`

Purpose: preserve a lightweight, auditable explanation of why an action or recommendation existed.

It should prioritize temporal clarity, evidence, responsible party, recommended next step, and status. It does not fabricate a completed action from a recommendation.

### 9.5 Pulse Timeline

**Sub-surface:** `SURF.MB.COMMAND.TIMELINE`

Purpose: show the operational story of the day in sequence.

Suggested phases:

- opening;
- normal operation;
- peak;
- follow-up;
- close.

Events must preserve ordering, source, and confidence. Missing periods are not filled with synthetic activity.

### 9.6 Health Radar

**Sub-surface:** `SURF.MB.COMMAND.HEALTH`

Purpose: show operational health across the dimensions that matter to the owner.

Typical dimensions may include sales, cash, inventory, alerts/actions, branch health, data/source health, and sync/readiness when evidence exists.

A visual score must never hide the underlying cause. Critical conditions remain explicit.

### 9.7 Compact owner analytics

The useful ideas currently represented by a separate command/charts surface belong conceptually inside Mando. Compact charts may summarize:

- pulse timeline;
- action priority stack;
- health radar;
- freshness rings;
- incident sparks;
- confidence bands.

These are decision aids, not a seventh primary product surface.

## 10. Interface contract: Sistema

**Surface ID:** `SURF.MB.SYSTEM`

### Human question

**¿La app está correctamente autorizada, conectada y viendo datos confiables?**

### Product responsibilities

Sistema consolidates the technical/operator-facing information that should not fragment the main navigation:

- plan and license state;
- Mobile/Tablet/PC device slot visibility;
- setup code / customer setup / device claim state;
- current authorized context;
- source health;
- sync/readiness summary;
- upstream availability;
- freshness and confidence diagnostics;
- cache/fallback state;
- retry/refresh controls that are safe and already authorized;
- installation/PWA guidance;
- diagnostic information appropriate for the operator/customer;
- version/build information when useful.

### Setup and install surfaces

Customer Setup, device claim, PWA installation, and offline fallback remain real supporting surfaces, but they are not primary business sections. They are reached from onboarding, Sistema, a setup link/code, or recovery flow.

### No hidden failure

System problems must not be disguised as green business health. Mobile truthfulness applies across the entire app.

## 11. Transversal surface: Multi-context Switcher

**Surface ID:** `SURF.MB.CONTEXT`

MultiSucursal is **not** a primary navigation section.

The canonical model is a global context switcher that can resolve, when authorized and supported:

- customer/business;
- branch/store;
- terminal/device context;
- source/readiness context;
- relevant role or supervision scope.

A single-location customer should see almost no complexity. A multi-location customer should gain context without entering a different product identity.

The switcher must use real authorized contexts. Query parameters, arbitrary local storage, or decorative fake branches do not create authority.

## 12. Transversal state: offline, stale, partial, degraded

**Surface ID:** `SURF.MB.STATE.TRUTH`

Offline and degraded states are product states, not error-screen afterthoughts.

Mobile must visibly distinguish:

- live/connected;
- stale but usable;
- partial source availability;
- offline with bounded cached/memory fallback when permitted;
- unauthorized or session-invalid;
- source timeout;
- empty but valid data;
- actual application error.

Every state should answer:

1. What is known?
2. How fresh is it?
3. What source produced it?
4. What is unavailable?
5. What can the user safely do next?

## 13. Transversal detail pattern

**Surface ID:** `SURF.MB.DETAIL`

Alerts, actions, products, sales, branches, incidents, and evidence should open a focused detail drawer/sheet/page rather than force new permanent primary tabs.

A detail should prioritize:

- what happened;
- severity/priority;
- business impact;
- source/evidence;
- time/freshness;
- recommended next step;
- authoritative handoff when a mutation belongs elsewhere.

## 14. Canonical mapping from previous navigation models

| Previous concept | Canonical destination |
| --- | --- |
| Hoy / Resumen | **Inicio / Pulso** |
| Ventas | **Ventas** |
| Caja | **Caja** |
| Inventario / Stock | **Inventario** |
| Alertas | **Mando > Action Inbox / Command Center**, with alert detail |
| Reportes | **Mando > Daily Brief** and contextual summaries |
| MultiSucursal | **Global Multi-context Switcher** |
| Sync | **Sistema**, with health signals also visible in Mando when consequential |
| Licencias | **Sistema** |
| Operación | decomposed into **Inicio, Mando, Caja, Inventario, Sistema** according to meaning |
| Command Center | **Mando > Command Center** |
| Action Inbox | **Mando > Action Inbox** |
| Daily Brief | **Mando > Daily Brief** |
| Decision Ledger | **Mando > Decision Ledger** |
| Pulse Timeline | **Mando > Pulse Timeline** |
| Health Radar | **Mando > Health Radar** |
| separate command/charts preview | **Mando > Compact owner analytics** |

## 15. Visual direction: one Mobile identity

PRISMA Mobile should have one coherent premium operational identity, not a pile of competing themes.

### Canonical visual language

- graphite/obsidian operational base;
- restrained titanium/silver neutral surfaces;
- blue/cyan accents only for meaning, focus, and live state;
- shallow, controlled glass rather than deep blur stacks;
- high text contrast and touch readability;
- compact spacing without desktop density;
- low-overhead motion only for state change, navigation, attention, and confirmation;
- no heavy WebGL or atmospheric layer that competes with business truth;
- critical states use unmistakable semantic treatment rather than decorative glow.

The former Obsidian, Silver, and Graphite experiments are consolidated into this **single graphite-obsidian identity with titanium neutrals**, not exposed as three competing product identities.

## 16. Motion and interaction

Motion should explain state, not entertain at the expense of speed.

Allowed uses include:

- tab/section transition;
- context-switch confirmation;
- sheet open/close;
- priority change;
- refresh/freshness feedback;
- safe CTA confirmation;
- subtle loading/progress state.

Avoid long ambient animation, excessive sheen, unbounded loops, or effects that make stale/critical data harder to read.

## 17. Truthfulness and evidence rules

The Mobile interface is fail-closed for product truth.

- No number without a source or trustworthy aggregation path.
- No healthy state inferred from missing data.
- No cached value presented as live.
- No recommendation presented as an executed action.
- No branch/context invented from unauthenticated client state.
- No report without source data.
- No alert without severity/context sufficient to understand it.
- No green readiness when a required source is unknown, timed out, contradictory, or unauthorized.

## 18. Actions and mutations

This interface canon does not authorize new Mobile mutations.

Mobile may surface safe actions already governed elsewhere, such as refresh, retry, copy/share, navigation, context selection, setup/claim flows, or an explicit handoff to an authoritative surface.

Any future approval, cash mutation, inventory mutation, sync recovery, device operation, license operation, or queued offline command requires its own governed product and technical authorization.

## 19. Relationship to current implementation

Current Mobile code may expose a different set of tabs, route names, component ownership, or mounted modules. Those differences are **implementation drift** until intentionally reconciled.

This governance task does **not** change:

- application source code;
- APIs;
- data contracts;
- sync/outbox behavior;
- licensing behavior;
- authentication/session behavior;
- PWA/service-worker behavior;
- Tablet;
- PC;
- Shared UI;
- Shared Core;
- Chart Lab;
- Control Center.

Future implementation work must start from a fresh task-exact Authority Mesh and treat this canon as the product interface authority.

## 20. Compatibility documents

Some legacy documentation paths are still hard-coded as existence checks inside current Mobile verifier scripts. Those files may remain only as **non-authoritative compatibility pointers** to this canon.

A compatibility pointer:

- contains no independent UI/UX/product specification;
- cannot override this canon;
- exists only to avoid breaking a technical verifier during this documentation-only consolidation;
- may be deleted later only together with an explicitly authorized verifier-path cleanup.

## 21. Acceptance bar for the canon

A future Mobile implementation is aligned when:

1. The six primary sections are the product hierarchy.
2. Mando owns the six advanced decision modules and compact owner analytics.
3. MultiSucursal is context, not product identity.
4. Alerts become actionable signals rather than a competing silo.
5. Reports resolve into Daily Brief and contextual evidence.
6. Licenses, devices, setup, source health, sync/readiness, install, and diagnostics resolve into Sistema.
7. Freshness, confidence, partial/offline state, and source truth are visible.
8. Mobile remains supervision-first and does not become a POS or miniature PC.
9. Visual language is one coherent low-overhead premium Mobile identity.
10. Runtime differences are tracked as implementation drift rather than silently rewriting this document.

## 22. Final authority statement

**PRISMA Mobile has one product-interface canon: this file.**

Previous UI/UX/navigation/product-interface iteration documents are either deleted or reduced to technical compatibility pointers with no normative product content. Git history remains the historical record; it is not active product authority.
