import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { conteosPorUbicacion } from "@/lib/i03/audit-data";

export default function Page() {
  return (
    <AppShell currentPath="/counts">
      <section className="hero">
        <div className="kicker">inyección i03</div>
        <h1 style={{ margin: 0 }}>Conteos operativos</h1>
        <div className="subtle">Visibilidad rápida de conteos abiertos, cerrados y variación por ubicación.</div>
      </section>
      <SectionCard title="Ubicaciones con más fricción" subtitle="Resumen corto para revisar dónde se sigue cargando riesgo operativo.">
        <div className="list">
          {conteosPorUbicacion.map((row) => (
            <div key={row.location} className="list-item">
              <strong>{row.location}</strong> · abiertos {row.abiertos} · cerrados {row.cerrados} · var abs prom {row.variacionAbsProm}
            </div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
