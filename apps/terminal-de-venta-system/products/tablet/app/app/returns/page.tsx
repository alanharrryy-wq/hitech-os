import { ReturnsLandingScreen } from "@components/returns/return-from-ticket-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Devoluciones - PRISMA Tablet",
  description: "Pantalla operativa para iniciar devoluciones desde tickets cerrados."
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

export default async function ReturnsPage({ searchParams }: { searchParams?: Promise<SearchParams> | SearchParams }) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const runtimeInput = readRuntimeSnapshotInput(toUrlSearchParams(resolvedSearchParams));
  const runtimeSnapshot = await getTabletRuntimeSnapshot(runtimeInput);
  const businessId = typeof resolvedSearchParams.businessId === "string" ? resolvedSearchParams.businessId : runtimeInput.businessId;

  return <ReturnsLandingScreen businessId={businessId} runtimeSnapshot={runtimeSnapshot} />;
}
