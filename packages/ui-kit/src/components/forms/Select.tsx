"use client";

import * as SelectPrimitive from "@radix-ui/react-select";
import { cva, type VariantProps } from "class-variance-authority";
import { Check, ChevronDown, ChevronUp } from "lucide-react";
import { forwardRef } from "react";
import { cn } from "../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../lib/focus-ring.js";

const selectTriggerVariants = cva(
  [
    "flex h-9 w-full items-center justify-between rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))]",
    "bg-[hsl(var(--ui-surface-1))] px-3 text-sm text-[hsl(var(--ui-text-1))]",
    "hover:border-[hsl(var(--ui-border-2))]",
    FOCUS_RING_CLASS
  ].join(" "),
  {
    variants: {
      size: {
        sm: "h-8 text-xs",
        md: "h-9 text-sm",
        lg: "h-10 text-sm"
      }
    },
    defaultVariants: {
      size: "md"
    }
  }
);

export type SelectProps = SelectPrimitive.SelectProps;
export const Select = SelectPrimitive.Root;
export const SelectGroup = SelectPrimitive.Group;
export const SelectValue = SelectPrimitive.Value;

export interface SelectTriggerProps
  extends SelectPrimitive.SelectTriggerProps,
    VariantProps<typeof selectTriggerVariants> {}

export const SelectTrigger = forwardRef<HTMLButtonElement, SelectTriggerProps>(
  function SelectTrigger({ className, children, size, ...props }, ref) {
    return (
      <SelectPrimitive.Trigger
        ref={ref}
        className={cn(selectTriggerVariants({ size }), className)}
        {...props}
      >
        {children}
        <SelectPrimitive.Icon asChild>
          <ChevronDown className="h-4 w-4 text-[hsl(var(--ui-text-3))]" />
        </SelectPrimitive.Icon>
      </SelectPrimitive.Trigger>
    );
  }
);

export const SelectScrollUpButton = forwardRef<
  HTMLDivElement,
  SelectPrimitive.SelectScrollUpButtonProps
>(function SelectScrollUpButton({ className, ...props }, ref) {
  return (
    <SelectPrimitive.ScrollUpButton
      ref={ref}
      className={cn(
        "flex cursor-default items-center justify-center py-1 text-[hsl(var(--ui-text-3))]",
        className
      )}
      {...props}
    >
      <ChevronUp className="h-4 w-4" />
    </SelectPrimitive.ScrollUpButton>
  );
});

export const SelectScrollDownButton = forwardRef<
  HTMLDivElement,
  SelectPrimitive.SelectScrollDownButtonProps
>(function SelectScrollDownButton({ className, ...props }, ref) {
  return (
    <SelectPrimitive.ScrollDownButton
      ref={ref}
      className={cn(
        "flex cursor-default items-center justify-center py-1 text-[hsl(var(--ui-text-3))]",
        className
      )}
      {...props}
    >
      <ChevronDown className="h-4 w-4" />
    </SelectPrimitive.ScrollDownButton>
  );
});

export const SelectContent = forwardRef<HTMLDivElement, SelectPrimitive.SelectContentProps>(
  function SelectContent({ className, children, position = "popper", ...props }, ref) {
    return (
      <SelectPrimitive.Portal>
        <SelectPrimitive.Content
          ref={ref}
          className={cn(
            "relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-[var(--ui-core-radius-md)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] shadow-[var(--ui-shadow-2)]",
            className
          )}
          position={position}
          {...props}
        >
          <SelectScrollUpButton />
          <SelectPrimitive.Viewport
            className={cn(
              "p-1",
              position === "popper" &&
                "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]"
            )}
          >
            {children}
          </SelectPrimitive.Viewport>
          <SelectScrollDownButton />
        </SelectPrimitive.Content>
      </SelectPrimitive.Portal>
    );
  }
);

export const SelectLabel = forwardRef<HTMLDivElement, SelectPrimitive.SelectLabelProps>(
  function SelectLabel({ className, ...props }, ref) {
    return (
      <SelectPrimitive.Label
        ref={ref}
        className={cn("px-2 py-1.5 text-xs font-medium text-[hsl(var(--ui-text-3))]", className)}
        {...props}
      />
    );
  }
);

export const SelectItem = forwardRef<HTMLDivElement, SelectPrimitive.SelectItemProps>(
  function SelectItem({ className, children, ...props }, ref) {
    return (
      <SelectPrimitive.Item
        ref={ref}
        className={cn(
          "relative flex w-full cursor-default select-none items-center rounded-[var(--ui-core-radius-sm)] py-1.5 pl-8 pr-2 text-sm outline-none",
          "text-[hsl(var(--ui-text-2))] data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[highlighted]:bg-[hsl(var(--ui-surface-2))]",
          className
        )}
        {...props}
      >
        <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
          <SelectPrimitive.ItemIndicator>
            <Check className="h-4 w-4 text-[hsl(var(--ui-accent))]" />
          </SelectPrimitive.ItemIndicator>
        </span>
        <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
      </SelectPrimitive.Item>
    );
  }
);

export const SelectSeparator = forwardRef<HTMLDivElement, SelectPrimitive.SelectSeparatorProps>(
  function SelectSeparator({ className, ...props }, ref) {
    return (
      <SelectPrimitive.Separator
        ref={ref}
        className={cn("-mx-1 my-1 h-px bg-[hsl(var(--ui-border-1))]", className)}
        {...props}
      />
    );
  }
);
