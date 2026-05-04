import { prisma } from "@/server/prisma/client";
import { getConflictCatalog } from "./conflicts";

export type BackofficeModuleKey =
  | "catalog"
  | "stock"
  | "movements"
  | "counts"
  | "purchasing"
  | "receiving"
  | "replenishment"
  | "audit"
  | "sync"
  | "settings";



type CatalogProductOverviewRow = {
  sku: string;
  name: string;
  category: string;
  priceCents: number;
  isActive: boolean;
  barcodes: Array<unknown>;
};

export type BackofficeModuleOverview = {
  key: BackofficeModuleKey;
  route: string;
  eyebrow: string;
  title: string;
  description: string;
  metrics: Array<{ label: string; value: string; note: string }>;
  table: {
    title: string;
    columns: string[];
    rows: Array<Record<string, string | number>>;
    emptyMessage: string;
  };
  notes: string[];
  meta: {
    source: "canonical_prisma" | "policy_contract";
    persistence: "available" | "unavailable" | "not_required";
    generatedAt: string;
    warnings: string[];
  };
};

const MODULE_TEXT: Record<BackofficeModuleKey, Pick<BackofficeModuleOverview, "route" | "eyebrow" | "title" | "description">> = {
  catalog: {
    route: "/catalog",
    eyebrow: "catálogo",
    title: "Catálogo operativo",
    description: "Control de SKUs, categorías, precios, barcodes y vigencia para la operación."
  },
  stock: {
    route: "/stock",
    eyebrow: "existencias",
    title: "Stock consolidado",
    description: "Lectura de cobertura, disponibles y quiebres sin interferir con la venta local Tablet."
  },
  movements: {
    route: "/movements",
    eyebrow: "movimientos",
    title: "Movimientos de inventario",
    description: "Trazabilidad de entradas, salidas y ajustes generados por operación o sincronización."
  },
  counts: {
    route: "/counts",
    eyebrow: "conteos",
    title: "Conteos físicos",
    description: "Fundación para auditoría de conteos, variaciones y conciliación de inventario."
  },
  purchasing: {
    route: "/purchasing",
    eyebrow: "compras",
    title: "Compras",
    description: "Órdenes abiertas, proveedores y líneas de planeación de abasto."
  },
  receiving: {
    route: "/receiving",
    eyebrow: "recepción",
    title: "Recepción",
    description: "Recepciones, incidencias y confirmación de mercancía contra orden de compra."
  },
  replenishment: {
    route: "/replenishment",
    eyebrow: "reabasto",
    title: "Reabasto",
    description: "Señales de reabasto y prioridades calculadas desde snapshots y reglas canónicas."
  },
  audit: {
    route: "/audit",
    eyebrow: "auditoría",
    title: "Auditoría y conflictos",
    description: "Vista de eventos sensibles, conteos y categorías de conflicto listas para revisión."
  },
  sync: {
    route: "/sync",
    eyebrow: "sync",
    title: "Ingesta y reconciliación",
    description: "PC valida eventos Tablet, clasifica conflictos y prepara consolidación explícita."
  },
  settings: {
    route: "/settings",
    eyebrow: "ajustes",
    title: "Políticas y terminales",
    description: "Marco de permisos, terminales y reglas offline; no bloquea ventas locales Tablet."
  }
};

function formatDate(value: Date | string | null | undefined) {
  if (!value) return "No disponible";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

function baseOverview(key: BackofficeModuleKey): BackofficeModuleOverview {
  const text = MODULE_TEXT[key];
  return {
    key,
    ...text,
    metrics: [],
    table: {
      title: "Detalle",
      columns: [],
      rows: [],
      emptyMessage: "No hay datos consolidados todavía."
    },
    notes: [],
    meta: {
      source: "canonical_prisma",
      persistence: "available",
      generatedAt: new Date().toISOString(),
      warnings: []
    }
  };
}

function unavailable(key: BackofficeModuleKey, error: unknown): BackofficeModuleOverview {
  const message = error instanceof Error ? error.message : "Error desconocido.";
  const overview = baseOverview(key);
  return {
    ...overview,
    table: {
      ...overview.table,
      emptyMessage: "No se pudo leer persistencia canónica; la pantalla queda en modo estado vacío honesto."
    },
    notes: ["PC conserva la venta local Tablet como independiente.", "La pantalla no inventa datos si Prisma no está disponible."],
    meta: {
      ...overview.meta,
      persistence: "unavailable",
      warnings: [`Persistencia no disponible: ${message}`]
    }
  };
}

export async function getBackofficeModuleOverview(key: BackofficeModuleKey): Promise<BackofficeModuleOverview> {
  try {
    if (key === "catalog") {
      const [totalProducts, activeProducts, products] = await Promise.all([
        prisma.product.count(),
        prisma.product.count({ where: { isActive: true } }),
        prisma.product.findMany({ include: { barcodes: true }, orderBy: { updatedAt: "desc" }, take: 200 })
      ]) as [number, number, CatalogProductOverviewRow[]];
      const categories = new Set(products.map((product: CatalogProductOverviewRow) => product.category));
      return {
        ...baseOverview(key),
        metrics: [
          { label: "SKUs totales", value: String(totalProducts), note: "Conteo completo de Product." },
          { label: "Activos", value: String(activeProducts), note: "isActive=true en persistencia canónica." },
          { label: "Categorías visibles", value: String(categories.size), note: "Agrupación de la muestra visible." }
        ],
        table: {
          title: "Productos consolidados recientes",
          columns: ["SKU", "Producto", "Categoría", "Precio", "Barcodes", "Estado"],
          rows: products.map((product: CatalogProductOverviewRow) => ({
            SKU: product.sku,
            Producto: product.name,
            Categoría: product.category,
            Precio: money(product.priceCents),
            Barcodes: product.barcodes.length,
            Estado: product.isActive ? "activo" : "inactivo"
          })),
          emptyMessage: "No hay productos consolidados en PC todavía. Ejecuta pnpm run db:pc:mass-catalog si ya cargaste Tablet."
        },
        notes: [
          "Catálogo PC gobierna productos consolidados; Tablet conserva su catálogo local para vender aunque PC no exista.",
          "La carga masiva 04D espejea el catálogo operativo de Tablet en la base canónica de PC sin resetear stock existente por defecto."
        ]
      };
    }

    if (key === "stock") {
      const snapshots: any[] = await prisma.stockSnapshot.findMany({ include: { product: true }, orderBy: { daysCover: "asc" }, take: 25 });
      const critical = snapshots.filter((row) => row.daysCover < 2).length;
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Snapshots", value: String(snapshots.length), note: "StockSnapshot reciente." },
          { label: "Críticos", value: String(critical), note: "Cobertura menor a dos días." },
          { label: "Ubicaciones", value: String(new Set(snapshots.map((row) => row.location)).size), note: "Locaciones con snapshot." }
        ],
        table: {
          title: "Cobertura por SKU",
          columns: ["SKU", "Producto", "Ubicación", "Disponible", "Días", "Estado"],
          rows: snapshots.map((row) => ({
            SKU: row.product.sku,
            Producto: row.product.name,
            Ubicación: row.location,
            Disponible: row.available,
            Días: row.daysCover.toFixed(1),
            Estado: row.daysCover < 1 ? "crítico" : row.daysCover < 2 ? "en riesgo" : "estable"
          })),
          emptyMessage: "No hay snapshots de stock consolidados todavía."
        },
        notes: ["Stock PC es vista de gobierno; Tablet decrementa localmente en su venta operativa."]
      };
    }

    if (key === "movements") {
      const movements: any[] = await prisma.stockMovement.findMany({ include: { product: true }, orderBy: { createdAt: "desc" }, take: 25 });
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Movimientos", value: String(movements.length), note: "Últimos registros leídos." },
          { label: "Salidas", value: String(movements.filter((row) => row.qty < 0).length), note: "Cantidad negativa." },
          { label: "Entradas/ajustes", value: String(movements.filter((row) => row.qty >= 0).length), note: "Cantidad positiva o cero." }
        ],
        table: {
          title: "Movimientos recientes",
          columns: ["SKU", "Producto", "Movimiento", "Cantidad", "Razón", "Ubicación", "Fecha"],
          rows: movements.map((row) => ({
            SKU: row.product.sku,
            Producto: row.product.name,
            Movimiento: row.movement,
            Cantidad: row.qty,
            Razón: row.reason,
            Ubicación: row.location,
            Fecha: formatDate(row.createdAt)
          })),
          emptyMessage: "No hay movimientos consolidados todavía."
        },
        notes: ["Los movimientos importados desde Tablet deberán entrar por eventos validados."]
      };
    }

    if (key === "counts") {
      const counts: any[] = await prisma.auditCount.findMany({ orderBy: { countedAt: "desc" }, take: 25 });
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Conteos", value: String(counts.length), note: "AuditCount reciente." },
          { label: "Con variación", value: String(counts.filter((row) => row.variance !== 0).length), note: "variance diferente de cero." },
          { label: "Pendientes", value: String(counts.filter((row) => row.status.toLowerCase() !== "posted").length), note: "Estado no cerrado." }
        ],
        table: {
          title: "Conteos recientes",
          columns: ["Ubicación", "Contó", "Variación", "Estado", "Fecha"],
          rows: counts.map((row) => ({
            Ubicación: row.location,
            Contó: row.countedBy,
            Variación: row.variance,
            Estado: row.status,
            Fecha: formatDate(row.countedAt)
          })),
          emptyMessage: "No hay conteos físicos consolidados todavía."
        },
        notes: ["La conciliación de conteos queda lista como módulo PC, no como flujo de venta."]
      };
    }

    if (key === "purchasing") {
      const orders: any[] = await prisma.purchaseOrder.findMany({ include: { supplier: true, lines: true }, orderBy: { createdAt: "desc" }, take: 25 });
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Órdenes", value: String(orders.length), note: "PurchaseOrder reciente." },
          { label: "Abiertas", value: String(orders.filter((row) => ["ordered", "partial"].includes(row.status)).length), note: "ordered + partial." },
          { label: "Líneas", value: String(orders.reduce((acc: number, row) => acc + row.lines.length, 0)), note: "Planeación total." }
        ],
        table: {
          title: "Órdenes recientes",
          columns: ["Folio", "Proveedor", "Estado", "Líneas", "Total", "Esperada"],
          rows: orders.map((row) => ({
            Folio: row.folio,
            Proveedor: row.supplier.name,
            Estado: row.status,
            Líneas: row.lines.length,
            Total: money(row.totalCents),
            Esperada: formatDate(row.expectedAt)
          })),
          emptyMessage: "No hay órdenes de compra consolidadas todavía."
        },
        notes: ["Compras es backoffice; no participa en autorización de venta local Tablet."]
      };
    }

    if (key === "receiving") {
      const receipts: any[] = await prisma.goodsReceipt.findMany({ include: { supplier: true, lines: true }, orderBy: { receivedAt: "desc" }, take: 25 });
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Recepciones", value: String(receipts.length), note: "GoodsReceipt reciente." },
          { label: "Incidencias", value: String(receipts.filter((row) => row.status !== "posted").length), note: "Estado distinto de posted." },
          { label: "Líneas", value: String(receipts.reduce((acc: number, row) => acc + row.lines.length, 0)), note: "Líneas recibidas." }
        ],
        table: {
          title: "Recepciones recientes",
          columns: ["Folio", "Proveedor", "Estado", "Líneas", "Total", "Recibida"],
          rows: receipts.map((row) => ({
            Folio: row.folio,
            Proveedor: row.supplier.name,
            Estado: row.status,
            Líneas: row.lines.length,
            Total: money(row.totalCents),
            Recibida: formatDate(row.receivedAt)
          })),
          emptyMessage: "No hay recepciones consolidadas todavía."
        },
        notes: ["Recepción prepara inventario PC, pero no bloquea ventas ya ejecutadas en Tablet."]
      };
    }

    if (key === "replenishment") {
      const signals: any[] = await prisma.replenishmentSignal.findMany({ include: { product: true }, orderBy: [{ priority: "asc" }, { createdAt: "desc" }], take: 25 });
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Señales", value: String(signals.length), note: "ReplenishmentSignal." },
          { label: "Alta prioridad", value: String(signals.filter((row) => row.priority.toLowerCase().includes("high")).length), note: "priority high." },
          { label: "Sugerido total", value: String(signals.reduce((acc: number, row) => acc + row.suggestedQty, 0)), note: "Unidades sugeridas." }
        ],
        table: {
          title: "Señales de reabasto",
          columns: ["SKU", "Producto", "Ubicación", "Sugerido", "Prioridad", "Fecha"],
          rows: signals.map((row) => ({
            SKU: row.product.sku,
            Producto: row.product.name,
            Ubicación: row.location,
            Sugerido: row.suggestedQty,
            Prioridad: row.priority,
            Fecha: formatDate(row.createdAt)
          })),
          emptyMessage: "No hay señales de reabasto consolidadas todavía."
        },
        notes: ["Reabasto ayuda a gobernar compras; Tablet no depende de PC para cerrar tickets."]
      };
    }

    if (key === "audit") {
      const [counts, events] = await Promise.all([
        prisma.auditCount.findMany({ orderBy: { countedAt: "desc" }, take: 10 }),
        prisma.outboxEvent.findMany({ orderBy: { createdAt: "desc" }, take: 25 })
      ]) as [any[], any[]];
      const catalog = getConflictCatalog();
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Eventos auditables", value: String(events.length), note: "OutboxEvent reciente." },
          { label: "Conteos", value: String(counts.length), note: "AuditCount reciente." },
          { label: "Clasificadores", value: String(catalog.length), note: "Conflictos definidos." }
        ],
        table: {
          title: "Eventos auditables recientes",
          columns: ["Evento", "Topic", "Estado", "Intentos", "Fecha"],
          rows: events.map((row) => ({
            Evento: row.id,
            Topic: row.topic,
            Estado: row.status,
            Intentos: row.attempts,
            Fecha: formatDate(row.createdAt)
          })),
          emptyMessage: "No hay eventos auditables consolidados todavía."
        },
        notes: catalog.slice(0, 5).map((item) => `${item.label}: ${item.severity}`)
      };
    }

    if (key === "sync") {
      const events: any[] = await prisma.outboxEvent.findMany({ orderBy: { createdAt: "desc" }, take: 25 });
      return {
        ...baseOverview(key),
        metrics: [
          { label: "Pendientes", value: String(events.filter((row) => row.status.toLowerCase() === "pending").length), note: "Outbox pending." },
          { label: "Fallidos", value: String(events.filter((row) => row.status.toLowerCase() === "failed").length), note: "Outbox failed." },
          { label: "Conflictos", value: String(events.filter((row) => row.status.toLowerCase() === "conflict").length), note: "Outbox conflict." }
        ],
        table: {
          title: "Eventos de outbox",
          columns: ["Evento", "Topic", "Aggregate", "Estado", "Intentos", "Fecha"],
          rows: events.map((row) => ({
            Evento: row.id,
            Topic: row.topic,
            Aggregate: row.aggregateId,
            Estado: row.status,
            Intentos: row.attempts,
            Fecha: formatDate(row.createdAt)
          })),
          emptyMessage: "No hay eventos de outbox consolidados todavía."
        },
        notes: ["Ingest PC actual: persiste eventos validados en OutboxEvent con idempotencia por eventId."]
      };
    }

    const overview = baseOverview("settings");
    return {
      ...overview,
      metrics: [
        { label: "Modo offline", value: "permitido", note: "Venta local Tablet no depende de PC." },
        { label: "Ingest", value: "explícito", note: "Sin watchers de archivos." },
        { label: "Referencia visual", value: "separada", note: "/prisma-dark-pos-reference no es POS operativo." }
      ],
      table: {
        title: "Políticas activas",
        columns: ["Política", "Estado", "Nota"],
        rows: [
          { Política: "Tablet vende sola", Estado: "obligatoria", Nota: "PC no bloquea venta local." },
          { Política: "Eventos son verdad", Estado: "obligatoria", Nota: "Sync valida y reconcilia." },
          { Política: "Ingest explícito", Estado: "base lista", Nota: "POST API acepta lotes JSON." },
          { Política: "Permisos sensibles offline", Estado: "pendiente de motor", Nota: "No se finge persistencia." }
        ],
        emptyMessage: "No hay políticas configuradas."
      },
      notes: ["Ajustes es marco de gobierno; cambios reales de permisos quedan para etapa posterior."],
      meta: { ...overview.meta, source: "policy_contract", persistence: "not_required" }
    };
  } catch (error) {
    return unavailable(key, error);
  }
}
