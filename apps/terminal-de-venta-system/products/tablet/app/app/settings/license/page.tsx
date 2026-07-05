import { FeatureList, LicenseStatusCard } from "@components/license/license-status-card";
import { LicenseRefreshPanel } from "@components/license/license-refresh-panel";
import { QuickActionGrid, QuickActionTile } from "@components/tablet-action-tiles/tablet-action-tiles";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletSettingsSurfaceV2 } from "@components/tablet-visual-v2";
import { getTabletLicenseGovernor } from "@/server/licensing/tablet-license-service";
import { getTabletLicenseRefreshStatus } from "@/server/licensing/tablet-license-refresh";
import styles from "@components/license/license-ui.module.css";

export const dynamic = "force-dynamic";

function statusTone(state: string) {
  if (state === "active" || state === "development") return "ok" as const;
  if (state === "offline_grace") return "warn" as const;
  return "danger" as const;
}

function statusLabel(state: string) {
  const labels: Record<string, string> = {
    active: "Lista para operar",
    development: "Lista para operar",
    offline_grace: "Operando offline",
    missing: "Licencia pendiente",
    invalid: "Licencia inválida",
    expired: "Licencia vencida",
    suspended: "Licencia suspendida",
    revoked: "Licencia revocada"
  };
  return labels[state] ?? "Requiere revisión";
}

export default async function TabletLicensePage() {
  const governor = getTabletLicenseGovernor();
  const status = governor.status;
  const refreshStatus = getTabletLicenseRefreshStatus();
  const features = governor.decisions;

  return (
    <PrismaTabletShellUnified
      currentPath="/settings/license"
      title="Licencia y equipo"
      subtitle="Estado visible de autorización y continuidad de esta Tablet."
      kicker="Configuración Tablet"
      status={<TabletShellStatusPill tone={statusTone(status.state)}>{statusLabel(status.state)}</TabletShellStatusPill>}
    >
      <TabletSettingsSurfaceV2 routeId="/settings/license" title="Licencia y equipo" description="Autorización visible, continuidad de operación y capacidades disponibles en esta Tablet." statusLabel={statusLabel(status.state)}>
        <main className={styles.pageStack} data-prisma-license-client-view="readonly">
          <QuickActionGrid label="Acciones rapidas de licencia" density="wide">
            <QuickActionTile title="Importar licencia" description="La importación no se ejecuta desde la vista cliente." icon="save" tone="neutral" deferredReason="Pendiente: activación e importación pertenecen al flujo administrativo." owner="license" kind="deferred-create" />
            <QuickActionTile title="Prisma Customer Setup" description="Abrir Setup Link o Setup Code para reclamar Tablet POS Slot." actionLabel="Setup" icon="settings" tone="license" href="/setup" owner="license" />
            <QuickActionTile title="Contactar soporte" description="Abre el detalle visible para compartir estado de equipo." actionLabel="Soporte" icon="users" tone="license" href="#license-support" owner="license" />
            <QuickActionTile title="Exportar respaldo" description="Revisa respaldo offline y archivos locales." actionLabel="Respaldo" icon="save" tone="sync" href="/offline" owner="offline" />
            <QuickActionTile title="Detalles para soporte" description="Estado, asignación, vigencia y origen de licencia." actionLabel="Ver detalle" icon="settings" tone="jewel" href="#license-support" owner="license" />
          </QuickActionGrid>
          <LicenseStatusCard status={status} runtimeContext={governor.runtimeContext} />
          <LicenseRefreshPanel initialStatus={refreshStatus} />
          <FeatureList features={features} />
        </main>
      </TabletSettingsSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
