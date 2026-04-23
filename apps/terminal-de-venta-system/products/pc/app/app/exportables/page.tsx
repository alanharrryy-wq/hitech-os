import { exportCatalog, stockExceptionPreview } from '@/lib/i10/reporting-data';
import { OpsTable } from '@components/ui/ops-table';

const columns = ['SKU', 'Nombre', 'Ubicación', 'Disponible', 'Cobertura', 'Severidad'];

export default function ExportablesPage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Exportables</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">Capa para sacar CSV y JSON sin brincar a scripts sueltos ni a peregrinaciones de carpeta. Aquí vive el catálogo de salidas listas para backoffice.</p>
      </section>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {exportCatalog.map((item) => (
          <article key={item.key} className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-sm font-medium text-white">{item.title}</div>
            <div className="mt-2 flex gap-2 text-xs">
              <span className="rounded-full border border-white/10 px-2 py-1 text-white/70">{item.format}</span>
              <span className="rounded-full border border-white/10 px-2 py-1 text-white/70">{item.cadence}</span>
            </div>
            <p className="mt-3 text-sm text-white/65">{item.note}</p>
          </article>
        ))}
      </section>
      <section className="space-y-3">
        <h2 className="text-lg font-medium text-white">Preview de excepciones exportables</h2>
        <OpsTable columns={columns} rows={stockExceptionPreview} />
      </section>
    </main>
  );
}
