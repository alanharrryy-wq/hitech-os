import { queueHighlights, stockColumns, purchaseColumns } from '@/lib/i08/ux-data';
import { OpsTable } from '@components/ui/ops-table';

const stockRows = [
  ['SKU-00000', 'Bebidas producto 0', 'Bebidas', 'A-01', '0', '0.0 días', 'quiebre'],
  ['SKU-00015', 'Snacks producto 15', 'Snacks', 'B-02', '2', '0.8 días', 'critico'],
  ['SKU-00041', 'Abarrotes producto 41', 'Abarrotes', 'C-01', '5', '1.3 días', 'bajo'],
];
const purchaseRows = [
  ['PO-1900', 'Bebidas del Centro', 'ordered', '2026-04-01', '2026-04-02', '1 día'],
  ['PO-1901', 'Snacks MX', 'partial', '2026-04-01', '2026-04-03', '2 días'],
  ['PO-1902', 'Limpieza Total', 'received', '2026-04-01', '2026-04-04', '3 días'],
];

export default function TablasOperativasPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Tablas operativas</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Capa UX para backoffice con tablas orientadas a cola de trabajo, columnas cortas y semáforo visible.
        </p>
      </section>
      <section className="grid gap-3 md:grid-cols-5">
        {queueHighlights.map((item) => (
          <div key={item.title} className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs uppercase tracking-wide text-white/50">{item.title}</div>
            <div className="mt-2 text-lg font-semibold text-white">{item.value}</div>
            <div className="mt-1 text-xs text-white/65">{item.note}</div>
          </div>
        ))}
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Stock crítico</h2>
        <OpsTable columns={[...stockColumns]} rows={stockRows} />
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Compras en cola</h2>
        <OpsTable columns={[...purchaseColumns]} rows={purchaseRows} />
      </section>
    </main>
  );
}
