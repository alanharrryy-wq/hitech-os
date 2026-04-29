import { FeatureList, LicenseStatusCard } from "@components/license/license-status-card";
import { LicenseRefreshPanel } from "@components/license/license-refresh-panel";
import { getPcFeatureList, getPcLicenseStatus } from "@/server/licensing/pc-license-service";
import { getPcLicenseRefreshStatus } from "@/server/licensing/pc-license-refresh";

export const dynamic = "force-dynamic";

export default async function PcLicensePage() {
  const status = getPcLicenseStatus();
  const refreshStatus = getPcLicenseRefreshStatus();
  const features = getPcFeatureList();
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
