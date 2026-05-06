import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcI07ValidationData } from "@/lib/i07/validation-data";

export default function Page() {
  return (
    <AppShell currentPath="/politica-precios">
      <section className="hero">
        <div className="kicker">capa i07</div>
        <h1 style={{ margin: 0 }}>Política de precios</h1>
        <div className="subtle">Vigilancia de antigüedad y presión comercial para actualización de precios.</div>
      </section>
      <SectionCard title="Regla vigente" subtitle="Política operativa para esta iteración.">
        <div className="list">
          <div className="list-item"><strong>Precio desactualizado:</strong> mayor a {pcI07ValidationData.policy.priceStaleDays} días desde <code>updatedAt</code>.</div>
          <div className="list-item"><strong>Stale &gt; 14 días:</strong> {pcI07ValidationData.totals.stale_prices_14d}</div>
          <div className="list-item"><strong>Stale &gt; 7 días:</strong> {pcI07ValidationData.totals.stale_prices_7d}</div>
        </div>
      </SectionCard>
      <SectionCard title="Presión comercial" subtitle="Muestra de SKUs viejos con movimiento de venta proxy.">
        <div className="list">
          {pcI07ValidationData.samples.salePressureTop.slice(0, 8).map((item) => (
            <div key={item.sku} className="list-item">{item.sku} · {item.name} · {item.priceAgeDays} días · {item.unitsSold} uds</div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
