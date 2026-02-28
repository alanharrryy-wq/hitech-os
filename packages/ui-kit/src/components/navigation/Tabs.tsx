"use client";

import * as TabsPrimitive from "@radix-ui/react-tabs";
import { forwardRef } from "react";
import { cn } from "../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../lib/focus-ring.js";

export const Tabs = TabsPrimitive.Root;

export const TabsList = forwardRef<HTMLDivElement, TabsPrimitive.TabsListProps>(function TabsList(
  { className, ...props },
  ref
) {
  return (
    <TabsPrimitive.List
      ref={ref}
      className={cn(
        "inline-flex h-10 items-center rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))] p-1",
        className
      )}
      {...props}
    />
  );
});

export const TabsTrigger = forwardRef<HTMLButtonElement, TabsPrimitive.TabsTriggerProps>(
  function TabsTrigger({ className, ...props }, ref) {
    return (
      <TabsPrimitive.Trigger
        ref={ref}
        className={cn(
          "inline-flex h-8 items-center justify-center whitespace-nowrap rounded-[var(--ui-core-radius-sm)] px-3 text-sm font-medium",
          "text-[hsl(var(--ui-text-2))] transition-colors data-[state=active]:bg-[hsl(var(--ui-surface-1))] data-[state=active]:text-[hsl(var(--ui-text-1))]",
          FOCUS_RING_CLASS,
          className
        )}
        {...props}
      />
    );
  }
);

export const TabsContent = forwardRef<HTMLDivElement, TabsPrimitive.TabsContentProps>(
  function TabsContent({ className, ...props }, ref) {
    return (
      <TabsPrimitive.Content ref={ref} className={cn("mt-3 outline-none", className)} {...props} />
    );
  }
);
