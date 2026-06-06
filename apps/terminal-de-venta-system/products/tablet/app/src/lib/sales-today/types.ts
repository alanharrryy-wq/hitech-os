export type ReturnLineStatus = "available" | "partial_returned" | "fully_returned";

export type SalesTodayLine = {
  id: string;
  productId: string;
  sku: string;
  productName: string;
  qty: number;
  priceCents: number;
  totalCents: number;
  returnedQty?: number;
  returnAvailableQty?: number;
  returnedCents?: number;
  returnStatus?: ReturnLineStatus;
};

export type SalesTodayTicket = {
  saleId: string;
  folio: string;
  businessId: string;
  terminalId: string;
  cashSessionId: string | null;
  clientRequestId: string | null;
  cashier: string;
  status: string;
  createdAt: string;
  completedAt: string | null;
  paymentMethod: string;
  totalCents: number;
  lineCount: number;
  unitsSold: number;
  lines: SalesTodayLine[];
};

export type SalesTodaySummary = {
  businessId: string;
  terminalId: string | null;
  date: string;
  salesCount: number;
  ticketsClosed: number;
  totalCents: number;
  averageTicketCents: number;
  unitsSold: number;
  topProducts: Array<{ productId: string; sku: string; name: string; qty: number; totalCents: number }>;
  tickets: SalesTodayTicket[];
};
