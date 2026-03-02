"use client";

import {
  useEffect,
  useId,
  useRef,
  useState,
  type HTMLAttributes,
  type ReactNode
} from "react";
import { cn } from "../../../lib/cn.js";

export interface TooltipProps {
  readonly content: ReactNode;
  readonly children: ReactNode;
  readonly delayMs?: number;
  readonly sideOffset?: number;
  readonly className?: string;
  readonly contentClassName?: string;
  readonly disabled?: boolean;
}

export function NeonTooltip({
  content,
  children,
  delayMs = 120,
  sideOffset = 8,
  className,
  contentClassName,
  disabled = false
}: TooltipProps) {
  const triggerRef = useRef<HTMLSpanElement | null>(null);
  const [open, setOpen] = useState(false);
  const [coords, setCoords] = useState<{ top: number; left: number } | null>(null);
  const tooltipId = useId();

  useEffect(() => {
    if (!open || !triggerRef.current) {
      return;
    }

    const rect = triggerRef.current.getBoundingClientRect();
    setCoords({
      top: rect.top + window.scrollY - sideOffset,
      left: rect.left + window.scrollX + rect.width / 2
    });
  }, [open, sideOffset]);

  const openTimeout = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (openTimeout.current) {
        window.clearTimeout(openTimeout.current);
      }
    };
  }, []);

  const scheduleOpen = () => {
    if (disabled) {
      return;
    }

    if (openTimeout.current) {
      window.clearTimeout(openTimeout.current);
    }

    openTimeout.current = window.setTimeout(() => {
      setOpen(true);
    }, delayMs);
  };

  const close = () => {
    if (openTimeout.current) {
      window.clearTimeout(openTimeout.current);
      openTimeout.current = null;
    }
    setOpen(false);
  };

  return (
    <span className={cn("relative inline-flex", className)}>
      <span
        ref={triggerRef}
        aria-describedby={open ? tooltipId : undefined}
        onMouseEnter={scheduleOpen}
        onMouseLeave={close}
        onFocus={scheduleOpen}
        onBlur={close}
      >
        {children}
      </span>
      {open && coords ? (
        <span
          id={tooltipId}
          role="tooltip"
          className={cn("ui-neon-tooltip", "pointer-events-none absolute", contentClassName)}
          style={{
            position: "absolute",
            top: coords.top,
            left: coords.left,
            transform: "translate(-50%, -100%)",
            zIndex: 70
          }}
        >
          {content}
        </span>
      ) : null}
    </span>
  );
}

export interface TooltipCardProps extends HTMLAttributes<HTMLDivElement> {
  readonly heading?: ReactNode;
  readonly description?: ReactNode;
}

export function NeonTooltipCard({
  className,
  heading,
  description,
  children,
  ...props
}: TooltipCardProps) {
  return (
    <div className={cn("ui-neon-tooltip", className)} {...props}>
      {heading ? <p className="m-0 text-xs font-semibold uppercase tracking-[0.08em]">{heading}</p> : null}
      {description ? <p className="m-0 mt-1 text-xs">{description}</p> : null}
      {children ? <div className="mt-1 text-xs">{children}</div> : null}
    </div>
  );
}
