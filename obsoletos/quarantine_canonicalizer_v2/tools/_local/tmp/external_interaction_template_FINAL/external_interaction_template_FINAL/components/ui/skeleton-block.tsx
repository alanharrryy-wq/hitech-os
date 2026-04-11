import { cn } from "@/lib/utils";

export interface SkeletonBlockProps {
  className?: string;
  lines?: number;
  pulse?: "soft" | "strong";
}

function shimmerClass(pulse: SkeletonBlockProps["pulse"]) {
  return pulse === "soft" ? "animate-[pulse_2.6s_ease-in-out_infinite] before:animate-[shimmer_2.8s_linear_infinite]" : "animate-pulse before:animate-[shimmer_1.8s_linear_infinite]";
}

export function SkeletonBlock({ className, lines = 1, pulse = "strong" }: SkeletonBlockProps) {
  if (lines <= 1) {
    return (
      <div
        aria-hidden="true"
        className={cn(
          "relative overflow-hidden rounded-lg border border-white/5 bg-white/[0.055] before:absolute before:inset-y-0 before:left-[-20%] before:w-[20%] before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent before:blur-md before:content-['']",
          shimmerClass(pulse),
          className
        )}
      />
    );
  }

  return (
    <div aria-hidden="true" className="grid gap-2">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={cn(
            "relative h-4 overflow-hidden rounded-lg border border-white/5 bg-white/[0.055] before:absolute before:inset-y-0 before:left-[-20%] before:w-[20%] before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent before:blur-md before:content-['']",
            shimmerClass(pulse),
            index === lines - 1 ? "w-4/5" : "w-full"
          )}
        />
      ))}
    </div>
  );
}
