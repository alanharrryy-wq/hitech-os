export function suggestedReplenishment(current:number,min:number|null,max:number|null){if(min==null||current>min)return 0; return Math.max(0,(max??min*2)-current)}
