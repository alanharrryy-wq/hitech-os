import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcMessages } from "@/lib/i18n/messages/es";

export default function Page() {
  const page = pcMessages.pages.sync;
  return (
    <AppShell currentPath="/sync">
      <section className="hero">
        <div className="kicker">módulo</div>
        <h1 style={{ margin: 0 }}>{page.title}</h1>
        <div className="subtle">{page.subtitle}</div>
      </section>
      <SectionCard title="Qué ya viene listo" subtitle="Base modular pensada para seguir creciendo por inyección.">
        <div className="list">
          {page.bullets.map((item) => <div key={item} className="list-item">{item}</div>)}
        </div>
      </SectionCard>
    </AppShell>
  );
}
