import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { varianzaPorUsuario } from "@/lib/i03/audit-data";

export default function Page() {
  return (
    <AppShell currentPath="/audit">
      <section className="hero">
        <div className="kicker">inyección i03</div>
        <h1 style={{ margin: 0 }}>Auditoría de inventario</h1>
        <div className="subtle">Quién concentra más conteos sensibles y dónde conviene revisar primero.</div>
      </section>
      <SectionCard title="Varianza por usuario" subtitle="Corte resumido de conteos sensibles y promedio de desviación absoluta.">
        <div className="list">
          {varianzaPorUsuario.map((row) => (
            <div key={row.countedBy} className="list-item">
              <strong>{row.countedBy}</strong> · sensibles {row.conteosSensibles} · abiertos {row.abiertos} · var abs prom {row.variacionAbsProm}
            </div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
