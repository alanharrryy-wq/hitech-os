"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type HTMLAttributes,
  type ReactNode
} from "react";
import { cn } from "../../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../../lib/focus-ring.js";

interface PopoverContextValue {
  readonly open: boolean;
  readonly setOpen: (open: boolean) => void;
  readonly triggerRef: React.RefObject<HTMLElement | null>;
  readonly contentRef: React.RefObject<HTMLDivElement | null>;
}

const PopoverContext = createContext<PopoverContextValue | null>(null);

function usePopoverContext(): PopoverContextValue {
  const context = useContext(PopoverContext);
  if (!context) {
    throw new Error("Popover components must be used within <PopoverRoot>");
  }
  return context;
}

export interface PopoverRootProps {
  readonly defaultOpen?: boolean;
  readonly open?: boolean;
  readonly onOpenChange?: (open: boolean) => void;
  readonly children: ReactNode;
}

export function PopoverRoot({ defaultOpen = false, open, onOpenChange, children }: PopoverRootProps) {
  const [internalOpen, setInternalOpen] = useState(defaultOpen);
  const resolvedOpen = open ?? internalOpen;

  const triggerRef = useRef<HTMLElement | null>(null);
  const contentRef = useRef<HTMLDivElement | null>(null);

  const setOpen = useCallback(
    (next: boolean) => {
      if (open === undefined) {
        setInternalOpen(next);
      }
      onOpenChange?.(next);
    },
    [onOpenChange, open]
  );

  useEffect(() => {
    if (!resolvedOpen) {
      return;
    }

    const onPointerDown = (event: MouseEvent) => {
      const target = event.target;
      if (!(target instanceof Node)) {
        return;
      }

      if (contentRef.current?.contains(target) || triggerRef.current?.contains(target)) {
        return;
      }

      setOpen(false);
    };

    const onEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };

    window.addEventListener("mousedown", onPointerDown);
    window.addEventListener("keydown", onEscape);
    return () => {
      window.removeEventListener("mousedown", onPointerDown);
      window.removeEventListener("keydown", onEscape);
    };
  }, [resolvedOpen, setOpen]);

  const value = useMemo<PopoverContextValue>(
    () => ({
      open: resolvedOpen,
      setOpen,
      triggerRef,
      contentRef
    }),
    [resolvedOpen, setOpen]
  );

  return <PopoverContext.Provider value={value}>{children}</PopoverContext.Provider>;
}

export interface PopoverTriggerProps extends HTMLAttributes<HTMLElement> {
  readonly asChild?: boolean;
  readonly children: ReactNode;
}

interface PopoverTriggerElementProps {
  readonly ref?: React.Ref<HTMLElement>;
  readonly onClick?: (event: React.MouseEvent<HTMLElement>) => void;
}

export function PopoverTrigger({ asChild = false, children, className, ...props }: PopoverTriggerProps) {
  const { open, setOpen, triggerRef } = usePopoverContext();

  if (asChild && children && typeof children === "object") {
    const element = children as React.ReactElement<PopoverTriggerElementProps>;
    return (
      <element.type
        {...element.props}
        {...props}
        ref={(node: HTMLElement | null) => {
          triggerRef.current = node;
          const { ref } = element as unknown as { ref?: React.RefCallback<HTMLElement> };
          if (typeof ref === "function") {
            ref(node);
          }
        }}
        aria-expanded={open}
        aria-haspopup="dialog"
        onClick={(event: React.MouseEvent<HTMLElement>) => {
          element.props.onClick?.(event);
          if (!event.defaultPrevented) {
            setOpen(!open);
          }
        }}
      />
    );
  }

  return (
    <button
      type="button"
      ref={(node) => {
        triggerRef.current = node;
      }}
      className={cn("ui-neon-button", FOCUS_RING_CLASS, className)}
      aria-expanded={open}
      aria-haspopup="dialog"
      onClick={() => setOpen(!open)}
      {...(props as React.ButtonHTMLAttributes<HTMLButtonElement>)}
    >
      {children}
    </button>
  );
}

export interface PopoverContentProps extends HTMLAttributes<HTMLDivElement> {
  readonly sideOffset?: number;
}

export function PopoverContent({ className, sideOffset = 8, children, style, ...props }: PopoverContentProps) {
  const { open, triggerRef, contentRef } = usePopoverContext();

  const [coords, setCoords] = useState<{ top: number; left: number; width: number } | null>(null);

  useEffect(() => {
    if (!open || !triggerRef.current) {
      return;
    }

    const rect = triggerRef.current.getBoundingClientRect();
    setCoords({
      top: rect.bottom + sideOffset + window.scrollY,
      left: rect.left + window.scrollX,
      width: rect.width
    });
  }, [open, sideOffset, triggerRef]);

  if (!open || !coords) {
    return null;
  }

  return (
    <div
      ref={contentRef}
      role="dialog"
      className={cn("ui-neon-popover ui-premium-float-004", className)}
      style={{
        position: "absolute",
        top: coords.top,
        left: coords.left,
        minWidth: coords.width,
        zIndex: 60,
        ...style
      }}
      {...props}
    >
      {children}
    </div>
  );
}

export function PopoverCloseButton({ className, children = "Close" }: { className?: string; children?: ReactNode }) {
  const { setOpen } = usePopoverContext();
  return (
    <button
      type="button"
      className={cn("ui-neon-button", className)}
      data-variant="ghost"
      onClick={() => setOpen(false)}
    >
      {children}
    </button>
  );
}
