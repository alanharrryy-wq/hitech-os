import {
  PrismaActionCard,
  PrismaDataTable,
  PrismaFlowList,
  PrismaKpiStrip,
  PrismaPanel,
  PrismaPillCloud,
  PrismaPrimaryButton,
  PrismaSecondaryButton,
  PrismaStatusBadge,
  PrismaTabletShell,
  PrismaTotalDisplay
} from "@components/prisma-dark-pos/prisma-route-ui";
import styles from "@components/prisma-dark-pos/prisma-dark-pos.module.css";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";

export default function CheckoutPage() {
  const page = tabletMessages.pages.checkout;
  const ux = getUxProKit();

  return (
    <PrismaTabletShell
      currentPath="/checkout"
      kicker={page.kicker}
      title={page.title}
      subtitle={page.subtitle}
      context={<PrismaStatusBadge tone="warn">ticket por confirmar</PrismaStatusBadge>}
    >
      <PrismaKpiStrip
        metrics={[
          { label: "Pendiente", value: "$0", note: "Sin ticket activo en esta vista", icon: "credit-card" },
          { label: "Métodos", value: "3", note: "Efectivo, tarjeta y mixto", icon: "wallet" },
          { label: "Guardias", value: String(ux.checkoutRail.guards.length), note: "Candados operativos", icon: "settings" },
          { label: "Cierre", value: "F2", note: "Acción principal visible", icon: "cart" }
        ]}
      />

      <div className={styles.checkoutLayout}>
        <div className={styles.routeSideStack}>
          <PrismaPanel title="Método de pago" subtitle="Tarjetas táctiles, jerarquía clara y lectura rápida de riesgo." eyebrow="cobro">
            <div className={styles.paymentGrid}>
              {ux.checkoutRail.payments.map((item, index) => (
                <PrismaActionCard key={item.title} title={item.title} description={item.description} meta={item.meta} tone={item.tone} icon={index === 0 ? "wallet" : index === 1 ? "credit-card" : "chart"} />
              ))}
            </div>
          </PrismaPanel>

          <PrismaPanel title="Candados y alertas" subtitle="Señales suaves antes de cerrar el ticket." eyebrow="validación">
            <PrismaDataTable
              columns={["Guardia", "Descripción", "Señal"]}
              emptyLabel="Sin alertas de cobro"
              rows={ux.checkoutRail.guards.map((item) => ({
                Guardia: item.title,
                Descripción: item.description,
                Señal: <PrismaStatusBadge tone={item.tone}>{item.signal}</PrismaStatusBadge>
              }))}
            />
          </PrismaPanel>

          <PrismaPanel title="Checklist mínimo de cierre" subtitle="Lo justo para no dejar la venta floja ni al cliente esperando." eyebrow="pasos">
            <PrismaPillCloud items={page.bullets} tone="ok" />
          </PrismaPanel>
        </div>

        <aside className={styles.routeSideStack}>
          <PrismaPanel title="Resumen de pago" subtitle="La acción de dinero queda separada y dominante." eyebrow="finalizar">
            <PrismaTotalDisplay label="Total a cobrar" value="$0.00" note="Esperando ticket activo desde ventas" />
            <div style={{ height: 14 }} />
            <div className={styles.routeSummaryRows}>
              <div className={styles.routeSummaryRow}>
                <span>Recibido</span>
                <strong>$0.00</strong>
              </div>
              <div className={styles.routeSummaryRow}>
                <span>Cambio</span>
                <strong>$0.00</strong>
              </div>
              <div className={styles.routeSummaryRow}>
                <span>Estado</span>
                <PrismaStatusBadge tone="warn">pendiente</PrismaStatusBadge>
              </div>
            </div>
            <div style={{ height: 14 }} />
            <PrismaPrimaryButton shortcut="F2">CONFIRMAR COBRO</PrismaPrimaryButton>
            <div style={{ height: 10 }} />
            <div className={styles.routeButtonGrid}>
              <PrismaSecondaryButton icon="arrow-left">Volver</PrismaSecondaryButton>
              <PrismaSecondaryButton icon="receipt">Recibo</PrismaSecondaryButton>
            </div>
          </PrismaPanel>

          <PrismaPanel title="Flujo recomendado" subtitle="Orden operativo para no brincar entre pasos." eyebrow="rail">
            <PrismaFlowList
              items={[
                { step: "01", title: "Validar ticket", description: "Confirma artículos, descuentos y alertas antes del cobro.", aside: "ticket" },
                { step: "02", title: "Elegir método", description: "Selecciona efectivo, tarjeta o mixto con cambio visible.", aside: "pago" },
                { step: "03", title: "Cerrar venta", description: "Confirma y entrega recibo sin perder la pantalla de estado.", aside: "F2" }
              ]}
            />
          </PrismaPanel>
        </aside>
      </div>
    </PrismaTabletShell>
  );
}
