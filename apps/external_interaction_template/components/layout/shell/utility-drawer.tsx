"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { RoundSvgIcon } from "@components/ui/round-svg-icon";
import type { ActionSlotPayload, WidgetSlotPayload } from "@/lib/ui/shell-system";
import type { UiThemeId } from "@/lib/ui/theme-system";
import { cn } from "@/lib/utils";

const DRAWER_EXIT_MS = 170;

export function UtilityDrawer({
  open,
  onClose,
  themeId,
  utilitySlot,
  pluginSlot,
  t
}: {
  open: boolean;
  onClose: () => void;
  themeId: UiThemeId;
  utilitySlot?: ActionSlotPayload;
  pluginSlot?: WidgetSlotPayload;
  t: (key: string) => string;
}) {
  const [isMounted, setIsMounted] = useState(open);
  const [isVisible, setIsVisible] = useState(open);
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!open) {
      setIsVisible(false);
      return;
    }

    setIsMounted(true);
  }, [open]);

  useEffect(() => {
    if (!isMounted) return;

    if (open) {
      const frame = window.requestAnimationFrame(() => setIsVisible(true));
      return () => window.cancelAnimationFrame(frame);
    }

    const timeout = window.setTimeout(() => setIsMounted(false), DRAWER_EXIT_MS);
    return () => window.clearTimeout(timeout);
  }, [isMounted, open]);

  useEffect(() => {
    if (!isVisible) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isVisible, onClose]);

  useEffect(() => {
    if (!isVisible) return;

    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const frame = window.requestAnimationFrame(() => closeButtonRef.current?.focus());

    return () => {
      window.cancelAnimationFrame(frame);
      previous?.focus();
    };
  }, [isVisible]);

  if (!isMounted) return null;

  return (
    <div
      className={cn("utility-drawer-wrap", isVisible ? "utility-drawer-wrap-open" : "utility-drawer-wrap-closing")}
      aria-hidden={!isVisible}
    >
      <button type="button" className="utility-drawer-backdrop" onClick={onClose} aria-label={t("shell.drawer.close")} />
      <aside className="utility-drawer" role="dialog" aria-modal="true" aria-label={t("shell.drawer.title")}>
        <div className="utility-drawer-head">
          <p className="utility-drawer-title">{t("shell.drawer.title")}</p>
          <button ref={closeButtonRef} type="button" className="utility-drawer-close" onClick={onClose}>
            {t("shell.drawer.close")}
          </button>
        </div>

        <div className="utility-drawer-body">
          {utilitySlot?.items?.length ? (
            <section className="grid gap-2">
              <p className="utility-drawer-section">{t("shell.drawer.actions")}</p>
              {utilitySlot.items.map((action) => (
                <Link key={action.id} href={action.href ?? "#"} className="utility-drawer-link" onClick={onClose}>
                  {action.iconName ? (
                    <RoundSvgIcon
                      name={action.iconName}
                      family={action.iconFamily ?? "system"}
                      themeId={themeId}
                      size={14}
                    />
                  ) : null}
                  <span>{t(action.labelKey)}</span>
                </Link>
              ))}
            </section>
          ) : null}

          {pluginSlot?.widgets?.length ? (
            <section className="grid gap-2">
              <p className="utility-drawer-section">{t("shell.drawer.plugins")}</p>
              {pluginSlot.widgets.map((widget) => (
                <div key={widget.id} className="utility-drawer-plugin">
                  <div className="utility-drawer-plugin-head">
                    {widget.icon ? (
                      <RoundSvgIcon
                        name={widget.icon.name}
                        family={widget.icon.family}
                        themeId={themeId}
                        size={14}
                      />
                    ) : null}
                    <span>{t(widget.titleKey)}</span>
                  </div>
                  {widget.summaryKey ? <p className="utility-drawer-plugin-summary">{t(widget.summaryKey)}</p> : null}
                </div>
              ))}
            </section>
          ) : null}
        </div>
      </aside>
    </div>
  );
}
