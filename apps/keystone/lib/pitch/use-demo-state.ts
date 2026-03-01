"use client";

import { useCallback, useMemo, useState } from "react";
import {
  applyAction,
  buildDemoScreens,
  createInitialDemoState,
  type DemoRole,
  type PitchDemoAction,
  type PitchDemoScreens,
  type PitchDemoState
} from "./demo-state";

export interface PitchDemoActions {
  readonly dispatch: (action: PitchDemoAction) => void;
  readonly setRole: (role: DemoRole) => void;
  readonly toggleSupplierStatus: () => void;
  readonly toggleDocsComplete: () => void;
  readonly toggleTempExcursion: () => void;
  readonly reset: () => void;
}

export function useDemoState(
  initialState: PitchDemoState = createInitialDemoState()
): readonly [PitchDemoState, PitchDemoActions] {
  const [state, setState] = useState<PitchDemoState>(initialState);

  const dispatch = useCallback(
    (action: PitchDemoAction) => {
      setState((currentState) => applyAction(currentState, action));
    },
    [applyAction]
  );

  const actions = useMemo<PitchDemoActions>(
    () => ({
      dispatch,
      setRole: (role) => {
        dispatch({ type: "SET_ROLE", role });
      },
      toggleSupplierStatus: () => {
        dispatch({
          type: "SET_SUPPLIER_STATUS",
          supplierStatus: state.supplierStatus === "BLOCKED" ? "ACTIVE" : "BLOCKED"
        });
      },
      toggleDocsComplete: () => {
        dispatch({ type: "TOGGLE_DOCS_COMPLETE" });
      },
      toggleTempExcursion: () => {
        dispatch({ type: "TOGGLE_TEMP_EXCURSION" });
      },
      reset: () => {
        dispatch("RESET");
      }
    }),
    [dispatch, state.supplierStatus]
  );

  return [state, actions] as const;
}

export function useDemoScreens(state: PitchDemoState): PitchDemoScreens {
  return useMemo(() => buildDemoScreens(state), [state]);
}
