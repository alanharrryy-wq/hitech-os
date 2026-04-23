import { headers } from "next/headers";

import { type ActorContext } from "@/lib/core/types";

function normalizeRole(value: string | undefined): ActorContext["role"] {
  if (!value) return "public";
  return ["public", "external_user", "reviewer", "approver", "operator"].includes(value)
    ? (value as ActorContext["role"])
    : "public";
}

export async function getActorFromHeaders(): Promise<ActorContext> {
  const headerStore = await headers();
  const role = normalizeRole(headerStore.get("x-actor-role") ?? undefined);

  const actor: ActorContext = {
    role,
    authenticated: headerStore.get("x-authenticated") === "true"
  };

  const actorId = headerStore.get("x-actor-id");
  const actorLabel = headerStore.get("x-actor-label");
  const token = headerStore.get("x-flow-token");

  if (actorId) actor.actorId = actorId;
  if (actorLabel) actor.actorLabel = actorLabel;
  if (token) actor.token = token;

  return actor;
}

export function getActorFromPayload(payload: Record<string, unknown>): ActorContext {
  const role = normalizeRole(typeof payload["role"] === "string" ? (payload["role"] as string) : undefined);

  const actor: ActorContext = {
    role,
    authenticated: payload["authenticated"] === true
  };

  if (typeof payload["actorId"] === "string") {
    actor.actorId = payload["actorId"];
  }
  if (typeof payload["actorLabel"] === "string") {
    actor.actorLabel = payload["actorLabel"];
  }
  if (typeof payload["token"] === "string") {
    actor.token = payload["token"];
  }

  return actor;
}
