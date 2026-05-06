import { FeatureList, LicenseStatusCard } from "@components/license/license-status-card";
import { LicenseRefreshPanel } from "@components/license/license-refresh-panel";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { getTabletFeatureList, getTabletLicenseStatus } from "@/server/licensing/tablet-license-service";
import { getTabletLicenseRefreshStatus } from "@/server/licensing/tablet-license-refresh";
import styles from "@components/license/license-ui.module.css";

export const dynamic = "force-dynamic";

function statusTone(state: string) {
  if (state === "active" || state === "development") return "ok" as const;
  if (state === "offline_grace") return "warn" as const;
  return "danger" as const;
}

export default async function TabletLicensePage() {
  const status = getTabletLicenseStatus();
  const refreshStatus = getTabletLicenseRefreshStatus();
  const features = getTabletFeatureList();
  return (
    <PrismaTabletShellUnified
      currentPath="/settings/license"
      title="Licencia"
      subtitle="Estado local de licenciamiento y continuidad operativa de Tablet."
      kicker="Configuracion Tablet"
      status={<TabletShellStatusPill tone={statusTone(status.state)}>{status.state}</TabletShellStatusPill>}
    >
      <main className={styles.pageStack}>
        <LicenseStatusCard status={status} />
        <LicenseRefreshPanel initialStatus={refreshStatus} />
        <FeatureList features={features} />
      </main>
    </PrismaTabletShellUnified>
  );
}
