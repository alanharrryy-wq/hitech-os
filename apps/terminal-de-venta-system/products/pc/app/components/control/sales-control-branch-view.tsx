import type { CommandCenterModel, SalesControlBranchSummary, SalesControlTicket } from "@/server/services/pc-command-center.service";
import { AppShell } from "@components/layout/app-shell";
import styles from "./sales-control-branch-view.module.css";

function MetricTile({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <article className={styles.metricTile}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

function TicketDetail({ ticket }: { ticket: SalesControlTicket }) {
  return (
    <div className={styles.ticketDetail}>
      <div className={styles.ticketDetailGrid}>
        <span>Folio</span><strong>{ticket.folio}</strong>
        <span>Sucursal</span><strong>{ticket.branchName}</strong>
        <span>Tablet</span><strong>{ticket.tabletName}</strong>
        <span>Caja</span><strong>{ticket.cashSessionId}</strong>
        <span>Cajero</span><strong>{ticket.cashier}</strong>
        <span>Total</span><strong>{ticket.total}</strong>
      </div>

      <div className={styles.ticketSplit}>
        <div>
          <h4>Productos</h4>
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
          <h4>Pagos</h4>
          {ticket.tenders.length ? (
            <ul>
              {ticket.tenders.map((tender) => <li key={`${ticket.id}-${tender}`}>{tender}</li>)}
            </ul>
          ) : <p>Sin desglose de pago consolidado.</p>}
        </div>
      </div>
    </div>
  );
}

function BranchSection({ branch, openByDefault }: { branch: SalesControlBranchSummary; openByDefault: boolean }) {
  return (
    <details className={styles.branchCard} open={openByDefault}>
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
        <div className={styles.tabletRail}>
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
              <small>Usa "Agregar sucursal nueva" para preparar la vinculación.</small>
            </article>
          )}
        </div>

        <div className={styles.ticketTableWrap}>
          <table className={styles.ticketTable}>
            <thead>
              <tr>
                <th>Folio</th>
                <th>Fecha</th>
                <th>Tablet</th>
                <th>Cajero</th>
                <th>Total</th>
                <th>Estado</th>
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
                  <td>{ticket.total}</td>
                  <td><span className={styles.statusPill}>{ticket.status}</span></td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={6}>Sin tickets consolidados en esta sucursal para el rango actual.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </details>
  );
}

function AddBranchTabletForm({ href }: { href: string }) {
  return (
    <details className={styles.addBranchDock}>
      <summary>Agregar sucursal nueva</summary>
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
          Responsable o cajero inicial
          <input name="operator" placeholder="Ej. tablet-cashier" />
        </label>
        <label>
          Nota de vinculación
          <textarea name="notes" placeholder="Ubicación física, caja, observaciones o motivo de alta." />
        </label>
        <button type="submit">Continuar vinculación en sincronización</button>
      </form>
    </details>
  );
}

export function SalesControlBranchView({ model }: { model: CommandCenterModel }) {
  const view = model.salesControl;
  if (!view) return null;

  return (
    <AppShell currentPath={model.currentPath}>
      <section className={styles.hero}>
        <div>
          <span className={styles.kicker}>Ventas / Caja</span>
          <h1>{model.title}</h1>
          <p><strong>Rol actual:</strong> {view.roleLabel}</p>
          <small>{model.description} Ventas por sucursal y tablet, con detalle de ticket sólo bajo demanda.</small>
        </div>
        <a className={styles.syncButton} href={view.syncHref}>Revisar sincronización</a>
      </section>

      <section className={styles.metricsGrid} aria-label="Resumen global de ventas">
        <MetricTile label="Venta bruta" value={view.totalLabel} note="Total obtenido hasta el momento" />
        <MetricTile label="Venta neta" value={view.netLabel} note="Bruta menos devoluciones" />
        <MetricTile label="Tickets" value={view.ticketsLabel} note="Tickets consolidados PC" />
        <MetricTile label="Ticket promedio" value={view.averageLabel} note="Promedio por ticket" />
        <MetricTile label="Sucursales" value={view.branchCountLabel} note="Con venta o registradas" />
        <MetricTile label="Tablets" value={view.tabletCountLabel} note="Tablets con venta en rango" />
      </section>

      <section className={styles.branchList}>
        <div className={styles.sectionHead}>
          <div>
            <span className={styles.kicker}>Ventas por sucursal</span>
            <h2>Sucursales, tablets y tickets</h2>
            <p>Abre una sucursal para revisar tablets. Pica un folio para desglosar el ticket.</p>
          </div>
          <small>Actualizado: {view.updatedLabel}</small>
        </div>

        {view.branches.length ? view.branches.map((branch, index) => (
          <BranchSection key={branch.id} branch={branch} openByDefault={index === 0} />
        )) : (
          <div className={styles.emptyState}>No hay sucursales o ventas consolidadas en este rango.</div>
        )}
      </section>

      <AddBranchTabletForm href={view.addBranchHref} />
    </AppShell>
  );
}
