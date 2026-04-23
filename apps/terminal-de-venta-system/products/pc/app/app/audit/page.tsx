import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";

export default function Page() {
  const bullets = ['ajustes', 'merma', 'conteos', 'bitácora'];
  return (
    <AppShell currentPath="/audit">
      <section className="hero">
        <div className="kicker">módulo</div>
        <h1 style={{ margin: 0 }}>Auditoría</h1>
        <div className="subtle">Ajustes, trazabilidad y revisiones con evidencia.</div>
      </section>
      <SectionCard title="Qué ya viene listo" subtitle="Base modular pensada para seguir creciendo por inyección.">
        <div className="list">
          {bullets.map((item) => <div key={item} className="list-item">{item}</div>)}
        </div>
      </SectionCard>
    </AppShell>
  );
}
