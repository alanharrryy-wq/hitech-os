import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import { StatusBadge } from "@components/backoffice/status-badge";
import type { SyncReleaseWorkspace as SyncReleaseWorkspaceModel } from "@/modules/sync/types";

function count(value: number | null) {
  return value === null || Number.isNaN(value) ? "sin datos" : value.toLocaleString("es-MX");
}

export function SyncReleaseWorkspace({ workspace }: { workspace: SyncReleaseWorkspaceModel }) {
  return (
    <AppShell currentPath="/sync">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">recepción de eventos</div>
            <h1 className="hero-title">Sync, dedupe y conflictos</h1>
            <p>
              PC recibe eventos de Tablet, valida contrato, clasifica duplicados y conflictos, y persiste la recepción cuando la ruta trabaja en modo real.
            </p>
          </div>
          <div className="inline-list">
            <span className="chip">Ruta: /api/sync/ingest</span>
            <span className="chip">Persistencia: {workspace.meta.persistence}</span>
            <span className="chip">Confianza: {workspace.meta.confidence}</span>
          </div>
        </div>
        <div className="hero-badges">
          <span className="alert-chip">ID de evento idempotente</span>
          <span className="alert-chip">Prueba sin persistir</span>
          <span className="alert-chip">conflictos visibles</span>
          <span className="alert-chip">Tablet no se bloquea</span>
        </div>
      </section>

      {workspace.meta.warnings.length ? (
        <div className="alert-strip">
          <strong>Limitación visible</strong>
          <span className="subtle">{workspace.meta.warnings.join(" · ")}</span>
        </div>
      ) : null}

      <section className="dashboard-grid">
        <article className="card metric-card">
          <div className="kicker">recepción</div>
          <div className="card-title">Eventos totales</div>
          <div className="metric">{count(workspace.summary.totalEvents)}</div>
          <div className="metric-note">Eventos de la bandeja operativa leídos por PC.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">estado</div>
          <div className="card-title">Aceptados</div>
          <div className="metric">{count(workspace.summary.ackedEvents)}</div>
          <div className="metric-note">Eventos clasificados como acked.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">conflictos</div>
          <div className="card-title">En conflicto</div>
          <div className="metric">{count(workspace.summary.conflictEvents)}</div>
          <div className="metric-note">Eventos que requieren revisión operativa.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">fallas</div>
          <div className="card-title">Rechazados</div>
          <div className="metric">{count(workspace.summary.failedEvents)}</div>
          <div className="metric-note">Eventos inválidos o rechazados por contrato.</div>
        </article>
      </section>

      <section className="grid cols-2">
        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">contrato</div>
              <h2 className="section-title">Campos requeridos</h2>
              <div className="section-copy">Todo evento sensible debe llegar completo. PC no traga cualquier JSON como buffet sin supervisión.</div>
            </div>
          </div>
          <div className="dashboard-actions">
            {workspace.requiredFields.map((field) => (
              <div className="action-card" key={field}><strong>{field}</strong><span>requerido</span></div>
            ))}
          </div>
        </article>

        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">clasificación</div>
              <h2 className="section-title">Estados de recepción</h2>
              <div className="section-copy">Cada evento termina aceptado, duplicado, en conflicto o rechazado.</div>
            </div>
          </div>
          <div className="list">
            {workspace.statusModel.map((row) => (
              <div className="list-item" key={row.status}>
                <span>{row.description}</span>
                <StatusBadge value={row.status} />
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">conflictos</div>
            <h2 className="section-title">Catálogo de conflictos</h2>
            <div className="section-copy">Casos que PC debe hacer visibles antes de consolidar información dudosa.</div>
          </div>
        </div>
        <DataTable
          columns={["Código", "Etiqueta", "Severidad", "Detalle"]}
          rows={workspace.conflictCatalog.map((item) => ({
            Código: item.code,
            Etiqueta: item.label,
            Severidad: item.severity,
            Detalle: item.detail
          }))}
          emptyMessage="No hay catálogo de conflictos."
        />
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">eventos recientes</div>
            <h2 className="section-title">Últimos eventos persistidos</h2>
            <div className="section-copy">Muestra lo que PC conoce en la bandeja operativa; si no hay base disponible, queda como estado honesto.</div>
          </div>
        </div>
        {workspace.recentEvents.length ? (
          <DataTable
            columns={["Evento", "Tema", "Estado", "Agregado", "Fecha"]}
            rows={workspace.recentEvents.map((event) => ({
              Evento: event.id,
              Tema: event.topic,
              Estado: event.status,
              Agregado: event.aggregateId,
              Fecha: event.createdAtLabel
            }))}
            emptyMessage="No hay eventos recientes."
          />
        ) : (
          <EmptyState title="Sin eventos recientes." description="Cuando Tablet exporte o envíe eventos, PC mostrará aquí la recepción clasificada." />
        )}
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">prueba</div>
            <h2 className="section-title">Payload de prueba dry-run</h2>
            <div className="section-copy">Úsalo contra POST /api/sync/ingest?dryRun=1 para validar contrato sin persistir.</div>
          </div>
        </div>
        <pre className="code-block">{JSON.stringify(workspace.sampleDryRunPayload, null, 2)}</pre>
      </section>
    </AppShell>
  );
}
