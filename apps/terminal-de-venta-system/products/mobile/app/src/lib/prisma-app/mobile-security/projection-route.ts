import { noStoreJsonInit } from "../prisma-app-api-contracts";
import { buildMobilePhase1ReadModel } from "./phase1-read-models";
import {
  buildMobileProjectionEnvelope,
  type MobilePhase1ReadModelId
} from "./projection-envelope";
import { loadAuthorizedMobileState } from "./route-guard";

export async function mobileProjectionJson(
  request: Request,
  readModelId: MobilePhase1ReadModelId
): Promise<Response> {
  const guarded = await loadAuthorizedMobileState(request, readModelId);
  if (!guarded.ok) return guarded.response;

  const data = buildMobilePhase1ReadModel(readModelId, guarded.state, guarded.context);
  const envelope = buildMobileProjectionEnvelope(
    readModelId,
    data,
    guarded.state,
    guarded.context
  );

  const init = noStoreJsonInit();
  const headers = new Headers(init.headers);
  headers.set("Vary", "Authorization, Cookie");
  headers.set("X-Prisma-Mobile-Context-Mode", guarded.context.authorizationMode);

  return Response.json(envelope, { ...init, headers });
}
