# 53_MUTATION_POLICY_MODE_MATRIX

## Safe Mode posture

Safe Mode is the default authority posture.
It should allow bounded, understandable, reversible-enough actions.

Typical Safe Mode mutations:
- scene look update
- layout move / resize within governed limits
- slot widget insertion from approved prefab
- widget props update
- widget style update
- selected element reset
- draft discard
- draft commit

## Advanced Mode posture

Advanced Mode may allow broader operations, but only by explicit contract expansion.
It is not a loophole.

## Matrix requirements

Policy decisions should consider:
- source trust
- target kind
- mutation type
- scope
- reversibility
- capability gating
- runtime adapter support
- stale selection or stale revision status

## Rule of thumb

If the system cannot explain why a mutation is allowed, it is not ready to allow it.
