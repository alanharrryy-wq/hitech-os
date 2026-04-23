import { AppShell } from "@components/layout/app-shell";
import { ActionChip } from "@components/ui/action-chip";
import { FlowStep } from "@components/ui/flow-step";
import { SectionCard } from "@components/ui/section-card";
import { StatusBadge } from "@components/ui/status-badge";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";

export default function SalesPage() {
  const page = tabletMessages.pages.sales;
  const ux = getUxProKit();

  return (
    <AppShell currentPath="/sales">
      <section className="hero">
        <div className="kicker">{page.kicker}</div>
        <h1 style={{ margin: 0 }}>{page.title}</h1>
        <div className="subtle">{page.subtitle}</div>
      </section>

      <div className="grid cols-2">
        <SectionCard title="Cola express de venta" subtitle="Secuencia corta para escanear, ajustar y vender sin meter reversa cada rato.">
          <div className="stack-list compact">
            {ux.salesDeck.queue.map((item) => (
              <FlowStep key={item.title} step={item.step} title={item.title} description={item.description} tone={item.tone} aside={<span className="code">{item.aside}</span>} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Favoritos del turno" subtitle="SKU rapidos para que caja no ande buscando lo que siempre vende.">
          <div className="pill-set">
            {ux.salesDeck.favorites.map((item) => (
              <span key={item} className="pill">{item}</span>
            ))}
          </div>
          <div style={{ height: 12 }} />
          <div className="stack-list compact">
            {ux.salesDeck.suggestions.map((item, index) => (
              <ActionChip key={item} title={item} description="Atajo sugerido por comportamiento del turno y presion de stock." meta={`S-${index + 1}`} tone={index === 1 ? "warn" : "ok"} />
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="KPIs del modulo" subtitle="El flow sigue amarrado a los indicadores que importan en caja.">
        <div className="pill-set">
          {page.bullets.map((item) => (
            <StatusBadge key={item} tone="ok">{item}</StatusBadge>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
