import { AppShell } from "@components/layout/app-shell";
import { ActionChip } from "@components/ui/action-chip";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { StatusBadge } from "@components/ui/status-badge";
import { TableSimple } from "@components/ui/table-simple";
import { getReturnsConsole } from "@/lib/services/returns";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";
import { formatInt, formatMoney } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ReturnsPage() {
  const page = tabletMessages.pages.returns;
  const returns = await getReturnsConsole();
  const ux = getUxProKit();

  return (
    <AppShell currentPath="/returns">
      <section className="hero">
        <div className="kicker">{page.kicker}</div>
        <h1 style={{ margin: 0 }}>{page.title}</h1>
        <div className="subtle">{page.subtitle}</div>
      </section>

      <div className="grid cols-4">
        <StatCard label="Devoluciones" value={formatInt(returns.kpis.returnCount)} note="SaleReturn" />
        <StatCard label="Monto" value={formatMoney(returns.kpis.amountToday)} note="amountCents" />
        <StatCard label="Promedio" value={formatMoney(returns.kpis.avgRefund)} note="calculado" />
        <StatCard label="Motivo top" value={returns.topReason.reason} note={`${formatInt(returns.topReason.count)} casos`} />
      </div>

      <div className="grid cols-2">
        <SectionCard title="Motivos de devolucion" subtitle="Set corto para clasificar sin tener que escribir biblia en plena fila.">
          <div className="pill-set">
            {ux.returnsKit.reasons.map((item) => (
              <span key={item} className="pill pill-danger">{item}</span>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Guardrails" subtitle="Candados que bajan fraude y suben trazabilidad sin matar el ritmo.">
          <div className="stack-list compact">
            {ux.returnsKit.guardrails.map((item) => (
              <ActionChip key={item.title} title={item.title} description={item.description} meta={item.signal} tone={item.tone} />
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Checklist de caso" subtitle="Pasos minimos para que la devolucion salga limpia y defendible.">
        <div className="pill-set">
          {page.bullets.map((item, index) => (
            <StatusBadge key={item} tone={index === 0 ? "danger" : "ok"}>{item}</StatusBadge>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Devoluciones recientes" subtitle="Lectura runtime desde SaleReturn canónico.">
        <TableSimple
          columns={["Folio", "Motivo", "Monto", "Cajero", "Estado"]}
          rows={returns.recentReturns.map((row) => ({
            Folio: row.folio,
            Motivo: row.reason,
            Monto: formatMoney(row.amount),
            Cajero: row.cashier,
            Estado: <StatusBadge tone={row.tone}>{row.status}</StatusBadge>
          }))}
        />
      </SectionCard>
    </AppShell>
  );
}
