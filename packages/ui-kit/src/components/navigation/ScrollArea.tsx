"use client";

import * as ScrollAreaPrimitive from "@radix-ui/react-scroll-area";
import { forwardRef } from "react";
import { cn } from "../../lib/cn.js";

export interface ScrollAreaProps extends ScrollAreaPrimitive.ScrollAreaProps {
  readonly edgeFade?: boolean;
}

export const ScrollArea = forwardRef<HTMLDivElement, ScrollAreaProps>(function ScrollArea(
  { className, children, edgeFade = true, ...props },
  ref
) {
  return (
    <ScrollAreaPrimitive.Root
      ref={ref}
      className={cn("ui-scroll-area ui-premium-scroll-area", className)}
      {...props}
    >
      <ScrollAreaPrimitive.Viewport className="h-full w-full rounded-[inherit]">
        {children}
      </ScrollAreaPrimitive.Viewport>
      {edgeFade ? (
        <>
          <span className="ui-premium-scroll-area__fade-top" aria-hidden="true" />
          <span className="ui-premium-scroll-area__fade-bottom" aria-hidden="true" />
        </>
      ) : null}
      <ScrollBar />
      <ScrollAreaPrimitive.Corner />
    </ScrollAreaPrimitive.Root>
  );
});

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
        <ScrollAreaPrimitive.ScrollAreaThumb className="relative flex-1 rounded-full ui-premium-gradient-subtle-018" />
      </ScrollAreaPrimitive.ScrollAreaScrollbar>
    );
  }
);
