import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { procurementStats, purchasePulse, supplierHeat } from "@/lib/i04/procurement-data";

export default function Page() {
  return (
    <AppShell currentPath="/purchasing">
      <section className="hero">
        <div className="kicker">i04 · compras</div>
        <h1 style={{ margin: 0 }}>Órdenes de compra</h1>
        <div className="subtle">Seguimiento operativo de órdenes abiertas, presión por proveedor y foco de abastecimiento.</div>
      </section>
      <section style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <StatCard label="Órdenes abiertas" value={String(procurementStats.ordenesAbiertas)} note="ordered + partial" />
        <StatCard label="Proveedores activos" value={String(procurementStats.proveedoresActivos)} note="con órdenes en la base demo" />
        <StatCard label="Top proveedor" value={procurementStats.topProveedor} note="mayor volumen detectado" />
      </section>
      <SectionCard title="Pulso inmediato" subtitle="Órdenes con ventana de atención administrativa">
        <div className="list">{purchasePulse.map((item) => <div key={item.folio} className="list-item">{item.folio} · {item.supplier} · {item.status} · ETA {item.eta_days} días</div>)}</div>
      </SectionCard>
      <SectionCard title="Presión por proveedor" subtitle="Lectura rápida para compras y seguimiento">
        <div className="list">{supplierHeat.map((item) => <div key={item.supplier} className="list-item">{item.supplier}: {item.total_orders} órdenes · parciales {item.partial_count} · recibidas {item.received_count}</div>)}</div>
      </SectionCard>
    </AppShell>
  );
}
