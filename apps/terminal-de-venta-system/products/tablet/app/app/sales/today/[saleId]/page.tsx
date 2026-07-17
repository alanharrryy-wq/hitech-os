import { SalesWorkspace } from "@components/sales/sales-workspace";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ saleId: string }> | { saleId: string };
  searchParams?: Promise<{ businessId?: string }> | { businessId?: string };
}) {
  const resolvedParams = await params;
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return (
    <SalesWorkspace
      view="today-detail"
      saleId={decodeURIComponent(resolvedParams.saleId)}
      businessId={typeof resolvedSearchParams.businessId === "string" ? resolvedSearchParams.businessId : undefined}
      runtimeSnapshot={runtimeSnapshot}
    />
  );
}
