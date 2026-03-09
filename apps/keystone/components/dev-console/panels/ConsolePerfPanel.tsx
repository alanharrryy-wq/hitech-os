"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

function formatMemory(valueMb: number | null) {
  if (valueMb == null || Number.isNaN(valueMb)) return "n/a";
  return `${valueMb.toFixed(1)} MB`;
}

function formatAge(timestamp: string | null): string {
  if (!timestamp) return "none yet";
  const age = Math.max(0, Date.now() - Date.parse(timestamp));
  return `${Math.round(age / 1000)}s`;
}

export function ConsolePerfPanel() {
  const { bridgeStatus, lastDiagnosticsAt, runtime } = useDevConsole();
  const [fps, setFps] = useState(0);
  const [peakFps, setPeakFps] = useState(0);
  const [memoryMb, setMemoryMb] = useState<number | null>(null);
  const framesRef = useRef(0);
  const lastTimeRef = useRef(performance.now());

  useEffect(() => {
    let mounted = true;
    let raf = 0;

    const tick = (now: number) => {
      framesRef.current += 1;
      const elapsed = now - lastTimeRef.current;

      if (elapsed >= 1000) {
        const nextFps = Math.round((framesRef.current * 1000) / elapsed);
        if (mounted) {
          setFps(nextFps);
          setPeakFps((prev) => Math.max(prev, nextFps));

          const perfMaybe = performance as Performance & {
            memory?: {
              usedJSHeapSize?: number;
            };
          };

          const used = perfMaybe.memory?.usedJSHeapSize;
          setMemoryMb(typeof used === "number" ? used / (1024 * 1024) : null);
        }

        framesRef.current = 0;
        lastTimeRef.current = now;
      }

      raf = window.requestAnimationFrame(tick);
    };

    raf = window.requestAnimationFrame(tick);

    return () => {
      mounted = false;
      window.cancelAnimationFrame(raf);
    };
  }, []);

  const perfHint = useMemo(() => {
    if (fps >= 55) return "Healthy";
    if (fps >= 40) return "Watch it";
    return "Heavy";
  }, [fps]);

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Perf meter</div>
        <div className={cls("cardHint")}>
          Lightweight browser telemetry plus runtime freshness clues. Fast enough to catch the obvious GPU novela.
        </div>

        <div className={cls("metricGrid")}>
          <div className={cls("metricCard")}>
            <div className={cls("metricValue")}>{fps}</div>
            <div className={cls("metricLabel")}>FPS</div>
          </div>
          <div className={cls("metricCard")}>
            <div className={cls("metricValue")}>{peakFps}</div>
            <div className={cls("metricLabel")}>Peak FPS</div>
          </div>
          <div className={cls("metricCard")}>
            <div className={cls("metricValue")}>{perfHint}</div>
            <div className={cls("metricLabel")}>Status</div>
          </div>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Runtime pressure</div>
        <div className={cls("kvGrid")}>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Heap used</div>
            <div className={cls("kvValue")}>{formatMemory(memoryMb)}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Bridge</div>
            <div className={cls("kvValue")}>{bridgeStatus}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Diagnostics age</div>
            <div className={cls("kvValue")}>{formatAge(lastDiagnosticsAt)}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Enabled layers</div>
            <div className={cls("kvValue")}>{runtime?.enabledLayerIds.length ?? 0}</div>
          </div>
        </div>
        <pre className={cls("codeBox")}>
{JSON.stringify(
  {
    fps,
    peakFps,
    memoryMb,
    bridgeStatus,
    diagnosticsAge: formatAge(lastDiagnosticsAt),
    enabledLayerIds: runtime?.enabledLayerIds ?? []
  },
  null,
  2
)}
        </pre>
      </section>
    </div>
  );
}
