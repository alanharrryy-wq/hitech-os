import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { SalesHistoryScreen } from "./sales-history-screen";
import { SalesTicketDetailScreen } from "./sales-ticket-detail-screen";
import { SalesTodayScreen } from "./sales-today-screen";

export type SalesWorkspaceView = "today" | "history" | "today-detail" | "history-detail";

export function SalesWorkspace({
  view,
  saleId,
  businessId,
  runtimeSnapshot
}: {
  view: SalesWorkspaceView;
  saleId?: string;
  businessId?: string;
  runtimeSnapshot?: TabletRuntimeSnapshot;
}) {
  if (view === "history") return <SalesHistoryScreen runtimeSnapshot={runtimeSnapshot} />;
  if (view === "today-detail" && saleId) {
    return <SalesTicketDetailScreen saleId={saleId} businessId={businessId} runtimeSnapshot={runtimeSnapshot} />;
  }
  if (view === "history-detail" && saleId) {
    return (
      <SalesTicketDetailScreen
        saleId={saleId}
        businessId={businessId}
        runtimeSnapshot={runtimeSnapshot}
        currentPath="/sales/history"
        backHref="/sales/history"
      />
    );
  }
  return <SalesTodayScreen runtimeSnapshot={runtimeSnapshot} />;
}
