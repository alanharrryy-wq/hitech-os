"use client";

import type { KeyboardEvent, ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface FilterPillOption<TValue extends string> {
  value: TValue;
  label: string;
  count?: number;
  icon?: ReactNode;
  disabled?: boolean;
}

export interface FilterPillsProps<TValue extends string> {
  options: readonly FilterPillOption<TValue>[];
  value: TValue;
  onChange: (value: TValue) => void;
  ariaLabel?: string;
  size?: "sm" | "md";
  wrap?: boolean;
  className?: string;
}

export function FilterPills<TValue extends string>({
  options,
  value,
  onChange,
  ariaLabel = "Filter options",
  size = "md",
  wrap = true,
  className
}: FilterPillsProps<TValue>) {
  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>, optionValue: TValue) {
    const currentIndex = options.findIndex((option) => option.value === optionValue);
    if (currentIndex < 0) return;

    const enabled = options.filter((option) => !option.disabled);
    const enabledIndex = enabled.findIndex((option) => option.value === optionValue);
    if (enabledIndex < 0) return;

    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      event.preventDefault();
      onChange(enabled[(enabledIndex + 1) % enabled.length]!.value);
    }
    if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      event.preventDefault();
      onChange(enabled[(enabledIndex - 1 + enabled.length) % enabled.length]!.value);
    }
    if (event.key === "Home") {
      event.preventDefault();
      onChange(enabled[0]!.value);
    }
    if (event.key === "End") {
      event.preventDefault();
      onChange(enabled[enabled.length - 1]!.value);
    }
  }

  return (
    <div className={cn("flex gap-2", wrap ? "flex-wrap" : "overflow-x-auto pb-1", className)} role="tablist" aria-label={ariaLabel}>
      {options.map((option) => {
        const active = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            role="tab"
            aria-selected={active}
            aria-pressed={active}
            disabled={option.disabled}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(option.value)}
            onKeyDown={(event) => onKeyDown(event, option.value)}
            className={cn(
              "group inline-flex items-center gap-2 rounded-full border transition outline-none focus-visible:ring-2 focus-visible:ring-accent/55 disabled:pointer-events-none disabled:opacity-40",
              size === "sm" ? "h-8 px-3 text-xs" : "h-9 px-3.5 text-sm",
              active
                ? "border-accent/35 bg-accent/16 text-accent shadow-[0_0_24px_rgba(128,226,255,0.08)]"
                : "border-white/10 bg-white/5 text-muted hover:border-white/15 hover:bg-white/7 hover:text-text"
            )}
          >
            {option.icon ? <span className="shrink-0">{option.icon}</span> : null}
            <span className="font-medium">{option.label}</span>
            {typeof option.count === "number" ? (
              <span className={cn("inline-flex min-w-6 items-center justify-center rounded-full px-1.5 text-[11px] font-semibold", active ? "bg-accent/18 text-accent" : "bg-white/8 text-muted")}>
                {option.count}
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
