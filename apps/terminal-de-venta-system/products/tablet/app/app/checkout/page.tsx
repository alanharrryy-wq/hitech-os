import { CheckoutWorkspace } from "@components/checkout/checkout-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Cobro - PRISMA Tablet",
  description: "Confirmación del ticket y método de pago de la venta activa."
};

export default async function CheckoutPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <CheckoutWorkspace runtimeSnapshot={runtimeSnapshot} />;
}
