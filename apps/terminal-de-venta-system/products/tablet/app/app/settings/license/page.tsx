import { FeatureList, LicenseStatusCard } from "@components/license/license-status-card";
import { LicenseRefreshPanel } from "@components/license/license-refresh-panel";
import { getTabletFeatureList, getTabletLicenseStatus } from "@/server/licensing/tablet-license-service";
import { getTabletLicenseRefreshStatus } from "@/server/licensing/tablet-license-refresh";

export const dynamic = "force-dynamic";

export default async function TabletLicensePage() {
  const status = getTabletLicenseStatus();
  const refreshStatus = getTabletLicenseRefreshStatus();
  const features = getTabletFeatureList();
  return (
    <main style={{ minHeight: "100vh", padding: 24, background: "#090a0c" }}>
      <div style={{ maxWidth: 1120, margin: "0 auto", display: "grid", gap: 18 }}>
        <LicenseStatusCard status={status} />
        <LicenseRefreshPanel initialStatus={refreshStatus} />
        <FeatureList features={features} />
      </div>
    </main>
  );
}
