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
            <p>Consulta el estado de tu plan, la vigencia de esta PC y las funciones disponibles para tu negocio.</p>
          </div>
        </div>
      </section>

      <section className="card" data-prisma-component="LicenseLiveStatus">
        <div className="section-head">
          <div>
            <div className="kicker">estado actual</div>
            <h2 className="section-title">Tu licencia en esta PC</h2>
            <div className="section-copy">La pantalla muestra únicamente lo necesario para operar o resolver una restricción.</div>
          </div>
        </div>
        <div className="grid cols-2">
          <LicenseStatusCard status={status} />
          <LicenseReadinessCard readiness={readiness} />
          <LicenseRefreshPanel initialStatus={refreshStatus} />
        </div>
      </section>

      <section className="card" data-prisma-component="CustomerSetupEntrypoint">
        <div className="section-head">
          <div>
            <div className="kicker">activación</div>
            <h2 className="section-title">Vincular esta PC con tu licencia</h2>
            <div className="section-copy">Usa el código de activación de tu negocio para habilitar este equipo de forma segura.</div>
          </div>
          <a className="btn primary" href="/setup">Activar equipo</a>
        </div>
      </section>

      <section className="card" data-prisma-component="LicenseFeatureList">
        <div className="kicker">funciones disponibles</div>
        <h2 className="section-title">Herramientas incluidas en tu plan</h2>
        <FeatureList features={features} />
      </section>
    </AppShell>
  );
}
