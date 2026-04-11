# External Interaction Forms

Public WhatsApp-shareable intake app.

## Local run

```powershell
pnpm --filter @hitech/external_interaction_forms dev
```

Default URL:

- `http://127.0.0.1:3200`

Required env:

- `NEXT_PUBLIC_API_BASE_URL` (dev: `http://127.0.0.1:3100`, prod: `https://engine.hitechrts.com`)
- `NEXT_PUBLIC_FORMS_APP_URL` (dev: `http://127.0.0.1:3200`, prod: `https://forms.hitechrts.com`)
