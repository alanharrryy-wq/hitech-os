import { cn } from "../lib/cn.js";
import { resolveMotionDataAttrs, resolveMotionGate, type ReducedMotionInput } from "./reducedMotion.js";
import type { MotionPrimitive } from "./primitives.js";

export interface ApplyMotionOptions extends ReducedMotionInput {
  readonly className?: string;
  readonly primitives?: ReadonlyArray<MotionPrimitive | null | false | undefined>;
  readonly attrs?: Readonly<Record<string, string | undefined>>;
  readonly style?: Readonly<Record<string, string | undefined>>;
}

export interface AppliedMotion {
  readonly className: string;
  readonly attrs: Record<string, string>;
  readonly style: Record<string, string>;
}

function mergeStringRecord(
  base: Record<string, string>,
  incoming?: Readonly<Record<string, string | undefined>>
): Record<string, string> {
  if (!incoming) {
    return base;
  }

  for (const [key, value] of Object.entries(incoming)) {
    if (value !== undefined) {
      base[key] = value;
    }
  }

  return base;
}

export function applyMotion(options: ApplyMotionOptions = {}): AppliedMotion {
  const gate = resolveMotionGate(options);
  const primitiveList = (options.primitives ?? []).filter(Boolean) as MotionPrimitive[];

  const className = cn(
    "ui-motion-root",
    options.className,
    ...primitiveList.map((primitive) => primitive.className)
  );

  const attrs = mergeStringRecord({}, resolveMotionDataAttrs(gate));
  mergeStringRecord(attrs, options.attrs);

  const style = mergeStringRecord({}, options.style);

  for (const primitive of primitiveList) {
    mergeStringRecord(attrs, primitive.attrs);
    mergeStringRecord(style, primitive.style);
  }

  return {
    className,
    attrs,
    style
  };
}
