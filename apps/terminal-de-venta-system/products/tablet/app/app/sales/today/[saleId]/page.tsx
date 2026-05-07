import { SalesTicketDetailScreen } from "@components/sales/sales-ticket-detail-screen";

export default function Page({
  params,
  searchParams,
}: {
  params: { saleId: string };
  searchParams?: { businessId?: string };
}) {
  return (
    <SalesTicketDetailScreen
      saleId={decodeURIComponent(params.saleId)}
      businessId={typeof searchParams?.businessId === "string" ? searchParams.businessId : undefined}
    />
  );
}
