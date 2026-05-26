import type { SummaryCard, SummaryTone } from "./decision-types";

const TONE_ICON: Record<SummaryTone, string> = {
  danger: "●",
  warn: "●",
  ok: "●",
  info: "●"
};

function keyPart(value: string | number | undefined) {
  return String(value ?? "empty").replace(/\s+/g, "-").slice(0, 72);
}

function summaryCardKey(card: SummaryCard, index: number) {
  return ["summary-card", index, keyPart(card.eyebrow), keyPart(card.title), keyPart(card.tone)].join("-");
}

function summaryLineKey(card: SummaryCard, cardIndex: number, line: string, lineIndex: number) {
  return [summaryCardKey(card, cardIndex), "line", lineIndex, keyPart(line)].join("-");
}

export function AttentionSummary({ cards }: { cards: SummaryCard[] }) {
  const safeCards = cards.slice(0, 5);
  return (
    <section className="dashboard-grid" data-prisma-component="AttentionSummary" aria-label="Lectura rápida">
      {safeCards.map((card, cardIndex) => (
        <article className="card metric-card" key={summaryCardKey(card, cardIndex)} data-summary-tone={card.tone}>
          <div className="kicker">
            <span aria-hidden="true">{TONE_ICON[card.tone]} </span>
            {card.eyebrow}
          </div>
          <div className="card-title">{card.title}</div>
          <div className="list" style={{ marginTop: 12 }}>
            {card.lines.slice(0, 5).map((line, lineIndex) => (
              <div className="list-item" key={summaryLineKey(card, cardIndex, line, lineIndex)}>{line}</div>
            ))}
          </div>
        </article>
      ))}
    </section>
  );
}
