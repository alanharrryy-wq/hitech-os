import { AppShell } from "@components/layout/app-shell";
import { ActionChip } from "@components/ui/action-chip";
import { SectionCard } from "@components/ui/section-card";
import { StatusBadge } from "@components/ui/status-badge";
import { TableSimple } from "@components/ui/table-simple";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";

export default function CheckoutPage() {
  const page = tabletMessages.pages.checkout;
  const ux = getUxProKit();

  return (
    <AppShell currentPath="/checkout">
      <section className="hero">
        <div className="kicker">{page.kicker}</div>
        <h1 style={{ margin: 0 }}>{page.title}</h1>
        <div className="subtle">{page.subtitle}</div>
      </section>

      <div className="grid cols-2">
        <SectionCard title="Rail de pago" subtitle="Metodos ordenados para que el cobro no se sienta como sudoku en la caja.">
          <div className="stack-list compact">
            {ux.checkoutRail.payments.map((item) => (
              <ActionChip key={item.title} title={item.title} description={item.description} meta={item.meta} tone={item.tone} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Candados y alertas" subtitle="Senales suaves para detectar bronca antes de cerrar el ticket.">
          <TableSimple
            columns={["Guardia", "Descripcion", "Senal"]}
            rows={ux.checkoutRail.guards.map((item) => ({
              Guardia: item.title,
              Descripcion: item.description,
              Senal: <StatusBadge tone={item.tone}>{item.signal}</StatusBadge>
            }))}
          />
        </SectionCard>
      </div>

      <SectionCard title="Checklist minimo de cierre" subtitle="Lo justo para no dejar la venta floja ni al cliente colgado.">
        <div className="pill-set">
          {page.bullets.map((item, index) => (
            <StatusBadge key={item} tone={index === 2 ? "warn" : "ok"}>{item}</StatusBadge>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
