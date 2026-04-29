import { NextResponse } from "next/server";

export type BackofficeApiOk<T> = {
  ok: true;
  data: T;
  meta: Record<string, unknown>;
};

export type BackofficeApiError = {
  ok: false;
  code: string;
  message: string;
  details: Record<string, unknown>;
};

export function ok<T>(data: T, meta: Record<string, unknown> = {}, init?: ResponseInit) {
  const body: BackofficeApiOk<T> = { ok: true, data, meta };
  return NextResponse.json(body, init);
}

export function fail(code: string, message: string, status = 400, details: Record<string, unknown> = {}) {
  const body: BackofficeApiError = { ok: false, code, message, details };
  return NextResponse.json(body, { status });
}

export function toBackofficeError(error: unknown) {
  const message = error instanceof Error ? error.message : "Error desconocido.";
  return fail("BACKOFFICE_API_ERROR", "No fue posible completar la operación de backoffice.", 500, { message });
}
