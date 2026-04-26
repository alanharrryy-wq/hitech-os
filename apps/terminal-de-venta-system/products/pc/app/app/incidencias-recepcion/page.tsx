import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { getProcurementConsole } from "@/lib/services/procurement";

export const dynamic = "force-dynamic";

export default async function Page() {
  const { receivingIncidents } = await getProcurementConsole();

  return (
    <AppShell currentPath="/receiving">
      <section className="hero">
        <div className="kicker">i04 · discrepancias</div>
        <h1 style={{ margin: 0 }}>Incidencias de recepción</h1>
        <div className="subtle">Faltantes, sobrantes y recibos con ruido antes de contaminar inventario.</div>
      </section>
      <SectionCard title="Bitácora breve" subtitle="Overlay aditivo para no tocar el módulo base">
        <div className="list">{receivingIncidents.map((item) => <div key={item.folio} className="list-item">{item.folio} · {item.supplier} · {item.lines} líneas comprometidas</div>)}</div>
      </SectionCard>
    </AppShell>
  );
}
