import type { ChartInsight } from "./decision-types";

function barKey(label: string, value: string, index: number) {
  return ["insight-bar", index, label, value].join("-");
}

export function ChartInsightCard({ insight }: { insight: ChartInsight }) {
  return (
    <section className="card" data-prisma-component="ChartInsightCard">
      <div className="section-head">
        <div>
          <div className="kicker">{insight.title}</div>
          <h2 className="section-title">{insight.question}</h2>
          <div className="section-copy">{insight.reading}</div>
          <div className="section-copy">Acción sugerida: {insight.action}</div>
        </div>
      </div>
      <div className="list">
        {insight.bars.map((bar, index) => (
          <div className="list-item" key={barKey(bar.label, bar.value, index)}>
            <strong>{bar.label}</strong>
            <span style={{ display: "inline-block", minWidth: 180, marginLeft: 12 }}>{bar.value}</span>
            <span>{bar.level}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
