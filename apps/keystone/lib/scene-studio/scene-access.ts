import type { SearchParamsLike } from "@hitech/ui-kit";

function firstParam(value: string | string[] | undefined): string | undefined {
  if (typeof value === "string") {
    return value;
  }

  if (Array.isArray(value)) {
    return value[0];
  }

  return undefined;
}

export interface SceneStudioAccessResult {
  readonly allowed: boolean;
  readonly debugEnabled: boolean;
  readonly envEnabled: boolean;
}

export function resolveSceneStudioAccess(searchParams?: SearchParamsLike): SceneStudioAccessResult {
  const debugEnabled = firstParam(searchParams?.["debug"]) === "1";
  const envEnabled = process.env["NEXT_PUBLIC_SCENE_STUDIO"] === "1";

  const allowed =
    process.env["NODE_ENV"] !== "production" &&
    (debugEnabled || envEnabled);

  return {
    allowed,
    debugEnabled,
    envEnabled
  };
}
