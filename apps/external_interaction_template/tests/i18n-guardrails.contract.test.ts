import { describe, expect, it } from "vitest";

import { stateDescription, stateLabel } from "@/lib/core/record-view";
import { getTranslator } from "@/lib/i18n/dictionary";
import { mapDispatchStatusLabel, mapRecordStateDescription, mapRecordStateLabel, mapSyncStatusLabel } from "@/lib/i18n/enum-labels";

describe("i18n guardrails", () => {
  it("centralizes record state labels and descriptions by locale", () => {
    expect(stateLabel("awaiting_update", "es")).toBe("Requiere actualización");
    expect(stateLabel("awaiting_update", "en")).toBe("Needs update");
    expect(stateDescription("approved", "es")).toBe("Aprobado y listo para despacho.");
    expect(stateDescription("approved", "en")).toBe("Approved and ready for dispatch.");
  });

  it("maps sync and dispatch statuses through a shared translator", () => {
    const tEs = getTranslator("es");
    const tEn = getTranslator("en");

    expect(mapRecordStateLabel("submitted", tEs)).toBe("Enviado");
    expect(mapRecordStateDescription("submitted", tEn)).toBe("Waiting for reviewer triage.");
    expect(mapDispatchStatusLabel("running", tEs)).toBe("En ejecución");
    expect(mapSyncStatusLabel("retryable", tEn)).toBe("Retryable");
  });
});
