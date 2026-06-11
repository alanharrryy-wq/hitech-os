import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { prisma } from "@/server/prisma/client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const stores = await prisma.store.findMany({
      include: { terminals: true },
      orderBy: { name: "asc" },
      take: 100
    });
    return ok({
      branches: stores.map((store) => ({
        id: store.id,
        businessId: store.businessId,
        code: store.code,
        name: store.name,
        terminals: store.terminals.map((terminal) => ({
          id: terminal.id,
          code: terminal.code,
          name: terminal.name,
          isActive: terminal.isActive
        }))
      }))
    }, { endpoint: "GET /api/backoffice/branches", source: "pc.canonical.store-terminal", readOnly: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}
