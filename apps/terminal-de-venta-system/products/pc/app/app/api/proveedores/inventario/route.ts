import { NextResponse } from "next/server";
import { getSupplierInventoryBridgeSnapshot } from "@/lib/suppliers/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const inventoryBridge = await getSupplierInventoryBridgeSnapshot();
  return NextResponse.json({
    ok: true,
    data: inventoryBridge,
    meta: {
      source: "pc.suppliers.inventory_bridge.v11",
      language: "es-MX",
      rule: "Proveedores lee señales de inventario cuando están disponibles; si no, declara fuente alternativa."
    }
  });
}
