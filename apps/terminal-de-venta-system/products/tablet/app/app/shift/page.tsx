import { AppShell } from "@components/layout/app-shell";
import { FlowStep } from "@components/ui/flow-step";
import { MiniProgress } from "@components/ui/mini-progress";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { StatusBadge } from "@components/ui/status-badge";
import { TableSimple } from "@components/ui/table-simple";
import { getShiftConsole } from "@/lib/services/shift";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";
import { formatMoney } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ShiftPage() {
  const page = tabletMessages.pages.shift;
  const shift = await getShiftConsole();
  const ux = getUxProKit();

  return (
    <AppShell currentPath="/shift">
      <section className="hero">
        <div className="kicker">{page.kicker}</div>
        <h1 style={{ margin: 0 }}>{page.title}</h1>
        <div className="subtle">{page.subtitle}</div>
      </section>

      <div className="grid cols-4">
        <StatCard label="Fondo inicial" value={formatMoney(shift.kpis.cashStart)} note="CashSession.cashStartCents" />
        <StatCard label="Venta esperada" value={formatMoney(shift.kpis.salesTotal)} note="CashSession.expectedCashCents" />
        <StatCard label="Efectivo esperado" value={formatMoney(shift.kpis.expectedCash)} note="turno abierto" />
        <StatCard label="Variación" value={formatMoney(shift.kpis.variance)} note="CashSession.varianceCents" />
      </div>

      <div className="grid cols-2">
        <SectionCard title="Checklist del turno" subtitle="Tres pasos y ya sabes si el dia va fino o te va a querer morder.">
          <div className="stack-list compact">
            {ux.shiftKit.checklist.map((item) => (
              <FlowStep key={item.title} step={item.step} title={item.title} description={item.description} tone={item.tone} aside={<span className="code">{item.aside}</span>} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Salud del turno" subtitle="Lectura corta para que el supervisor entienda el piso sin pedir novela.">
          <div className="stack-list compact">
            <MiniProgress label="Ritmo de caja" value={84} note="Flujo rapido con dos pausas cortas por devolucion." tone="ok" />
            <MiniProgress label="Arqueo vivo" value={68} note="Efectivo controlado, pero ya pide corte intermedio." tone="warn" />
            <MiniProgress label="Cierre listo" value={52} note="Faltan pendientes de sync y cierre documental." tone="danger" />
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Notas rapidas" subtitle="Lo minimo que conviene dejar cantado para el siguiente relevo.">
        <div className="pill-set">
          {ux.shiftKit.notes.map((item, index) => (
            <StatusBadge key={item} tone={index === 1 ? "warn" : "ok"}>{item}</StatusBadge>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="CashSession canónica" subtitle="Turnos leídos desde Prisma por terminal.">
        <TableSimple
          columns={["Turno", "Cajero", "Ventas", "Variación", "Estado"]}
          rows={shift.recentShifts.map((row) => ({
            Turno: row.label,
            Cajero: row.cashier,
            Ventas: formatMoney(row.netSales),
            Variación: formatMoney(row.variance),
            Estado: <StatusBadge tone={row.tone}>{row.status}</StatusBadge>
          }))}
        />
      </SectionCard>
    </AppShell>
  );
}
