import { DecisionScreen } from "@components/uiux/decision-screen";
import { suppliersScreenContract } from "@/uiux/suppliers-screen-contract";

export const dynamic = "force-dynamic";

export default async function SuppliersPage() {
  return <DecisionScreen {...suppliersScreenContract} currentPath="/proveedores" />;
}
