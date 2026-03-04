import { notFound } from "next/navigation";
import type { SearchParamsLike } from "@hitech/ui-kit";
import { resolveSceneStudioAccess } from "../../../lib/scene-studio";
import { SceneStudioPage } from "../../../components/scene-studio/scene-studio-page";

interface SceneStudioRouteProps {
  readonly searchParams?: SearchParamsLike | Promise<SearchParamsLike>;
}

export const dynamic = "force-dynamic";

export default async function SceneStudioRoute({ searchParams }: SceneStudioRouteProps) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  const access = resolveSceneStudioAccess(resolvedSearchParams);

  if (!access.allowed) {
    notFound();
  }

  return <SceneStudioPage />;
}
