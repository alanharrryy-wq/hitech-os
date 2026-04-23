import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";

export default function Page() {
  const bullets = ['señales', 'prioridad', 'sugerido', 'ubicación'];
  return (
    <AppShell currentPath="/replenishment">
      <section className="hero">
        <div className="kicker">módulo</div>
        <h1 style={{ margin: 0 }}>Reabasto</h1>
        <div className="subtle">Señales de reabasto y sugerencias de reposición.</div>
      </section>
      <SectionCard title="Qué ya viene listo" subtitle="Base modular pensada para seguir creciendo por inyección.">
        <div className="list">
          {bullets.map((item) => <div key={item} className="list-item">{item}</div>)}
        </div>
      </SectionCard>
    </AppShell>
  );
}
