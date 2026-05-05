import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { Badge } from "@components/ui/badge";
import { i01GovernanceData } from "@/lib/i01/governance-data";

export default function GobiernoPage() {
  return (
    <AppShell currentPath="/gobierno">
      <section className="hero">
        <div className="kicker">i01</div>
        <h1 style={{ margin: 0 }}>Gobierno base de PC</h1>
        <div className="subtle">Primera capa acumulativa para ordenar el frente administrativo sin romper el contrato gemelo.</div>
      </section>

      <div className="grid cols-2">
        <SectionCard title="Principios" subtitle="Reglas madres para seguir creciendo por iteraciones.">
          <div className="list">
            {i01GovernanceData.principles.map((item) => (
              <div key={item} className="list-item">{item}</div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Superficies compartidas" subtitle="Cuando algo toque esto, el cambio deja de ser local.">
          <div className="list">
            {i01GovernanceData.sharedSurfaces.map((item) => (
              <div key={item} className="list-item">{item}</div>
            ))}
          </div>
        </SectionCard>
      </div>

      <div className="grid cols-2">
        <SectionCard title="Zonas locales de PC" subtitle="Territorio donde la app puede especializarse como backoffice.">
          <div className="list">
            {i01GovernanceData.localPcSurfaces.map((item) => (
              <div key={item} className="list-item" style={{ display: "flex", justifyContent: "space-between" }}>
                <span>{item}</span>
                <Badge tone="ok">local</Badge>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Parentesco" subtitle="Identidad visible congelada para esta ola.">
          <div className="list">
            <div className="list-item">Producto activo: {i01GovernanceData.product}</div>
            <div className="list-item">Gemela contractual: {i01GovernanceData.twin}</div>
            <div className="list-item">Idioma visible preferido: es-MX</div>
            <div className="list-item">Modo de crecimiento: append-only</div>
          </div>
        </SectionCard>
      </div>
    </AppShell>
  );
}
