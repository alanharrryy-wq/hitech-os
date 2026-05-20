import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { readCompleteSaleInput, validatorErrorToMessage } from "@/server/pos-api/validators";
import { posEngineRepository } from "@/server/pos-engine";
import { tabletAuditMeta } from "@/server/pos-security/audit";

import { guardTabletFeatureForApi } from "@/server/licensing/tablet-license-api"; // PRISMA_LICENSE_02AB_TABLET_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function buildTicketEvidence(sale: Awaited<ReturnType<typeof posEngineRepository.completeLocalSale>>) {
  const lookupAliases = [sale.saleId, sale.folio, sale.clientRequestId].filter((value): value is string => Boolean(value));
  return {
    contract: "SALE_AS_TICKET_EVIDENCE_V1",
    canonicalTicketId: sale.saleId,
    saleId: sale.saleId,
    folio: sale.folio,
    businessId: sale.businessId,
    terminalId: sale.terminalId,
    cashSessionId: sale.cashSessionId,
    clientRequestId: sale.clientRequestId,
    status: sale.status,
    completedAt: sale.completedAt?.toISOString() ?? sale.createdAt.toISOString(),
    localDetailHref: `/sales/today/${encodeURIComponent(sale.saleId)}?businessId=${encodeURIComponent(sale.businessId)}`,
    lookupAliases,
    payment: {
      method: sale.paymentMethod,
      cashReceivedCents: sale.cashReceivedCents,
      changeCents: sale.changeCents,
      totalCents: sale.totalCents
    },
    evidenceEventIds: sale.events.map((event) => event.eventId),
    evidenceTopics: sale.events.map((event) => event.topic)
  };
}

export async function POST(request: Request) {
  // PRISMA_LICENSE_02AB_BEGIN:pos.sale.complete
  const prismaLicenseGate = await guardTabletFeatureForApi("pos.sale.complete");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:pos.sale.complete
  try {
    const input = await readCompleteSaleInput(request);
    const sale = await posEngineRepository.completeLocalSale(input);
    const ticketEvidence = buildTicketEvidence(sale);
    const audit = tabletAuditMeta("pos.sale.complete", {
      actorId: sale.cashier,
      role: "tablet_operator",
      terminalId: sale.terminalId,
      businessId: sale.businessId,
      entityType: "Sale",
      entityId: sale.saleId,
      after: {
        status: sale.status,
        totalCents: sale.totalCents,
        lineCount: sale.lines.length
      },
      createdAt: sale.createdAt
    });
    return ok({ sale: { ...sale, ticketEvidence }, ticketEvidence }, { status: 201 }, {
      endpoint: "POST /api/pos/sales/complete",
      businessId: sale.businessId,
      terminalId: sale.terminalId,
      canonicalTicketId: ticketEvidence.canonicalTicketId,
      ticketDetailHref: ticketEvidence.localDetailHref,
      events: sale.events.map((event) => event.topic),
      audit
    });
  } catch (error) {
    const validation = validatorErrorToMessage(error);
    if (validation.code !== "POS_API_VALIDATION_ERROR") {
      return fail(validation.code, validation.message, 400);
    }
    return toPosApiError(error);
  }
}
