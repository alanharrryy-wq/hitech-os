"use client";

import type { ReactNode } from "react";
import {
  Badge,
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  cn
} from "@hitech/ui-kit";

export interface NeonButtonProps {
  readonly children: ReactNode;
  readonly onClick?: () => void;
  readonly disabled?: boolean;
  readonly variant?: "solid" | "subtle" | "outline" | "ghost";
  readonly className?: string;
}

export function NeonButton({
  children,
  onClick,
  disabled,
  variant = "solid",
  className
}: NeonButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      variant={variant}
      className={cn(
        "transition-all duration-200",
        "shadow-[0_0_0_0_hsl(var(--ui-accent)/0)] hover:shadow-[0_0_22px_hsl(var(--ui-accent)/0.28)]",
        "active:scale-[0.98]",
        className
      )}
    >
      {children}
    </Button>
  );
}

export interface ChipProps {
  readonly tone?: "neutral" | "accent" | "success" | "warning" | "danger";
  readonly children: ReactNode;
  readonly className?: string;
}

export function Chip({ tone = "neutral", children, className }: ChipProps) {
  return (
    <Badge
      tone={tone}
      className={cn(
        "rounded-full border border-[hsl(var(--ui-border-1))] px-2.5 py-1 text-[11px] tracking-[0.04em]",
        className
      )}
    >
      {children}
    </Badge>
  );
}

export interface DropdownOption {
  readonly value: string;
  readonly label: string;
}

export interface DropdownFieldProps {
  readonly label: string;
  readonly value: string;
  readonly options: readonly DropdownOption[];
  readonly onChange: (next: string) => void;
}

export function DropdownField({ label, value, options, onChange }: DropdownFieldProps) {
  return (
    <label className="grid gap-1.5">
      <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
        {label}
      </span>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </label>
  );
}
