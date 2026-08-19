import { AppShell } from "@components/layout/app-shell";
import { FeatureList, LicenseReadinessCard, LicenseStatusCard } from "@components/license/license-status-card";
import { LicenseRefreshPanel } from "@components/license/license-refresh-panel";
import { getPcFeatureList, getPcLicenseReadiness, getPcLicenseStatus } from "@/server/licensing/pc-license-service";
import { getPcLicenseRefreshStatus } from "@/server/licensing/pc-license-refresh";

export const dynamic = "force-dynamic";

export default async function PcLicensePage() {
  const status = getPcLicenseStatus();
  const refreshStatus = getPcLicenseRefreshStatus();
  const features = getPcFeatureList();
  const readiness = getPcLicenseReadiness();

  return (
    <AppShell currentPath="/settings/license">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">licencia</div>
            <h1 className="hero-title">Licencia y funciones</h1>
            <p>Estado real de licencia, actualización, setup y capacidades visibles. Sin filtros universales ni resumen ficticio.</p>
          </div>
        </div>
      </section>

      <section className="card" data-prisma-component="LicenseLiveStatus">
        <div className="section-head"><div><div className="kicker">estado conectado</div><h2 className="section-title">Licencia, actualización y funciones visibles.</h2><div className="section-copy">La lectura conserva el estado real antes de tocar permisos o equipos.</div></div></div>
        <div className="grid cols-2">
          <LicenseStatusCard status={status} />
          <LicenseReadinessCard readiness={readiness} />
          <LicenseRefreshPanel initialStatus={refreshStatus} />
        </div>
      </section>

      <section className="card" data-prisma-component="CustomerSetupEntrypoint">
        <div className="section-head">
          <div><div className="kicker">Prisma Customer Setup</div><h2 className="section-title">Reclamar PC Admin Slot con Setup Code.</h2><div className="section-copy">El setup usa Setup Link, Setup Code y Device Claim. No usa admin token ni reemplaza License Admin Bridge.</div></div>
          <a className="btn primary" href="/setup">Abrir setup</a>
        </div>
      </section>

      <section className="card" data-prisma-component="LicenseFeatureList">
        <div className="kicker">funciones disponibles</div>
        <h2 className="section-title">Herramientas activas y restricciones explicadas.</h2>
        <FeatureList features={features} />
      </section>
    </AppShell>
  );
}
