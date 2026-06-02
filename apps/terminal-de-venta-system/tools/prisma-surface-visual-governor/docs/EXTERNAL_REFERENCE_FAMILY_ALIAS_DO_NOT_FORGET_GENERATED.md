# PRISMA M-04B fix2 · DO NOT FORGET

- Las familias externas granularizadas ya fueron normalizadas.
- Usar `external-reference-atmosphere-pack.normalized.generated.json` para próximos rollouts.
- Usar `surface-atmosphere-assets.external-overlay.normalized.generated.json` para decidir superficies.
- No consumir raw `family_id` anterior si hay `normalized_family_id`.
- POS/Checkout sigue con gate.
- Tablet productiva sólo light-first.