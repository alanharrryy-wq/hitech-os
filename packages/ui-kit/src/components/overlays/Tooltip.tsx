"use client";

import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import { forwardRef } from "react";
import { cn } from "../../lib/cn.js";

export const TooltipProvider = TooltipPrimitive.Provider;
export const Tooltip = TooltipPrimitive.Root;
export const TooltipTrigger = TooltipPrimitive.Trigger;

export const TooltipContent = forwardRef<HTMLDivElement, TooltipPrimitive.TooltipContentProps>(
  function TooltipContent({ className, sideOffset = 6, ...props }, ref) {
    return (
      <TooltipPrimitive.Portal>
        <TooltipPrimitive.Content
          ref={ref}
          sideOffset={sideOffset}
          className={cn(
            "z-50 max-w-xs rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] px-2.5 py-1.5 text-xs text-[hsl(var(--ui-text-2))] shadow-[var(--ui-shadow-2)]",
            className
          )}
          {...props}
        />
      </TooltipPrimitive.Portal>
    );
  }
);
