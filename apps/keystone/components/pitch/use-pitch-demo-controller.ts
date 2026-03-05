"use client";

import { useCallback, useMemo, useState } from "react";
import {
  applyPitchDemoAction,
  createInitialDemoState,
  cycleDocumentLifecycle,
  getDemoAffordances,
  getGuardIndicators,
  getHoldState,
  setRole as setDemoRole,
  setSupplierStatus as setDemoSupplierStatus,
  setTempExcursion as setDemoTempExcursion,
  type CreateDemoStateInput,
  type DemoDocumentId,
  type DemoRole,
  type DemoSupplierStatus,
  type PitchDemoState
} from "../../lib/pitch/demo-state";

export interface PitchDemoController {
  readonly state: PitchDemoState;
  readonly guards: ReturnType<typeof getGuardIndicators>;
  readonly hold: ReturnType<typeof getHoldState>;
  readonly affordances: ReturnType<typeof getDemoAffordances>;
  readonly setRole: (role: DemoRole) => void;
  readonly setSupplierStatus: (status: DemoSupplierStatus) => void;
  readonly toggleDocumentLifecycle: (documentId: DemoDocumentId) => void;
  readonly setTempExcursion: (nextValue: boolean) => void;
  readonly advance: () => void;
  readonly reset: () => void;
  readonly forceQuarantine: () => void;
}

export function usePitchDemoController(seed?: CreateDemoStateInput): PitchDemoController {
  const [state, setState] = useState<PitchDemoState>(() => createInitialDemoState(seed));

  const guards = useMemo(() => getGuardIndicators(state), [state]);
  const hold = useMemo(() => getHoldState(state), [state]);
  const affordances = useMemo(() => getDemoAffordances(state), [state]);

  const setRole = useCallback((role: DemoRole) => {
    setState((current) => setDemoRole(current, role));
  }, []);

  const setSupplierStatus = useCallback((status: DemoSupplierStatus) => {
    setState((current) => setDemoSupplierStatus(current, status));
  }, []);

  const toggleDocumentLifecycle = useCallback((documentId: DemoDocumentId) => {
    setState((current) => cycleDocumentLifecycle(current, documentId));
  }, []);

  const setTempExcursion = useCallback((nextValue: boolean) => {
    setState((current) => setDemoTempExcursion(current, nextValue));
  }, []);

  const advance = useCallback(() => {
    setState((current) => applyPitchDemoAction(current, "ADVANCE"));
  }, []);

  const reset = useCallback(() => {
    setState((current) => applyPitchDemoAction(current, "RESET"));
  }, []);

  const forceQuarantine = useCallback(() => {
    setState((current) => applyPitchDemoAction(current, "FORCE_QUARANTINE"));
  }, []);

  return {
    state,
    guards,
    hold,
    affordances,
    setRole,
    setSupplierStatus,
    toggleDocumentLifecycle,
    setTempExcursion,
    advance,
    reset,
    forceQuarantine
  };
}
