export function inventoryAccuracy(a:number,b:number){return b<=0?null:a/b}
export function stockState(s:number){return s<=0?'out':s<5?'low':'ok'}
