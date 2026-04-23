import type { SlotBadgeDescriptor } from "@/lib/ui/shell-system/types";

export interface BadgeResolverContext {
  currentPath: string;
}

type BadgeResolver = (context: BadgeResolverContext) => string | undefined;

const badgeResolvers: Record<string, BadgeResolver> = {
  "records.pending": (context) => (context.currentPath.startsWith("/inbox") ? "live" : "queue"),
  "sync.pending": () => "ops"
};

export function resolveBadge(descriptor: SlotBadgeDescriptor | undefined, context: BadgeResolverContext): SlotBadgeDescriptor | undefined {
  if (!descriptor) return undefined;
  if (!descriptor.resolverId) return descriptor;
  const resolvedText = badgeResolvers[descriptor.resolverId]?.(context);
  if (!resolvedText) return descriptor.text ? descriptor : undefined;
  return {
    ...descriptor,
    text: descriptor.text ?? resolvedText
  };
}

