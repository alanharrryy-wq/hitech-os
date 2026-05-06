import { PrismaOperationalScreen } from "@components/operational-screen";
import { moneyMXN, numberMX, operationalStatus } from "@components/operational-screen";

export default function ScreenStandardPreviewPage() {
  return (
    <PrismaOperationalScreen
      model={{
        currentPath: "/screen-standard-preview",
        title: "Estandar operativo Tablet",
        subtitle: "Patron visual y funcional para Stock, Ventas, Sync, Turno y Devoluciones.",
        kicker: "PRISMA screen standard 01A",
        status: operationalStatus("listo para inyecciones", "ok"),
        density: "executive",
        actions: [
          { label: "Ver Stock", href: "/stock", description: "Primera pantalla recomendada", tone: "ok" },
          { label: "Ver ventas", href: "/sales", description: "Segunda pantalla recomendada", tone: "neutral" }
        ],
        hero: {
          eyebrow: "motor visual unificado",
          title: "Una sola gramatica premium para todas las pantallas operativas.",
          description: "El estandar obliga jerarquia, metricas, estados, secciones y acciones consistentes. Nada de pantallas con estilo de volante fotocopiado atras del mostrador.",
          signal: operationalStatus("homologado", "ok")
        },
        metrics: [
          { label: "Pantallas objetivo", value: numberMX(5), note: "stock, sales, sync, shift, returns", tone: "ok", emphasis: "primary" },
          { label: "DB nueva", value: "0", note: "usa servicios y Prisma existentes", tone: "ok" },
          { label: "Placeholders", value: "bloqueados", note: "el motor rechaza copy provisional", tone: "warn" },
          { label: "Rollback", value: "por pantalla", note: "inyecciones pequeñas y reversibles", tone: "ok" }
        ],
        sections: [
          {
            id: "pantallas",
            title: "Orden de conversion recomendado",
            subtitle: "Cada pantalla debe conectar servicio, pintar modelo y pasar verificacion visual.",
            kind: "table",
            table: {
              columns: [
                { key: "route", label: "Ruta" },
                { key: "service", label: "Servicio" },
                { key: "risk", label: "Riesgo" },
                { key: "goal", label: "Salida" }
              ],
              rows: [
                { id: "stock", route: "/stock", service: "stock.ts", risk: "bajo", goal: "existencias y movimientos", tone: "ok" },
                { id: "sales", route: "/sales", service: "sales.ts", risk: "bajo", goal: "tickets y ventas", tone: "ok" },
                { id: "sync", route: "/sync", service: "sync.ts", risk: "medio", goal: "outbox y eventos", tone: "warn" },
                { id: "shift", route: "/shift", service: "shift.ts", risk: "medio", goal: "turno y caja", tone: "warn" },
                { id: "returns", route: "/returns", service: "returns.ts", risk: "medio", goal: "devoluciones trazables", tone: "warn" }
              ]
            }
          },
          {
            id: "guardrails",
            title: "Guardrails de pantalla",
            subtitle: "Reglas para que esto no sea chile, mole y pozole con backdrop-filter.",
            kind: "alerts",
            items: [
              { title: "Una pantalla, un servicio", description: "page.tsx no debe traer queries improvisadas. Consume un view model claro.", value: "obligatorio", tone: "ok" },
              { title: "Cero estilos locales", description: "Nada de style={{ padding: 24 }} para simular layout premium.", value: "bloqueado", tone: "danger" },
              { title: "Estados visibles", description: "ready, empty, error, offline y sync_pending cuando aplique.", value: "QA", tone: "warn" },
              { title: "DB existente", description: `La pantalla debe usar la base local Tablet y servicios actuales; ${moneyMXN(0)} en DBs nuevas.`, value: "canon", tone: "ok" }
            ]
          }
        ]
      }}
    />
  );
}
