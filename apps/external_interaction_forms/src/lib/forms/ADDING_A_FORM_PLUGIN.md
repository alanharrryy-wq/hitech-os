# Adding A Form Plugin

This app uses governed internal form plugins.

## 1) Create a plugin module

Path:

- `src/lib/forms/plugins/<your-form>.plugin.ts`

Implement `FormPluginDefinition` from:

- `src/lib/forms/contracts.ts`

Required parts:

1. `formTypeId` (unique)
2. `schemaId` (must exist in `external_interaction_template`)
3. `display`
4. `steps`
5. `defaults`
6. `validateStep`
7. `buildCreatePayload`
8. `buildUpdatePayload`
9. `buildSubmitPayload`

Optional:

1. `attachmentRules`

## 2) Register the plugin

Edit:

- `src/lib/forms/registry.ts`

Add your plugin to `FORM_PLUGINS`.

The registry enforces:

1. unique `formTypeId`
2. non-empty steps
3. valid attachment field references

## 3) Map backend governance

Edit `external_interaction_template`:

- `src/lib/integrations/public-forms/registry.ts`

Add:

1. `formTypeId`
2. `schemaId`
3. `createStepId`
4. allowed `updateStepIds`
5. `attachmentsAllowed`

## 4) Verify

Run:

```powershell
pnpm --filter @hitech/external_interaction_forms typecheck
pnpm --filter @hitech/external_interaction_forms build
pnpm --filter @hitech/external_interaction_template test
```

