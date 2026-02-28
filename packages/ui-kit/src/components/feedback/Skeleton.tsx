import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";

const skeletonVariants = cva("ui-skeleton", {
  variants: {
    shape: {
      rect: "",
      pill: "rounded-full",
      circle: "rounded-full"
    }
  },
  defaultVariants: {
    shape: "rect"
  }
});

export interface SkeletonProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {
  readonly width?: number | string;
  readonly height?: number | string;
}

export function Skeleton({ className, shape, width, height, style, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(skeletonVariants({ shape }), className)}
      style={{
        width,
        height,
        ...style
      }}
      {...props}
    />
  );
}
