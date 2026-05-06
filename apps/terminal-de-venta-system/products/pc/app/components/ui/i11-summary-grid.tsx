type SummaryCard = {
  label: string;
  value: string;
  tone: 'sky' | 'amber' | 'rose' | 'violet';
};

const classes: Record<SummaryCard['tone'], string> = {
  sky: 'from-sky-500/20 to-sky-900/10',
  amber: 'from-amber-500/20 to-amber-900/10',
  rose: 'from-rose-500/20 to-rose-900/10',
  violet: 'from-violet-500/20 to-violet-900/10',
};

export function I11SummaryGrid({ items }: { items: readonly SummaryCard[] }) {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <article key={item.label} className={`rounded-2xl border border-white/10 bg-gradient-to-br ${classes[item.tone]} p-4`}>
          <div className="text-sm text-white/70">{item.label}</div>
          <div className="mt-2 text-3xl font-semibold text-white">{item.value}</div>
        </article>
      ))}
    </section>
  );
}
