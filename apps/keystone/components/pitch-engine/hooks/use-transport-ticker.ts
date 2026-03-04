"use client";

import { useEffect, useRef } from "react";
import { usePitchEngineStore } from "../state/use-pitch-engine-store";

export function useTransportTicker(): void {
  const isPlaying = usePitchEngineStore((state) => state.transport.isPlaying);
  const tickTransport = usePitchEngineStore((state) => state.tickTransport);
  const lastTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isPlaying) {
      lastTimeRef.current = null;
      return;
    }

    let frame = 0;

    const loop = (now: number) => {
      if (lastTimeRef.current === null) {
        lastTimeRef.current = now;
      }

      const delta = now - lastTimeRef.current;
      lastTimeRef.current = now;
      tickTransport(delta);
      frame = window.requestAnimationFrame(loop);
    };

    frame = window.requestAnimationFrame(loop);

    return () => {
      window.cancelAnimationFrame(frame);
      lastTimeRef.current = null;
    };
  }, [isPlaying, tickTransport]);
}
