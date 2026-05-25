import { DecisionScreen } from "@components/uiux/decision-screen";
import { FeatureList, LicenseStatusCard } from "@components/license/license-status-card";
import { LicenseRefreshPanel } from "@components/license/license-refresh-panel";
import { settingsLicenseScreenContract } from "@/uiux/settings-screen-contract";
import { getPcFeatureList, getPcLicenseStatus } from "@/server/licensing/pc-license-service";
import { getPcLicenseRefreshStatus } from "@/server/licensing/pc-license-refresh";

export const dynamic = "force-dynamic";

export default async function PcLicensePage() {
  const status = getPcLicenseStatus();
  const refreshStatus = getPcLicenseRefreshStatus();
  const features = getPcFeatureList();

  return (
    <DecisionScreen {...settingsLicenseScreenContract} currentPath="/settings">
      <section className="card" data-prisma-component="LicenseLiveStatus">
        <div className="section-head">
          <div>
            <div className="kicker">estado conectado</div>
            <h2 className="section-title">Licencia, actualización y funciones visibles.</h2>
            <div className="section-copy">
              Esta sección conserva la lectura real de licencia y la presenta como decisión segura antes de tocar permisos o equipos.
            </div>
          </div>
        </div>
        <div className="grid cols-2">
          <LicenseStatusCard status={status} />
          <LicenseRefreshPanel initialStatus={refreshStatus} />
        </div>
      </section>

      <section className="card" data-prisma-component="LicenseFeatureList">
        <div className="kicker">funciones disponibles</div>
        <h2 className="section-title">Herramientas activas y restricciones explicadas.</h2>
        <FeatureList features={features} />
      </section>
    </DecisionScreen>
  );
}
