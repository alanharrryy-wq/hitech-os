"use client";

import * as ScrollAreaPrimitive from "@radix-ui/react-scroll-area";
import { forwardRef } from "react";
import { cn } from "../../lib/cn.js";

export const ScrollArea = forwardRef<HTMLDivElement, ScrollAreaPrimitive.ScrollAreaProps>(
  function ScrollArea({ className, children, ...props }, ref) {
    return (
      <ScrollAreaPrimitive.Root ref={ref} className={cn("ui-scroll-area", className)} {...props}>
        <ScrollAreaPrimitive.Viewport className="h-full w-full rounded-[inherit]">
          {children}
        </ScrollAreaPrimitive.Viewport>
        <ScrollBar />
        <ScrollAreaPrimitive.Corner />
      </ScrollAreaPrimitive.Root>
    );
  }
);

export const ScrollBar = forwardRef<HTMLDivElement, ScrollAreaPrimitive.ScrollAreaScrollbarProps>(
  function ScrollBar({ className, orientation = "vertical", ...props }, ref) {
    return (
      <ScrollAreaPrimitive.ScrollAreaScrollbar
        ref={ref}
        orientation={orientation}
        className={cn(
          "flex touch-none select-none rounded-full p-0.5 transition-colors",
          orientation === "vertical" && "h-full w-2.5 border-l border-l-transparent",
          orientation === "horizontal" && "h-2.5 flex-col border-t border-t-transparent",
          className
        )}
        {...props}
      >
        <ScrollAreaPrimitive.ScrollAreaThumb className="relative flex-1 rounded-full bg-[hsl(var(--ui-border-2))]" />
      </ScrollAreaPrimitive.ScrollAreaScrollbar>
    );
  }
);
