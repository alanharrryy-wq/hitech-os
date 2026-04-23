import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { receivingIncidents } from "@/lib/i04/procurement-data";

export default function Page() {
  return (
    <AppShell currentPath="/receiving">
      <section className="hero">
        <div className="kicker">i04 · discrepancias</div>
        <h1 style={{ margin: 0 }}>Incidencias de recepción</h1>
        <div className="subtle">Faltantes, sobrantes y recibos con ruido antes de contaminar inventario.</div>
      </section>
      <SectionCard title="Bitácora breve" subtitle="Overlay aditivo para no tocar el módulo base">
        <div className="list">{receivingIncidents.map((item) => <div key={item.purchaseId} className="list-item">{item.purchaseId} · {item.supplier} · {item.lines} líneas comprometidas</div>)}</div>
      </SectionCard>
    </AppShell>
  );
}
