import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { StatusBadge } from "@components/ui/status-badge";
import { TableSimple } from "@components/ui/table-simple";
import { getSyncConsole } from "@/lib/services/sync";
import { formatInt } from "@/lib/utils";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const dynamic = "force-dynamic";

export default async function Page() {
  const page = tabletMessages.pages.sync;
  const sync = await getSyncConsole();

  return (
    <AppShell currentPath="/sync">
      <section className="hero hero-split">
        <div>
          <div className="kicker">{page.kicker}</div>
          <h1 style={{ margin: 0 }}>{page.title}</h1>
          <div className="subtle">{page.subtitle}</div>
        </div>
        <div className="hero-side">
          <div className="mini-stat">
            <span className="mini-stat-label">estado</span>
            <strong>{sync.health.title}</strong>
            <span className="subtle">{sync.health.description}</span>
          </div>
          <div className="mini-stat">
            <span className="mini-stat-label">último sync sano</span>
            <strong>{sync.health.lastSuccess}</strong>
            <span className="subtle">cola visible y reintentos controlados</span>
          </div>
        </div>
      </section>

      <div className="grid cols-4">
        <StatCard label="pendientes" value={formatInt(sync.kpis.pending)} note="eventos esperando salida" />
        <StatCard label="fallidos" value={formatInt(sync.kpis.failed)} note="reintentos necesarios" />
        <StatCard label="latencia media" value={`${sync.kpis.avgLatencyMs} ms`} note="de operación local a confirmación" />
        <StatCard label="offline activo" value={`${sync.kpis.offlineShare}%`} note="movimientos capturados sin red" />
      </div>

      <div className="grid cols-2">
        <SectionCard title="Canales del outbox" subtitle="Qué tan cargado viene cada carril operativo.">
          <div className="stack-list compact">
            {sync.channels.map((channel) => (
              <div key={channel.name} className="queue-card">
                <div className="stack-item-head">
                  <div>
                    <strong>{channel.name}</strong>
                    <div className="subtle">{channel.description}</div>
                  </div>
                  <StatusBadge tone={channel.tone}>{channel.status}</StatusBadge>
                </div>
                <div className="latency-bar">
                  <div className="latency-fill" style={{ width: `${channel.load}%` }} />
                </div>
                <div className="pill-row">
                  <span className="signal-pill">pendientes {formatInt(channel.pending)}</span>
                  <span className="signal-pill">máx. atraso {channel.maxAge}</span>
                  <span className="signal-pill">reintentos {formatInt(channel.retries)}</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Alertas y conflictos" subtitle="Broncas que no deben esconderse como calcetín atrás del refri.">
          <div className="stack-list">
            {sync.alerts.map((alert) => (
              <div key={alert.title} className="stack-item">
                <div className="stack-item-head">
                  <strong>{alert.title}</strong>
                  <StatusBadge tone={alert.tone}>{alert.level}</StatusBadge>
                </div>
                <div className="subtle">{alert.description}</div>
                <div className="code">{alert.action}</div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <div className="grid cols-2">
        <SectionCard title="Outbox pendiente" subtitle="Eventos listos para salir cuando regrese la red o pase el reintento.">
          <TableSimple
            columns={["Evento", "Agregado", "Edad", "Intentos", "Estado"]}
            rows={sync.pendingEvents.map((event) => ({
              Evento: event.topic,
              Agregado: event.aggregate,
              Edad: event.age,
              Intentos: formatInt(event.attempts),
              Estado: <StatusBadge tone={event.tone}>{event.status}</StatusBadge>
            }))}
          />
        </SectionCard>

        <SectionCard title="Latencia por tramo" subtitle="Señal corta para ver dónde se está atascando la tubería.">
          <TableSimple
            columns={["Tramo", "Promedio", "P95", "Señal"]}
            rows={sync.latency.map((item) => ({
              Tramo: item.stage,
              Promedio: `${item.avgMs} ms`,
              P95: `${item.p95Ms} ms`,
              Señal: <StatusBadge tone={item.tone}>{item.signal}</StatusBadge>
            }))}
          />
        </SectionCard>
      </div>

      <div className="grid cols-2">
        <SectionCard title="Modo offline" subtitle="Guardrails para seguir vendiendo sin convertir la cola en volcán.">
          <TableSimple
            columns={["Control", "Valor", "Estado"]}
            rows={sync.offlineRules.map((rule) => ({
              Control: rule.label,
              Valor: rule.value,
              Estado: <StatusBadge tone={rule.tone}>{rule.status}</StatusBadge>
            }))}
          />
        </SectionCard>

        <SectionCard title="Atajos del centro de sync" subtitle="Acciones rápidas para caja, turno y supervisor.">
          <div className="action-grid">
            {page.quickActions.map((item) => (
              <div key={item.title} className="action-tile">
                <div className="action-kicker">{item.kicker}</div>
                <strong>{item.title}</strong>
                <div className="subtle">{item.description}</div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </AppShell>
  );
}
