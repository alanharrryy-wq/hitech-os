import { CatalogStockSellingAssistScreen } from "@components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";
export const metadata={title:"Catálogo - PRISMA Tablet",description:"Catálogo operativo local."};
export default async function CatalogPage(){
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <CatalogStockSellingAssistScreen mode="catalog" runtimeSnapshot={runtimeSnapshot}/>;
}
