# Override Ledger

This ledger records the major places where the final framework intentionally changed the source material.

| Source element | Final decision | Final location | Reason |
|---|---|---|---|
| Zip A package `01-security-auth-tenant` | generalized to `01-identity-access-and-trust` | `01-identity-access-and-trust/` | universal projects may not be tenant-based or portal-based, but they still have trust and access boundaries |
| Zip A package `02-data-bitacora-persistence` | generalized to `02-domain-data-and-persistence` | `02-domain-data-and-persistence/` | `bitacora` is domain-specific; the universal layer must cover broader state and persistence concerns |
| Zip A package `03-api-contracts-and-service-wiring` | generalized to `03-service-contracts-and-orchestration` | `03-service-contracts-and-orchestration/` | not every project is API-first, but most serious projects have service and orchestration boundaries |
| Zip A package `04-frontend-portal-and-client-state` | generalized to `04-experience-clients-and-interactions` | `04-experience-clients-and-interactions/` | websites, dashboards, portals, and client apps all fit better under experience and interaction surfaces |
| Zip A package `05-cloudflare-infra-and-deployment` | generalized to `05-platform-infrastructure-and-delivery` | `05-platform-infrastructure-and-delivery/` | provider-neutral core is required for universality |
| Zip B fixed lanes | downgraded to optional tactical profile only | `docs/parallel_execution/15_repo_shape_profiles.md` | lane taxonomy was too repo-specific to govern universally |
| Zip B separate mission-control chat | collapsed into governance chat by default | `master_chat_routing.md` | the target operating model is explicitly 1 governing chat + 6 package chats |
| Zip B `round` as top-level identity | nested under `run` | `00-governance-core/docs/control/run_lifecycle.md` | stronger traceability requires project and run context above tactical rounds |
| Both zips lacked intake and homologation | added as new constitutional capability | `00-governance-core/docs/control/idea_intake_and_homologation.md` | vague ideas must be normalized before package launch |
| Both zips lacked a full canonical-source model | added as new constitutional capability | `00-governance-core/docs/control/canonical_source_rules.md` | prompts and examples needed to be explicitly subordinated |
