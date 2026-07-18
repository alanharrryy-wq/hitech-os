import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { getPricingPolicySnapshot } from "@/server/services/pricing-policy.service";

export const dynamic = "force-dynamic";

function dateLabel(value: Date | null) {
  if (!value) return "Sin actualización registrada";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(value);
}

function taxLabel(rateBps: number) {
  return new Intl.NumberFormat("es-MX", { style: "percent", maximumFractionDigits: 2 }).format(rateBps / 10_000);
}

export default async function PricingPolicyPage() {
  const snapshot = await getPricingPolicySnapshot();

  return (
    <AppShell currentPath="/politica-precios">
      <section className="hero">
        <div className="kicker">precios e impuestos</div>
        <h1 style={{ margin: 0 }}>Política de precios</h1>
        <div className="subtle">Consulta las listas e impuestos disponibles para el negocio activo.</div>
      </section>

      <SectionCard title="Resumen vigente" subtitle="Lectura actual de productos, listas de precio e impuestos configurados.">
        <div className="list">
          <div className="list-item"><strong>Productos con precio:</strong> {snapshot.productCount}</div>
          <div className="list-item"><strong>Listas disponibles:</strong> {snapshot.priceLists.length}</div>
          <div className="list-item"><strong>Impuestos configurados:</strong> {snapshot.taxRates.length}</div>
          <div className="list-item"><strong>Última actualización de producto:</strong> {dateLabel(snapshot.lastProductPriceUpdate)}</div>
        </div>
      </SectionCard>

      <SectionCard title="Listas de precio" subtitle="Las listas publicadas para este negocio y sus productos asociados.">
        {snapshot.priceLists.length ? (
          <div className="list">
            {snapshot.priceLists.map((list) => (
              <div key={list.id} className="list-item">
                <strong>{list.name}</strong> · {list.itemCount} producto(s) · {list.currency} · {list.isDefault ? "Predeterminada" : "Alterna"} · {list.isActive ? "Activa" : "Inactiva"}
              </div>
            ))}
          </div>
        ) : <p className="subtle">No hay listas de precio registradas para este negocio.</p>}
      </SectionCard>

      <SectionCard title="Impuestos" subtitle="Tasas actualmente disponibles para el catálogo.">
        {snapshot.taxRates.length ? (
          <div className="list">
            {snapshot.taxRates.map((taxRate) => (
              <div key={taxRate.id} className="list-item">
                <strong>{taxRate.name}</strong> · {taxLabel(taxRate.rateBps)} · {taxRate.isDefault ? "Predeterminado" : "Opcional"} · {taxRate.isActive ? "Activo" : "Inactivo"}
              </div>
            ))}
          </div>
        ) : <p className="subtle">No hay impuestos registrados para este negocio.</p>}
      </SectionCard>
    </AppShell>
  );
}
