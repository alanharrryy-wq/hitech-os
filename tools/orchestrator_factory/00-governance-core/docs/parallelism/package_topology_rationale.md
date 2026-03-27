# Package Topology Rationale

## Why the default topology still uses one governance package plus six downstream packages
The 1+6 pattern is operationally small enough to launch tomorrow and large enough to separate the most failure-prone responsibilities.

## Why the original package names were generalized
The governing backbone from the source material was strong, but several package names were too tied to one company, one portal, or one infrastructure provider. The final topology keeps the same constitutional separation while generalizing the labels:

- security/auth/tenant -> identity, access, and trust
- data/bitacora/persistence -> domain, data, and persistence
- API contracts/service wiring -> service contracts and orchestration
- frontend/portal/client state -> experience, clients, and interactions
- Cloudflare infra/deployment -> platform, infrastructure, and delivery
- QA/release/operations -> quality, release, and operations

## Why these six packages are still useful across many project types
- every serious project has trust boundaries
- every serious project has domain and state assumptions
- most projects have service or orchestration boundaries, even if not public APIs
- most projects expose some experience or interaction surface
- every project ships through some platform and delivery boundary
- every project needs quality and operational evidence

## Override rule
A project may use a different topology, but only through homologation and a recorded governance override.
