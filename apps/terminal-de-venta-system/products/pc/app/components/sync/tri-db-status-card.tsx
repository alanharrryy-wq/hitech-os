import type { ReactNode } from "react";
import type { TriDbStatusCardModel, TriDbStatusTableParity } from "../../src/modules/sync/tri-db-status.types";
import { formatTriDbCurrency } from "../../src/server/services/tri-db-status.service";

const STATUS_LABEL: Record<TriDbStatusCardModel["status"], string> = {
  READY: "Bridge de rescate listo",
  READY_WITH_CAVEATS: "Lista con advertencias",
  BLOCKED: "Bloqueada",
  UNKNOWN: "Sin lectura"
};

const STATUS_COPY: Record<TriDbStatusCardModel["status"], string> = {
  READY: "La herramienta secundaria puede proyectar datos para rescate/backfill; el sync primario es OutboxEvent -> PC ingest -> Prisma projectors.",
  READY_WITH_CAVEATS: "La proyeccion secundaria funciona, pero hay advertencias por revisar.",
  BLOCKED: "La proyeccion secundaria no se completo. La operacion de Tablet no se afecta.",
  UNKNOWN: "Aun no hay una lectura confiable del bridge secundario."
};

const CRYSTAL = {
  text: "#102033",
  soft: "#56677d",
  muted: "#8190a3",
  blue: "#126bff",
  line: "rgba(203, 213, 225, 0.78)",
  panel: "rgba(255, 255, 255, 0.82)",
  page: "linear-gradient(145deg, rgba(255,255,255,.96), rgba(243,247,252,.76))",
  shadow: "0 18px 46px rgba(45, 74, 105, 0.10), inset 0 1px 0 rgba(255,255,255,.92)"
};

function numberLabel(value: number) {
  return value.toLocaleString("es-MX");
}

function Pill({ children, tone = "muted" }: { children: ReactNode; tone?: "ok" | "warn" | "danger" | "muted" }) {
  const colors = {
    ok: { color: "#126346", border: "rgba(22,185,120,.28)", bg: "rgba(232,250,242,.92)" },
    warn: { color: "#77530a", border: "rgba(245,158,11,.30)", bg: "rgba(255,244,219,.92)" },
    danger: { color: "#9d2626", border: "rgba(239,68,68,.30)", bg: "rgba(255,233,233,.92)" },
    muted: { color: CRYSTAL.soft, border: "rgba(203,213,225,.9)", bg: "rgba(255,255,255,.72)" }
  }[tone];
  return (
    <span style={{
      alignItems: "center",
      background: colors.bg,
      border: `1px solid ${colors.border}`,
      borderRadius: 999,
      color: colors.color,
      display: "inline-flex",
      fontSize: 12,
      fontWeight: 900,
      justifyContent: "center",
      lineHeight: 1.15,
      minHeight: 34,
      padding: "8px 11px",
      textAlign: "center",
      whiteSpace: "normal"
    }}>{children}</span>
  );
}

function tone(status: TriDbStatusCardModel["status"]) {
  if (status === "READY") return "ok";
  if (status === "READY_WITH_CAVEATS") return "warn";
  if (status === "BLOCKED") return "danger";
  return "muted";
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div style={{
      background: CRYSTAL.panel,
      border: `1px solid ${CRYSTAL.line}`,
      borderRadius: 16,
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.9)",
      minWidth: 0,
      padding: 14
    }}>
      <div style={{ color: CRYSTAL.blue, fontSize: 11, fontWeight: 900, letterSpacing: ".08em", textTransform: "uppercase" }}>{label}</div>
      <div style={{ color: CRYSTAL.text, fontSize: "clamp(1.25rem, 5vw, 1.9rem)", fontWeight: 950, lineHeight: 1, marginTop: 8, overflowWrap: "anywhere" }}>{value}</div>
      <div style={{ color: CRYSTAL.muted, fontSize: 13, lineHeight: 1.28, marginTop: 5, overflowWrap: "anywhere" }}>{note}</div>
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
    <article style={{ background: CRYSTAL.panel, border: `1px solid ${CRYSTAL.line}`, borderRadius: 20, minWidth: 0, padding: 16 }}>
      <h3 style={{ color: CRYSTAL.text, margin: 0 }}>{title}</h3>
      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(128px, 1fr))", marginTop: 12 }}>
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
    <div style={{ alignItems: "center", borderBottom: "1px solid rgba(203,213,225,.58)", display: "grid", gap: 8, gridTemplateColumns: "minmax(90px,.7fr) minmax(0,1.2fr) auto", padding: "10px 0" }}>
      <strong style={{ color: CRYSTAL.text, overflowWrap: "anywhere" }}>{row.table}</strong>
      <span style={{ color: CRYSTAL.soft, fontSize: 13, overflowWrap: "anywhere" }}>Tablet {numberLabel(row.tabletRows)} · PC {numberLabel(row.pcRows)} · delta {numberLabel(row.deltaPcMinusTablet)}</span>
      <Pill tone={row.pcCoversTablet ? "ok" : "danger"}>{row.pcCoversTablet ? "cubierta" : "faltante"}</Pill>
    </div>
  );
}

export function TriDbStatusCard({ status }: { status: TriDbStatusCardModel }) {
  const parity = status.parityTables.slice(0, 8);
  return (
    <section style={{
      background: CRYSTAL.page,
      border: "1px solid rgba(18,107,255,.16)",
      borderRadius: 28,
      boxShadow: CRYSTAL.shadow,
      color: CRYSTAL.text,
      overflow: "hidden",
      padding: "clamp(16px, 3vw, 24px)"
    }}>
      <header style={{ alignItems: "flex-start", display: "grid", gap: 14, gridTemplateColumns: "minmax(0,1fr) auto" }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ color: CRYSTAL.blue, fontSize: 12, fontWeight: 950, letterSpacing: ".14em", textTransform: "uppercase" }}>Estado TRI-DB</div>
          <h2 style={{ color: CRYSTAL.text, fontSize: "clamp(1.35rem, 5vw, 2.15rem)", letterSpacing: 0, lineHeight: 1.04, margin: "7px 0 0", overflowWrap: "anywhere" }}>{"TRI-DB rescue/backfill bridge"}</h2>
          <p style={{ color: CRYSTAL.soft, lineHeight: 1.45, margin: "8px 0 0", maxWidth: 760 }}>{STATUS_COPY[status.status]}</p>
        </div>
        <Pill tone={tone(status.status)}>{STATUS_LABEL[status.status]}</Pill>
      </header>
      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(138px, 1fr))", marginTop: 16 }}>
        <Metric label="Bridge" value={status.latestBridgeStatus} note="ultima corrida" />
        <Metric label="Tablas" value={numberLabel(status.bridgeTablesProjected)} note="proyectadas" />
        <Metric label="Filas" value={numberLabel(status.bridgeRowsInsertedOrUpdated)} note="copiadas/actualizadas" />
        <Metric label="Outbox" value={numberLabel(status.bridgeOutboxAcknowledged)} note="compat acked, no reconciliacion" />
      </div>
      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", marginTop: 14 }}>
        <SurfacePanel title="Tablet local" {...status.tablet} />
        <SurfacePanel title="PC canonical" {...status.pc} />
      </div>
      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", marginTop: 14 }}>
        <article style={{ background: CRYSTAL.panel, border: `1px solid ${CRYSTAL.line}`, borderRadius: 20, minWidth: 0, padding: 16 }}>
          <h3 style={{ color: CRYSTAL.text, marginTop: 0 }}>Cobertura PC cubre Tablet: {status.parityOk ? "Si" : "Revisar"}</h3>
          {parity.length ? parity.map((row) => <ParityRow key={row.table} row={row} />) : <p>Sin tabla de paridad disponible.</p>}
        </article>
        <article style={{ background: CRYSTAL.panel, border: `1px solid ${CRYSTAL.line}`, borderRadius: 20, color: CRYSTAL.soft, minWidth: 0, padding: 16 }}>
          <h3 style={{ color: CRYSTAL.text, marginTop: 0 }}>Evidencia</h3>
          <p><strong>Generado:</strong> {status.generatedAtLabel}</p>
          <p><strong>Ultimo sync:</strong> {status.lastSyncLabel}</p>
          <p style={{ overflowWrap: "anywhere" }}><strong>Fuente:</strong> {status.sourcePath}</p>
          {status.warnings.length ? <p><strong>Advertencias:</strong> {status.warnings.join(" · ")}</p> : <p>Sin advertencias reportadas.</p>}
        </article>
      </div>
    </section>
  );
}
