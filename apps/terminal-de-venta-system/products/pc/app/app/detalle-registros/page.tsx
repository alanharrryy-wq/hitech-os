import { detailSummary, movementPreview, receiptPreview, outboxPreview } from '@/lib/i09/detail-data';
import { OpsTable } from '@components/ui/ops-table';

export default function DetalleRegistrosPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Detalle de registros</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Vista de detalle para movimientos, recepciones y outbox. Menos niebla administrativa, más trazabilidad con placa y apellido.
        </p>
      </section>
      <section className="grid gap-3 md:grid-cols-4">
        {detailSummary.map((item) => (
          <div key={item.title} className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs uppercase tracking-wide text-white/50">{item.title}</div>
            <div className="mt-2 text-lg font-semibold text-white">{item.value}</div>
            <div className="mt-1 text-xs text-white/65">{item.note}</div>
          </div>
        ))}
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Movimientos recientes</h2>
        <OpsTable columns={['SKU', 'Producto', 'Tipo', 'Qty', 'Razón', 'Ubicación', 'Fecha']} rows={movementPreview} />
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Recepciones</h2>
        <OpsTable columns={['Folio', 'Proveedor', 'Estado', 'Líneas', 'Lead', 'Recibido']} rows={receiptPreview} />
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Outbox</h2>
        <OpsTable columns={['Topic', 'Aggregate', 'Estado', 'Edad min', 'Creado', 'Enviado']} rows={outboxPreview} />
      </section>
    </main>
  );
}
