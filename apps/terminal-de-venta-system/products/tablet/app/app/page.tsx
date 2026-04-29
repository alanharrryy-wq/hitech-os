import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { ActionChip } from "@components/ui/action-chip";
import { EmptyState } from "@components/ui/empty-state";
import { FlowStep } from "@components/ui/flow-step";
import { InlineAlert } from "@components/ui/inline-alert";
import { MiniProgress } from "@components/ui/mini-progress";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { StatusBadge } from "@components/ui/status-badge";
import { TableSimple } from "@components/ui/table-simple";
import { getTabletDashboard } from "@/lib/services/dashboard";
import { getHardeningConsole } from "@/lib/services/hardening";
import { getUxProKit } from "@/lib/services/ux-pro";
import { formatInt, formatMoney } from "@/lib/utils";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const dashboard = await getTabletDashboard();
  const hardening = getHardeningConsole();
  const ux = getUxProKit();

  return (
    <PrismaTabletShellUnified
      currentPath="/"
      kicker={tabletMessages.home.kicker}
      title={dashboard.hero.title}
      subtitle={dashboard.hero.subtitle}
      status={<TabletShellStatusPill tone={hardening.releaseTone}>Listo para operar</TabletShellStatusPill>}
    >
      <section className="hero hero-split">
        <div>
          <div className="kicker">{tabletMessages.home.kicker}</div>
          <h1 style={{ margin: 0 }}>{dashboard.hero.title}</h1>
          <div className="subtle">{dashboard.hero.subtitle}</div>
        </div>
        <div className="hero-side">
          <div className="mini-stat">
            <span className="mini-stat-label">sucursal</span>
            <strong>{dashboard.hero.branch}</strong>
            <span className="subtle">{dashboard.hero.window}</span>
          </div>
          <div className="mini-stat">
            <span className="mini-stat-label">estado operativo</span>
            <strong>{dashboard.hero.healthLabel}</strong>
            <span className="subtle">{dashboard.hero.healthNote}</span>
          </div>
        </div>
      </section>

      <InlineAlert tone={hardening.releaseTone} title={hardening.releaseTitle} description={hardening.releaseDescription} note={hardening.releaseAction} />

      <div className="grid cols-4">
        {dashboard.kpis.map((kpi) => (
          <StatCard key={kpi.label} label={kpi.label} value={kpi.value} note={kpi.note} />
        ))}
      </div>

      <div className="grid cols-2">
        <SectionCard title="Modo caja express" subtitle="Atajos cortos para que el dedo llegue primero que el drama.">
          <div className="chip-grid">
            {ux.homeActions.map((item) => (
              <ActionChip key={item.title} title={item.title} description={item.description} meta={item.meta} tone={item.tone} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Pulso UX del turno" subtitle="Lectura rapida de lo que ya se siente mas fino y donde aun raspa la operacion.">
          <div className="stack-list compact">
            {ux.focusBars.map((item) => (
              <MiniProgress key={item.label} label={item.label} value={item.value} note={item.note} tone={item.tone} />
            ))}
          </div>
        </SectionCard>
      </div>

      <div className="grid cols-2">
        <SectionCard title="Carril del operador" subtitle="La cola de tareas vivas para no andar saltando entre modulos como chapulin con cafe.">
          <div className="stack-list compact">
            {ux.operatorLane.map((item, index) => (
              <FlowStep
                key={item.title}
                step={`0${index + 1}`}
                title={item.title}
                description={item.description}
                tone={item.tone}
                aside={<StatusBadge tone={item.tone}>{item.signal}</StatusBadge>}
              />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Top productos y presión de venta" subtitle="Vista rapida de los productos que si jalan y donde el existencias ya chifla feo.">
          <TableSimple
            columns={["SKU", "Producto", "Unidades", "Ventas", "Senal"]}
            rows={dashboard.topSkus.map((row) => ({
              SKU: row.sku,
              Producto: row.name,
              Unidades: formatInt(row.qty),
              Ventas: formatMoney(row.revenue),
              Senal: <StatusBadge tone={row.tone}>{row.signal}</StatusBadge>
            }))}
          />
        </SectionCard>
      </div>

      <div className="grid cols-2">
        <SectionCard title="Release gate del turno" subtitle="Smoke checks y bloqueos visibles para no cerrar a ciegas.">
          {hardening.blockers.length ? (
            <div className="stack-list compact">
              {hardening.blockers.map((risk) => (
                <ActionChip key={risk.title} title={risk.title} description={risk.description} meta={risk.level} tone={risk.tone}>
                  <div className="code">{risk.action}</div>
                </ActionChip>
              ))}
            </div>
          ) : (
            <EmptyState title="Sin bloqueos criticos" description="El gate esta limpio y la tablet puede aguantar otra ronda sin rosario tecnico." />
          )}
        </SectionCard>

        <SectionCard title="Smoke checks" subtitle="Verificacion corta para saber si ventas, devoluciones, sync y existencias siguen enteros.">
          <TableSimple
            columns={["Check", "Resultado", "Evidencia", "Senal"]}
            rows={hardening.smokeChecks.map((row) => ({
              Check: row.label,
              Resultado: row.result,
              Evidencia: row.evidence,
              Senal: <StatusBadge tone={row.tone}>{row.status}</StatusBadge>
            }))}
          />
        </SectionCard>
      </div>
    </PrismaTabletShellUnified>
  );
}
