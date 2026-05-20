import { SalesTicketDetailScreen } from "@components/sales/sales-ticket-detail-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function Page({
  params,
  searchParams,
}: {
  params: { saleId: string };
  searchParams?: { businessId?: string };
}) {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return (
    <SalesTicketDetailScreen
      saleId={decodeURIComponent(params.saleId)}
      businessId={typeof searchParams?.businessId === "string" ? searchParams.businessId : undefined}
      runtimeSnapshot={runtimeSnapshot}
    />
  );
}
