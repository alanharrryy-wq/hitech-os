# PRISMA Source Code Licensing Policy

**Status:** PROPRIETARY_CUTOVER_PENDING_PRIVATE_REPOSITORY  
**Owner:** HITECH RECTIFIERS, S.A. DE C.V.  
**Scope:** PRISMA / HITECH-authored source, documentation, governance, tooling and product surfaces  
**Last historical Apache 2.0 public baseline:** `615d6732fd733696a60bb549bc88b23c0b573de4`  
**Cutover branch:** `legal/prisma-proprietary-cutover-20260825`

## 1. Purpose

This policy establishes a clean, auditable source-code licensing boundary for PRISMA. It does not rewrite repository history and it does not claim to revoke rights already granted for historical public versions.

The repository was historically public with a root Apache License 2.0. From the proprietary relicensing cutover forward, HITECH-authorized versions of HITECH-authored PRISMA materials are offered under the proprietary root `LICENSE`, subject to the historical and third-party boundaries below.

## 2. Historical boundary

The commit below is recorded as the final public baseline before the proprietary cutover:

```text
615d6732fd733696a60bb549bc88b23c0b573de4
```

Historical copies or versions validly made available under Apache License 2.0 keep the rights granted by that historical license. The cutover does not attempt to erase or revoke those rights.

No Git history rewrite is authorized for the purpose of obscuring the prior Apache license. Auditability is more valuable than cosmetic history rewriting.

## 3. Proprietary boundary

At the cutover, HITECH-authored PRISMA materials in the HITECH-authorized current version and subsequent HITECH-authored revisions are governed by the proprietary root `LICENSE`, unless a file or component expressly states another license.

The proprietary boundary includes, where authored by HITECH and not otherwise licensed:

- PRISMA application and platform source code;
- Change Assurance implementation and governance;
- POS and vertical product implementation;
- PRISMA Cloud Center / control-plane implementation;
- internal operational tooling and governed automation;
- proprietary schemas, contracts, policies and orchestration logic;
- HITECH-authored UI, workflow, evidence and verification implementation.

This source-code license boundary is distinct from PRISMA runtime entitlements, customer plans, billing, subscriptions and license-control infrastructure already present in the product. Those are commercial/runtime mechanisms, not the copyright license of this repository.

## 4. Third-party boundary

Third-party intellectual property remains under its own terms. The proprietary cutover must not delete, replace or suppress third-party license obligations.

Separate license terms control when a file or component contains or is accompanied by, for example:

- its own `LICENSE` or `NOTICE`;
- an SPDX license identifier;
- a third-party copyright header;
- bundled dependency license material;
- asset-specific license terms.

A complete dependency/SBOM and third-party-notice review remains a release-readiness requirement before customer distribution. This policy does not certify that review as complete.

## 5. Corporate ownership representation and diligence boundary

For current investment and productization planning, the founder represents that PRISMA was developed after the incorporation of HITECH RECTIFIERS, S.A. DE C.V., that the substantive PRISMA code was authored under HITECH, and that no external human contributor has been granted independent ownership of PRISMA source code.

That representation is recorded for diligence but is not a substitute for final corporate/IP counsel review. Before an investor closing or first customer distribution, counsel should confirm the documentary chain of title and whether any confirmatory assignment, administrator resolution, employment/work-made-for-hire instrument, or contributor representation is desirable under applicable law.

## 6. Repository visibility gate

The proprietary cutover is not considered operationally closed while the canonical source repository remains public.

Required closure sequence:

1. Record the final Apache public baseline SHA.
2. Change the canonical repository visibility from public to private.
3. Merge the proprietary licensing cutover only after private visibility is confirmed.
4. Preserve historical Git evidence; do not rewrite history to hide Apache.
5. Verify the root license is detected as proprietary/no open-source SPDX license.
6. Verify third-party license and notice files remain intact.
7. Run a dependency/SBOM and third-party-license review before distribution.
8. Add the final IP/licensing diligence evidence to the investor data room.

## 7. Commercial customer boundary

A customer does not acquire ownership of PRISMA merely by purchasing a subscription, deployment, support package or managed service. Customer rights must be defined by separate commercial terms.

Unless a signed agreement expressly provides otherwise, source-code ownership remains with HITECH and customer access is limited to the licensed product/service rights stated in the applicable agreement.

Customer data ownership, custody, portability and privacy are separate contractual subjects and must not be conflated with ownership of PRISMA source code.

## 8. Investor-safe statement

The following statement may be used only after the repository is private and the cutover is merged:

> HITECH controls the current PRISMA source-code line as proprietary software. Historical public revisions were previously available under Apache License 2.0 and remain subject to those historical grants. Current and future HITECH-authored versions are proprietary, while third-party components remain governed by their respective licenses.

Do not state that Apache rights were retroactively revoked, that historical public copies became proprietary, or that third-party components are owned by HITECH.

## 9. No-fake-green closure criteria

This licensing transition is `DONE` only when all of the following are evidenced:

- canonical repository is private;
- proprietary root `LICENSE` is merged to the protected default branch;
- historical Apache baseline SHA is recorded;
- third-party notices remain present;
- no runtime/product behavior changed as part of the cutover;
- GitHub/CI checks required by the repository pass;
- investor-facing language accurately preserves the historical Apache boundary;
- legal/IP counsel review is tracked before financing close or customer distribution.

Until then, status remains `PROPRIETARY_CUTOVER_PENDING_PRIVATE_REPOSITORY`.
