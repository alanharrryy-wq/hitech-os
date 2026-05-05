import { i11PageData } from '../../src/lib/i11/page-data';
import { I11Pill } from '../../components/ui/i11-pill';
import { I11Table } from '../../components/ui/i11-table';

export default function AlertasEjecutivasPage() {
  const rows = i11PageData.alertsTop.map((item) => [
    item.severity,
    item.area,
    item.entity,
    item.title,
    item.owner,
    item.action,
  ]);

  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Alertas ejecutivas</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">
          Feed corto y grosero, en el buen sentido: lo que sí merece ojo humano hoy, sin enterrarte en 40 pestañas ni
          convertir el panel en árbol de Navidad.
        </p>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {i11PageData.alertsTop.slice(0, 8).map((item, index) => (
          <article key={`${item.entity}-${index}`} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <I11Pill tone={item.severity === 'critica' ? 'rose' : item.severity === 'alta' ? 'amber' : 'sky'}>{item.severity}</I11Pill>
              <I11Pill>{item.area}</I11Pill>
              <span className="text-xs text-white/45">{item.owner}</span>
            </div>
            <h2 className="mt-3 text-base font-medium text-white">{item.title}</h2>
            <p className="mt-2 text-sm text-white/65">{item.detail}</p>
            <div className="mt-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/75">
              Acción sugerida: {item.action}
            </div>
          </article>
        ))}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Feed tabular</h2>
        <I11Table columns={['Severidad', 'Área', 'Entidad', 'Alerta', 'Dueño', 'Acción']} rows={rows} />
      </section>
    </main>
  );
}
