import { useCallback, useMemo, useRef, type KeyboardEvent } from "react";
import { cn } from "../../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../../lib/focus-ring.js";

export interface SegmentedOption {
  readonly value: string;
  readonly label: string;
  readonly disabled?: boolean;
}

export interface SegmentedControlProps {
  readonly id?: string;
  readonly ariaLabel: string;
  readonly options: readonly SegmentedOption[];
  readonly value: string;
  readonly onValueChange: (value: string) => void;
  readonly className?: string;
}

function nextEnabledIndex(
  options: readonly SegmentedOption[],
  start: number,
  direction: -1 | 1
): number {
  let cursor = start;
  for (let step = 0; step < options.length; step += 1) {
    cursor = (cursor + direction + options.length) % options.length;
    if (!options[cursor]?.disabled) {
      return cursor;
    }
  }
  return start;
}

export function SegmentedControl({
  id,
  ariaLabel,
  options,
  value,
  onValueChange,
  className
}: SegmentedControlProps) {
  const buttonRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const selectedIndex = useMemo(
    () => options.findIndex((option) => option.value === value),
    [options, value]
  );

  const handleKeyDown = useCallback(
    (index: number, event: KeyboardEvent<HTMLButtonElement>) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight" && event.key !== "Home" && event.key !== "End") {
        return;
      }

      event.preventDefault();
      const direction: -1 | 1 = event.key === "ArrowLeft" ? -1 : 1;

      let targetIndex = index;
      if (event.key === "Home") {
        targetIndex = nextEnabledIndex(options, options.length - 1, 1);
      } else if (event.key === "End") {
        targetIndex = nextEnabledIndex(options, 0, -1);
      } else {
        targetIndex = nextEnabledIndex(options, index, direction);
      }

      const target = options[targetIndex];
      if (!target || target.disabled) {
        return;
      }

      onValueChange(target.value);
      buttonRefs.current[targetIndex]?.focus();
    },
    [onValueChange, options]
  );

  return (
    <div className={cn("ui-segmented-control", className)} role="radiogroup" aria-label={ariaLabel} id={id}>
      {options.map((option, index) => {
        const isActive = option.value === value;
        return (
          <button
            key={option.value}
            ref={(element) => {
              buttonRefs.current[index] = element;
            }}
            type="button"
            role="radio"
            aria-checked={isActive}
            tabIndex={isActive || selectedIndex < 0 ? 0 : -1}
            data-state={isActive ? "active" : "inactive"}
            disabled={option.disabled}
            className={cn("ui-segmented-control__item", FOCUS_RING_CLASS)}
            onClick={() => onValueChange(option.value)}
            onKeyDown={(event) => {
              handleKeyDown(index, event);
            }}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
