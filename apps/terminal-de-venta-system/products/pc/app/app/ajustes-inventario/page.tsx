import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { ajustesResumen, projectIterationIndex } from "@/lib/i03/project-index";

export default function Page() {
  return (
    <AppShell currentPath="/audit">
      <section className="hero">
        <div className="kicker">inyección i03</div>
        <h1 style={{ margin: 0 }}>Ajustes de inventario</h1>
        <div className="subtle">Bitácora resumida por ubicación y categoría, más memoria externa del proyecto.</div>
      </section>
      <SectionCard title="Ajustes más repetidos" subtitle="Este resumen viene de movimientos de tipo adjustment en la base demo.">
        <div className="list">
          {ajustesResumen.map((row) => (
            <div key={`${row.location}-${row.category}`} className="list-item">
              <strong>{row.location}</strong> · {row.category} · eventos {row.eventos} · unidades {row.unidades}
            </div>
          ))}
        </div>
      </SectionCard>
      <SectionCard title="Memoria acumulativa" subtitle="Rastro corto de iteraciones aplicadas al proyecto.">
        <div className="list">
          {projectIterationIndex.map((row) => (
            <div key={row.id} className="list-item">
              <strong>{row.id}</strong> · {row.scope}
            </div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
