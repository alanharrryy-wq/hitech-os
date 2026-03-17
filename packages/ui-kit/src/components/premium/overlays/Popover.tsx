"use client";

import * as React from "react";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  isValidElement,
  type HTMLAttributes,
  type MutableRefObject,
  type ReactNode
} from "react";
import { cn } from "../../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../../lib/focus-ring.js";

interface PopoverContextValue {
  readonly open: boolean;
  readonly setOpen: (open: boolean) => void;
  readonly triggerRef: MutableRefObject<HTMLElement | null>;
  readonly contentRef: MutableRefObject<HTMLDivElement | null>;
}

const PopoverContext = createContext<PopoverContextValue | null>(null);

function usePopoverContext(): PopoverContextValue {
  const context = useContext(PopoverContext);
  if (!context) {
    throw new Error("Popover components must be used within <PopoverRoot>");
  }
  return context;
}

function assignElementRef<T>(ref: React.Ref<T> | undefined, value: T | null): void {
  if (!ref) {
    return;
  }

  if (typeof ref === "function") {
    ref(value);
    return;
  }

  (ref as MutableRefObject<T | null>).current = value;
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
  readonly className?: string;
}

interface PopoverTriggerElementProps {
  readonly ref?: React.Ref<HTMLElement>;
  readonly onClick?: (event: React.MouseEvent<HTMLElement>) => void;
  readonly className?: string;
}

export function PopoverTrigger({ asChild = false, children, className, ...props }: PopoverTriggerProps) {
  const { open, setOpen, triggerRef } = usePopoverContext();

  if (asChild && isValidElement<PopoverTriggerElementProps>(children)) {
    const element = children;
    const originalRef = (element as unknown as { ref?: React.Ref<HTMLElement> }).ref;

    return (
      <element.type
        {...element.props}
        {...props}
        className={cn(element.props.className, className)}
        ref={(node: HTMLElement | null) => {
          triggerRef.current = node;
          assignElementRef(originalRef, node);
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
      ref={(node: HTMLButtonElement | null) => {
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
  readonly className?: string;
  readonly children?: React.ReactNode;
  readonly style?: React.CSSProperties;
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
      ref={(node: HTMLDivElement | null) => {
        contentRef.current = node;
      }}
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