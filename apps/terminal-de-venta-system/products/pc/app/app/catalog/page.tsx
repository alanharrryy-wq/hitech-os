import { DecisionScreen } from "@components/uiux/decision-screen";
import { catalogScreenContract } from "@/uiux/catalog-screen-contract";

export const dynamic = "force-dynamic";

export default async function CatalogPage() {
  return <DecisionScreen {...catalogScreenContract} currentPath="/catalog" />;
}
