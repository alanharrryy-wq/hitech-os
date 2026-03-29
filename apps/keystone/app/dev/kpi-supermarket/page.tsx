import { notFound } from "next/navigation";
import { KpiSupermarketClient } from "./KpiSupermarketClient";

export const dynamic = "force-dynamic";
export const fetchCache = "force-no-store";

function assertDevOnlyRoute(): void {
  if (process.env.NODE_ENV === "production") {
    notFound();
  }
}

export default function KpiSupermarketPage() {
  assertDevOnlyRoute();

  return <KpiSupermarketClient />;
}
