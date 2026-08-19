// PRISMA_PRICING_OWNER_V1
import { AppShell } from "@components/layout/app-shell";
import { PricingPolicyWorkspace } from "@components/pricing/pricing-policy-workspace";
import { getPricingPolicySnapshot } from "@/server/services/pricing-policy.service";

export const dynamic = "force-dynamic";

export default async function PricingPolicyPage() {
  const workspace = await getPricingPolicySnapshot();
  return (
    <AppShell currentPath="/politica-precios">
      <section className="hero">
        <div className="kicker">precios, impuestos y autorización</div>
        <h1 style={{ margin: 0 }}>Política de precios</h1>
        <div className="subtle">Consulta reglas de precio, impuestos y autorizaciones con historial de cambios.</div>
      </section>
      <PricingPolicyWorkspace initialWorkspace={workspace} />
    </AppShell>
  );
}
