import { DecisionScreen } from "@components/uiux/decision-screen";
import { getPcLicenseStatus } from "@/server/licensing/pc-license-service";
import { resolvePcCustomerSetup, PC_CUSTOMER_SETUP_SLOT_LABEL } from "@/server/licensing/pc-customer-setup";

export const dynamic = "force-dynamic";

export default function PcCustomerSetupPage({ searchParams }: { searchParams?: { code?: string; setupCode?: string } }) {
  const code = searchParams?.code || searchParams?.setupCode || "";
  const setup = resolvePcCustomerSetup(code);
  const license = getPcLicenseStatus();

  return (
    <DecisionScreen
      currentPath="/setup"
      title="Prisma Customer Setup"
      subtitle="Setup Link, Setup Code y Device Claim para PC Admin."
      status="Source ready"
      tableTitle="Device Slots"
      tableSubtitle="Cada superficie reclama su slot correcto sin admin token."
      columns={["Slot", "Surface", "Estado"]}
      rows={setup.slots.map((slot) => ({ Slot: slot.label, Surface: slot.surface, Estado: `${slot.claimed} / ${slot.allowed}` }))}
    >
      <section className="card" data-prisma-customer-setup-surface="pc">
        <div className="section-head">
          <div>
            <div className="kicker">Setup Code</div>
            <h2 className="section-title">{setup.setupCode || "Pendiente"}</h2>
            <div className="section-copy">This PC will claim {PC_CUSTOMER_SETUP_SLOT_LABEL}. Estado licencia PC: {license.state} · Plan {license.plan}.</div>
          </div>
        </div>
      </section>
    </DecisionScreen>
  );
}
