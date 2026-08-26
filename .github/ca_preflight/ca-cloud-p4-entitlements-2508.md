# Change Assurance Cloud Center P4 Authority Carrier

Exact base: `22c6fbc74774a1083721ccf225a537f87f38edc4`

Task: map Change Assurance entitlements from the existing canonical licensing owner into the existing Cloud Center projection without rebuilding licensing, mutating licenses, touching Worker/D1, changing billing, or inventing product entitlements.

Expected fail-closed rule: if the canonical plan/feature catalog does not contain a Change Assurance feature, the projection must say so explicitly and must not claim live enforcement, grant, production readiness, or certification.

This carrier is evidence-only and must not merge.
