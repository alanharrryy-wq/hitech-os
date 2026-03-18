import type { RoutedMutationPlan } from "./contracts";

export function assertPlanRoute(plan: RoutedMutationPlan): readonly string[] {
  const diagnostics: string[] = [];
  if (plan.routeAction === "preview" && plan.mutationScope === "accepted-state-transition") {
    diagnostics.push("accepted-state-transition should not route as preview");
  }
  if (plan.routeAction === "commit" && plan.mutationScope === "preview-only") {
    diagnostics.push("preview-only action should not route as commit without explicit commitIntent");
  }
  if (plan.routeAction === "discard" && plan.mutationType !== "draft-discard") {
    diagnostics.push("discard route should use draft-discard mutation type");
  }
  return diagnostics;
}
