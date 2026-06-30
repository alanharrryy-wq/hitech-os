import type { CommandCenterModel, CommandMetric, CommandPanel, CommandTable } from "@/server/services/pc-command-center.service";
import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { PcCommandActions } from "./pc-command-actions";
import { SmartDropdownDock } from "@components/uiux/smart-dropdown-dock";
import styles from "./cash-sessions-operational-view.module.css";

function toneClass(tone?: CommandMetric["tone"]) {
  if (tone === "danger") return styles.toneDanger;
  if (tone === "warn") return styles.toneWarn;
  return styles.toneOk;
}

function tableByTitle(tables: CommandTable[], title: string) {
  return tables.find((table) => table.title.toLowerCase().includes(title.toLowerCase()));
}

function CashMetricStack({ metrics }: { metrics: CommandMetric[] }) {
  const [primary, ...rest] = metrics;
  return (
    <section className={styles.cashBalanceStrip} data-prisma-component="PcCashBalanceHierarchy">
      <div className={styles.primaryBalance}>
        <span className={styles.kicker}>consola de caja</span>
        <strong>{primary?.value ?? "sin dato"}</strong>
        <small>{primary?.label ?? "Métrica principal"} · {primary?.note ?? "pendiente de lectura"}</small>
      </div>
      <div className={styles.balanceFacts}>
        {rest.slice(0, 5).map((metric) => (
          <span key={metric.label} className={toneClass(metric.tone)}>
            <strong>{metric.value}</strong>
            <small>{metric.label}</small>
            <em>{metric.note}</em>
          </span>
        ))}
      </div>
    </section>
  );
}

function PanelStack({ panels }: { panels: CommandPanel[] }) {
  return (
    <section className={styles.panelStack} data-prisma-component="PcCashRiskStack">
      <div>
        <span className={styles.kicker}>señales</span>
        <h2>Riesgo de caja</h2>
      </div>
      {panels.length ? panels.map((panel) => (
        <article key={panel.title} className={styles.panelCard}>
          <strong>{panel.title}</strong>
          <span>{panel.body}</span>
        </article>
      )) : <p>Sin alertas de caja para este corte.</p>}
    </section>
  );
}

function RenderTable({ table, focus }: { table?: CommandTable; focus: "sessions" | "movements" | "conflicts" }) {
  if (!table) return null;
  return (
    <section className={`${styles.tableCard} ${styles[focus]}`} data-prisma-component={`PcCash${focus}Ledger`}>
      <div className={styles.sectionHead}>
        <div>
          <span>ledger de caja</span>
          <h2>{table.title}</h2>
          <p>{table.caption}</p>
        </div>
      </div>
      <DataTable columns={table.columns} rows={table.rows} emptyMessage={table.emptyMessage} />
    </section>
  );
}

function CashGuidedAction() {
  return (
    <section className={styles.guidedAction} data-prisma-component="PcCashGuidedClose">
      <div>
        <span className={styles.kicker}>acción sensible</span>
        <h2>Cierre guiado</h2>
        <p>Antes de confirmar, PRISMA exige esperado, contado, diferencia, motivo y responsable.</p>
      </div>

      <form className={styles.actionForm} action="/cash-sessions" method="get">
        <label>
          Acción de caja
          <select name="cashAction" defaultValue="close">
            <option value="withdrawal">Registrar retiro</option>
            <option value="deposit">Registrar ingreso</option>
            <option value="close">Cerrar caja</option>
            <option value="reopen">Reabrir con permiso</option>
            <option value="markVarianceReviewed">Marcar diferencia revisada</option>
          </select>
        </label>
        <label>
          Motivo obligatorio
          <select name="reason" defaultValue="cash-count">
            <option value="cash-count">Conteo de efectivo</option>
            <option value="variance">Faltante o sobrante</option>
            <option value="manager-approval">Aprobación de gerente</option>
            <option value="sync-review">Revisión por sync</option>
          </select>
        </label>
        <label>
          Responsable
          <input name="responsible" placeholder="Cajero, gerente o auditor" />
        </label>
        <div className={styles.formActions}>
          <button type="submit">Preparar acción</button>
          <span title="La mutación queda bloqueada hasta existir endpoint auditable.">
            Confirmar cierre requiere endpoint auditable
          </span>
        </div>
      </form>
    </section>
  );
}

function EvidenceSteps() {
  return (
    <section className={styles.evidenceSteps} data-prisma-component="PcCashEvidenceSteps">
      <div>
        <span className={styles.kicker}>auditoría</span>
        <h2>Cadena de evidencia</h2>
      </div>
      <ol>
        <li><strong>Ver caja:</strong> abierta, cerrada o con conflicto.</li>
        <li><strong>Comparar dinero:</strong> esperado contra contado.</li>
        <li><strong>Explicar diferencia:</strong> motivo obligatorio si hay faltante o sobrante.</li>
        <li><strong>Guardar evidencia:</strong> responsable, horario, terminal y estado sync.</li>
      </ol>
    </section>
  );
}

export function CashSessionsOperationalView({ model }: { model: CommandCenterModel }) {
  const sessionsTable = tableByTitle(model.tables, "Sesiones");
  const conflictsTable = tableByTitle(model.tables, "Conflictos");
  const movementsTable = tableByTitle(model.tables, "Movimientos");

  return (
    <AppShell currentPath={model.currentPath}>
      <main className={styles.cashConsole} data-prisma-surface="pc-cash-drawer-console">
        <section className={styles.cashHero}>
          <div>
            <span className={styles.kicker}>{model.kicker}</span>
            <h1>{model.title}</h1>
            <p>{model.description}</p>
            <small>{model.sourceLine}</small>
          </div>
          <a href="/sales-control">Volver al ledger de ventas</a>
        </section>

        <section className={styles.consoleGrid}>
          <aside className={styles.cashRail} aria-label="Filtros y cierre guiado">
            <SmartDropdownDock currentPath={model.currentPath} title="Filtros compactos de caja" />
            <CashGuidedAction />
            <EvidenceSteps />
            {model.actions?.length ? (
              <section className={styles.commandActions}>
                <div>
                  <span className={styles.kicker}>acciones reales</span>
                  <h2>Rutas disponibles</h2>
                </div>
                <PcCommandActions actions={model.actions} />
              </section>
            ) : null}
          </aside>

          <section className={styles.cashMain} aria-label="Ledger y balance de caja">
            <CashMetricStack metrics={model.metrics} />
            <PanelStack panels={model.panels} />
            <RenderTable table={sessionsTable} focus="sessions" />
            <RenderTable table={movementsTable} focus="movements" />
            <RenderTable table={conflictsTable} focus="conflicts" />

            <section className={styles.diagnosticsCard}>
              <details>
                <summary>Diagnóstico admin sanitizado</summary>
                <pre>{JSON.stringify(model.diagnostics, null, 2)}</pre>
              </details>
            </section>
          </section>
        </section>
      </main>
    </AppShell>
  );
}
