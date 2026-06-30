import { AppShell } from "@components/layout/app-shell";
import { SmartPurchaseWorkbench } from "@components/suppliers/smart-purchase-workbench";
import { getSupplierDashboardSnapshot } from "@/lib/suppliers/server";
import { SmartDropdownDock } from "@components/uiux/smart-dropdown-dock";

export const dynamic = "force-dynamic";

export default async function SuppliersPage() {
  const snapshot = await getSupplierDashboardSnapshot();
  return (
    <AppShell currentPath="/proveedores">
      <SmartDropdownDock currentPath="/proveedores" title="Filtros de proveedores y compras" />
      <SmartPurchaseWorkbench
        generatedAt={snapshot.generatedAt}
        suppliers={snapshot.suppliers}
        recommendations={snapshot.recommendations}
        signals={snapshot.signals}
        openOrders={snapshot.openOrders}
        receivingQueue={snapshot.receivingQueue}
        payables={snapshot.payables}
        lifecycle={snapshot.lifecycle}
        inventoryBridge={snapshot.inventoryBridge}
      />
    </AppShell>
  );
}
