import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import { appendWave3Audit } from "@/server/services/wave3-mutation-audit";

type DeviceClaimInput = {
  deviceId?: unknown;
  deviceName?: unknown;
  appVersion?: unknown;
  runtimeMode?: unknown;
  operatorLabel?: unknown;
  reason?: unknown;
};

function text(value: unknown, fallback: string, max = 180) {
  const parsed = typeof value === "string" ? value.trim() : "";
  return (parsed || fallback).slice(0, max);
}

function requiredDeviceId(value: unknown) {
  const deviceId = typeof value === "string" ? value.trim() : "";
  if (deviceId.length < 3) throw new Error("DEVICE_ID_REQUIRED");
  return deviceId.slice(0, 160);
}

function heartbeatView(row: any) {
  return {
    id: row.id,
    businessId: row.businessId,
    deviceId: row.deviceId,
    source: row.source,
    surface: row.surface,
    runtimeMode: row.runtimeMode,
    appVersion: row.appVersion,
    licenseStatus: row.licenseStatus,
    syncStatus: row.syncStatus,
    health: row.health,
    status: row.status,
    lastSeenAt: row.lastSeenAt,
    observedAt: row.observedAt,
    metadataJson: row.metadataJson,
    createdAt: row.createdAt,
    updatedAt: row.updatedAt
  };
}

export async function getDurableDeviceClaim(deviceIdRaw: unknown) {
  const businessId = await resolvePcBusinessScope();
  const deviceId = requiredDeviceId(deviceIdRaw);
  const row = await (prisma as any).deviceHeartbeat.findFirst({ where: { businessId, deviceId }, orderBy: { updatedAt: "desc" } });
  return row ? heartbeatView(row) : null;
}

export async function claimDurablePcDevice(input: DeviceClaimInput) {
  const businessId = await resolvePcBusinessScope();
  const deviceId = requiredDeviceId(input.deviceId);
  const now = new Date();
  const db = prisma as any;
  const current = await db.deviceHeartbeat.findFirst({ where: { businessId, deviceId }, orderBy: { updatedAt: "desc" } });
  const metadata = {
    deviceName: text(input.deviceName, "PC Admin"),
    operatorLabel: text(input.operatorLabel, "operator:pc-wave3"),
    claimedAt: now.toISOString(),
    claimOwner: "pc-operational-device-registry",
    wave: 3
  };

  return db.$transaction(async (tx: any) => {
    const row = current
      ? await tx.deviceHeartbeat.update({
          where: { id: current.id },
          data: {
            source: "pc",
            surface: "pc",
            runtimeMode: text(input.runtimeMode, "managed"),
            appVersion: text(input.appVersion, "wave3"),
            licenseStatus: "active",
            syncStatus: "ready",
            health: "healthy",
            status: "claimed",
            lastSeenAt: now,
            observedAt: now,
            metadataJson: JSON.stringify(metadata)
          }
        })
      : await tx.deviceHeartbeat.create({
          data: {
            id: randomUUID(), businessId, deviceId,
            source: "pc", surface: "pc",
            runtimeMode: text(input.runtimeMode, "managed"),
            appVersion: text(input.appVersion, "wave3"),
            schemaVersion: null,
            licenseStatus: "active", syncStatus: "ready",
            health: "healthy", status: "claimed",
            outboxCount: 0,
            lastSeenAt: now, observedAt: now,
            metadataJson: JSON.stringify(metadata)
          }
        });
    await appendWave3Audit(tx, {
      businessId,
      topic: "device.claimed",
      entityType: "DeviceHeartbeat",
      entityId: row.id,
      summary: `Dispositivo ${deviceId} reclamado para PC`,
      before: current ? heartbeatView(current) : null,
      after: heartbeatView(row),
      metadata: { deviceId }
    });
    return heartbeatView(row);
  });
}

export async function revokeDurablePcDevice(input: DeviceClaimInput) {
  const businessId = await resolvePcBusinessScope();
  const deviceId = requiredDeviceId(input.deviceId);
  const reason = text(input.reason, "Revocación operativa confirmada", 240);
  const db = prisma as any;
  const current = await db.deviceHeartbeat.findFirst({ where: { businessId, deviceId }, orderBy: { updatedAt: "desc" } });
  if (!current) return null;
  if (current.status === "revoked") return heartbeatView(current);
  const now = new Date();
  let metadata: Record<string, unknown> = {};
  try { metadata = current.metadataJson ? JSON.parse(current.metadataJson) : {}; } catch { metadata = {}; }
  metadata = { ...metadata, revokedAt: now.toISOString(), revokeReason: reason, wave: 3 };

  return db.$transaction(async (tx: any) => {
    const row = await tx.deviceHeartbeat.update({
      where: { id: current.id },
      data: { status: "revoked", health: "revoked", syncStatus: "revoked", observedAt: now, metadataJson: JSON.stringify(metadata) }
    });
    await appendWave3Audit(tx, {
      businessId,
      topic: "device.revoked",
      entityType: "DeviceHeartbeat",
      entityId: row.id,
      summary: `Dispositivo ${deviceId} revocado desde PC`,
      before: heartbeatView(current),
      after: heartbeatView(row),
      metadata: { deviceId, reason }
    });
    return heartbeatView(row);
  });
}
