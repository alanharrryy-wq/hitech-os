import { executiveCards, categoryHighlights, stockExceptionPreview, syncSlaPreview } from '@/lib/i10/reporting-data';
import { OpsTable } from '@components/ui/ops-table';

export default function VistasEjecutivasPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Vistas ejecutivas detalladas</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">Resumen para dirección y supervisión con tres lentes: margen, excepciones de stock y salud de sincronización.</p>
      </section>
      <section className="grid gap-3 md:grid-cols-4">
        {executiveCards.map((item) => (
          <div key={item.title} className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs uppercase tracking-wide text-white/50">{item.title}</div>
            <div className="mt-2 text-lg font-semibold text-white">{item.value}</div>
            <div className="mt-1 text-xs text-white/65">{item.note}</div>
          </div>
        ))}
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Top margen por categoría</h2>
        <OpsTable columns={['Categoría', 'Productos', 'Margen prom.', 'Margen %']} rows={categoryHighlights} />
      </section>
      <section className="grid gap-6 xl:grid-cols-2">
        <div className="space-y-3">
          <h2 className="text-lg font-medium text-white">Excepciones de stock</h2>
          <OpsTable columns={['SKU', 'Nombre', 'Ubicación', 'Disponible', 'Cobertura', 'Severidad']} rows={stockExceptionPreview} />
        </div>
        <div className="space-y-3">
          <h2 className="text-lg font-medium text-white">SLA de sincronización</h2>
          <OpsTable columns={['Topic', 'Eventos', 'Pendiente', 'Fallo', 'Enviado', 'Latencia prom.']} rows={syncSlaPreview} />
        </div>
      </section>
    </main>
  );
}
