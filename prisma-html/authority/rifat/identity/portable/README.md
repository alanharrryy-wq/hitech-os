# PRISMA Portable Element Export

`IDEXPORT1` turns a governed identity object into one portable instruction file.

The artifact is **not a product patch**. It preserves exact values, neutral meaning,
identity/profile, recipe, target surface, known bindings, missing bindings, origin,
compatibility, manifest and SHA-256 integrity. Unknown owner, route, region, slot or
component bindings remain `null` and are reported as blocking.

Supported source objects:

- identity profile;
- semantic token;
- surface adapter;
- Identity Dictionary preview component recipe.

Import is inspection-only in this iteration. Applying an artifact to Tablet, PC,
Mobile, Web, Chart Lab or Control Center requires a future governed application gate.
