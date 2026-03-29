
import { type EntityRef, type StructureTreeProjection, refKey } from "./contracts";

export type TreeNavigationDirection = "up" | "down" | "home" | "end";

export function moveTreeFocus(projection: StructureTreeProjection, current: EntityRef | null, direction: TreeNavigationDirection): EntityRef | null {
  const order = projection.flatOrder;
  if (order.length === 0) return null;
  const currentIndex = current ? order.findIndex((item) => refKey(item) === refKey(current)) : -1;

  switch (direction) {
    case "home":
      return order[0] ?? null;
    case "end":
      return order[order.length - 1] ?? null;
    case "up":
      return order[Math.max(0, currentIndex <= 0 ? 0 : currentIndex - 1)] ?? null;
    case "down":
      return order[Math.min(order.length - 1, currentIndex < 0 ? 0 : currentIndex + 1)] ?? null;
  }
}
