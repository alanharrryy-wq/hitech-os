import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";

export default function Page() {
  const bullets = ['recepciones', 'faltantes', 'sobrantes', 'daños'];
  return (
    <AppShell currentPath="/receiving">
      <section className="hero">
        <div className="kicker">módulo</div>
        <h1 style={{ margin: 0 }}>Recepción</h1>
        <div className="subtle">Recepción física, incidencias y confirmación de líneas.</div>
      </section>
      <SectionCard title="Qué ya viene listo" subtitle="Base modular pensada para seguir creciendo por inyección.">
        <div className="list">
          {bullets.map((item) => <div key={item} className="list-item">{item}</div>)}
        </div>
      </SectionCard>
    </AppShell>
  );
}
