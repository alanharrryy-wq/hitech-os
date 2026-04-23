import { bulkActions } from '@/lib/i09/detail-data';
import { BulkActionCard } from '@components/ui/bulk-action-card';

export default function AccionesMasivasPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Acciones masivas controladas</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Aquí no hay botón nuclear. Solo propuestas auditables para reintentar, revisar y empujar colas de trabajo con barandales.
        </p>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {bulkActions.map((item) => <BulkActionCard key={item.key} item={item} />)}
      </section>
      <section className="rounded-xl border border-cyan-400/30 bg-cyan-500/10 p-4 text-sm text-cyan-50">
        Política: toda acción masiva debe pasar por previsualización, límite de lote y trazabilidad. Nada de “seleccionar todo y que Dios reparta suerte”.
      </section>
    </main>
  );
}
