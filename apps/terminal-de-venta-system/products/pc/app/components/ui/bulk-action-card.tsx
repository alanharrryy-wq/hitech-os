type BulkAction = { key: string; title: string; candidates: number; mode: string; note: string };

export function BulkActionCard({ item }: { item: BulkAction }) {
  return (
    <article className="rounded-xl border border-white/10 bg-black/20 p-4">
      <div className="text-xs uppercase tracking-wide text-white/50">{item.key}</div>
      <h2 className="mt-2 text-lg font-semibold text-white">{item.title}</h2>
      <div className="mt-3 text-2xl font-bold text-cyan-300">{item.candidates}</div>
      <div className="mt-1 text-xs text-white/60">candidatos</div>
      <div className="mt-3 rounded-lg border border-cyan-400/20 bg-cyan-500/10 px-3 py-2 text-xs text-cyan-50">{item.mode}</div>
      <p className="mt-3 text-sm text-white/70">{item.note}</p>
    </article>
  );
}
