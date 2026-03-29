import { ALL_LAYERS, LAYER_DATA_ATTRIBUTES, type LayerFlags, type LayerProfile } from "./layerIds.js";
import type { LayerResolutionSource } from "./resolveLayerFlags.js";

type LayerDomTarget = Pick<Element, "setAttribute" | "removeAttribute">;

interface AppliedDomState {
  enabledAttributes: Set<string>;
  source: string;
  profile: string;
}

export interface ApplyLayerFlagsToDomInput {
  readonly flags: LayerFlags;
  readonly source?: LayerResolutionSource;
  readonly profile?: LayerProfile | string | null;
  readonly target?: LayerDomTarget;
}

export const LAYER_DOM_METADATA_SOURCE_ATTRIBUTE = "data-layer-source";
export const LAYER_DOM_METADATA_PROFILE_ATTRIBUTE = "data-layer-profile";

const APPLIED_STATE = new WeakMap<LayerDomTarget, AppliedDomState>();

function resolveTarget(target?: LayerDomTarget): LayerDomTarget | undefined {
  if (target) {
    return target;
  }

  if (typeof document === "undefined") {
    return undefined;
  }

  return document.documentElement;
}

function normalizeSource(source: LayerResolutionSource | undefined): string {
  if (source === "profile" || source === "layers" || source === "mixed") {
    return source;
  }

  return "defaults";
}

function normalizeProfile(profile: LayerProfile | string | null | undefined): string {
  if (!profile) {
    return "none";
  }

  const trimmed = profile.trim();
  return trimmed.length > 0 ? trimmed : "none";
}

export function applyLayerFlagsToDom(input: ApplyLayerFlagsToDomInput): void {
  const target = resolveTarget(input.target);
  if (!target) {
    return;
  }

  const previous = APPLIED_STATE.get(target) ?? {
    enabledAttributes: new Set<string>(),
    source: "",
    profile: ""
  };

  const nextEnabledAttributes = new Set<string>();
  for (const id of ALL_LAYERS) {
    if (!input.flags[id]) {
      continue;
    }

    nextEnabledAttributes.add(LAYER_DATA_ATTRIBUTES[id]);
  }

  for (const attribute of previous.enabledAttributes) {
    if (!nextEnabledAttributes.has(attribute)) {
      target.removeAttribute(attribute);
    }
  }

  for (const attribute of nextEnabledAttributes) {
    if (!previous.enabledAttributes.has(attribute)) {
      target.setAttribute(attribute, "1");
    }
  }

  const nextSource = normalizeSource(input.source);
  if (previous.source !== nextSource) {
    target.setAttribute(LAYER_DOM_METADATA_SOURCE_ATTRIBUTE, nextSource);
  }

  const nextProfile = normalizeProfile(input.profile);
  if (previous.profile !== nextProfile) {
    target.setAttribute(LAYER_DOM_METADATA_PROFILE_ATTRIBUTE, nextProfile);
  }

  APPLIED_STATE.set(target, {
    enabledAttributes: nextEnabledAttributes,
    source: nextSource,
    profile: nextProfile
  });
}

export function clearLayerFlagsFromDom(target?: LayerDomTarget): void {
  const resolvedTarget = resolveTarget(target);
  if (!resolvedTarget) {
    return;
  }

  const previous = APPLIED_STATE.get(resolvedTarget);
  if (previous) {
    for (const attribute of previous.enabledAttributes) {
      resolvedTarget.removeAttribute(attribute);
    }
  } else {
    for (const id of ALL_LAYERS) {
      resolvedTarget.removeAttribute(LAYER_DATA_ATTRIBUTES[id]);
    }
  }

  resolvedTarget.removeAttribute(LAYER_DOM_METADATA_SOURCE_ATTRIBUTE);
  resolvedTarget.removeAttribute(LAYER_DOM_METADATA_PROFILE_ATTRIBUTE);
  APPLIED_STATE.delete(resolvedTarget);
}
