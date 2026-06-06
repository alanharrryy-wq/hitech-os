import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcLicenseRuntimeControl, type CommandCenterModel } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

const SCREEN_TIMEOUT_MS = 4200;

function timeoutModel(): CommandCenterModel {
  return {
    mode: "licenseRuntime",
    currentPath: "/license-runtime",
    kicker: "licencias y runtime",
    title: "Licencias y Runtime",
    description: "La lectura de runtime tardó demasiado; se muestra una vista segura sin overlay rojo ni datos inventados.",
    sourceLine: "Fuente: modo seguro por timeout de lectura local.",
    independenceLine: "La licencia local de Tablet sigue siendo válida para operación offline.",
    metrics: [
      { label: "Estado PC", value: "pendiente", note: "Timeout de lectura local", tone: "warn" },
      { label: "Refresh remoto", value: "no validado", note: "No se consultó remoto en modo seguro", tone: "warn" },
      { label: "Tablets", value: "n/d", note: "Heartbeat no leído" }
    ],
    panels: [{ title: "Modo seguro", body: "La pantalla respondió rápido para evitar caída de captura o overlay rojo.", tone: "warn" }],
    tables: [],
    diagnostics: { safeMode: true, reason: "license-runtime-timeout", timeoutMs: SCREEN_TIMEOUT_MS },
    actions: [{ label: "Volver al dashboard", href: "/dashboard" }]
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

export default async function LicenseRuntimePage() {
  const model = await withTimeout(getPcLicenseRuntimeControl(), timeoutModel());
  return <PcCommandCenterPage model={model} />;
}
