import { z } from "zod";

export type Brand<TValue, TBrand extends string> = TValue & {
  readonly __brand: TBrand;
};

const ID_PATTERN = /^[a-z]+_[a-z0-9][a-z0-9-]{3,63}$/;

export const RunIdSchema = z.string().regex(/^run_[a-z0-9][a-z0-9-]{3,63}$/);
export const EvidenceIdSchema = z.string().regex(/^evi_[a-z0-9][a-z0-9-]{3,63}$/);
export const WidgetIdSchema = z.string().regex(/^wid_[a-z0-9][a-z0-9-]{3,63}$/);
export const UserIdSchema = z.string().regex(/^usr_[a-z0-9][a-z0-9-]{3,63}$/);

export type RunId = Brand<string, "RunId">;
export type EvidenceId = Brand<string, "EvidenceId">;
export type WidgetId = Brand<string, "WidgetId">;
export type UserId = Brand<string, "UserId">;

function assertGenericId(input: string): string {
  if (!ID_PATTERN.test(input)) {
    throw new Error(`Invalid branded identifier: ${input}`);
  }
  return input;
}

export function asRunId(input: string): RunId {
  return RunIdSchema.parse(assertGenericId(input)) as RunId;
}

export function asEvidenceId(input: string): EvidenceId {
  return EvidenceIdSchema.parse(assertGenericId(input)) as EvidenceId;
}

export function asWidgetId(input: string): WidgetId {
  return WidgetIdSchema.parse(assertGenericId(input)) as WidgetId;
}

export function asUserId(input: string): UserId {
  return UserIdSchema.parse(assertGenericId(input)) as UserId;
}

export function runId(input: string): RunId {
  return asRunId(input);
}

export function evidenceId(input: string): EvidenceId {
  return asEvidenceId(input);
}

export function widgetId(input: string): WidgetId {
  return asWidgetId(input);
}

export function userId(input: string): UserId {
  return asUserId(input);
}

export function isRunId(input: string): input is RunId {
  return RunIdSchema.safeParse(input).success;
}

export function isEvidenceId(input: string): input is EvidenceId {
  return EvidenceIdSchema.safeParse(input).success;
}

export function isWidgetId(input: string): input is WidgetId {
  return WidgetIdSchema.safeParse(input).success;
}

export function isUserId(input: string): input is UserId {
  return UserIdSchema.safeParse(input).success;
}

export function toPlainId(input: RunId | EvidenceId | WidgetId | UserId): string {
  return input;
}
