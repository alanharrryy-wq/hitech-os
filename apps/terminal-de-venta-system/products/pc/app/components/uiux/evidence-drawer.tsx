import type { EvidenceItem } from "./decision-types";

function keyPart(value: string | undefined) {
  return String(value ?? "empty").replace(/\s+/g, "-").slice(0, 88);
}

function evidenceItemKey(section: EvidenceItem["kind"], item: EvidenceItem, index: number) {
  return ["evidence", section, index, keyPart(item.label), keyPart(item.value)].join("-");
}

export function EvidenceDrawer({ items, title = "Ver evidencia técnica" }: { items: EvidenceItem[]; title?: string }) {
  const operational = items.filter((item) => item.kind === "operational");
  const technical = items.filter((item) => item.kind === "technical");
  const governance = items.filter((item) => item.kind === "governance");

  const renderItems = (rows: EvidenceItem[], section: EvidenceItem["kind"]) => (
    <div className="list" style={{ marginTop: 12 }}>
      {rows.map((item, index) => (
        <div className="list-item" key={evidenceItemKey(section, item, index)}>
          <strong>{item.label}:</strong> {item.value}
        </div>
      ))}
    </div>
  );

  return (
    <details className="card" data-prisma-component="EvidenceDrawer" data-evidence-default="closed">
      <summary className="section-title">{title}</summary>
      {operational.length ? (
        <section aria-label="Evidencia operativa">
          <div className="kicker">lectura operativa</div>
          {renderItems(operational, "operational")}
        </section>
      ) : null}
      {technical.length ? (
        <section aria-label="Evidencia técnica" style={{ marginTop: 12 }}>
          <div className="kicker">detalle técnico</div>
          {renderItems(technical, "technical")}
        </section>
      ) : null}
      {governance.length ? (
        <section aria-label="Gobierno" style={{ marginTop: 12 }}>
          <div className="kicker">gobierno y trazabilidad</div>
          {renderItems(governance, "governance")}
        </section>
      ) : null}
    </details>
  );
}
