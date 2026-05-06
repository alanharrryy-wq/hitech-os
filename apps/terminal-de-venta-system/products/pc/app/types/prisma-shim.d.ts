declare module "@prisma/client" {
  export class PrismaClient {
    constructor(options?: any);
    $disconnect(): Promise<void>;
    $executeRawUnsafe(query: string, ...values: any[]): Promise<any>;
    business: any;
    store: any;
    terminal: any;
    taxRate: any;
    priceList: any;
    priceListItem: any;
    product: any;
    barcode: any;
    stockSnapshot: any;
    stockMovement: any;
    supplier: any;
    purchaseOrder: any;
    purchaseOrderLine: any;
    goodsReceipt: any;
    goodsReceiptLine: any;
    auditCount: any;
    replenishmentSignal: any;
    cashSession: any;
    cashMovement: any;
    sale: any;
    saleLine: any;
    saleReturn: any;
    outboxEvent: any;
  }
}
