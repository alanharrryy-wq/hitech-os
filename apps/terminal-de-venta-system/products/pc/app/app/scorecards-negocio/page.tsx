import { i11PageData } from '../../src/lib/i11/page-data';
import { I11Pill } from '../../components/ui/i11-pill';
import { I11Table } from '../../components/ui/i11-table';

export default function ScorecardsNegocioPage() {
  const supplierRows = i11PageData.supplierScorecards.map((item) => [
    item.supplier,
    item.servicePct,
    item.partialPct,
    item.incidentReceiptPct,
    item.pendingQty,
    item.healthBand,
  ]);

  const categoryRows = i11PageData.categoryScorecards.map((item) => [
    item.category,
    item.suggestedBuyQty,
    item.stockoutNow,
    item.stalePriceSkus,
    item.avgMarginPct,
    item.healthBand,
  ]);

  return (
    <main className="space-y-8">
      <section>
        <h1 className="text-2xl font-semibold text-white">Scorecards de negocio</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Lectura rápida para comprar y corregir sin hacer arqueología administrativa. Aquí viven proveedores y categorías con
          su semáforo, su porcentaje y su jalón de oreja.
        </p>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {i11PageData.supplierScorecards.slice(0, 5).map((item) => (
          <article key={item.supplier} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-base font-medium text-white">{item.supplier}</h2>
              <I11Pill tone={item.healthBand === 'rojo' ? 'rose' : item.healthBand === 'ambar' ? 'amber' : 'sky'}>{item.healthBand}</I11Pill>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm text-white/75">
              <div><dt className="text-white/45">Servicio</dt><dd>{item.servicePct}%</dd></div>
              <div><dt className="text-white/45">Parciales</dt><dd>{item.partialPct}%</dd></div>
              <div><dt className="text-white/45">Incidentes</dt><dd>{item.incidentReceiptPct}%</dd></div>
              <div><dt className="text-white/45">Pendiente</dt><dd>{item.pendingQty}</dd></div>
            </dl>
          </article>
        ))}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Proveedor</h2>
        <I11Table
          columns={['Proveedor', 'Servicio %', 'Parcial %', 'Incidente %', 'Pendiente', 'Banda']}
          rows={supplierRows}
        />
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Categoría</h2>
        <I11Table
          columns={['Categoría', 'Compra sugerida', 'Stockout', 'Precio viejo', 'Margen %', 'Banda']}
          rows={categoryRows}
        />
      </section>
    </main>
  );
}
