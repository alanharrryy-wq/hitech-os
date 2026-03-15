"use client";

import { useEffect, useMemo, useState } from "react";
import { useDevConsole } from "../../DevConsoleContext";
import { DEV_CONSOLE_EVENT_CONTRACTS } from "../../core/console-core-contracts";
import { snapshotConsoleEventListenerCounts } from "../../core/console-core-events";
import styles from "../../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

const POLL_MS = 1000;

export function InspectEventMonitorPanel() {
  const { lastActionResult } = useDevConsole();
  const [listenerSnapshot, setListenerSnapshot] = useState<Readonly<Record<string, number>>>({});

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const sync = () => setListenerSnapshot(snapshotConsoleEventListenerCounts());
    sync();
    const timer = window.setInterval(sync, POLL_MS);
    return () => window.clearInterval(timer);
  }, []);

  const rows = useMemo(
    () =>
      DEV_CONSOLE_EVENT_CONTRACTS.map((contract) => ({
        symbol: contract.symbol,
        eventName: contract.eventName,
        listeners: listenerSnapshot[contract.eventName] ?? 0,
        mustHaveListener: contract.mustHaveListener,
        mustHaveEmitter: contract.mustHaveEmitter
      })),
    [listenerSnapshot]
  );

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Event contract monitor</div>
        <div className={cls("cardHint")}>
          InspectConsole can observe event plumbing health without mutating runtime state.
        </div>

        <div className={cls("list")}>
          {rows.map((row) => (
            <div key={row.symbol} className={cls("profileRow")}>
              <div className={cls("kvValue")}>{row.symbol}</div>
              <div className={cls("kvLabel")}>listeners={row.listeners}</div>
              <div className={cls("kvLabel")}>required={row.mustHaveListener ? "yes" : "no"}</div>
            </div>
          ))}
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Latest action result</div>
        <pre className={cls("codeBox")}>
          {JSON.stringify(
            {
              lastActionResult,
              listenerSnapshot
            },
            null,
            2
          )}
        </pre>
      </section>
    </div>
  );
}
