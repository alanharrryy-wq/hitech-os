type StatCardProps = {
  label: string;
  value: string;
  note: string;
  className?: string;
};

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function StatCard({ label, value, note, className }: StatCardProps) {
  return (
    <section
      className={joinClasses("card", "pc-foundation-card", "pc-foundation-stat", className)}
      data-prisma-component="StatCard"
      data-value-length={value.length > 12 ? "long" : "standard"}
    >
      <div className="card-title-row pc-foundation-stat__header">
        <div>
          <div className="kicker pc-foundation-card__eyebrow">Indicador</div>
          <div className="card-title pc-foundation-stat__label">{label}</div>
        </div>
        <span className="card-icon pc-foundation-stat__icon" aria-hidden="true">
          ✦
        </span>
      </div>
      <div className="metric pc-foundation-stat__value">{value}</div>
      <div className="metric-note pc-foundation-stat__note">{note}</div>
    </section>
  );
}
