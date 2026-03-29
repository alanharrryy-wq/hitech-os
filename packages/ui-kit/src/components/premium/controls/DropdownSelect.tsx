"use client";

import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactNode
} from "react";
import { cn } from "../../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../../lib/focus-ring.js";

export interface DropdownOption {
  readonly value: string;
  readonly label: string;
  readonly description?: string;
  readonly disabled?: boolean;
  readonly icon?: ReactNode;
}

export interface DropdownSelectProps {
  readonly id?: string;
  readonly options: readonly DropdownOption[];
  readonly value?: string;
  readonly defaultValue?: string;
  readonly placeholder?: string;
  readonly label?: string;
  readonly disabled?: boolean;
  readonly className?: string;
  readonly triggerClassName?: string;
  readonly menuClassName?: string;
  readonly onValueChange?: (value: string) => void;
}

function firstEnabledOptionIndex(options: readonly DropdownOption[]): number {
  return options.findIndex((option) => !option.disabled);
}

function nextEnabledOptionIndex(
  options: readonly DropdownOption[],
  startIndex: number,
  direction: 1 | -1
): number {
  if (options.length === 0) {
    return -1;
  }

  let cursor = startIndex;
  for (let i = 0; i < options.length; i += 1) {
    cursor = (cursor + direction + options.length) % options.length;
    if (!options[cursor]?.disabled) {
      return cursor;
    }
  }

  return startIndex;
}

export function DropdownSelect({
  id,
  options,
  value,
  defaultValue,
  placeholder = "Select option",
  label,
  disabled = false,
  className,
  triggerClassName,
  menuClassName,
  onValueChange
}: DropdownSelectProps) {
  const generatedId = useId();
  const baseId = id ?? `dropdown-select-${generatedId}`;
  const listboxId = `${baseId}-listbox`;

  const [internalValue, setInternalValue] = useState(defaultValue ?? "");
  const [open, setOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(() =>
    firstEnabledOptionIndex(options)
  );

  const rootRef = useRef<HTMLDivElement | null>(null);

  const currentValue = value ?? internalValue;
  const selectedOption = useMemo(
    () => options.find((option) => option.value === currentValue),
    [currentValue, options]
  );

  const selectedIndex = useMemo(
    () => options.findIndex((option) => option.value === currentValue),
    [currentValue, options]
  );

  useEffect(() => {
    if (!open) {
      return;
    }

    const handler = (event: MouseEvent) => {
      const target = event.target;
      if (!(target instanceof Node)) {
        return;
      }
      if (!rootRef.current?.contains(target)) {
        setOpen(false);
      }
    };

    window.addEventListener("mousedown", handler);
    return () => {
      window.removeEventListener("mousedown", handler);
    };
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }

    if (selectedIndex >= 0 && !options[selectedIndex]?.disabled) {
      setHighlightedIndex(selectedIndex);
      return;
    }

    setHighlightedIndex(firstEnabledOptionIndex(options));
  }, [open, options, selectedIndex]);

  const commit = useCallback(
    (nextValue: string) => {
      if (value === undefined) {
        setInternalValue(nextValue);
      }
      onValueChange?.(nextValue);
      setOpen(false);
    },
    [onValueChange, value]
  );

  const onTriggerKeyDown = useCallback(
    (event: KeyboardEvent<HTMLButtonElement>) => {
      if (disabled) {
        return;
      }

      switch (event.key) {
        case "ArrowDown": {
          event.preventDefault();
          if (!open) {
            setOpen(true);
            return;
          }
          setHighlightedIndex((current) => {
            const seed = current < 0 ? firstEnabledOptionIndex(options) : current;
            return nextEnabledOptionIndex(options, seed, 1);
          });
          break;
        }
        case "ArrowUp": {
          event.preventDefault();
          if (!open) {
            setOpen(true);
            return;
          }
          setHighlightedIndex((current) => {
            const seed = current < 0 ? firstEnabledOptionIndex(options) : current;
            return nextEnabledOptionIndex(options, seed, -1);
          });
          break;
        }
        case "Enter":
        case " ": {
          event.preventDefault();
          if (!open) {
            setOpen(true);
            return;
          }
          const target = options[highlightedIndex];
          if (target && !target.disabled) {
            commit(target.value);
          }
          break;
        }
        case "Escape": {
          if (open) {
            event.preventDefault();
            setOpen(false);
          }
          break;
        }
        default:
          break;
      }
    },
    [commit, disabled, highlightedIndex, open, options]
  );

  return (
    <div ref={rootRef} className={cn("ui-dropdown-select", className)}>
      {label ? (
        <label htmlFor={baseId} className="mb-2 block text-xs font-medium text-[hsl(var(--ui-text-2))]">
          {label}
        </label>
      ) : null}
      <button
        id={baseId}
        type="button"
        role="combobox"
        aria-expanded={open}
        aria-controls={listboxId}
        aria-haspopup="listbox"
        aria-activedescendant={highlightedIndex >= 0 ? `${baseId}-option-${highlightedIndex}` : undefined}
        disabled={disabled}
        className={cn("ui-dropdown-select__trigger", FOCUS_RING_CLASS, triggerClassName)}
        onClick={() => {
          if (!disabled) {
            setOpen((previous) => !previous);
          }
        }}
        onKeyDown={onTriggerKeyDown}
      >
        <span className="truncate">
          {selectedOption ? selectedOption.label : <span className="opacity-70">{placeholder}</span>}
        </span>
        <span aria-hidden="true">▾</span>
      </button>

      {open ? (
        <div
          id={listboxId}
          role="listbox"
          tabIndex={-1}
          className={cn("ui-dropdown-select__menu", menuClassName)}
        >
          {options.map((option, index) => {
            const highlighted = index === highlightedIndex;
            const selected = option.value === currentValue;
            return (
              <button
                key={option.value}
                id={`${baseId}-option-${index}`}
                type="button"
                role="option"
                aria-selected={selected}
                disabled={option.disabled}
                data-highlighted={highlighted}
                className="ui-dropdown-select__option"
                onMouseEnter={() => {
                  if (!option.disabled) {
                    setHighlightedIndex(index);
                  }
                }}
                onClick={() => {
                  if (!option.disabled) {
                    commit(option.value);
                  }
                }}
              >
                <span className="flex min-w-0 items-center gap-2">
                  {option.icon ? <span aria-hidden="true">{option.icon}</span> : null}
                  <span className="min-w-0">
                    <span className="block truncate">{option.label}</span>
                    {option.description ? (
                      <span className="block text-xs text-[hsl(var(--ui-text-3))]">{option.description}</span>
                    ) : null}
                  </span>
                </span>
                {selected ? <span aria-hidden="true">✓</span> : null}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
