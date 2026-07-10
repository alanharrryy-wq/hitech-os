# 09. NDC Surface, UI and Chart Atlas

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Runtime map

| Runtime | Surface family | Visibility | Rol |
|---|---|---|---|
| 3000 | Chart Lab | internal | fábrica analytics. |
| 3110 | Portal/Marketplace | client/commercial | venta/onboarding. |
| 3120 | Tablet POS | client operational | eventos POS. |
| 3130 | PC Admin | client admin | auditoría/reportes. |
| 3140 | Mobile | client supervisor | alertas/resumen. |
| 3150 | SaaS Control | hybrid | tenants/licencias/slots. |
| 3160 | Cloud Command | internal | runtime/evidence/releases. |

## UI hierarchy

```text
SURF → ZONE → PNL → WID/TBL/FRM/CHT/BTN
```

## Panel types

KPI panel, Action panel, Audit panel, Alert panel, Evidence panel, Licensing panel, Chart panel, Drilldown panel, Timeline panel, Health panel, Billing panel, Module marketplace panel.

## Widget types

KPI Card, Sparkline, Table, Form, Button, Chart, Badge, Timeline, Evidence viewer, Drilldown, Filter bar, Warning banner, Map, Funnel, Heatmap, Checklist, Drawer, Modal, Command palette.

## Chart contract

Toda chart declara: MET, DS, formula, scope dimensions, destination surfaces, role, license, evidence/demo, commercial limit y success criterion.
