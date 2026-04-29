import type { TwinCapabilityManifest } from "../types/capability";

export const TWIN_CAPABILITY_MANIFEST: TwinCapabilityManifest[] = [
{
  "id": "catalog-master",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "catalog",
  "title": "Catálogo maestro",
  "businessOutcome": "PC mantiene catálogo canónico y tablet consume contexto limpio para venta/stock.",
  "owner": "pc",
  "parityKey": "catalog.master",
  "status": "ready",
  "mode": "authoritative_control",
  "syncDirection": "pc_to_tablet",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "catalog",
      "route": "/catalog",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC-02 catálogo maestro"
      ],
      "allowedEvents": [
        "catalog.product.updated"
      ],
      "offlineMode": "read_only",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "stock",
      "route": "/stock",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "TAB-06 inventario rápido"
      ],
      "allowedEvents": [
        "catalog.product.updated"
      ],
      "offlineMode": "read_only",
      "auditLevel": "summary"
    }
  ],
  "invariants": [
    "Catálogo maestro no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "catalog.product.updated",
      "producedBy": [
        "pc"
      ],
      "consumedBy": [
        "tablet"
      ],
      "required": true,
      "notes": "El catálogo publicado por PC alimenta búsqueda y disponibilidad operativa en tablet."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "stock-signal",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "inventory",
  "title": "Señal de stock operativa",
  "businessOutcome": "Tablet puede consultar/levantar señales de stock sin apropiarse del ledger global.",
  "owner": "pc",
  "parityKey": "inventory.stock_signal",
  "status": "ready",
  "mode": "bidirectional_bridge",
  "syncDirection": "bidirectional",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "stock",
      "route": "/stock",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC-04 inventario global"
      ],
      "allowedEvents": [
        "stock.adjusted",
        "stock.adjusted"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "stock",
      "route": "/stock",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB-06 inventario rápido"
      ],
      "allowedEvents": [
        "stock.adjusted"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Señal de stock operativa no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "stock.adjusted",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Ajustes con origen claro y reconciliación por outbox."
    },
    {
      "name": "stock.adjusted",
      "producedBy": [
        "pc"
      ],
      "consumedBy": [
        "tablet"
      ],
      "required": false,
      "notes": "Recepciones visibles para operación de piso."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "inventory-count",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "inventory",
  "title": "Conteos físicos",
  "businessOutcome": "PC gobierna conteos y tablet prepara captura rápida sin romper saldos.",
  "owner": "pc",
  "parityKey": "inventory.count",
  "status": "partial",
  "mode": "bidirectional_bridge",
  "syncDirection": "bidirectional",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "counts",
      "route": "/counts",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC conteos"
      ],
      "allowedEvents": [
        "sync.event.sent",
        "stock.adjusted"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "stock",
      "route": "/stock",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB-06 inventario rápido"
      ],
      "allowedEvents": [
        "stock.adjusted"
      ],
      "offlineMode": "full_local",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Conteos físicos no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "stock.adjusted",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Captura offline de conteos se vuelve propuesta de ajuste."
    },
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc"
      ],
      "consumedBy": [
        "tablet"
      ],
      "required": false,
      "notes": "Cierre de conteo publicado hacia piso."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "purchase-order",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "procurement",
  "title": "Órdenes de compra",
  "businessOutcome": "PC administra abasto; tablet solo observa compromisos relevantes para recepción.",
  "owner": "pc",
  "parityKey": "procurement.purchase_order",
  "status": "ready",
  "mode": "authoritative_control",
  "syncDirection": "pc_to_tablet",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "purchasing",
      "route": "/purchasing",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC-05 pedidos y órdenes"
      ],
      "allowedEvents": [
        "sync.event.sent"
      ],
      "offlineMode": "read_only",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "stock",
      "route": "/stock",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "TAB-07 recepción compras"
      ],
      "allowedEvents": [
        "sync.event.sent"
      ],
      "offlineMode": "read_only",
      "auditLevel": "summary"
    }
  ],
  "invariants": [
    "Órdenes de compra no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc"
      ],
      "consumedBy": [
        "tablet"
      ],
      "required": true,
      "notes": "Una orden liberada habilita recepción guiada en tablet."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "receiving-flow",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "procurement",
  "title": "Recepción de compras",
  "businessOutcome": "Tablet puede apoyar recepción física mientras PC consolida costo, lote y stock.",
  "owner": "pc",
  "parityKey": "procurement.receiving",
  "status": "ready",
  "mode": "bidirectional_bridge",
  "syncDirection": "bidirectional",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "receiving",
      "route": "/receiving",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC recepción"
      ],
      "allowedEvents": [
        "stock.adjusted"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "stock",
      "route": "/stock",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB-07 recepción compras"
      ],
      "allowedEvents": [
        "stock.adjusted"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Recepción de compras no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "stock.adjusted",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Recepción física genera señal conciliable con orden y stock."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "replenishment-signal",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "procurement",
  "title": "Reabasto inteligente",
  "businessOutcome": "PC calcula reabasto y tablet reporta señales de agotado o urgencia.",
  "owner": "pc",
  "parityKey": "procurement.replenishment",
  "status": "partial",
  "mode": "bidirectional_bridge",
  "syncDirection": "bidirectional",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "replenishment",
      "route": "/replenishment",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC reabasto"
      ],
      "allowedEvents": [
        "sync.event.sent"
      ],
      "offlineMode": "read_only",
      "auditLevel": "summary"
    },
    {
      "surface": "tablet",
      "moduleKey": "stock",
      "route": "/stock",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB-06 inventario rápido"
      ],
      "allowedEvents": [
        "sync.event.sent"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "summary"
    }
  ],
  "invariants": [
    "Reabasto inteligente no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Solicitud de reabasto con origen de piso o cálculo central."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "sales-ticket",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "sales",
  "title": "Ticket de venta",
  "businessOutcome": "Tablet vende y PC observa la transacción para control, auditoría y reportes.",
  "owner": "tablet",
  "parityKey": "sales.ticket",
  "status": "ready",
  "mode": "local_execution",
  "syncDirection": "tablet_to_pc",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "audit",
      "route": "/audit",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "PC auditoría"
      ],
      "allowedEvents": [
        "sale.created",
        "ticket.closed"
      ],
      "offlineMode": "read_only",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "sales",
      "route": "/sales",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB-02 venta checkout"
      ],
      "allowedEvents": [
        "sale.created",
        "ticket.closed"
      ],
      "offlineMode": "full_local",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Ticket de venta no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "sale.created",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Venta creada en tablet entra a control y reporteo PC."
    },
    {
      "name": "ticket.closed",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Cierre del ticket congela totales para caja y auditoría."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "checkout-payment",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "sales",
  "title": "Cobro y medios de pago",
  "businessOutcome": "Tablet ejecuta cobro y PC concentra consistencia de caja y conciliación.",
  "owner": "tablet",
  "parityKey": "sales.checkout_payment",
  "status": "ready",
  "mode": "local_execution",
  "syncDirection": "tablet_to_pc",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "audit",
      "route": "/audit",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "PC caja y auditoría"
      ],
      "allowedEvents": [
        "ticket.closed"
      ],
      "offlineMode": "read_only",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "checkout",
      "route": "/checkout",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB-02 venta checkout",
        "TAB-03 caja táctil"
      ],
      "allowedEvents": [
        "ticket.closed"
      ],
      "offlineMode": "full_local",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Cobro y medios de pago no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "ticket.closed",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Cobro finalizado alimenta caja, turno y reportes."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "shift-cash",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "cash",
  "title": "Turno y caja",
  "businessOutcome": "Tablet abre/cierra turno y PC audita diferencias, retiros y arqueos.",
  "owner": "tablet",
  "parityKey": "cash.shift",
  "status": "ready",
  "mode": "bidirectional_bridge",
  "syncDirection": "tablet_to_pc",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "audit",
      "route": "/audit",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "PC-06 caja y finanzas operativas"
      ],
      "allowedEvents": [
        "shift.opened",
        "shift.closed"
      ],
      "offlineMode": "read_only",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "shift",
      "route": "/shift",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB-03 caja táctil"
      ],
      "allowedEvents": [
        "shift.opened",
        "shift.closed"
      ],
      "offlineMode": "full_local",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Turno y caja no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "shift.opened",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Apertura de turno visible para control central."
    },
    {
      "name": "shift.closed",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Cierre con totales y diferencias auditable en PC."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "return-flow",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "returns",
  "title": "Devoluciones",
  "businessOutcome": "Tablet captura devolución; PC retiene auditoría y decisión de ajuste contable/stock.",
  "owner": "tablet",
  "parityKey": "returns.transaction",
  "status": "ready",
  "mode": "bidirectional_bridge",
  "syncDirection": "tablet_to_pc",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "audit",
      "route": "/audit",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "PC auditoría"
      ],
      "allowedEvents": [
        "sale.refunded",
        "stock.adjusted"
      ],
      "offlineMode": "read_only",
      "auditLevel": "transaction"
    },
    {
      "surface": "tablet",
      "moduleKey": "returns",
      "route": "/returns",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB devoluciones"
      ],
      "allowedEvents": [
        "sale.refunded",
        "stock.adjusted"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Devoluciones no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "sale.refunded",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Devolución registrada con ticket origen y motivo."
    },
    {
      "name": "stock.adjusted",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": false,
      "notes": "Ajuste de stock derivado de devolución cuando aplique."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "sync-health",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "sync",
  "title": "Salud de sincronización",
  "businessOutcome": "Ambas superficies exponen estado de outbox, conflictos y último checkpoint.",
  "owner": "pc",
  "parityKey": "sync.health",
  "status": "ready",
  "mode": "bidirectional_bridge",
  "syncDirection": "bidirectional",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "sync",
      "route": "/sync",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC-07 sync y eventos"
      ],
      "allowedEvents": [
        "sync.event.sent",
        "sync.event.sent",
        "sync.event.failed",
        "sync.conflict.detected",
        "sync.event.sent",
        "sync.event.sent"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "summary"
    },
    {
      "surface": "tablet",
      "moduleKey": "sync",
      "route": "/sync",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB sync"
      ],
      "allowedEvents": [
        "sync.event.sent",
        "sync.event.sent",
        "sync.event.failed",
        "sync.conflict.detected",
        "sync.event.sent",
        "sync.event.sent"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "summary"
    }
  ],
  "invariants": [
    "Salud de sincronización no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": false,
      "notes": "Inicio de ciclo."
    },
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Checkpoint exitoso."
    },
    {
      "name": "sync.event.failed",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Falla visible y accionable."
    },
    {
      "name": "sync.conflict.detected",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Conflicto con entidad y estrategia de resolución."
    },
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Evento agregado a cola."
    },
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Evento entregado a destino."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "audit-trail",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "audit",
  "title": "Trazabilidad operativa",
  "businessOutcome": "PC concentra auditoría y tablet produce eventos con actor, terminal, turno y origen.",
  "owner": "pc",
  "parityKey": "audit.trail",
  "status": "ready",
  "mode": "authoritative_control",
  "syncDirection": "tablet_to_pc",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "audit",
      "route": "/audit",
      "role": "source_of_truth",
      "ownsWrites": true,
      "requiredScreens": [
        "PC auditoría"
      ],
      "allowedEvents": [
        "sync.event.sent",
        "sale.created",
        "sale.refunded",
        "shift.closed"
      ],
      "offlineMode": "read_only",
      "auditLevel": "regulatory"
    },
    {
      "surface": "tablet",
      "moduleKey": "sync",
      "route": "/sync",
      "role": "executor",
      "ownsWrites": true,
      "requiredScreens": [
        "TAB actividad historial"
      ],
      "allowedEvents": [
        "sale.created",
        "sale.refunded",
        "shift.closed"
      ],
      "offlineMode": "queue_required",
      "auditLevel": "transaction"
    }
  ],
  "invariants": [
    "Trazabilidad operativa no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "sync.event.sent",
      "producedBy": [
        "pc"
      ],
      "consumedBy": [
        "tablet"
      ],
      "required": false,
      "notes": "Cierre o revisión publicada."
    },
    {
      "name": "sale.created",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Evento auditable."
    },
    {
      "name": "sale.refunded",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Evento auditable."
    },
    {
      "name": "shift.closed",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc"
      ],
      "required": true,
      "notes": "Evento auditable."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "dashboard-kpis",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "reporting",
  "title": "KPIs gemelos",
  "businessOutcome": "PC muestra lectura gerencial y tablet muestra lectura operativa sin inventar métricas paralelas.",
  "owner": "pc",
  "parityKey": "reporting.kpi",
  "status": "partial",
  "mode": "mirror_observer",
  "syncDirection": "bidirectional",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "audit",
      "route": "/audit",
      "role": "source_of_truth",
      "ownsWrites": false,
      "requiredScreens": [
        "PC-01 dashboard ejecutivo"
      ],
      "allowedEvents": [
        "sale.created",
        "stock.adjusted",
        "shift.closed"
      ],
      "offlineMode": "read_only",
      "auditLevel": "summary"
    },
    {
      "surface": "tablet",
      "moduleKey": "sales",
      "route": "/sales",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "TAB-01 inicio operativo"
      ],
      "allowedEvents": [
        "sale.created",
        "stock.adjusted",
        "shift.closed"
      ],
      "offlineMode": "read_only",
      "auditLevel": "summary"
    }
  ],
  "invariants": [
    "KPIs gemelos no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "sale.created",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Base para ventas del día."
    },
    {
      "name": "stock.adjusted",
      "producedBy": [
        "pc",
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": false,
      "notes": "Base para alertas operativas."
    },
    {
      "name": "shift.closed",
      "producedBy": [
        "tablet"
      ],
      "consumedBy": [
        "pc",
        "tablet"
      ],
      "required": true,
      "notes": "Base para cierre de caja diario."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
},
{
  "id": "customer-context",
  "version": "1.0.0",
  "updatedAt": "2026-04-26",
  "domain": "customer",
  "title": "Contexto de cliente",
  "businessOutcome": "Ambas apps leen cliente/cartera con escritura controlada hasta que exista módulo dedicado.",
  "owner": "pc",
  "parityKey": "customer.context",
  "status": "planned",
  "mode": "planned_bridge",
  "syncDirection": "pc_to_tablet",
  "surfaces": [
    {
      "surface": "pc",
      "moduleKey": "catalog",
      "route": "/catalog",
      "role": "source_of_truth",
      "ownsWrites": false,
      "requiredScreens": [
        "PC-03 clientes y cartera"
      ],
      "allowedEvents": [
        "catalog.product.updated"
      ],
      "offlineMode": "read_only",
      "auditLevel": "summary"
    },
    {
      "surface": "tablet",
      "moduleKey": "sales",
      "route": "/sales",
      "role": "observer",
      "ownsWrites": false,
      "requiredScreens": [
        "TAB-04 clientes en piso"
      ],
      "allowedEvents": [
        "catalog.product.updated"
      ],
      "offlineMode": "read_only",
      "auditLevel": "summary"
    }
  ],
  "invariants": [
    "Contexto de cliente no puede tener estados divergentes sin evento de sync o auditoría.",
    "PC y tablet deben conservar actor, terminal, turno y origen cuando el evento sea transaccional.",
    "Una superficie no puede apropiarse de escrituras que su binding declara como ownsWrites=false."
  ],
  "events": [
    {
      "name": "catalog.product.updated",
      "producedBy": [
        "pc"
      ],
      "consumedBy": [
        "tablet"
      ],
      "required": false,
      "notes": "Se reutiliza hasta que exista customer.updated dedicado."
    }
  ],
  "acceptance": [
    "La capability aparece en el registry compartido sin errores de validación.",
    "PC puede resolver su binding local por id y moduleKey.",
    "Tablet puede resolver su binding local por id y moduleKey.",
    "Los eventos requeridos tienen productor, consumidor y surface allowedEvents."
  ],
  "risks": [
    "Si una app agrega pantalla sin actualizar capability, la paridad vuelve a vivir en la memoria del desarrollador, esa vecindad peligrosa.",
    "Si una app escribe fuera de ownsWrites, el ledger empieza a parecer libreta mojada."
  ]
}
];

export const TWIN_CAPABILITY_MANIFEST_VERSION = "2026.04.26-runtime-kernel" as const;
