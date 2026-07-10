# 01. NDC Canon and Doctrine

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Tesis

PRISMA dejó de ser apps sueltas. La lectura correcta es un sistema multi-scope donde cada dato nace en contexto operacional, produce eventos, cruza sync/provenance, llega a canonical projection y luego aparece en superficies y widgets.

## Cambio mental

Malo:

```text
Tablet creó venta 231. PC ve venta 228. Mobile muestra venta 229.
```

Correcto:

```text
ENT.sale → EVT.sale.created → ACT.sale.checkout → scope tenant/business/store/device/user → sync/provenance → CAN.sale → SURF.tb.pos / SURF.pc.sales_control / SURF.mb.owner_home / SURF.cl.sales_trend → UI widgets
```

## Autoridad

1. Curation humana explícita.
2. Canon NDC.
3. Canon PRISMA vivo.
4. Evidence runtime/tooling.
5. Observaciones de herramientas.
6. Matrices generadas.
7. Candidatos inferidos.

## Reglas no negociables

- Puerto no es producto.
- App no es fuente de verdad.
- UI no manda.
- DB futura no inventa verdad.
- Evidence sostiene claims, readiness y canonical promotion.
- Curation se registra, no se sobreescribe matrix export.
- Chart Lab diseña analytics, no reemplaza canonical data.
- Control Center gobierna tenants/licencias/slots/módulos.

## Anti-patrones

| Anti-patrón | Corrección |
|---|---|
| `TB_POS_SALE` como canonical | `ENT.sale` + projections. |
| Editar CSV generado | Registrar curation y regenerar. |
| Screenshot como canonical truth | Screenshot evidencia proyección, no verdad. |
| DB antes de neutral IDs | Primero contratos, luego persistencia. |
| Claim sin licencia/evidencia | `needs_review` o `blocked`. |
