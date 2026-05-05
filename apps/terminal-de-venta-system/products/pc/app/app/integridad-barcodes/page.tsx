import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcI07ValidationData } from "@/lib/i07/validation-data";

export default function Page() {
  return (
    <AppShell currentPath="/integridad-barcodes">
      <section className="hero">
        <div className="kicker">capa i07</div>
        <h1 style={{ margin: 0 }}>Integridad de barcodes</h1>
        <div className="subtle">Chequeo de duplicidad y productos con múltiples códigos.</div>
      </section>
      <SectionCard title="Lectura general" subtitle="Duplicado es incidente crítico; múltiple barcode es cola de revisión.">
        <div className="list">
          <div className="list-item"><strong>Duplicados reales:</strong> {pcI07ValidationData.totals.duplicate_codes}</div>
          <div className="list-item"><strong>Sin barcode:</strong> {pcI07ValidationData.totals.active_without_barcode}</div>
          <div className="list-item"><strong>Con más de un barcode:</strong> {pcI07ValidationData.totals.multi_barcode_products}</div>
        </div>
      </SectionCard>
      <SectionCard title="Muestra de revisión" subtitle="Top de productos con más de un código en el snapshot.">
        <div className="list">
          {pcI07ValidationData.samples.multiBarcodeTop.slice(0, 8).map((item) => (
            <div key={item.sku} className="list-item">{item.sku} · {item.name} · {item.barcode_count} códigos</div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
