import { ReturnFromTicketScreen } from "@components/returns/return-from-ticket-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Devolución desde ticket - PRISMA Tablet",
  description: "Flujo contextual para devolver productos de un ticket cerrado."
};

type SearchParams = Record<string, string | string[] | undefined>;

function toUrlSearchParams(searchParams: SearchParams) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(searchParams)) {
    if (Array.isArray(value)) {
      for (const item of value) params.append(key, item);
    } else if (typeof value === "string") {
      params.set(key, value);
    }
  }
  return params;
}

export default async function Page({
  params,
  searchParams
}: {
  params: Promise<{ saleId: string }> | { saleId: string };
  searchParams?: Promise<SearchParams> | SearchParams;
}) {
  const resolvedParams = await params;
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const runtimeInput = readRuntimeSnapshotInput(toUrlSearchParams(resolvedSearchParams));
  const runtimeSnapshot = await getTabletRuntimeSnapshot(runtimeInput);
  const businessId = typeof resolvedSearchParams.businessId === "string" ? resolvedSearchParams.businessId : runtimeInput.businessId;

  return (
    <ReturnFromTicketScreen
      saleId={decodeURIComponent(resolvedParams.saleId)}
      businessId={businessId}
      runtimeSnapshot={runtimeSnapshot}
    />
  );
}
