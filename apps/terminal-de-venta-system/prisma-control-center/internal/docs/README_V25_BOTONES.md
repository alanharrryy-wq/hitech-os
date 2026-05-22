# PRISMA Control Center V25 - botones reales

Esta version agrega botones visibles y conectados en el panel web:

- Levantar local
- Levantar Cloudflare
- Levantar todo
- Web Control local
- Chart Lab
- Diagnostico / run-health
- Operator Brief
- Kill PRISMA

Los botones llaman endpoints locales en `/api/ops/action/...` y estos endpoints lanzan wrappers PowerShell desde `internal/wrappers`.

Notas:
- Las acciones son local-only. En modo publico devuelven FORBIDDEN.
- Los launchers se ejecutan asincronicamente y dejan logs/evidencia.
- Ctrl+F5 recomendado tras reemplazar.
