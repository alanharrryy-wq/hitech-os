import { cn } from "@hitech/ui-kit";

export interface BulletListProps {
  readonly bullets: readonly string[];
  readonly className?: string;
  readonly itemClassName?: string;
}

export function BulletList({ bullets, className, itemClassName }: BulletListProps) {
  return (
    <ul className={cn("m-0 grid list-disc gap-1 pl-5", className)}>
      {bullets.map((bullet) => (
        <li
          key={bullet}
          className={cn("text-sm leading-6 text-[hsl(var(--ui-text-1))]", itemClassName)}
        >
          {bullet}
        </li>
      ))}
    </ul>
  );
}
