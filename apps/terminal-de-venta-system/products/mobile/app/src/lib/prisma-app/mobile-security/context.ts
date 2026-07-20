import { createHmac, randomUUID, timingSafeEqual } from "node:crypto";
import { z } from "zod";
import { getMobileDataPlaneConfig, type MobileDataPlaneConfigOverrides } from "../mobile-data-plane/config";

export const PRISMA_MOBILE_SESSION_COOKIE = "prisma.mobile.session";
export const PRISMA_MOBILE_SESSION_CONTRACT = "PRISMA_MOBILE_SESSION_V1";
export const MOBILE_READ_ALL_PERMISSION = "MOBILE.READ.ALL";

const MobileSessionPayloadSchema = z.object({
  contractVersion: z.literal(PRISMA_MOBILE_SESSION_CONTRACT),
  sessionId: z.string().min(8),
  sessionVersion: z.number().int().positive(),
  actorId: z.string().min(1),
  roleIds: z.array(z.string().min(1)).min(1),
  permissionScopes: z.array(z.string().min(1)).default([]),
  tenantId: z.string().min(1),
  businessId: z.string().min(1),
  branchId: z.string().min(1).nullable().optional(),
  terminalId: z.string().min(1),
  deviceId: z.string().min(1),
  licenseId: z.string().min(1),
  customerId: z.string().min(1),
  businessName: z.string().min(1),
  planLabel: z.string().min(1),
  issuedAt: z.string().min(1),
  expiresAt: z.string().min(1)
});

export type MobileSessionPayload = z.infer<typeof MobileSessionPayloadSchema>;
export type MobileAuthorizationMode = "signed-session" | "development-loopback";

export type MobileRequestContext = MobileSessionPayload & {
  authorizationMode: MobileAuthorizationMode;
  traceId: string;
};

type MobileContextFailure = {
  ok: false;
  response: Response;
};

type MobileContextSuccess = {
  ok: true;
  context: MobileRequestContext;
};

export type MobileContextResult = MobileContextSuccess | MobileContextFailure;

const DEVELOPMENT_READ_PERMISSIONS = [
  MOBILE_READ_ALL_PERMISSION,
  "MOBILE.SNAPSHOT.LEGACY.READ",
  "RM.SYSTEM.SUMMARY",
  "RM.DATA.READINESS",
  "RM.SYNC.SOURCE_HEALTH",
  "RM.BUSINESS.EXECUTIVE_SUMMARY",
  "RM.SALES.SUMMARY",
  "RM.RISK.DETAIL",
  "RM.CONTEXT.ACTIVE",
  "RM.CASH.SUMMARY",
  "RM.INVENTORY.WATCHLIST",
  "RM.DAILY_BRIEF",
  "RM.ACTION.INBOX",
  "RM.DECISION_LEDGER.LIST",
  "RM.HEALTH.RADAR",
  "RM.ACTIVITY.TIMELINE"
] as const;

function jsonError(status: number, code: string, message: string, traceId: string): Response {
  return Response.json(
    {
      ok: false,
      error: { code, message, traceId },
      meta: {
        contractVersion: PRISMA_MOBILE_SESSION_CONTRACT,
        generatedAt: new Date().toISOString()
      }
    },
    {
      status,
      headers: {
        "Cache-Control": "no-store, max-age=0",
        "Content-Type": "application/json; charset=utf-8",
        "Vary": "Authorization, Cookie"
      }
    }
  );
}

function readCookie(cookieHeader: string | null, name: string): string | null {
  if (!cookieHeader) return null;
  for (const part of cookieHeader.split(";")) {
    const separator = part.indexOf("=");
    if (separator < 0) continue;
    const key = part.slice(0, separator).trim();
    if (key !== name) continue;
    const raw = part.slice(separator + 1).trim();
    try {
      return decodeURIComponent(raw);
    } catch {
      return raw;
    }
  }
  return null;
}

function readSessionToken(request: Request): string | null {
  const authorization = request.headers.get("authorization")?.trim();
  if (authorization?.toLowerCase().startsWith("bearer ")) {
    return authorization.slice(7).trim() || null;
  }
  return readCookie(request.headers.get("cookie"), PRISMA_MOBILE_SESSION_COOKIE);
}

function decodeSignedSession(token: string, secret: string): MobileSessionPayload | null {
  const segments = token.split(".");
  if (segments.length !== 2) return null;
  const [payloadSegment, signatureSegment] = segments;
  if (!payloadSegment || !signatureSegment) return null;

  let suppliedSignature: Buffer;
  let payloadBytes: Buffer;
  try {
    suppliedSignature = Buffer.from(signatureSegment, "base64url");
    payloadBytes = Buffer.from(payloadSegment, "base64url");
  } catch {
    return null;
  }

  const expectedSignature = createHmac("sha256", secret).update(payloadSegment).digest();
  if (suppliedSignature.length !== expectedSignature.length) return null;
  if (!timingSafeEqual(suppliedSignature, expectedSignature)) return null;

  try {
    return MobileSessionPayloadSchema.parse(JSON.parse(payloadBytes.toString("utf8")));
  } catch {
    return null;
  }
}

function isLoopbackHost(value: string): boolean {
  const host = value.trim().toLowerCase().replace(/^\[/, "").replace(/\]$/, "");
  return host === "localhost" || host === "127.0.0.1" || host === "::1";
}

function isDevelopmentLoopback(request: Request): boolean {
  if (process.env.NODE_ENV === "production") return false;
  if (process.env.PRISMA_MOBILE_DEV_LOOPBACK_CONTEXT === "disabled") return false;

  let hostname = "";
  try {
    hostname = new URL(request.url).hostname;
  } catch {
    return false;
  }
  if (!isLoopbackHost(hostname)) return false;

  const forwardedHost = request.headers.get("x-forwarded-host");
  if (!forwardedHost) return true;
  const firstForwardedHost = forwardedHost.split(",")[0]?.trim() ?? "";
  const hostWithoutPort = firstForwardedHost.startsWith("[")
    ? firstForwardedHost.slice(1, firstForwardedHost.indexOf("]"))
    : firstForwardedHost.split(":")[0] ?? "";
  return isLoopbackHost(hostWithoutPort);
}

function developmentContext(traceId: string): MobileRequestContext {
  const config = getMobileDataPlaneConfig();
  const now = Date.now();
  return {
    contractVersion: PRISMA_MOBILE_SESSION_CONTRACT,
    sessionId: "session_mobile_development_loopback",
    sessionVersion: 1,
    actorId: config.actorId,
    roleIds: ["ROLE.MOBILE.OWNER"],
    permissionScopes: [...DEVELOPMENT_READ_PERMISSIONS],
    tenantId: config.tenantId,
    businessId: config.businessId,
    branchId: config.branchId,
    terminalId: config.terminalId,
    deviceId: config.mobileDeviceId,
    licenseId: config.licenseId,
    customerId: config.customerId,
    businessName: config.businessName,
    planLabel: config.planLabel,
    issuedAt: new Date(now - 1_000).toISOString(),
    expiresAt: new Date(now + 15 * 60_000).toISOString(),
    authorizationMode: "development-loopback",
    traceId
  };
}

function validateSessionTimes(payload: MobileSessionPayload): boolean {
  const now = Date.now();
  const issuedAt = Date.parse(payload.issuedAt);
  const expiresAt = Date.parse(payload.expiresAt);
  if (!Number.isFinite(issuedAt) || !Number.isFinite(expiresAt)) return false;
  if (issuedAt > now + 5 * 60_000) return false;
  return expiresAt > now;
}

export function resolveMobileRequestContext(request: Request): MobileContextResult {
  const traceId = request.headers.get("x-request-id")?.trim().slice(0, 128) || randomUUID();
  const token = readSessionToken(request);

  if (token) {
    const secret = process.env.PRISMA_MOBILE_SESSION_SECRET?.trim();
    if (!secret || secret.length < 32) {
      return {
        ok: false,
        response: jsonError(503, "ERR.AUTH.CONFIGURATION", "La sesión Mobile no está disponible.", traceId)
      };
    }

    const payload = decodeSignedSession(token, secret);
    if (!payload || !validateSessionTimes(payload)) {
      return {
        ok: false,
        response: jsonError(401, "ERR.AUTH.REQUIRED", "La sesión Mobile no es válida o expiró.", traceId)
      };
    }

    return {
      ok: true,
      context: {
        ...payload,
        authorizationMode: "signed-session",
        traceId
      }
    };
  }

  if (isDevelopmentLoopback(request)) {
    return { ok: true, context: developmentContext(traceId) };
  }

  return {
    ok: false,
    response: jsonError(401, "ERR.AUTH.REQUIRED", "Se requiere una sesión Mobile autorizada.", traceId)
  };
}

export function authorizeMobileRead(context: MobileRequestContext, permissionScope: string): Response | null {
  if (
    context.permissionScopes.includes(MOBILE_READ_ALL_PERMISSION) ||
    context.permissionScopes.includes(permissionScope)
  ) {
    return null;
  }

  return jsonError(
    403,
    "ERR.PERMISSION.DENIED",
    "La sesión no tiene permiso para esta proyección.",
    context.traceId
  );
}

export function mobileContextToConfigOverrides(context: MobileRequestContext): MobileDataPlaneConfigOverrides {
  return {
    actorId: context.actorId,
    tenantId: context.tenantId,
    businessId: context.businessId,
    branchId: context.branchId ?? null,
    terminalId: context.terminalId,
    licenseId: context.licenseId,
    mobileDeviceId: context.deviceId,
    customerId: context.customerId,
    businessName: context.businessName,
    planLabel: context.planLabel,
    authorizationLabel:
      context.authorizationMode === "signed-session"
        ? "Sesión Mobile autorizada"
        : "Contexto sintético de desarrollo local"
  };
}
