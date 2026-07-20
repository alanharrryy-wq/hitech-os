import { deriveMobileDataReadiness } from "../mobile-data-plane/data-readiness";
import {
  buildSalesTodayPayload,
  buildSummaryPayload
} from "../mobile-data-plane/payload-builders";
import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import type { MobileRequestContext } from "./context";
import type { MobilePhase1ReadModelId } from "./projection-envelope";
import { sanitizeMobileDiagnosticText } from "./sanitize";

function sanitizedSources(state: MobileDataPlaneState) {
  return state.sourceStatuses.map((source) => ({
    id: source.id,
    status: source.status,
    lastSeenAt: source.lastSeenAt,
    freshnessSeconds: source.freshnessSeconds,
    latencyMs: source.latencyMs,
    errorCount: source.errorCount,
    lastError: sanitizeMobileDiagnosticText(source.lastError),
    warnings: source.warnings
      .map((warning) => sanitizeMobileDiagnosticText(warning))
      .filter((warning): warning is string => Boolean(warning))
  }));
}

export function buildMobilePhase1ReadModel(
  readModelId: MobilePhase1ReadModelId,
  state: MobileDataPlaneState,
  context: MobileRequestContext
): unknown {
  switch (readModelId) {
    case "RM.SYSTEM.SUMMARY":
      return {
        context: {
          tenantId: context.tenantId,
          businessId: context.businessId,
          branchId: context.branchId ?? null,
          terminalId: context.terminalId ?? null
        },
        device: {
          deviceId: context.deviceId,
          state:
            context.authorizationMode === "signed-session"
              ? "STA.DEVICE.CLAIMED"
              : "STA.DEVICE.DEVELOPMENT_CONTEXT"
        },
        license: {
          licenseId: context.licenseId,
          state:
            context.authorizationMode === "signed-session"
              ? "STA.LICENSE.SESSION_VERIFIED"
              : "STA.LICENSE.DEVELOPMENT_CONTEXT"
        },
        runtimeMode: state.runtimeMode,
        sources: sanitizedSources(state)
      };

    case "RM.DATA.READINESS":
      return deriveMobileDataReadiness(state);

    case "RM.SYNC.SOURCE_HEALTH":
      return {
        runtimeMode: state.runtimeMode,
        outbox: {
          pending: state.outbox.pending,
          failed: state.outbox.failed,
          acknowledged: state.outbox.acked,
          lastSyncedAt: state.outbox.lastSyncedAt,
          oldestPendingAt: state.outbox.oldestPendingAt
        },
        sources: sanitizedSources(state).filter(
          (source) => source.id === "tablet" || source.id === "pc"
        ),
        conflictState:
          state.outbox.failed > 0 ? "STA.SYNC.CONFLICT_REVIEW_REQUIRED" : "STA.SYNC.NO_CONFIRMED_CONFLICT"
      };

    case "RM.BUSINESS.EXECUTIVE_SUMMARY": {
      const summary = buildSummaryPayload(state);
      return {
        businessName: summary.businessName,
        health: summary.health,
        urgentAlerts: summary.urgentAlerts,
        branchesToReview: summary.branchesToReview,
        dataReadiness: summary.dataReadiness,
        kpis: summary.kpis
      };
    }

    case "RM.SALES.SUMMARY": {
      const sales = buildSalesTodayPayload(state);
      return {
        totalSalesCents: sales.totalSalesCents,
        totalSalesLabel: sales.totalSalesLabel,
        tickets: sales.tickets,
        averageTicketCents: sales.averageTicketCents,
        averageTicketLabel: sales.averageTicketLabel,
        deltaAgainstYesterday: sales.deltaAgainstYesterday,
        strongCategory: sales.strongCategory,
        recentActivity: sales.recentActivity
      };
    }
  }
}
