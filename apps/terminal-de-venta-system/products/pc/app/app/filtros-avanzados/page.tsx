import { filterPresets } from '@/lib/i08/ux-data';
import { FilterChip } from '@components/ui/filter-chip';

const groups = [
  ['Categoría', filterPresets.categoria],
  ['Ubicación', filterPresets.ubicacion],
  ['Semáforo', filterPresets.semaforo],
  ['Fecha', filterPresets.fecha],
  ['Compra', filterPresets.estatusCompra],
] as const;

export default function FiltrosAvanzadosPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Filtros avanzados</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Presets para persistir filtros por módulo y evitar que la operación tenga que picar veinte veces lo mismo.
        </p>
      </section>
      <section className="grid gap-4 md:grid-cols-2">
        {groups.map(([title, values]) => (
          <div key={title} className="rounded-xl border border-white/10 bg-black/20 p-4">
            <h2 className="text-sm font-semibold text-white">{title}</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {values.map((value) => <FilterChip key={value} label={value} />)}
            </div>
          </div>
        ))}
      </section>
    </main>
  );
}
