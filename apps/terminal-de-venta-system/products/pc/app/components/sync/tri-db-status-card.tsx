import type { ReactNode } from "react";
import type { TriDbStatusCardModel, TriDbStatusTableParity } from "../../src/modules/sync/tri-db-status.types";
import { formatTriDbCurrency } from "../../src/server/services/tri-db-status.service";

const STATUS_LABEL: Record<TriDbStatusCardModel["status"], string> = {
  READY: "Sincronizacion lista",
  READY_WITH_CAVEATS: "Lista con advertencias",
  BLOCKED: "Bloqueada",
  UNKNOWN: "Sin lectura"
};

function numberLabel(value: number) {
  return value.toLocaleString("es-MX");
}

function Pill({ children, tone = "muted" }: { children: ReactNode; tone?: "ok" | "warn" | "danger" | "muted" }) {
  const colors = { ok: "#14532d", warn: "#713f12", danger: "#7f1d1d", muted: "#334155" };
  return <span style={{ borderRadius: 999, padding: "6px 10px", color: "white", background: colors[tone], fontSize: 12, fontWeight: 800 }}>{children}</span>;
}

function tone(status: TriDbStatusCardModel["status"]) {
  if (status === "READY") return "ok";
  if (status === "READY_WITH_CAVEATS") return "warn";
  if (status === "BLOCKED") return "danger";
  return "muted";
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div style={{ border: "1px solid rgba(148,163,184,.24)", borderRadius: 18, padding: 16, background: "rgba(15,23,42,.48)" }}>
      <div style={{ fontSize: 12, color: "#94a3b8", textTransform: "uppercase", letterSpacing: ".08em" }}>{label}</div>
      <div style={{ marginTop: 8, fontSize: 28, fontWeight: 900, color: "#f8fafc" }}>{value}</div>
      <div style={{ marginTop: 4, fontSize: 13, color: "#cbd5e1" }}>{note}</div>
    </div>
  );
}

function SurfacePanel({ title, productCount, saleCount, outboxCount, barcodeCount, lowStockCount, salesTotalCents }: {
  title: string;
  productCount: number;
  saleCount: number;
  outboxCount: number;
  barcodeCount: number;
  lowStockCount: number;
  salesTotalCents: number;
}) {
  return (
    <article style={{ border: "1px solid rgba(148,163,184,.22)", borderRadius: 22, padding: 18, background: "rgba(2,6,23,.55)" }}>
      <h3 style={{ margin: 0, color: "#f8fafc" }}>{title}</h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12, marginTop: 14 }}>
        <Metric label="Productos" value={numberLabel(productCount)} note={`${numberLabel(barcodeCount)} barcodes`} />
        <Metric label="Ventas" value={numberLabel(saleCount)} note={formatTriDbCurrency(salesTotalCents)} />
        <Metric label="Outbox" value={numberLabel(outboxCount)} note="eventos conocidos" />
        <Metric label="Stock bajo" value={numberLabel(lowStockCount)} note="senal operativa" />
      </div>
    </article>
  );
}

function ParityRow({ row }: { row: TriDbStatusTableParity }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, padding: "10px 0", borderBottom: "1px solid rgba(148,163,184,.16)" }}>
      <strong>{row.table}</strong>
      <span style={{ color: "#cbd5e1" }}>Tablet {numberLabel(row.tabletRows)} · PC {numberLabel(row.pcRows)} · Δ {numberLabel(row.deltaPcMinusTablet)}</span>
      <Pill tone={row.pcCoversTablet ? "ok" : "danger"}>{row.pcCoversTablet ? "cubierta" : "faltante"}</Pill>
    </div>
  );
}

export function TriDbStatusCard({ status }: { status: TriDbStatusCardModel }) {
  const parity = status.parityTables.slice(0, 8);
  return (
    <section style={{ borderRadius: 28, padding: 24, border: "1px solid rgba(125,211,252,.28)", background: "linear-gradient(135deg, rgba(15,23,42,.96), rgba(30,41,59,.92))", color: "#e2e8f0" }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "#7dd3fc", fontSize: 12, fontWeight: 900, letterSpacing: ".14em", textTransform: "uppercase" }}>estado tri-db</div>
          <h2 style={{ margin: "8px 0 0", color: "#f8fafc", fontSize: 28 }}>Tablet → PC canonical → Mobile</h2>
          <p style={{ maxWidth: 760, color: "#cbd5e1" }}>Estado compartido de sincronizacion. Si esto esta en verde, PC ya puede ver lo que Tablet proyecto, sin andar leyendo logs como si fueran posos de cafe.</p>
        </div>
        <Pill tone={tone(status.status)}>{STATUS_LABEL[status.status]}</Pill>
      </header>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 12, marginTop: 18 }}>
        <Metric label="Bridge" value={status.latestBridgeStatus} note="ultima corrida" />
        <Metric label="Tablas" value={numberLabel(status.bridgeTablesProjected)} note="proyectadas" />
        <Metric label="Filas" value={numberLabel(status.bridgeRowsInsertedOrUpdated)} note="copiadas/actualizadas" />
        <Metric label="Outbox" value={numberLabel(status.bridgeOutboxAcknowledged)} note="eventos acked" />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 14, marginTop: 16 }}>
        <SurfacePanel title="Tablet local" {...status.tablet} />
        <SurfacePanel title="PC canonical" {...status.pc} />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1.15fr .85fr", gap: 14, marginTop: 16 }}>
        <article style={{ border: "1px solid rgba(148,163,184,.22)", borderRadius: 22, padding: 18, background: "rgba(2,6,23,.45)" }}>
          <h3 style={{ marginTop: 0 }}>Cobertura PC cubre Tablet: {status.parityOk ? "Si" : "Revisar"}</h3>
          {parity.length ? parity.map((row) => <ParityRow key={row.table} row={row} />) : <p>Sin tabla de paridad disponible.</p>}
        </article>
        <article style={{ border: "1px solid rgba(148,163,184,.22)", borderRadius: 22, padding: 18, background: "rgba(2,6,23,.45)" }}>
          <h3 style={{ marginTop: 0 }}>Evidencia</h3>
          <p><strong>Generado:</strong> {status.generatedAtLabel}</p>
          <p><strong>Ultimo sync:</strong> {status.lastSyncLabel}</p>
          <p style={{ overflowWrap: "anywhere" }}><strong>Fuente:</strong> {status.sourcePath}</p>
          {status.warnings.length ? <p><strong>Advertencias:</strong> {status.warnings.join(" · ")}</p> : <p>Sin advertencias reportadas.</p>}
        </article>
      </div>
    </section>
  );
}
