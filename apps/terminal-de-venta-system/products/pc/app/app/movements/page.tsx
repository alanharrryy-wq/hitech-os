import { ModuleOverviewPage } from "@components/backoffice/module-overview-page";
import { getBackofficeModuleOverview, type BackofficeModuleOverview } from "@/lib/backoffice/overview";

export const dynamic = "force-dynamic";

const SCREEN_TIMEOUT_MS = 4200;

function fallbackOverview(): BackofficeModuleOverview {
  return {
    key: "movements",
    route: "/movements",
    eyebrow: "movimientos",
    title: "Movimientos de inventario",
    description: "La lectura de movimientos tardó demasiado; esta vista queda en estado vacío honesto para evitar overlay rojo.",
    metrics: [
      { label: "Movimientos", value: "pendiente", note: "Lectura local no disponible a tiempo." },
      { label: "Salidas", value: "n/d", note: "Sin datos inventados." },
      { label: "Entradas/ajustes", value: "n/d", note: "Sin datos inventados." }
    ],
    table: { title: "Movimientos recientes", columns: [], rows: [], emptyMessage: "No se pudo leer la persistencia canónica dentro del presupuesto de tiempo." },
    notes: ["La pantalla responde en modo seguro si Prisma tarda o la base local está ocupada.", "Tablet conserva su operación local; PC no bloquea venta."],
    meta: { source: "canonical_prisma", persistence: "unavailable", generatedAt: new Date().toISOString(), warnings: ["Lectura protegida por timeout para evitar error rojo en captura."] }
  };
}

async function withTimeout<T>(promise: Promise<T>, fallback: T, timeoutMs = SCREEN_TIMEOUT_MS): Promise<T> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      promise,
      new Promise<T>((resolve) => { timer = setTimeout(() => resolve(fallback), timeoutMs); })
    ]);
  } catch {
    return fallback;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

export default async function MovementsPage() {
  const overview = await withTimeout(getBackofficeModuleOverview("movements"), fallbackOverview());
  return <ModuleOverviewPage overview={overview} />;
}
