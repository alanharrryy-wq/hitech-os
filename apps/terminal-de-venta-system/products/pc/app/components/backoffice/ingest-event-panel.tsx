import { RECOGNIZED_EVENT_TOPICS, REQUIRED_EVENT_FIELDS, SUPPORTED_SCHEMA_VERSIONS } from "@/lib/backoffice/event-contract";

export function IngestEventPanel() {
  return (
    <section className="card">
      <div className="section-head">
        <div>
          <div className="kicker">ingesta explícita</div>
          <h2 className="section-title">Validador de eventos Tablet</h2>
          <div className="section-copy">
            La API acepta un evento, un arreglo o un export JSON con <span className="code">events</span>. Por ahora valida contrato y clasifica; no finge persistencia.
          </div>
        </div>
      </div>
      <div className="dashboard-actions">
        <div className="action-card">
          <strong>Campos requeridos</strong>
          <span>{REQUIRED_EVENT_FIELDS.join(", ")}</span>
        </div>
        <div className="action-card">
          <strong>Estados de resultado</strong>
          <span>accepted, rejected, duplicate, conflict</span>
        </div>
        <div className="action-card">
          <strong>Schema soportado</strong>
          <span>{SUPPORTED_SCHEMA_VERSIONS.join(", ")}</span>
        </div>
      </div>
      <div className="alert-strip" style={{ marginTop: 14 }}>
        <strong>{RECOGNIZED_EVENT_TOPICS.length} topics reconocidos</strong>
        <span className="subtle">PC consolida cuando exista persistencia de ingest; Tablet sigue vendiendo local.</span>
      </div>
    </section>
  );
}
