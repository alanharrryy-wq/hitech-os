"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { forwardRef, type HTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../lib/focus-ring.js";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogPortal = DialogPrimitive.Portal;
export const DialogClose = DialogPrimitive.Close;

export const DialogOverlay = forwardRef<HTMLDivElement, DialogPrimitive.DialogOverlayProps>(
  function DialogOverlay({ className, ...props }, ref) {
    return (
      <DialogPrimitive.Overlay
        ref={ref}
        className={cn(
          "fixed inset-0 z-50 bg-[hsl(var(--ui-text-1)/0.35)] data-[state=open]:animate-in data-[state=closed]:animate-out",
          className
        )}
        {...props}
      />
    );
  }
);

export const DialogContent = forwardRef<HTMLDivElement, DialogPrimitive.DialogContentProps>(
  function DialogContent({ className, children, ...props }, ref) {
    return (
      <DialogPortal>
        <DialogOverlay />
        <DialogPrimitive.Content
          ref={ref}
          className={cn(
            "fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 -translate-y-1/2",
            "rounded-[var(--ui-core-radius-lg)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-5 shadow-[var(--ui-shadow-3)]",
            "data-[state=open]:animate-in data-[state=closed]:animate-out",
            className
          )}
          {...props}
        >
          {children}
          <DialogPrimitive.Close
            className={cn(
              "absolute right-3 top-3 inline-flex h-7 w-7 items-center justify-center rounded-[var(--ui-core-radius-sm)]",
              "text-[hsl(var(--ui-text-3))] hover:bg-[hsl(var(--ui-surface-2))] hover:text-[hsl(var(--ui-text-1))]",
              FOCUS_RING_CLASS
            )}
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>
        </DialogPrimitive.Content>
      </DialogPortal>
    );
  }
);

export const DialogHeader = ({ className, ...props }: HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("mb-3 flex flex-col gap-1.5 text-left", className)} {...props} />
);

export const DialogFooter = ({ className, ...props }: HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("mt-4 flex flex-wrap justify-end gap-2", className)} {...props} />
);

export const DialogTitle = forwardRef<HTMLHeadingElement, DialogPrimitive.DialogTitleProps>(
  function DialogTitle({ className, ...props }, ref) {
    return (
      <DialogPrimitive.Title
        ref={ref}
        className={cn("text-base font-semibold text-[hsl(var(--ui-text-1))]", className)}
        {...props}
      />
    );
  }
);

export const DialogDescription = forwardRef<
  HTMLParagraphElement,
  DialogPrimitive.DialogDescriptionProps
>(function DialogDescription({ className, ...props }, ref) {
  return (
    <DialogPrimitive.Description
      ref={ref}
      className={cn("text-sm text-[hsl(var(--ui-text-3))]", className)}
      {...props}
    />
  );
});
