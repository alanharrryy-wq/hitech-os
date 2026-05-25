import { AppShell } from "@components/layout/app-shell";
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
    <AppShell currentPath="/settings">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">configuración</div>
            <h1 className="hero-title">Licencia y continuidad operativa</h1>
            <p>Estado local de licencia, actualización remota y funciones permitidas para el Panel administrativo de inventario.</p>
          </div>
        </div>
      </section>
      <div className="grid cols-2">
        <LicenseStatusCard status={status} />
        <LicenseRefreshPanel initialStatus={refreshStatus} />
      </div>
      <div className="grid">
        <FeatureList features={features} />
      </div>
    </AppShell>
  );
}
