# PRISMA Change Intelligence — Cloud Center Vertical Contract V1

**Classification:** BUILD / isolated product surface + read-only control-plane projection  
**Commercial identity:** PRISMA Change Intelligence  
**Internal engine:** Code Atlas Engine  
**Authority base:** `main@d14effee1a1223cc772247ea9d7ec8547dc15c78`  
**Fresh Authority Mesh:** run `32156981312`, artifact `9332162633`, profile `ci-cloud-vertical-v3`  
**Current claim ceiling:** source-ready vertical shell only. This document does not claim hosted multi-tenant execution, paid-pilot readiness, enterprise IAM/security certification, legal/privacy compliance or production certification.

## 1. Product boundary

PRISMA Change Intelligence is a new PRISMA vertical presented through Prisma Cloud Center. It is not a rename of the existing licensing/customer-registration UI and it does not replace those owners.

The vertical exposes the commercial product model:

1. **Discover** — repository intelligence and technical forensics.
2. **Guard** — change readiness, impact radius, protected scope and required evidence.
3. **Control** — AI-agent change authority, Authority Pack and verification.

Code Atlas Engine remains the internal technology owner for repository intelligence and Change Intelligence primitives.

## 2. V1 architecture

```text
Prisma Cloud Center
        |
        | one navigation seam only
        v
PRISMA Change Intelligence Console       NEW_OWNER
        |
        +-- governed source contract      NEW_OWNER
        +-- read-only status projection   NEW_OWNER
        |
        +-- customer/tenant context       SHARED_OWNER / not bound in V1
        +-- licensing/entitlements        SHARED_OWNER / adapter pending
        +-- commercial billing            SHARED_OWNER / reference only
        |
        +-- repository registry           NOT_CONNECTED
        +-- analysis run projection       NOT_CONNECTED
        +-- Authority Pack references     NOT_CONNECTED
        +-- evidence references           NOT_CONNECTED
        |
        v
Code Atlas Engine                         REUSE_AS_IS / doNotRebuild
```

The V1 page is served by the existing Cloud Center static HTTP owner. It does not create a new server, port, process, Worker, D1 database or Prisma schema.

## 3. Reuse matrix

| Capability | Current evidence | V1 decision | Boundary |
|---|---|---|---|
| `cloud_center.customer_registration_runtime` | `RUNTIME_VERIFIED` | `REUSE_AS_IS` | Do not rebuild customer registration. Only future read-only customer/tenant context adapter is allowed. |
| `licensing.source_contract_alignment` | `LOCAL_VERIFIED` | `SHARED_OWNER` | Future entitlements projection may read the licensing contract. Activate/refresh/revoke remain existing-owner operations. |
| `licensing.customer_setup.plan_based_onboarding` | `LOCAL_VERIFIED` | `SHARED_OWNER` | Setup Code is onboarding evidence, not repository authorization or a repository credential. |
| `commercial.billing.collections` | `LOCAL_VERIFIED` | `SHARED_OWNER` | Reuse commercial contract context only. Do not rebuild collections or CFDI. |
| Code Atlas private-repository rental hardening from PR #299 | source merged | `ADAPT` | Read-only, bounded lifecycle, sanitization before egress, source-code egress denied by default, cleanup evidence. |
| `code_atlas.change_intelligence.customer_wow_v1` | `LOCAL_VERIFIED` | `REUSE_AS_IS` | Do not rebuild repository discovery, graphs, Change Studio, Authority Pack, Verify or Evidence Report. |
| Cloud Center existing visual/runtime surfaces | mixed existing owners | `DO_NOT_TOUCH` | V1 changes only one navigation link. Existing rendering, licensing, billing, support and customer flows retain ownership. |

## 4. Layer Map contract

The fresh Mesh includes the mandatory Layer Map. The new surface follows these rules:

| Layer | Owner | Rule |
|---|---|---|
| Existing Cloud Center shell | `DO_NOT_TOUCH` | One navigation seam only. No existing renderer replacement. |
| CI page document | `NEW_OWNER` | `change_intelligence_center.html` only. |
| CI visual material | `NEW_OWNER` | `change_intelligence_center.css`; all surface classes use `pci-` namespace. |
| CI interaction/projection | `NEW_OWNER` | `change_intelligence_center.js`; read-only GETs only in V1. |
| CI source contract | `NEW_OWNER` | `change_intelligence_cloud.json`. |
| Repository/run/evidence data | `NOT_CONNECTED` | Display explicit blocked/unknown empty states until real adapters exist. |
| Existing `.cc-*` styles | `DO_NOT_TOUCH` | New CSS must not target `.cc-*`. |
| Global/wildcard patch layer | `FORBIDDEN` | No wildcard CSS owner, no `!important`, no priority override layer. |

Accessibility owners include keyboard focus visibility, responsive navigation, `prefers-reduced-motion` and `prefers-reduced-transparency` behavior.

## 5. V1 data semantics

The console may display:

- repository and product maturity recorded by existing evidence;
- fresh Mesh provenance for this task;
- Discover/Guard/Control contracts;
- explicit shared-owner reuse decisions;
- explicit `NOT_CONNECTED`, `UNKNOWN`, `BLOCKED` and `NOT_MEASURED` states;
- ROI formulas and documented commercial reference terms;
- safety and evidence invariants.

The console may not display as factual without a real adapter:

- customer repository inventory;
- live analysis-run history;
- customer Authority Packs;
- customer Evidence Reports;
- active Change Intelligence product entitlement;
- measured customer ROI or savings;
- hosted tenant isolation;
- enterprise IAM or compliance state.

## 6. No-fake-green rules

1. `UNKNOWN` remains `UNKNOWN`.
2. `NOT_CONNECTED` is not rendered as an empty healthy list.
3. Source/local verification is not production certification.
4. Retrieval is not proof.
5. A derived index is not authority.
6. Impact Radius is not authorization.
7. Missing evidence does not become a warning-only PASS.
8. Private customer source does not egress by default.
9. The browser must not collect or expose Cloud Center admin secrets.
10. The V1 surface performs no source/runtime/cloud mutation.

## 7. ROI contract

The V1 console exposes the documented equations only:

- **Measured Monthly Benefit** = Discovery + Rework + Agent Supervision + Release/Evidence
- **Net Monthly Value** = Measured Monthly Benefit − Price
- **ROI %** = `(Measured Monthly Benefit − Price) / Price × 100`

A customer-specific result requires measured or customer-supplied inputs. No fabricated risk-avoidance or engineering-savings number is allowed.

## 8. Verification gates

Before this source slice may be called source-ready:

1. new files parse/load structurally;
2. the machine-readable contract preserves conservative maturity flags;
3. exactly one Cloud Center navigation seam points to the new page;
4. existing `cloud_command_center.js` and `cloud_command_center.css` remain unmodified by the Change Intelligence implementation;
5. new JavaScript contains no mutating HTTP method or secret collection path;
6. new CSS contains no `!important`, `.cc-*` selector or wildcard priority layer;
7. the effective diff stays inside the authorized file boundary;
8. repository checks remain green.

Browser/runtime evidence is a later gate and must not be inferred from static verification.

## 9. Next gates

After source readiness:

1. browser/runtime evidence for the isolated console under an authorized workflow;
2. read-only repository-registry adapter;
3. projection of real Code Atlas analysis manifests;
4. Authority Pack and Evidence Report reference adapter;
5. Change Intelligence entitlement mapping onto the existing licensing owner;
6. customer-input ROI instrumentation;
7. human usefulness evidence and independent-agent replication when an independent evaluator is available;
8. only later, separately governed hosted/enterprise productization.

## 10. Explicit exclusions

This V1 does not authorize or modify:

- Tablet, PC, Mobile, Chart Lab or Shared UI;
- DB/Prisma schema, migrations, generation or data;
- Cloudflare Worker, D1, DNS or deploy state;
- ports, processes or development servers;
- existing Cloud Center licensing/admin/customer setup/customer registration/commercial billing behavior;
- Code Atlas frozen independent-evaluator work;
- unrelated UI Bridge/UIMAP work;
- enterprise IAM, SSO/SAML/SCIM or compliance claims.
