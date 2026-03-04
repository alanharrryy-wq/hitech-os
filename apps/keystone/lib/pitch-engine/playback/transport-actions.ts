export interface TransportLoadPayload {
  readonly durationMs: number;
  readonly stepCount: number;
}

export type TransportAction =
  | { readonly type: "transport/load"; readonly payload: TransportLoadPayload }
  | { readonly type: "transport/play" }
  | { readonly type: "transport/pause" }
  | { readonly type: "transport/stop" }
  | { readonly type: "transport/seek"; readonly payload: { readonly positionMs: number } }
  | { readonly type: "transport/tick"; readonly payload: { readonly deltaMs: number } }
  | { readonly type: "transport/set-step"; readonly payload: { readonly stepIndex: number } }
  | { readonly type: "transport/set-rate"; readonly payload: { readonly playbackRate: number } }
  | { readonly type: "transport/toggle-loop"; readonly payload?: { readonly loop?: boolean } };

export const transportActions = {
  load: (payload: TransportLoadPayload): TransportAction => ({
    type: "transport/load",
    payload
  }),
  play: (): TransportAction => ({
    type: "transport/play"
  }),
  pause: (): TransportAction => ({
    type: "transport/pause"
  }),
  stop: (): TransportAction => ({
    type: "transport/stop"
  }),
  seek: (positionMs: number): TransportAction => ({
    type: "transport/seek",
    payload: {
      positionMs
    }
  }),
  tick: (deltaMs: number): TransportAction => ({
    type: "transport/tick",
    payload: {
      deltaMs
    }
  }),
  setStep: (stepIndex: number): TransportAction => ({
    type: "transport/set-step",
    payload: {
      stepIndex
    }
  }),
  setRate: (playbackRate: number): TransportAction => ({
    type: "transport/set-rate",
    payload: {
      playbackRate
    }
  }),
  toggleLoop: (loop?: boolean): TransportAction => ({
    type: "transport/toggle-loop",
    payload: {
      loop
    }
  })
};
