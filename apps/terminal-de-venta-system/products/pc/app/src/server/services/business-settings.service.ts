import { prisma } from "@/server/prisma/client";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import { appendWave3Audit } from "@/server/services/wave3-mutation-audit";

type BusinessSettingsInput = { name?: unknown; taxId?: unknown; currency?: unknown };

function settingsView(row: any) {
  return { id: row.id, name: row.name, taxId: row.taxId, currency: row.currency, updatedAt: row.updatedAt };
}

export async function getBusinessSettings() {
  const businessId = await resolvePcBusinessScope();
  const row = await (prisma as any).business.findUnique({ where: { id: businessId } });
  if (!row) throw new Error("SETTINGS_BUSINESS_NOT_FOUND");
  return settingsView(row);
}

export async function updateBusinessSettings(input: BusinessSettingsInput) {
  const businessId = await resolvePcBusinessScope();
  const db = prisma as any;
  const current = await db.business.findUnique({ where: { id: businessId } });
  if (!current) throw new Error("SETTINGS_BUSINESS_NOT_FOUND");
  const data: Record<string, unknown> = {};

  if (input.name !== undefined) {
    const name = typeof input.name === "string" ? input.name.trim() : "";
    if (name.length < 2) throw new Error("SETTINGS_NAME_INVALID");
    data.name = name.slice(0, 180);
  }
  if (input.taxId !== undefined) {
    const taxId = typeof input.taxId === "string" ? input.taxId.trim().toUpperCase() : "";
    data.taxId = taxId ? taxId.slice(0, 32) : null;
  }
  if (input.currency !== undefined) {
    const currency = typeof input.currency === "string" ? input.currency.trim().toUpperCase() : "";
    if (!/^[A-Z]{3}$/.test(currency)) throw new Error("SETTINGS_CURRENCY_INVALID");
    data.currency = currency;
  }
  if (Object.keys(data).length === 0) throw new Error("SETTINGS_UPDATE_EMPTY");

  return db.$transaction(async (tx: any) => {
    const updated = await tx.business.update({ where: { id: businessId }, data });
    await appendWave3Audit(tx, {
      businessId,
      topic: "settings.business.updated",
      entityType: "Business",
      entityId: businessId,
      summary: "Configuración visible del negocio actualizada desde PC Wave 3",
      before: settingsView(current),
      after: settingsView(updated)
    });
    return settingsView(updated);
  });
}
