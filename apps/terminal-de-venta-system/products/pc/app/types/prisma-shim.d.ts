declare module "@prisma/client" {
  export class PrismaClient {
    product: any;
    barcode: any;
    stockSnapshot: any;
    stockMovement: any;
    purchaseOrder: any;
    receivingReceipt: any;
    auditCount: any;
    replenishmentSignal: any;
    outboxEvent: any;
  }
}
