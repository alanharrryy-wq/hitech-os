import { loadMobileDataPlaneState } from "../mobile-data-plane/state-loader";
import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import {
  authorizeMobileRead,
  mobileContextToConfigOverrides,
  resolveMobileRequestContext,
  type MobileRequestContext
} from "./context";
import { sanitizeMobileProbes, sanitizeMobileWarnings } from "./sanitize";

type AuthorizedMobileState = {
  ok: true;
  context: MobileRequestContext;
  state: MobileDataPlaneState;
  safeWarnings: string[];
  safeProbes: MobileDataPlaneState["probes"];
};

type RejectedMobileState = {
  ok: false;
  response: Response;
};

export type AuthorizedMobileStateResult = AuthorizedMobileState | RejectedMobileState;

export async function loadAuthorizedMobileState(
  request: Request,
  permissionScope: string
): Promise<AuthorizedMobileStateResult> {
  const resolved = resolveMobileRequestContext(request);
  if (!resolved.ok) return resolved;

  const denied = authorizeMobileRead(resolved.context, permissionScope);
  if (denied) return { ok: false, response: denied };

  const state = await loadMobileDataPlaneState(mobileContextToConfigOverrides(resolved.context));
  return {
    ok: true,
    context: resolved.context,
    state,
    safeWarnings: sanitizeMobileWarnings(state.warnings),
    safeProbes: sanitizeMobileProbes(state.probes)
  };
}
