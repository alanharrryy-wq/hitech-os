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
  type LayerId,
  type LayerProfile
} from "./layerIds.js";
import {
  createLayerFlagsQueryFromResolved,
  encodeLayersParam,
  resolveLayerFlags,
  type ResolvedLayerFlags,
  type SearchParamsLike
} from "./resolveLayerFlags.js";
import { extractEnabledLayerIds, LayerFlagsContext } from "./useLayerFlags.js";

export interface LayerFlagsProviderProps extends PropsWithChildren {
  readonly initialResolved: ResolvedLayerFlags;
}

function buildRaw(raw: {
  layers?: string | undefined;
  layerProfile?: string | undefined;
  debug?: string | undefined;
}): ResolvedLayerFlags["raw"] {
  return {
    ...(raw.layers !== undefined ? { layers: raw.layers } : {}),
    ...(raw.layerProfile !== undefined ? { layerProfile: raw.layerProfile } : {}),
    ...(raw.debug !== undefined ? { debug: raw.debug } : {})
  };
}

function toSearchParamsLike(params: URLSearchParams): SearchParamsLike {
  const byKey = new Map<string, string[]>();

  params.forEach((value, key) => {
    const current = byKey.get(key) ?? [];
    byKey.set(key, [...current, value]);
  });

  const record: SearchParamsLike = {};
  for (const [key, values] of byKey.entries()) {
    if (values.length === 1) {
      record[key] = values[0];
    } else if (values.length > 1) {
      record[key] = values;
    }
  }

  return record;
}

function getResolvedSignature(resolved: ResolvedLayerFlags): string {
  const enabled = ALL_LAYERS.filter((id) => resolved.flags[id]).join(",");
  return `${resolved.source}|${resolved.profile}|${resolved.debug ? "1" : "0"}|${enabled}`;
}

function normalizeFromLayers(
  flags: ResolvedLayerFlags["flags"],
  debug: boolean
): ResolvedLayerFlags {
  return {
    flags,
    profile: "neutral",
    debug,
    source: "layers",
    raw: buildRaw({
      layers: encodeLayersParam(flags),
      debug: debug ? "1" : undefined
    })
  };
}

function normalizeFromProfile(profile: LayerProfile, debug: boolean): ResolvedLayerFlags {
  return {
    flags: applyLayerPreset(profile),
    profile,
    debug,
    source: "profile",
    raw: buildRaw({
      layerProfile: profile,
      debug: debug ? "1" : undefined
    })
  };
}

function normalizeDefault(debug: boolean): ResolvedLayerFlags {
  return {
    flags: createAllLayersOff(),
    profile: "neutral",
    debug,
    source: "default",
    raw: buildRaw({
      debug: debug ? "1" : undefined
    })
  };
}

export function LayerFlagsProvider({ initialResolved, children }: LayerFlagsProviderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [resolved, setResolved] = useState<ResolvedLayerFlags>(initialResolved);
  const lastAppliedUrlSignatureRef = useRef<string>(getResolvedSignature(initialResolved));

  const setLayer = useCallback((id: LayerId, on: boolean) => {
    setResolved((previous) => {
      const flags = mergeLayerFlags(previous.flags, { [id]: on });
      return normalizeFromLayers(flags, previous.debug);
    });
  }, []);

  const setAll = useCallback((on: boolean) => {
    setResolved((previous) => {
      const flags = on ? createAllLayersOn() : createAllLayersOff();
      return normalizeFromLayers(flags, previous.debug);
    });
  }, []);

  const setProfile = useCallback((profile: LayerProfile) => {
    setResolved((previous) => {
      if (profile === "neutral") {
        return normalizeFromProfile("neutral", previous.debug);
      }
      return normalizeFromProfile(profile, previous.debug);
    });
  }, []);

  const resetNeutral = useCallback(() => {
    setResolved((previous) => normalizeDefault(previous.debug));
  }, []);

  useEffect(() => {
    const fromUrl = resolveLayerFlags(
      toSearchParamsLike(new URLSearchParams(searchParams.toString()))
    );
    const currentSignature = getResolvedSignature(resolved);
    const fromUrlSignature = getResolvedSignature(fromUrl);

    if (
      fromUrlSignature !== currentSignature &&
      fromUrlSignature !== lastAppliedUrlSignatureRef.current
    ) {
      setResolved(fromUrl);
    }
  }, [resolved, searchParams]);

  useEffect(() => {
    const current = new URLSearchParams(searchParams.toString());
    const next = createLayerFlagsQueryFromResolved(resolved, current);

    const currentString = current.toString();
    const nextString = next.toString();

    if (currentString !== nextString) {
      const target = nextString.length > 0 ? `${pathname}?${nextString}` : pathname;
      router.replace(target, { scroll: false });
    }

    lastAppliedUrlSignatureRef.current = getResolvedSignature(resolved);
  }, [pathname, resolved, router, searchParams]);

  const contextValue = useMemo(
    () => ({
      resolved,
      flags: resolved.flags,
      enabledLayers: extractEnabledLayerIds(resolved.flags),
      setLayer,
      setAll,
      setProfile,
      resetNeutral
    }),
    [resolved, resetNeutral, setAll, setLayer, setProfile]
  );

  return <LayerFlagsContext.Provider value={contextValue}>{children}</LayerFlagsContext.Provider>;
}
