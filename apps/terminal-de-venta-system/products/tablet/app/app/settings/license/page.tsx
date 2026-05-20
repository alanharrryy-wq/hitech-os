import { FeatureList, LicenseStatusCard } from "@components/license/license-status-card";
import { LicenseRefreshPanel } from "@components/license/license-refresh-panel";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
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
    active: "Licencia activa",
    development: "Desarrollo",
    offline_grace: "Gracia offline",
    missing: "Licencia no configurada",
    invalid: "Licencia inválida",
    expired: "Licencia vencida",
    suspended: "Licencia suspendida",
    revoked: "Licencia revocada"
  };
  return labels[state] ?? "Licencia requiere revisión";
}

export default async function TabletLicensePage() {
  const governor = getTabletLicenseGovernor();
  const status = governor.status;
  const refreshStatus = getTabletLicenseRefreshStatus();
  const features = governor.decisions;
  return (
    <PrismaTabletShellUnified
      currentPath="/settings/license"
      title="Licencia"
      subtitle="Estado local de licenciamiento y continuidad operativa de Tablet."
      kicker="Configuracion Tablet"
      status={<TabletShellStatusPill tone={statusTone(status.state)}>{statusLabel(status.state)}</TabletShellStatusPill>}
    >
      <main className={styles.pageStack}>
        <LicenseStatusCard status={status} runtimeContext={governor.runtimeContext} />
        <LicenseRefreshPanel initialStatus={refreshStatus} />
        <FeatureList features={features} />
      </main>
    </PrismaTabletShellUnified>
  );
}
