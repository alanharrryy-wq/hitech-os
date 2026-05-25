import { stateCards } from '@/lib/i08/ux-data';
import { DataStateCard } from '@components/ui/data-state-card';

export default function EstadosOperativosPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Estados operativos</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Estados estándar para carga, vacío, error, datos envejecidos y sync caído. Menos drama, más contexto.
        </p>
      </section>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {stateCards.map((item) => <DataStateCard key={item.key} title={item.title} note={item.note} />)}
      </section>
      <section className="rounded-xl border border-amber-400/30 bg-amber-500/10 p-4 text-sm text-amber-50">
        Regla base: si no hay resultados, muestra filtros activos y una salida clara. Nada de pantallas vacías estilo desierto existencial.
      </section>
    </main>
  );
}
