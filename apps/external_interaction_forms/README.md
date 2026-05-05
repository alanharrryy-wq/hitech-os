# External Interaction Forms

Public WhatsApp-shareable intake app.

## Multi-form plugin architecture

This app now runs through governed internal form plugins:

- Plugin contract: `src/lib/forms/contracts.ts`
- Registry: `src/lib/forms/registry.ts`
- Shared submit engine: `src/lib/forms/submit-engine.ts`
- Shared transport: `src/lib/forms/transport.ts`
- Same-origin gateway proxy: `app/api/forms-gateway/[...path]/route.ts`
- Draft persistence: `src/lib/forms/draft-storage.ts`

Included plugins:

1. `service_request_public` -> schema `service_request`
2. `approval_packet_public` -> schema `approval_packet`

UI runtime:

- `src/components/forms/forms-flow.tsx`
- Landing route accepts `?form=<form_type_id>`

## Local run

```powershell
pnpm --filter @hitech/external_interaction_forms dev
```

Default URL:

- `http://127.0.0.1:3200`

Required env:

- `NEXT_PUBLIC_API_BASE_URL` (dev: `http://127.0.0.1:3100`, prod: `https://engine.hitechrts.com`)
- `NEXT_PUBLIC_FORMS_APP_URL` (dev: `http://127.0.0.1:3200`, prod: `https://forms.hitechrts.com`)
- `FORMS_ENGINE_API_BASE_URL` (server-side target for gateway proxy; dev: `http://127.0.0.1:3100`)

## Add a new form plugin

1. Create plugin module in `src/lib/forms/plugins/<your-form>.plugin.ts`.
2. Implement `FormPluginDefinition`:
   - `formTypeId`
   - `schemaId`
   - `display`
   - `steps`
   - `defaults`
   - `validateStep`
   - `buildCreatePayload`
   - `buildUpdatePayload`
   - `buildSubmitPayload`
   - optional `attachmentRules`
3. Register plugin in `src/lib/forms/registry.ts`.
4. Ensure target schema exists in `external_interaction_template`.
5. Run:
   - `pnpm --filter @hitech/external_interaction_forms typecheck`
   - `pnpm --filter @hitech/external_interaction_forms build`
