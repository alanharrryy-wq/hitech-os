import { notFound } from "next/navigation";
import { PitchEngineWorkbench } from "../../../components/pitch-engine";
import {
  hasDebugToken,
  isPitchEngineDevRouteAllowed,
  parseCapabilityMode
} from "../../../lib/scene-studio/scene-access";

interface PitchEnginePageProps {
  readonly searchParams?: Record<string, string | string[] | undefined>;
}

function first(value: string | string[] | undefined): string | null {
  if (Array.isArray(value)) {
    return value[0] ?? null;
  }

  return value ?? null;
}

export default function PitchEnginePage({ searchParams }: PitchEnginePageProps) {
  const requestedMode = parseCapabilityMode(first(searchParams?.mode));
  const debugToken = hasDebugToken(first(searchParams?.debug));
  const access = isPitchEngineDevRouteAllowed({
    debugToken,
    requestedMode
  });

  if (!access.allowed) {
    notFound();
  }

  return <PitchEngineWorkbench requestedMode={requestedMode} />;
}
