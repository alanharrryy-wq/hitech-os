import { NextResponse } from "next/server";

export type PosApiOk<T> = {
  ok: true;
  data: T;
  meta?: Record<string, unknown>;
};

export type PosApiError = {
  ok: false;
  code: string;
  message: string;
  details?: Record<string, unknown>;
};

export function ok<T>(data: T, init?: ResponseInit, meta?: Record<string, unknown>) {
  const body: PosApiOk<T> = meta ? { ok: true, data, meta } : { ok: true, data };
  return NextResponse.json(body, init);
}

export function fail(code: string, message: string, status = 400, details: Record<string, unknown> = {}) {
  const body: PosApiError = Object.keys(details).length
    ? { ok: false, code, message, details }
    : { ok: false, code, message };
  return NextResponse.json(body, { status });
}

export function methodNotAllowed(method: string) {
  return fail("METHOD_NOT_ALLOWED", `Metodo no permitido para este recurso POS: ${method}.`, 405, { method });
}
