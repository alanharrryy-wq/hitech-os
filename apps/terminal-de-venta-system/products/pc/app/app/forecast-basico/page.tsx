import { i11PageData } from '../../src/lib/i11/page-data';
import { I11SummaryGrid } from '../../components/ui/i11-summary-grid';
import { I11Table } from '../../components/ui/i11-table';
import { I11Pill } from '../../components/ui/i11-pill';

export default function ForecastBasicoPage() {
  const rows = i11PageData.forecastTop.map((item) => [
    item.sku,
    item.name,
    item.category,
    item.forecast7d,
    item.forecast14d,
    item.availableProxy,
    item.suggestedBuyQty,
    item.risk,
  ]);

  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Forecast básico</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Esta vista junta demanda proxy, cobertura y compra sugerida para que el backoffice vea por dónde viene el golpe
          antes de que llegue con trompeta y quiebre el anaquel.
        </p>
      </section>

      <I11SummaryGrid items={i11PageData.summaryCards} />

      <section className="grid gap-4 lg:grid-cols-3">
        {i11PageData.forecastTop.slice(0, 6).map((item) => (
          <article key={item.sku} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-medium text-white">{item.sku}</div>
                <div className="mt-1 text-sm text-white/65">{item.name}</div>
              </div>
              <I11Pill tone={item.risk === 'critico' ? 'rose' : item.risk === 'alto' ? 'amber' : 'sky'}>{item.risk}</I11Pill>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm text-white/75">
              <div><dt className="text-white/45">Forecast 14d</dt><dd>{item.forecast14d} uds</dd></div>
              <div><dt className="text-white/45">Compra sugerida</dt><dd>{item.suggestedBuyQty} uds</dd></div>
              <div><dt className="text-white/45">Disponible</dt><dd>{item.availableProxy}</dd></div>
              <div><dt className="text-white/45">Cobertura</dt><dd>{item.daysCover} días</dd></div>
            </dl>
          </article>
        ))}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Top forecast con compra sugerida</h2>
        <I11Table
          columns={['SKU', 'Nombre', 'Categoría', 'Forecast 7d', 'Forecast 14d', 'Disponible', 'Compra', 'Riesgo']}
          rows={rows}
        />
      </section>
    </main>
  );
}
