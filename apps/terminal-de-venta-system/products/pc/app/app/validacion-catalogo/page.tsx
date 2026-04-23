import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcI07ValidationData } from "@/lib/i07/validation-data";
import { badgeTone } from "@/lib/i07/validation-helpers";

export default function Page() {
  const totals = pcI07ValidationData.totals;
  return (
    <AppShell currentPath="/validacion-catalogo">
      <section className="hero">
        <div className="kicker">capa i07</div>
        <h1 style={{ margin: 0 }}>Validación de catálogo</h1>
        <div className="subtle">Chequeo duro de integridad crítica y cola de revisión operativa.</div>
      </section>
      <SectionCard title="Semáforo" subtitle={`Estado ${pcI07ValidationData.headline.status}`}>
        <div className="list">
          <div className="list-item"><strong>Incidentes críticos:</strong> {pcI07ValidationData.headline.criticalIncidents} · tono {badgeTone(pcI07ValidationData.headline.criticalIncidents)}</div>
          <div className="list-item"><strong>Cola de revisión:</strong> {pcI07ValidationData.headline.reviewQueue} · tono {badgeTone(pcI07ValidationData.headline.reviewQueue)}</div>
          <div className="list-item"><strong>SKUs activos:</strong> {totals.active_products}</div>
          <div className="list-item"><strong>Stockouts visibles:</strong> {totals.stockout_slots}</div>
        </div>
      </SectionCard>
      <SectionCard title="Integridad crítica" subtitle="Lo que debería romper release si sale rojo.">
        <div className="list">
          <div className="list-item"><strong>Barcodes duplicados:</strong> {totals.duplicate_codes}</div>
          <div className="list-item"><strong>SKUs sin barcode:</strong> {totals.active_without_barcode}</div>
          <div className="list-item"><strong>Precio menor a costo:</strong> {totals.negative_margin}</div>
          <div className="list-item"><strong>Precio cero o negativo:</strong> {totals.zero_or_negative_price}</div>
        </div>
      </SectionCard>
    </AppShell>
  );
}
