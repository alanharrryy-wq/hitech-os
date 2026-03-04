"use client";

import type { PropsWithChildren } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  ALL_LAYERS,
  applyLayerPreset,
  createAllLayersOff,
  createAllLayersOn,
  mergeLayerFlags,
  type LayerFlags,
  type LayerId,
  type LayerProfile
} from "./layerIds.js";
import {
  createLayerFlagsQueryFromResolved,
  deriveLayerResolutionSource,
  encodeLayersParam,
  type LayerBaseSource,
  type LayerMotionSource,
  type ResolvedLayerFlags
} from "./resolveLayerFlags.js";
import { applyLayerFlagsToDom, clearLayerFlagsFromDom } from "./applyLayerFlagsToDom.js";
import { extractEnabledLayerIds, LayerFlagsContext } from "./useLayerFlags.js";

export interface LayerFlagsProviderProps extends PropsWithChildren {
  readonly initialResolved: ResolvedLayerFlags;
}

function getResolvedSignature(resolved: ResolvedLayerFlags): string {
  const enabled = ALL_LAYERS.filter((id) => resolved.flags[id]).join(",");
  return [
    resolved.source,
    resolved.baseSource,
    resolved.motionSource,
    resolved.profile,
    resolved.debug ? "1" : "0",
    enabled,
    resolved.unknownTokens.join(",")
  ].join("|");
}

function shouldPersistMotion(input: {
  readonly flags: LayerFlags;
  readonly motionSource: LayerMotionSource;
}): boolean {
  if (input.motionSource === "motion") {
    return true;
  }

  return input.flags["motion.enabled"];
}

function createRawFromState(input: {
  readonly flags: LayerFlags;
  readonly profile: LayerProfile;
  readonly debug: boolean;
  readonly baseSource: LayerBaseSource;
  readonly motionSource: LayerMotionSource;
}): ResolvedLayerFlags["raw"] {
  const includeMotion = shouldPersistMotion(input);

  return {
    ...(input.baseSource === "layers" ? { layers: encodeLayersParam(input.flags) } : {}),
    ...(input.baseSource === "profile" ? { layerProfile: input.profile } : {}),
    ...(includeMotion ? { motion: input.flags["motion.enabled"] ? "on" : "off" } : {}),
    ...(input.debug ? { debug: "1" } : {})
  };
}

function createResolvedState(input: {
  readonly flags: LayerFlags;
  readonly profile: LayerProfile;
  readonly debug: boolean;
  readonly baseSource: LayerBaseSource;
  readonly motionSource: LayerMotionSource;
}): ResolvedLayerFlags {
  return {
    flags: input.flags,
    profile: input.profile,
    debug: input.debug,
    source: deriveLayerResolutionSource(input.baseSource, input.motionSource),
    baseSource: input.baseSource,
    motionSource: input.motionSource,
    unknownTokens: [],
    raw: createRawFromState(input)
  };
}

function normalizeFromLayers(
  flags: ResolvedLayerFlags["flags"],
  debug: boolean,
  motionSource: LayerMotionSource
): ResolvedLayerFlags {
  return createResolvedState({
    flags,
    profile: "neutral",
    debug,
    baseSource: "layers",
    motionSource
  });
}

function normalizeFromProfile(
  profile: LayerProfile,
  debug: boolean,
  explicitMotion: { enabled: boolean; active: boolean }
): ResolvedLayerFlags {
  const profileFlags = applyLayerPreset(profile);
  const motionSource: LayerMotionSource = explicitMotion.active ? "motion" : "profile";
  const flags = explicitMotion.active
    ? mergeLayerFlags(profileFlags, { "motion.enabled": explicitMotion.enabled })
    : profileFlags;

  return createResolvedState({
    flags,
    profile,
    debug,
    baseSource: "profile",
    motionSource
  });
}

function normalizeDefault(debug: boolean): ResolvedLayerFlags {
  return createResolvedState({
    flags: createAllLayersOff(),
    profile: "neutral",
    debug,
    baseSource: "default",
    motionSource: "default"
  });
}

export function LayerFlagsProvider({ initialResolved, children }: LayerFlagsProviderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [resolved, setResolved] = useState<ResolvedLayerFlags>(initialResolved);
  const userInitiatedSyncRef = useRef(false);

  const setLayer = useCallback((id: LayerId, on: boolean) => {
    userInitiatedSyncRef.current = true;

    setResolved((previous) => {
      const flags = mergeLayerFlags(previous.flags, { [id]: on });
      const motionSource =
        id === "motion.enabled"
          ? "motion"
          : previous.motionSource === "motion"
            ? "motion"
            : "layers";

      return normalizeFromLayers(flags, previous.debug, motionSource);
    });
  }, []);

  const setAll = useCallback((on: boolean) => {
    userInitiatedSyncRef.current = true;

    setResolved((previous) => {
      const flags = on ? createAllLayersOn() : createAllLayersOff();
      return normalizeFromLayers(flags, previous.debug, "layers");
    });
  }, []);

  const setProfile = useCallback((profile: LayerProfile) => {
    userInitiatedSyncRef.current = true;

    setResolved((previous) => {
      return normalizeFromProfile(profile, previous.debug, {
        enabled: previous.flags["motion.enabled"],
        active: previous.motionSource === "motion"
      });
    });
  }, []);

  const setMotion = useCallback((on: boolean) => {
    userInitiatedSyncRef.current = true;

    setResolved((previous) => {
      const flags = mergeLayerFlags(previous.flags, { "motion.enabled": on });
      return createResolvedState({
        flags,
        profile: previous.profile,
        debug: previous.debug,
        baseSource: previous.baseSource,
        motionSource: "motion"
      });
    });
  }, []);

  const resetNeutral = useCallback(() => {
    userInitiatedSyncRef.current = true;
    setResolved((previous) => normalizeDefault(previous.debug));
  }, []);

  useEffect(() => {
    const incomingSignature = getResolvedSignature(initialResolved);
    setResolved((previous) =>
      getResolvedSignature(previous) === incomingSignature ? previous : initialResolved
    );
  }, [initialResolved]);

  useEffect(() => {
    applyLayerFlagsToDom({
      flags: resolved.flags,
      source: resolved.source,
      profile: resolved.profile
    });

    if (process.env["NODE_ENV"] !== "production" && resolved.unknownTokens.length > 0) {
      // Preserve visibility of URL mistakes without breaking rendering.
      console.warn("[layers] Ignored unknown layer tokens:", resolved.unknownTokens.join(", "));
    }
  }, [resolved]);

  useEffect(() => {
    return () => {
      clearLayerFlagsFromDom();
    };
  }, []);

  useEffect(() => {
    if (!userInitiatedSyncRef.current) {
      return;
    }

    const current = new URLSearchParams(searchParams.toString());
    const next = createLayerFlagsQueryFromResolved(resolved, current);

    const currentString = current.toString();
    const nextString = next.toString();

    if (currentString !== nextString) {
      const target = nextString.length > 0 ? `${pathname}?${nextString}` : pathname;
      router.replace(target, { scroll: false });
    }

    userInitiatedSyncRef.current = false;
  }, [pathname, resolved, router, searchParams]);

  const contextValue = useMemo(
    () => ({
      resolved,
      flags: resolved.flags,
      enabledLayers: extractEnabledLayerIds(resolved.flags),
      setLayer,
      setAll,
      setProfile,
      setMotion,
      resetNeutral
    }),
    [resolved, resetNeutral, setAll, setLayer, setMotion, setProfile]
  );

  return <LayerFlagsContext.Provider value={contextValue}>{children}</LayerFlagsContext.Provider>;
}
