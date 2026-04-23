export function StatCard({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <section className="card">
      <div className="card-title-row">
        <div>
          <div className="kicker">Indicador</div>
          <div className="card-title">{label}</div>
        </div>
        <span className="card-icon" aria-hidden="true">
          ✦
        </span>
      </div>
      <div className="metric">{value}</div>
      <div className="metric-note">{note}</div>
    </section>
  );
}
