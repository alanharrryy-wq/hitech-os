import type { CommandCenterModel, SalesControlBranchSummary, SalesControlTicket } from "@/server/services/pc-command-center.service";
import { AppShell } from "@components/layout/app-shell";
import { SmartDropdownDock } from "@components/uiux/smart-dropdown-dock";
import styles from "./sales-control-branch-view.module.css";

function queryHref(path: string, params: Record<string, string>) {
  const search = new URLSearchParams(params);
  return `${path}?${search.toString()}`;
}

function domId(value: string) {
  return value.replace(/[^a-zA-Z0-9_-]/g, "-");
}

function firstTenderLabel(ticket: SalesControlTicket) {
  return ticket.tenders[0] ?? "sin desglose";
}

function allTickets(branches: SalesControlBranchSummary[]) {
  return branches.flatMap((branch) => branch.ticketRows);
}

function paymentCounts(branches: SalesControlBranchSummary[]) {
  const counts = new Map<string, number>();
  for (const ticket of allTickets(branches)) {
    const label = firstTenderLabel(ticket);
    counts.set(label, (counts.get(label) ?? 0) + 1);
  }
  return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5);
}

function TicketActionBoard({ ticket }: { ticket: SalesControlTicket }) {
  const folioHref = queryHref("/sales-control", { q: ticket.folio });
  const exportHref = queryHref("/api/backoffice/sales-control", { format: "json", q: ticket.folio });

  return (
    <div className={styles.ticketActionBoard} data-prisma-component="PcSalesTicketActions">
      <a href={folioHref}>Filtrar folio</a>
      <a href="/cash-sessions">Abrir caja</a>
      <a href="/sync-operativo">Revisar sync</a>
      <a href={exportHref}>Exportar JSON</a>
      <span title="Marcar revisado requiere endpoint auditable con actor, motivo y timestamp.">
        Marcar revisado requiere endpoint auditable
      </span>
    </div>
  );
}

function TicketDetail({ ticket }: { ticket: SalesControlTicket }) {
  return (
    <div className={styles.ticketDetail} data-prisma-component="PcSalesTicketDrawer">
      <div className={styles.ticketDetailHeader}>
        <div>
          <span className={styles.kicker}>drawer de ticket</span>
          <h3>{ticket.folio}</h3>
        </div>
        <strong>{ticket.total}</strong>
      </div>

      <div className={styles.ticketDetailGrid}>
        <span>Sucursal</span><strong>{ticket.branchName}</strong>
        <span>Tablet</span><strong>{ticket.tabletName}</strong>
        <span>Terminal</span><strong>{ticket.terminalId}</strong>
        <span>Caja</span><strong>{ticket.cashSessionId}</strong>
        <span>Cajero</span><strong>{ticket.cashier}</strong>
        <span>Estado sync</span><strong>{ticket.status}</strong>
      </div>

      <div className={styles.ticketSplit}>
        <div>
          <h4>Productos vendidos</h4>
          {ticket.lines.length ? (
            <ul>
              {ticket.lines.map((line) => (
                <li key={`${ticket.id}-${line.sku}-${line.productName}`}>
                  <span>{line.productName}</span>
                  <small>{line.qty} × {line.price}</small>
                  <strong>{line.total}</strong>
                </li>
              ))}
            </ul>
          ) : <p>Sin líneas consolidadas para este ticket.</p>}
        </div>
        <div>
          <h4>Pagos y evidencia</h4>
          {ticket.tenders.length ? (
            <ul>
              {ticket.tenders.map((tender) => <li key={`${ticket.id}-${tender}`}>{tender}</li>)}
            </ul>
          ) : <p>Sin desglose de pago consolidado.</p>}
          <div className={styles.evidenceNote}>
            Caja, cajero, terminal y estado quedan visibles para auditoría sin abrir otra pantalla.
          </div>
        </div>
      </div>

      <TicketActionBoard ticket={ticket} />
    </div>
  );
}

function BranchSection({ branch, openByDefault }: { branch: SalesControlBranchSummary; openByDefault: boolean }) {
  const branchAnchor = `branch-${domId(branch.id)}`;
  return (
    <details id={branchAnchor} className={styles.branchCard} open={openByDefault}>
      <summary className={styles.branchSummary}>
        <div>
          <span className={styles.kicker}>Sucursal</span>
          <strong>{branch.name}</strong>
          <small>{branch.code} · último ticket: {branch.lastSaleAt}</small>
        </div>
        <div className={styles.branchStats}>
          <span>{branch.total}<small>Total</small></span>
          <span>{branch.tickets}<small>Tickets</small></span>
          <span>{branch.tablets.length}<small>Tablets</small></span>
          <em className={branch.syncStatus === "ok" ? styles.okPill : styles.warnPill}>{branch.syncStatus}</em>
        </div>
      </summary>

      <div className={styles.branchBody}>
        <div className={styles.tabletRail} aria-label={`Tablets de ${branch.name}`}>
          {branch.tablets.length ? branch.tablets.map((tablet) => (
            <article key={tablet.id} className={styles.tabletCard}>
              <strong>{tablet.name}</strong>
              <span>{tablet.total}</span>
              <small>{tablet.tickets} tickets · {tablet.lastSync}</small>
              <em>{tablet.pendingSync ? `${tablet.pendingSync} pendientes` : tablet.status}</em>
            </article>
          )) : (
            <article className={styles.tabletCard}>
              <strong>Sin tablet vinculada</strong>
              <span>$0</span>
              <small>Usa el alta rápida para preparar vinculación.</small>
            </article>
          )}
        </div>

        <div className={styles.ticketTableWrap} data-prisma-component="PcSalesDenseTicketLedger">
          <table className={styles.ticketTable}>
            <thead>
              <tr>
                <th>Folio</th>
                <th>Fecha</th>
                <th>Tablet</th>
                <th>Cajero</th>
                <th>Total</th>
                <th>Método</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {branch.ticketRows.length ? branch.ticketRows.map((ticket) => (
                <tr key={ticket.id}>
                  <td>
                    <details className={styles.ticketDisclosure}>
                      <summary>{ticket.folio}</summary>
                      <TicketDetail ticket={ticket} />
                    </details>
                  </td>
                  <td>{ticket.date}</td>
                  <td>{ticket.tabletName}</td>
                  <td>{ticket.cashier}</td>
                  <td className={styles.amountCell}>{ticket.total}</td>
                  <td>{firstTenderLabel(ticket)}</td>
                  <td><span className={styles.statusPill}>{ticket.status}</span></td>
                  <td>
                    <div className={styles.inlineActions}>
                      <a href={queryHref("/sales-control", { q: ticket.folio })}>Detalle</a>
                      <a href="/cash-sessions">Caja</a>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={8}>Sin tickets consolidados en esta sucursal para el rango actual.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </details>
  );
}

function BranchRail({ branches, updatedLabel }: { branches: SalesControlBranchSummary[]; updatedLabel: string }) {
  return (
    <nav className={styles.branchRail} aria-label="Atajos de sucursal">
      <div>
        <span className={styles.kicker}>sucursales</span>
        <h2>Ledger por caja</h2>
        <p>Brinca directo al mostrador que necesita revisión. Esto ya no es jardín de tarjetas, es libreta de caja.</p>
      </div>
      <div className={styles.branchRailList}>
        {branches.slice(0, 8).map((branch) => (
          <a key={branch.id} href={`#branch-${domId(branch.id)}`}>
            <span>{branch.name}</span>
            <strong>{branch.total}</strong>
            <small>{branch.tickets} tickets · {branch.syncStatus}</small>
          </a>
        ))}
      </div>
      <small className={styles.updatedNote}>Actualizado: {updatedLabel}</small>
    </nav>
  );
}

function PaymentMethodStrip({ branches }: { branches: SalesControlBranchSummary[] }) {
  const counts = paymentCounts(branches);
  return (
    <section className={styles.paymentStrip} data-prisma-component="PcSalesPaymentMethodSummary">
      <div>
        <span className={styles.kicker}>métodos de pago</span>
        <h2>Conciliación rápida</h2>
      </div>
      {counts.length ? (
        <div className={styles.paymentList}>
          {counts.map(([label, count]) => (
            <span key={label}>
              <strong>{count}</strong>
              <small>{label}</small>
            </span>
          ))}
        </div>
      ) : <p>Sin desglose de métodos de pago para este rango.</p>}
    </section>
  );
}

function AddBranchTabletForm({ href }: { href: string }) {
  return (
    <details className={styles.addBranchDock}>
      <summary>Alta rápida sucursal/tablet</summary>
      <form className={styles.addBranchForm} action={href} method="get">
        <input type="hidden" name="from" value="sales-control" />
        <input type="hidden" name="focus" value="link-new-tablet" />
        <label>
          Nombre de sucursal
          <input name="storeName" placeholder="Ej. Sucursal Centro" />
        </label>
        <label>
          Código de sucursal
          <input name="storeCode" placeholder="Ej. CENTRO" />
        </label>
        <label>
          Nombre de tablet
          <input name="tabletName" placeholder="Ej. Tablet Caja 2" />
        </label>
        <label>
          Device ID / código terminal
          <input name="deviceId" placeholder="Pegar identificador de la tablet" />
        </label>
        <label>
          Responsable inicial
          <input name="operator" placeholder="Ej. cajero turno matutino" />
        </label>
        <button type="submit">Continuar vinculación</button>
      </form>
    </details>
  );
}

function CashActionDock({ syncHref }: { syncHref: string }) {
  return (
    <section className={styles.cashActionDock} data-prisma-component="PcSalesCashActionRail">
      <div>
        <span className={styles.kicker}>rail de caja</span>
        <h2>Acción de caja</h2>
        <p>Elige intención. PRISMA abre flujo seguro y deja bloqueadas las mutaciones que aún requieren auditoría.</p>
      </div>
      <form className={styles.cashActionForm} action="/cash-sessions" method="get">
        <label>
          Acción
          <select name="cashAction" defaultValue="close">
            <option value="withdrawal">Registrar retiro</option>
            <option value="deposit">Registrar ingreso</option>
            <option value="close">Cerrar caja</option>
            <option value="reopen">Reabrir con permiso</option>
            <option value="markVarianceReviewed">Marcar diferencia revisada</option>
          </select>
        </label>
        <label>
          Motivo
          <select name="reason" defaultValue="review">
            <option value="review">Revisión operativa</option>
            <option value="cash-count">Conteo de efectivo</option>
            <option value="variance">Diferencia detectada</option>
            <option value="manager-approval">Aprobación de gerente</option>
          </select>
        </label>
        <button type="submit">Abrir caja guiada</button>
        <a href={syncHref}>Ver sync</a>
      </form>
    </section>
  );
}

function SalesOperationChecklist() {
  return (
    <section className={styles.operationChecklist} data-prisma-component="PcSalesGuidedClose">
      <div>
        <span className={styles.kicker}>cierre guiado</span>
        <h2>Corte sin adivinar</h2>
      </div>
      <ol>
        <li><strong>Esperado:</strong> suma de ventas y movimientos.</li>
        <li><strong>Contado:</strong> captura física desde caja.</li>
        <li><strong>Diferencia:</strong> faltante o sobrante con motivo.</li>
        <li><strong>Evidencia:</strong> folio, cajero, terminal, horario y sync.</li>
      </ol>
    </section>
  );
}

function FinancialStrip({ model, view }: { model: CommandCenterModel; view: NonNullable<CommandCenterModel["salesControl"]> }) {
  const recent = view.recentActivity;
  return (
    <section className={styles.financialStrip} data-prisma-component="PcSalesFinancialStrip" data-prisma-recent-activity={recent.ticketsLabel}>
      <div className={styles.financialLead}>
        <div className={styles.primaryTotal}>
          <span className={styles.kicker}>ledger operativo</span>
          <strong>{view.netLabel}</strong>
          <small>Venta neta · {model.periodLabel ?? "periodo actual"}</small>
        </div>
        <div className={styles.recentActivityTotal}>
          <span className={styles.kicker}>actividad reciente</span>
          <strong>{recent.netLabel}</strong>
          <small>{recent.label} · {recent.ticketsLabel} tickets · último: {recent.lastSaleAt}</small>
        </div>
      </div>
      <div className={styles.financialFacts}>
        <span><strong>{view.totalLabel}</strong><small>Venta bruta</small></span>
        <span><strong>{view.ticketsLabel}</strong><small>Tickets</small></span>
        <span><strong>{view.averageLabel}</strong><small>Ticket promedio</small></span>
        <span><strong>{view.branchCountLabel}</strong><small>Sucursales</small></span>
        <span><strong>{view.tabletCountLabel}</strong><small>Tablets</small></span>
        <span><strong>{recent.averageLabel}</strong><small>Promedio reciente</small></span>
      </div>
    </section>
  );
}

export function SalesControlBranchView({ model }: { model: CommandCenterModel }) {
  const view = model.salesControl;
  if (!view) return null;

  return (
    <AppShell currentPath={model.currentPath}>
      <main className={styles.salesLedger} data-prisma-surface="pcsales-operational-ledger">
        <section className={styles.ledgerHero}>
          <div>
            <span className={styles.kicker}>Ventas / Caja</span>
            <h1>{model.title}</h1>
            <p>{model.description}</p>
            <small>Rol actual: {view.roleLabel}. La tabla de tickets es la pieza principal, no un mosaico de tarjetas.</small>
          </div>
          <a className={styles.syncButton} href={view.syncHref}>Revisar sincronización</a>
        </section>

        <FinancialStrip model={model} view={view} />

        <section className={styles.ledgerShell}>
          <aside className={styles.operationRail} aria-label="Filtros y acciones de caja">
            <SmartDropdownDock currentPath={model.currentPath} title="Filtros compactos de ventas" />
            <CashActionDock syncHref={view.syncHref} />
            <PaymentMethodStrip branches={view.branches} />
            <SalesOperationChecklist />
            <AddBranchTabletForm href={view.addBranchHref} />
          </aside>

          <section className={styles.ledgerMain} aria-label="Tickets y sucursales">
            <BranchRail branches={view.branches} updatedLabel={view.updatedLabel} />

            <section className={styles.branchList}>
              {view.branches.length ? view.branches.map((branch, index) => (
                <BranchSection key={branch.id} branch={branch} openByDefault={index === 0} />
              )) : (
                <div className={styles.emptyState}>No hay sucursales o ventas consolidadas en este rango.</div>
              )}
            </section>
          </section>
        </section>
      </main>
    </AppShell>
  );
}
