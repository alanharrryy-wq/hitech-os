import { dateFilterGroups } from '@/lib/i09/detail-data';
import { FilterChip } from '@components/ui/filter-chip';

export default function FiltrosFechaPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Filtros por fecha</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Presets por día, semana y mes para recortar ruido. El calendario aquí no es adorno, es machete.
        </p>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {dateFilterGroups.map((group) => (
          <div key={group.title} className="rounded-xl border border-white/10 bg-black/20 p-4">
            <h2 className="text-sm font-semibold text-white">{group.title}</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {group.values.map((value) => <FilterChip key={value} label={value} />)}
            </div>
            <p className="mt-3 text-xs text-white/60">{group.note}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
