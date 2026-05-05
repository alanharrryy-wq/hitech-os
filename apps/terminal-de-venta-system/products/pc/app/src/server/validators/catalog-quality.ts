export function hasMissingBarcode(p:{barcode:string|null,isActive:boolean}){return p.isActive&&!p.barcode}
