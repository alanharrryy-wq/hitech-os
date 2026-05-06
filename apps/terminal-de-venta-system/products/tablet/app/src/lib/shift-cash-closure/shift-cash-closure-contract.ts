export type ShiftStatus = "OPEN" | "CLOSED";
export type ShiftCashSummary = { id:string; businessId:string; storeId:string; terminalId:string; cashierId:string; cashier:string; status:ShiftStatus; openedAt:string; closedAt:string|null; cashStartCents:number; cashEndCents:number|null; expectedCashCents:number; varianceCents:number|null; salesCount:number; salesTotalCents:number; movementCount:number; canSell:boolean; canClose:boolean; operatorMessage:string; };
export type ShiftKpi = { label:string; value:string; hint:string; };
export const SHIFT_VISIBLE_COPY = { noShiftTitle:"Abre turno antes de vender", openShiftTitle:"Turno abierto y caja controlada", closedShiftTitle:"Turno cerrado", noShiftBadge:"Sin turno", openShiftBadge:"Turno abierto", closedShiftBadge:"Turno cerrado" } as const;
